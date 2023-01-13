from django.urls import path
from rest_framework.routers import DefaultRouter

from product import views

router = DefaultRouter()
router.register('category', views.CategoryViewSet)
router.register('', views.ProductViewSet)

urlpatterns = [
    path('hello/', views.get_hello)
]
urlpatterns += router.urls
