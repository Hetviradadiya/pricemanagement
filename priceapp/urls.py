from django.urls import path,include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework.routers import DefaultRouter
from priceapp.View.ProductsView import ProductViewSet, ProductPriceViewSet, DealerViewSet, BulkProductCreateAPIView
from priceapp.views import (
    price_dashboard, LoginAPIView, LogoutAPIView, user_login, user_logout,
    GetUserDetailsAPIView, UpdateUserDetailsAPIView, ChangePasswordAPIView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='products')
router.register(r'product-prices', ProductPriceViewSet, basename='product-prices')
router.register(r'dealers', DealerViewSet, basename='dealers')

urlpatterns = router.urls

urlpatterns = [
    path('login/', user_login, name='login'),
    # path('logout/', user_logout, name='logout'),
    path('product/', price_dashboard, name='product'),

    path('api/auth/login/', LoginAPIView.as_view(), name='api_login'),
    path('api/auth/logout/', LogoutAPIView.as_view(), name='api_logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User Management APIs
    path('api/user/details/', GetUserDetailsAPIView.as_view(), name='user-details'),
    path('api/user/update/', UpdateUserDetailsAPIView.as_view(), name='user-update'),
    path('api/user/change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    
    path('api/', include(router.urls)),
    path('api/product-create/', BulkProductCreateAPIView.as_view(), name='bulk-products-create'),
    path('api/product-create/<int:pk>/', BulkProductCreateAPIView.as_view(), name='bulk-products-update'),
]