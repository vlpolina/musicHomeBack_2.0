from datetime import date

from django.shortcuts import render, HttpResponse, Http404
from django.urls import reverse_lazy
from django.views.generic import CreateView
from rest_framework.views import APIView
from .models import *
from .serializer import *
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .forms import *
from django.contrib.auth.mixins import LoginRequiredMixin


class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'online_shop/registration.html'
    success_url = reverse_lazy('login')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Регистрация'
        return context


class CatalogView(APIView):
   # login_url = 'http://localhost:8000/admin/'
    #success_url = reverse_lazy('http://localhost:3000')
    #login_url = reverse_lazy('http://localhost:3000')

    def get(self, request):
        output = [{ "id": output.id,
                    "name": output.name}
                  for output in Category.objects.all()]
        #annotate(Count('products')>0)
        return Response(output)


class CatalogViewAll(APIView):
  #  login_url = 'http://localhost:8000/admin/'

    def get(self, request):
        products = [{"id": prods.id,
                     "name": prods.name,
                     "slug": prods.slug,
                     "short_desc": prods.short_desc,
                     "cost": prods.cost,
                     "photo": 'http://localhost:8000'+prods.photo.url,
                     "cat_id": prods.cat_id
                     }
                    for prods in Products.objects.filter(is_published=True)]
        return Response(products)


class CatalogViewID(APIView):
   # login_url = 'http://localhost:8000/admin/'

    def get(self, request, cat_id):
        products = [{"id": prods.id,
                     "name": prods.name,
                     "slug": prods.slug,
                     "short_desc": prods.short_desc,
                     "cost": prods.cost,
                     "photo": 'http://localhost:8000'+prods.photo.url,
                     "cat_id": prods.cat_id
                     }
                    for prods in Products.objects.filter(cat_id=cat_id, is_published=True)]
        return Response(products)


class FilterCustomersView(APIView):

    def get(self, request):
        custom = [{ "id": custom.id,
                    "name": custom.name}
                  for custom in Customers.objects.all()]
        return Response(custom)


#подробнее о каждом товаре сделать фронт
class ProductView(APIView):

    def get(self, request, slug):
        products = [{"id": prods.id,
                     "name": prods.name,
                     "long_desc": prods.long_desc,
                     "cost": prods.cost,
                     "count": prods.count,
                    # "custom_name": prods.custom_name,
                     "photo": 'http://localhost:8000'+prods.photo.url,
                     "slug": prods.slug
                     }
                    for prods in Products.objects.filter(slug=slug, is_published=True)]
        return Response(products)


class TrashView(APIView):

    def post(self, request):
        serializer = TrashSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(date=date.today(), status='trash')
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        trashProds = Orders.objects.filter(status="trash").select_related("ID_product")
        response_data = []
        for trash in trashProds:
            prods = trash.ID_product
            item = {
                "id": trash.id,
                "cost": prods.cost,
              #  "ID_product": trash.ID_product.id,
                "name": prods.name,
                "count": prods.count,
                "photo": "http://localhost:8000" + prods.photo.url,
            }
            response_data.append(item)
        return Response(response_data)


#class TrashDetailView(APIView):

   # def delete(self, request, pk):
   #     try:
    #        trash = Orders.objects.get(id=pk, status='trash')
      #      trash.delete()
    #        return Response(status=status.HTTP_204_NO_CONTENT)
    #    except Orders.DoesNotExist:
   #         return Response(status=status.HTTP_404_NOT_FOUND)


#csrf_token?
# 404 if not page
# 16 работа с бд на джанго
#пост запросы отображаются в консоли
#cat__slug использовать из другой таблицы 14 видео
# см 13 видео
#14 выгрузка фото с сайта
#14 save data to database в корзину, использовать try except
# .save() - сохранение в бд
#можно ли передавать в запросах формы?
# linebreaks для переноса строки в длиннм описании trancetewords обрезать количество слов