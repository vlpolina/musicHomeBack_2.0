from rest_framework import generics, viewsets
from rest_framework.parsers import JSONParser
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
        # валидация на существующего пользователя
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


# проверка роли администратора
class CheckAdminView(APIView):
    permission_classes = (IsAuthenticated, )

    def get(self, request):
        user = User.objects.get(id=request.user.id)
        serializer = CheckAdminSerializer(user)
        return Response(serializer.data)

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


#получение поставщиков для фильтров в каталоге
class CustomersForCatList(generics.ListAPIView):
    queryset = Customers.objects.all()
    serializer_class = CustomersForCatSerializer


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

    def get(self, request, slug):
        try:
            product = Products.objects.get(slug=slug, is_published=True)
        except Products.DoesNotExist:
            return Response({"error": "Product not found"}, status=404)

        order = Orders.objects.filter(ID_product=product)
        product_data = ProductSerializer(product).data
        if order.exists():
            order_data = ProductCardSerializer(order.first()).data
        else:
            order_data = None
        response_data = {
            "product": product_data,
            "order": order_data
        }

        return Response(response_data)


#добавить в корзину
class TrashAddView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = TrashSerializer

    def create(self, request, *args, **kwargs):
        # Получаем данные из запроса
        product_id = request.data.get('ID_product')
        client_id = request.user.id

        # Пытаемся найти запись по указанным параметрам
        order = Orders.objects.filter(ID_client=client_id, ID_product=product_id).first()

        # Если запись найдена, устанавливаем is_liked в 1
        if order:
            order.in_trash = 1
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Если запись не найдена, создаем новую запись
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
                "in_liked": trash.in_liked,
                "count_buy": trash.count,
            }
            response_data.append(item)
        return Response(response_data)

#удалить запись по id из корзины
class TrashDeleteView(generics.DestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = TrashSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверяем условия для удаления или обновления записи
        if instance.in_liked == 0 and instance.is_applying == 0 and instance.is_payed == 0 and instance.is_delivered == 0:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Устанавливаем is_liked в 0
            instance.in_trash = 0
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


class TrashResetView(generics.UpdateAPIView):
    queryset = Orders.objects.all()
    serializer_class = TrashSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        # Получаем queryset со всеми записями, которые нужно изменить
        queryset = self.filter_queryset(self.get_queryset())

        # Обновляем in_liked в 0 для всех записей
        queryset.update(in_trash=0)

        # Удаляем записи, которые удовлетворяют условиям
        queryset.filter(
            in_liked=0,
            is_applying=0,
            is_payed=0,
            is_delivered=0
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class LikedAddView(generics.CreateAPIView):
    permission_classes = (IsAuthenticated,)
    queryset = Orders.objects.all()
    serializer_class = LikedSerializer

    def create(self, request, *args, **kwargs):
        # Получаем данные из запроса
        product_id = request.data.get('ID_product')
        client_id = request.user.id

        # Пытаемся найти запись по указанным параметрам
        order = Orders.objects.filter(ID_client=client_id, ID_product=product_id).first()

        # Если запись найдена, устанавливаем is_liked в 1
        if order:
            order.in_liked = 1
            order.save()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # Если запись не найдена, создаем новую запись
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


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
                "slug": liked.ID_product.slug,
                "name": prods.name,
                "short_desc": liked.ID_product.short_desc,
                "photo": "http://localhost:8000" + prods.photo.url,
                "in_trash": liked.in_trash,
            }
            response_data.append(item)
        return Response(response_data)


class StatusesForCatalogGetView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        prods = Orders.objects.select_related("ID_product")
        response_data = []
        for product in prods:
            item = {
                'order_id': product.id,
                'product_id': product.ID_product.id,
                'liked': product.in_liked,
                'trash': product.in_trash
            }
            response_data.append(item)
        return Response(response_data)


class LikedDeleteView(generics.DestroyAPIView):
    queryset = Orders.objects.all()
    serializer_class = LikedSerializer
    permission_classes = (IsAuthenticated,)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        # Проверяем условия для удаления или обновления записи
        if instance.in_trash == 0 and instance.is_applying == 0 and instance.is_payed == 0 and instance.is_delivered == 0:
            instance.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            # Устанавливаем is_liked в 0
            instance.in_liked = 0
            instance.save()
            serializer = self.get_serializer(instance)
            return Response(serializer.data)


class LikedResetView(generics.UpdateAPIView):
    queryset = Orders.objects.all()
    serializer_class = LikedSerializer
    permission_classes = (IsAuthenticated,)

    def update(self, request, *args, **kwargs):
        # Получаем queryset со всеми записями, которые нужно изменить
        queryset = self.filter_queryset(self.get_queryset())

        # Обновляем in_liked в 0 для всех записей
        queryset.update(in_liked=0)

        # Удаляем записи, которые удовлетворяют условиям
        queryset.filter(
            in_trash=0,
            is_applying=0,
            is_payed=0,
            is_delivered=0
        ).delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class CreateOrderView(APIView):
    permission_classes = (IsAuthenticated,)

    def put(self, request):
        products = request.data.get('products', [])
        address = request.data.get('address')
        client_phone = request.data.get('client_phone')
        payment = request.data.get('payment')
        ID_client = request.data.get('ID_client')

        for product_data in products:
            ID_product = product_data.get('ID_product')
            count = product_data.get('count')
            sum_cost = product_data.get('sum_cost')

            orders = Orders.objects.filter(ID_product=ID_product, ID_client=ID_client, in_trash=1)
            for order in orders:
                order.count = count
                order.sum_cost = sum_cost
                order.address = address
                order.client_phone = client_phone
                order.payment = payment
                order.in_trash = 0
                order.is_applying = 1
                order.save()

        return Response(status=status.HTTP_200_OK)

    def post(self, request):
        try:
            email = 'vlasova2002polina18@mail.ru'
            subject = 'MusicHome. Оформление заказа.'
            message = f'Здравствуйте!\n\nВы оформили заказ в интернет-магазине музыкальных инструментов "musicHome" на сумму: 40200 рублей.\nВаш заказ:\n - Укулеле ENYA EUC-20: 3 шт. - 22500 руб.\n - Синтезатор ROCKDALE PREVIERE 2: 1 шт. - 17700 руб.\n\nУведомляем Вас, что в системе магазина несколько инструментов, заказанных одновременно, доставляются и оплачиваются по отдельности и считаются отдельными заказами. Вы можете отслеживать статусы своих заказов в личном кабинете на нашем сайте.\n\nЕсли Вы не оформляли заказ, можете обратиться в техническую поддержку магазина, заполнив форму по ссылке ниже:\nhttps://forms.yandex.ru/cloud/6631f2d97c1515e8e45e3240/\n\nС уважением, команда MusicHome.'
            from_email = 'musichomeforyou@gmail.com'
            recipient_list = [email]
            sending = "Отправлено!"
            send_mail(subject, message, from_email, recipient_list)

            return Response({"status": "success", "message": sending}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class OrdersGetView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        orders = Orders.objects.filter(is_applying=True).select_related("ID_product")
        response_data = []
        for products in orders:
            prods = products.ID_product
            item = {
                "id": products.id,
                "sumCost": products.sum_cost,
                "count": products.count,
                "name": prods.name,
                "applying": products.is_applying,
                "payed": products.is_payed,
                "delivering": products.is_delivering,
                "delivered": products.is_delivered,
            }
            response_data.append(item)
        return Response(response_data)


class EmailForPassword(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            data = request.data
            email = data['email']
            subject = 'MusicHome. Восстановление пароля.'
            message = f'Здравствуйте!\n\nВы запросили сброс пароля для своего аккаунта на musicHome.\nЧтобы восстановить пароль, перейдите по этой ссылке:\n\nhttp://localhost:8000/reset-password/hg12Sa2\n\nЕсли вы не запрашивали сброс пароля, проигнорируйте это письмо.\n\nС уважением, команда MusicHome.'
            from_email = 'musichomeforyou@gmail.com'
            # password = 'f1BLhKKiv3EXCVY9UY3H'
            recipient_list = [email]
            sending = "Отправлено!"
            send_mail(subject, message, from_email, recipient_list)

            return Response({"status": "success", "message": sending}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SendEmail(APIView):
    parser_classes = [JSONParser]

    def post(self, request):
        try:
            email = 'vlasova2002polina18@mail.ru'
            # subject = 'MusicHome. Ваш заказ уже в пути!'
            # subject = 'MusicHome. Заказ уже почти у Вас!'
            subject = 'MusicHome. Заказ доставлен и оплачен!'
            # message = f'Здравствуйте!\n\nВы оформляли заказ в интернет-магазине музыкальных инструментов "musicHome" - Укулеле ENYA EUC-20: 3 шт. - 22500 руб. уже в пути!\n\nУведомляем Вас, что в системе магазина несколько инструментов, заказанных одновременно, доставляются и оплачиваются по отдельности и считаются отдельными заказами. Вы можете отслеживать статусы своих заказов в личном кабинете на нашем сайте.\n\nЕсли Вы не оформляли заказ, можете обратиться в техническую поддержку магазина, заполнив форму по ссылке ниже:\nhttps://forms.yandex.ru/cloud/6631f2d97c1515e8e45e3240/\n\nС уважением, команда MusicHome.'
            # message = f'Здравствуйте!\n\nВы оформляли заказ в интернет-магазине музыкальных инструментов "musicHome".\nУкулеле ENYA EUC-20: 3 шт. - 22500 руб. уже в Вашем городе, ожидайте курьера в течение следующего рабочего дня. Курьер дополнительно свяжется с Вами для обсуждения удобного Вам времени доставки.\n\nУведомляем Вас, что в системе магазина несколько инструментов, заказанных одновременно, доставляются и оплачиваются по отдельности и считаются отдельными заказами. Вы можете отслеживать статусы своих заказов в личном кабинете на нашем сайте.\n\nЕсли Вы не оформляли заказ, можете обратиться в техническую поддержку магазина, заполнив форму по ссылке ниже:\nhttps://forms.yandex.ru/cloud/6631f2d97c1515e8e45e3240/\n\nС уважением, команда MusicHome.'
            message = f'Здравствуйте!\n\nВаш заказ в интернет-магазине музыкальных инструментов "musicHome" "Укулеле ENYA EUC-20": 3 шт. - 22500 руб. Успешно доставлен и оплачен!\n\nБлагодарим Вас за покупку и ждем Ваших будущих заказов :)\n\nУведомляем Вас, что в системе магазина несколько инструментов, заказанных одновременно, доставляются и оплачиваются по отдельности и считаются отдельными заказами. Вы можете отслеживать статусы своих заказов в личном кабинете на нашем сайте.\n\nС уважением, команда MusicHome.'
            from_email = 'musichomeforyou@gmail.com'
            recipient_list = [email]
            sending = "Отправлено!"
            send_mail(subject, message, from_email, recipient_list)

            return Response({"status": "success", "message": sending}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"status": "error", "message": str(e)}, status=status.HTTP_400_BAD_REQUEST)

