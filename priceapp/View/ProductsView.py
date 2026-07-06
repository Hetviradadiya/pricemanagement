from rest_framework import viewsets, permissions, filters, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import SessionAuthentication
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db.models import Q, Prefetch
from ..models import Product, ProductPrice, Dealer, ProductSize
from ..serializers import ProductSerializer, ProductPriceSerializer, DealerSerializer

from rest_framework.pagination import PageNumberPagination
class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25  # Number of products per page
    page_size_query_param = 'page_size'
    max_page_size = 100
    
    # Add this method to customize the JSON output
    def get_paginated_response(self, data):
        return Response({
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data
        })

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('prices__dealers', 'sizes').all().order_by('-id')
    serializer_class = ProductSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sizes__size', 'sizes__code', 'sizes__hsn']

class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.select_related('product').prefetch_related('dealers').all().order_by('-id')
    serializer_class = ProductPriceSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'payment_type']

class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.select_related('product_price', 'product_price__product').all().order_by('-id')
    serializer_class = DealerSerializer
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['dlr_name', 'slol', 'product_price__product__name']

class BulkProductCreateAPIView(APIView):
    authentication_classes = [JWTAuthentication, SessionAuthentication]
    permission_classes = [permissions.IsAuthenticated]
    
    # Assign pagination class
    pagination_class = StandardResultsSetPagination

    def get(self, request):
        search = request.query_params.get('search', None)
        payment_type_param = request.query_params.get('payment_type', None)

        # 1. Base Query with optional Payment Type filtering
        if payment_type_param:
            # Parse comma-separated types (e.g. "cash,bill")
            payment_types = [pt.strip() for pt in payment_type_param.split(',')]
            
            # 2. Prefetch only prices that match the selected payment types
            filtered_prices = ProductPrice.objects.filter(
                payment_type__in=payment_types
            ).prefetch_related('dealers')
            
            filtered_sizes = ProductSize.objects.prefetch_related(
                Prefetch('prices', queryset=filtered_prices)
            )
            
            # 3. Filter products to only include those that have the selected payment type
            products = Product.objects.prefetch_related(
                Prefetch('sizes', queryset=filtered_sizes)
            ).filter(
                Q(sizes__prices__payment_type__in=payment_types) | 
                Q(sizes__isnull=True) | 
                Q(sizes__prices__isnull=True)
            ).distinct()
        else:
            # Default behavior if no filter is applied
            products = Product.objects.prefetch_related('sizes__prices__dealers').all()

        # 4. Apply existing Search filter
        if search:
            products = products.filter(
                Q(name__icontains=search) |
                Q(company_name__icontains=search) |
                Q(vp_name__icontains=search) |
                Q(description__icontains=search) |
                Q(sizes__size__icontains=search) |
                Q(sizes__code__icontains=search) |
                Q(sizes__hsn__icontains=search) |
                Q(sizes__prices__payment_type__icontains=search) |
                Q(sizes__prices__dealers__dlr_name__icontains=search) |
                Q(sizes__prices__dealers__slol__icontains=search)
            ).distinct()
        
        products = products.order_by('-id')
        
        # 3. Apply Pagination
        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(products, request, view=self)
        
        serializer = ProductSerializer(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        for key, value in request.data.items():
            if key == 'sizes' and isinstance(value, str):
                try:
                    import json
                    parsed = json.loads(value)
                    if parsed:
                        print(f"📦 First size structure: {list(parsed[0].keys()) if parsed else 'None'}")
                except Exception as e:
                    print(f"❌ Failed to parse sizes JSON: {e}")
        
        if isinstance(request.data, list):
            serializer = ProductSerializer(data=request.data, many=True)
        else:
            serializer = ProductSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
        result = serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        product.sizes.all().delete()  
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        if 'photo' in request.data:
            photo_data = request.data['photo']
            if isinstance(photo_data, (list, tuple)):
                if len(photo_data) > 0:
                    print(f"📷 First item type: {type(photo_data[0])}")
        
        product = get_object_or_404(Product, pk=pk)
        
        product.sizes.all().delete()  

        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        product.delete()
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
