from rest_framework import generics, viewsets
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from .permissions import IsOwnerOrReadOnly
from .serializer import *
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import logout
from django.core.mail import send_mail


class RegisterUser(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid()
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        })


# Восстановление пароля по электронной почте
# class ResetPasswordView(APIView):
#     def post(self, request):
#         email = request.data.get('email')
#         user = User.objects.get(email=email)
#         password = User.objects.make_random_password()
#         user.set_password(password)
#         user.save()
#         send_mail(
#             'Password Reset',
#             f'Your new password is: {password}',
#             settings.EMAIL_HOST_USER,
#             [email],
#             fail_silently=False,
#         )
#         return Response({'message': 'Password reset email has been sent'})


# Выход из аккаунта
class LogoutView(APIView):
    permission_classes = (IsAuthenticated, )

    def post(self, request):
        logout(request)
        return Response({'message': 'Logged out successfully'})


# получение данных пользователя
class UserView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user)
        return Response(serializer.data)


#изменение данных пользователя
class UserUpdateView(APIView):
    permission_classes = (IsAuthenticated, )
    #IsOwnerOrReadOnly

    def put(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = UserSerializer(user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


#получение категорий товаров
class CatalogCatList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

#получение всех опубликованных товаров
class CatalogProductsList(generics.ListAPIView):
    queryset = Products.objects.filter(is_published=True)
    serializer_class = ProductCatalogSerializer


#CRUD products for admin
class AdminProductsSet(viewsets.ModelViewSet):
    queryset = Products.objects.all()
    serializer_class = AdminProductsSerializer
    lookup_field = 'slug'
    permission_classes = (IsAdminUser, )

#получение товаров одной категории
class CatalogOneCatList(generics.ListAPIView):
    serializer_class = ProductCatalogSerializer

    def get_queryset(self):
        cat_id = self.kwargs['cat_id']
        queryset = Products.objects.filter(cat_id=cat_id, is_published=True)
        return queryset

#получение 1 товара
class ProductList(generics.ListAPIView):
    serializer_class = ProductSerializer

    def get_queryset(self):
        slug = self.kwargs['slug']
        queryset = Products.objects.filter(slug=slug, is_published=True)
        return queryset


#добавить в корзину
class TrashAddView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = TrashSerializer


#получить записи из корзины
class TrashGetView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        trashProds = Orders.objects.filter(in_trash=True).select_related("ID_product")
        response_data = []
        for trash in trashProds:
            prods = trash.ID_product
            item = {
                "id": trash.id,
                "cost": prods.cost,
                "ID_product": trash.ID_product.id,
                "name": prods.name,
                "count": prods.count,
                "photo": "http://localhost:8000" + prods.photo.url,
            }
            response_data.append(item)
        return Response(response_data)

#удалить запись по id из корзины
class TrashDeleteView(generics.DestroyAPIView):
    queryset = Orders.objects.filter(in_trash=True)
    serializer_class = TrashSerializer
    permission_classes = (IsAuthenticated,)


class LikedAddView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = LikedSerializer


class LikedGetView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        likedProds = Orders.objects.filter(in_liked=True).select_related("ID_product")
        response_data = []
        for liked in likedProds:
            prods = liked.ID_product
            item = {
                "id": liked.id,
                "cost": prods.cost,
                "ID_product": liked.ID_product.id,
                "name": prods.name,
                "count": prods.count,
                "photo": "http://localhost:8000" + prods.photo.url,
            }
            response_data.append(item)
        return Response(response_data)


class LikedDeleteView(generics.DestroyAPIView):
    queryset = Orders.objects.filter(in_liked=True)
    serializer_class = LikedSerializer
    permission_classes = (IsAuthenticated,)


