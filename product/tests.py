from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIRequestFactory, force_authenticate
from rest_framework_simplejwt.views import TokenObtainPairView

from product.models import Category, Product
from product.views import CategoryViewSet, ProductViewSet

User = get_user_model()


class CategoryTest(APITestCase):
    """
    Test category
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.setup_category()
        self.user = self.setup_user()

    def setup_user(self):
        return User.objects.create_user(email='test@test.com', password='test_password', is_active=True)

    def setup_category(self):
        list_of_category = [Category('category1'), Category('category2'), Category('category3')]
        Category.objects.bulk_create(list_of_category)

    def test_get_category(self):
        request = self.factory.get('/api/v1/product/category/')
        view = CategoryViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200
        assert Category.objects.count() == 3
        assert Category.objects.first().title == 'category1'

    def test_post_category(self):
        data = {
            'title': 'test'
        }
        request = self.factory.post('/api/v1/product/category/', data)
        force_authenticate(request, user=self.user)
        view = CategoryViewSet.as_view({'post': 'create'})
        response = view(request)
        assert response.status_code == 201
        assert Category.objects.get(title='test')


class ProductTest(APITestCase):
    """
    Test product
    """

    def setUp(self):
        self.factory = APIRequestFactory()
        self.setup_category()
        self.user = self.setup_user()
        self.setup_product()
        self.access_token = self.setup_token()

    def setup_user(self):
        return User.objects.create_user(email='test@test.com', password='test_password', is_active=True)

    def setup_token(self):
        data = dict(
            email=self.user.email,
            password='test_password'
        )
        request = self.factory.post('/api/v1/account/login/', data)
        view = TokenObtainPairView.as_view()
        response = view(request)
        return response.data['access']


    def setup_category(self):
        self.category = Category.objects.create(title='setup_category')

    def setup_product(self):
        products = [
            Product(
                owner=self.user,
                title='setup_product',
                price=1000,
                category=self.category,
                image='setup_image'
            ), Product(
                owner=self.user,
                title='setup_product2',
                price=2000,
                category=self.category,
                image='setup_image2'
            )
        ]
        Product.objects.bulk_create(products)

    def test_get_product(self):
        request = self.factory.get('/api/v1/product/')
        view = ProductViewSet.as_view({'get': 'list'})
        response = view(request)
        assert response.status_code == 200
        assert Product.objects.count() == 2
        assert Product.objects.first().category.title == 'setup_category'

    def test_post_category(self):
        image = open('media/images/Снимок_экрана_от_2023-01-04_02-22-12.png', 'rb')
        data = dict(
            owner=self.user.id,
            title='test_product',
            price=1000,
            category=self.category.title,
            image=image
        )
        request = self.factory.post('/api/v1/product/', data, HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        view = ProductViewSet.as_view({'post': 'create'})
        response = view(request)
        image.close()
        assert response.status_code == 201
        assert Product.objects.filter(title='test_product').exists()
        assert Product.objects.filter(owner=self.user.id).exists()
        assert Product.objects.filter(price=1000).exists()
        assert Product.objects.filter(category='setup_category').exists()
