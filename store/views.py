from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Category, Product, CartItem, Order, OrderItem


def ensure_session(request):
    if not request.session.session_key:
        request.session.create()
    return request.session.session_key


def get_cart_items(request):
    if request.user.is_authenticated:
        return CartItem.objects.filter(user=request.user)
    session_id = ensure_session(request)
    return CartItem.objects.filter(session_id=session_id)


def index(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'index.html', {
        'products': products,
        'banner_products': products[:3],
        'categories': categories,
    })


def product_list(request):
    categories = Category.objects.all()
    products = Product.objects.filter(is_active=True)

    selected_category = request.GET.get('category', '')
    search_query = request.GET.get('q', '').strip()
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    if selected_category:
        products = products.filter(category_id=selected_category)

    if search_query:
        products = products.filter(
            Q(name__icontains=search_query) | Q(description__icontains=search_query)
        )

    if min_price:
        try:
            products = products.filter(price__gte=min_price)
        except ValueError:
            pass

    if max_price:
        try:
            products = products.filter(price__lte=max_price)
        except ValueError:
            pass

    paginator = Paginator(products, 12)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    return render(request, 'list.html', {
        'categories': categories,
        'page_obj': page_obj,
        'search_query': search_query,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    return render(request, 'product.html', {'product': product})


def login_view(request):
    error = ''
    if request.method == 'POST':
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        user = User.objects.filter(email__iexact=email).first()
        if user:
            user = authenticate(request, username=user.username, password=password)
            if user:
                login(request, user)
                return redirect('shop:index')
        error = 'Неверный email или пароль.'
    return render(request, 'auth.html', {'error': error})


def logout_view(request):
    logout(request)
    return redirect('shop:login')


def register_view(request):
    error = ''
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')

        if not name or not email or not password:
            error = 'аполните все поля.'
        elif User.objects.filter(email__iexact=email).exists():
            error = 'ользователь с таким email уже существует.'
        else:
            username = email
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=name,
            )
            login(request, user)
            return redirect('shop:index')
    return render(request, 'register.html', {'error': error})


def cart_view(request):
    cart_items = get_cart_items(request)
    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'cart_total': cart_total,
    })


def cart_add(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    if request.method == 'POST':
        quantity = request.POST.get('quantity', '1')
        try:
            quantity = int(quantity)
        except (TypeError, ValueError):
            quantity = 1
        if quantity < 1:
            quantity = 1

        if request.user.is_authenticated:
            item, created = CartItem.objects.get_or_create(
                user=request.user,
                product=product,
                defaults={'quantity': quantity},
            )
        else:
            session_id = ensure_session(request)
            item, created = CartItem.objects.get_or_create(
                session_id=session_id,
                product=product,
                defaults={'quantity': quantity},
            )

        if not created:
            item.quantity += quantity
            item.save()

    return redirect('shop:cart')


def cart_remove(request, pk):
    item = get_object_or_404(CartItem, pk=pk)
    if request.user.is_authenticated:
        if item.user != request.user:
            return redirect('shop:cart')
    else:
        if item.session_id != ensure_session(request):
            return redirect('shop:cart')
    item.delete()
    return redirect('shop:cart')


def create_order(request):
    cart_items = get_cart_items(request)
    if not cart_items.exists():
        return redirect('shop:cart')

    error = ''
    if request.method == 'POST':
        full_name = request.POST.get('name', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()

        if not full_name or not phone or not address:
            error = 'аполните все поля для оформления заказа.'
        else:
            total_amount = sum(item.product.price * item.quantity for item in cart_items)
            order = Order.objects.create(
                user=request.user if request.user.is_authenticated else None,
                full_name=full_name,
                phone=phone,
                address=address,
                total_amount=total_amount,
            )
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price,
                )
            cart_items.delete()
            return redirect('shop:order_history')

    cart_total = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'create.html', {
        'cart_items': cart_items,
        'total': cart_total,
        'error': error,
    })


def client_dashboard(request):
    if not request.user.is_authenticated:
        return redirect('shop:login')
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'klient.html', {'orders': orders})


def order_history(request):
    if request.user.is_staff:
        orders = Order.objects.order_by('-created_at')
    elif request.user.is_authenticated:
        orders = Order.objects.filter(user=request.user).order_by('-created_at')
    else:
        return redirect('shop:login')

    return render(request, 'zakaz.html', {'orders': orders})


def product_admin_list(request):
    products = Product.objects.all()
    return render(request, 'spisok.html', {'products': products})


def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('shop:login')

    orders = Order.objects.all()
    total_revenue = orders.aggregate(total=Sum('total_amount'))['total'] or 0
    return render(request, 'admin.html', {
        'order_count': orders.count(),
        'total_revenue': total_revenue,
    })
