from rest_framework .views import APIView 
from rest_framework import viewsets ,status ,filters 
from rest_framework .decorators import action 
from rest_framework .response import Response 
from rest_framework .permissions import AllowAny ,IsAuthenticated 
from django .contrib .auth .models import User 
from django .shortcuts import get_object_or_404 
from django_filters .rest_framework import DjangoFilterBackend 
from store .models import Category ,Product ,CartItem ,Order ,OrderItem 
from .serializers import (
CategorySerializer ,ProductSerializer ,CartItemSerializer ,
OrderSerializer ,OrderCreateSerializer ,RegisterSerializer ,UserSerializer 
)


class CategoryViewSet (viewsets .ReadOnlyModelViewSet ):
    queryset =Category .objects .all ()
    serializer_class =CategorySerializer 
    permission_classes =[AllowAny ]


class ProductViewSet (viewsets .ReadOnlyModelViewSet ):
    queryset =Product .objects .filter (is_active =True )
    serializer_class =ProductSerializer 
    permission_classes =[AllowAny ]
    filter_backends =[filters .SearchFilter ]
    search_fields =['name','description']

    def get_queryset (self ):
        queryset =super ().get_queryset ()

        category_id =self .request .query_params .get ('category',None )
        if category_id :
            queryset =queryset .filter (category_id =category_id )
        return queryset 



class CartViewSet (viewsets .GenericViewSet ):
    serializer_class =CartItemSerializer 
    queryset =CartItem .objects .none ()
    permission_classes =[AllowAny ]

    def get_session_id (self ,request ):
        if request .user .is_authenticated :
            return None 
        session_id =request .session .session_key 
        if not session_id :
            request .session .create ()
            session_id =request .session .session_key 
        return session_id 

    def get_cart_items (self ,request ):
        if request .user .is_authenticated :
            return CartItem .objects .filter (user =request .user )
        session_id =self .get_session_id (request )
        return CartItem .objects .filter (session_id =session_id )

    def list (self ,request ):
        cart_items =self .get_cart_items (request )
        serializer =CartItemSerializer (cart_items ,many =True )
        return Response (serializer .data )

    def create (self ,request ):
        product_id =request .data .get ('product_id')or request .data .get ('product')
        quantity =request .data .get ('quantity',1 )

        if isinstance (product_id ,list ):
            product_id =product_id [0 ]
        if isinstance (quantity ,list ):
            quantity =quantity [0 ]

        try :
            product_id =int (product_id )
            quantity =int (quantity )
        except (TypeError ,ValueError ):
            return Response (
            {'error':'product_id и quantity должны быть числами'},
            status =status .HTTP_400_BAD_REQUEST 
            )

        try :
            product =Product .objects .get (id =product_id ,is_active =True )
        except Product .DoesNotExist :
            return Response (
            {'detail':f'Товар с id={product_id } не найден'},
            status =status .HTTP_404_NOT_FOUND 
            )

        session_id =self .get_session_id (request )

        if request .user .is_authenticated :
            cart_item ,created =CartItem .objects .get_or_create (
            user =request .user ,
            product =product ,
            defaults ={'quantity':quantity }
            )
            if not created :
                cart_item .quantity =quantity 
                cart_item .save ()
        else :
            cart_item ,created =CartItem .objects .get_or_create (
            session_id =session_id ,
            product =product ,
            defaults ={'quantity':quantity }
            )
            if not created :
                cart_item .quantity =quantity 
                cart_item .save ()

        serializer =CartItemSerializer (cart_item )
        return Response (serializer .data ,status =status .HTTP_201_CREATED )

    def destroy (self ,request ,pk =None ):
        if request .user .is_authenticated :
            cart_item =get_object_or_404 (CartItem ,id =pk ,user =request .user )
        else :
            session_id =self .get_session_id (request )
            cart_item =get_object_or_404 (CartItem ,id =pk ,session_id =session_id )
        cart_item .delete ()
        return Response (status =status .HTTP_204_NO_CONTENT )

    @action (detail =False ,methods =['delete'])
    def clear (self ,request ):
        if request .user .is_authenticated :
            CartItem .objects .filter (user =request .user ).delete ()
        else :
            session_id =self .get_session_id (request )
            CartItem .objects .filter (session_id =session_id ).delete ()
        return Response (status =status .HTTP_204_NO_CONTENT )

class OrderViewSet (viewsets .GenericViewSet ):
    serializer_class =OrderSerializer 
    permission_classes =[AllowAny ]

    def get_queryset (self ):
        if self .request .user .is_authenticated :
            return Order .objects .filter (user =self .request .user )
        return Order .objects .none ()

    def list (self ,request ):
        serializer =OrderSerializer (self .get_queryset (),many =True )
        return Response (serializer .data )

    def create (self ,request ):
        serializer =OrderCreateSerializer (data =request .data )
        if serializer .is_valid ():
            session_id =request .session .session_key 
            if not session_id :
                request .session .create ()
                session_id =request .session .session_key 

            cart_items =CartItem .objects .filter (session_id =session_id )

            if not cart_items .exists ():
                return Response ({'error':'Корзина пуста'},status =status .HTTP_400_BAD_REQUEST )

            order =Order .objects .create (
            user =request .user if request .user .is_authenticated else None ,
            full_name =serializer .validated_data ['full_name'],
            phone =serializer .validated_data ['phone'],
            address =serializer .validated_data ['address'],
            comment =serializer .validated_data .get ('comment',''),
            total_amount =0 
            )

            total =0 
            for cart_item in cart_items :
                OrderItem .objects .create (
                order =order ,
                product =cart_item .product ,
                quantity =cart_item .quantity ,
                unit_price =cart_item .product .price 
                )
                total +=cart_item .product .price *cart_item .quantity 

            order .total_amount =total 
            order .save ()

            cart_items .delete ()

            return Response (OrderSerializer (order ).data ,status =status .HTTP_201_CREATED )

        return Response (serializer .errors ,status =status .HTTP_400_BAD_REQUEST )

    def retrieve (self ,request ,pk =None ):
        order =get_object_or_404 (Order ,id =pk )
        serializer =OrderSerializer (order )
        return Response (serializer .data )


class RegisterView (APIView ):
    permission_classes =[AllowAny ]

    def post (self ,request ):
        serializer =RegisterSerializer (data =request .data )
        if serializer .is_valid ():
            user =serializer .save ()
            return Response ({
            'user':UserSerializer (user ).data ,
            'message':'Пользователь успешно создан'
            },status =status .HTTP_201_CREATED )
        return Response (serializer .errors ,status =status .HTTP_400_BAD_REQUEST )


class ProfileView (APIView ):
    permission_classes =[IsAuthenticated ]

    def get (self ,request ):
        serializer =UserSerializer (request .user )
        return Response (serializer .data )

    def put (self ,request ):
        user =request .user 
        user .first_name =request .data .get ('first_name',user .first_name )
        user .last_name =request .data .get ('last_name',user .last_name )
        user .email =request .data .get ('email',user .email )
        user .save ()
        serializer =UserSerializer (user )
        return Response (serializer .data )