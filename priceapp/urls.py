from django.urls import path,include
from rest_framework.routers import DefaultRouter
from priceapp.View.ProductsView import ProductViewSet, ProductPriceViewSet, DealerViewSet, BulkProductCreateAPIView
from priceapp.views import user_login, user_logout, price_dashboard

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-prices', ProductPriceViewSet, basename='product-prices')
router.register(r'dealers', DealerViewSet, basename='dealers')

urlpatterns = router.urls

urlpatterns = [
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    path('product/', price_dashboard, name='product'),
    path('api/', include(router.urls)),
    path('api/product-create/', BulkProductCreateAPIView.as_view(), name='bulk-products-create'),
    path('api/product-create/<int:pk>/', BulkProductCreateAPIView.as_view(), name='bulk-products-update'),
]