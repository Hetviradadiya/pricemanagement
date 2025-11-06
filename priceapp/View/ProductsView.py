from rest_framework import viewsets, permissions, filters, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from ..models import Product, ProductPrice, Dealer
from ..serializers import ProductSerializer, ProductPriceSerializer, DealerSerializer

# -------------------- PRODUCT VIEWSET --------------------
class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.prefetch_related('prices__dealers', 'sizes').all().order_by('-id')
    serializer_class = ProductSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['name', 'sizes__size', 'sizes__code', 'sizes__hsn']

# -------------------- PRODUCT PRICE VIEWSET --------------------
class ProductPriceViewSet(viewsets.ModelViewSet):
    queryset = ProductPrice.objects.select_related('product').prefetch_related('dealers').all().order_by('-id')
    serializer_class = ProductPriceSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['product__name', 'payment_type']

# -------------------- DEALER VIEWSET --------------------
class DealerViewSet(viewsets.ModelViewSet):
    queryset = Dealer.objects.select_related('product_price', 'product_price__product').all().order_by('-id')
    serializer_class = DealerSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['dlr_name', 'slol', 'product_price__product__name']

# -------------------- BULK PRODUCT API --------------------
class BulkProductCreateAPIView(APIView):
    # permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        products = Product.objects.prefetch_related('sizes__prices__dealers').all().order_by('-id')
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        print(f"🌐 ===== FRONTEND DATA RECEIVED =====")
        print(f"🔧 POST request received")
        print(f"📝 Request data type: {type(request.data)}")
        print(f"📝 Request content_type: {request.content_type}")
        print(f"📝 Request encoding: {getattr(request, 'encoding', 'Not set')}")
        print(f"📝 Request data keys: {list(request.data.keys())}")
        
        # Log each field in detail
        for key, value in request.data.items():
            print(f"� Field '{key}': type={type(value)} | value={str(value)[:200]}...")
            if key == 'sizes' and isinstance(value, str):
                try:
                    import json
                    parsed = json.loads(value)
                    print(f"📦 Sizes JSON parsed successfully: {len(parsed)} items")
                    if parsed:
                        print(f"📦 First size structure: {list(parsed[0].keys()) if parsed else 'None'}")
                except Exception as e:
                    print(f"❌ Failed to parse sizes JSON: {e}")
        
        print(f"�📝 Request FILES: {request.FILES}")
        print(f"🌐 ===== END FRONTEND DATA =====")
        
        # Check if we're receiving a list or single product
        if isinstance(request.data, list):
            serializer = ProductSerializer(data=request.data, many=True)
        else:
            serializer = ProductSerializer(data=request.data)
        
        print(f"🔍 Serializer validation...")
        if not serializer.is_valid():
            print(f"❌ Serializer validation failed!")
            print(f"❌ Serializer errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        print(f"✅ Serializer is valid")
            
        result = serializer.save()
        print(f"✅ Serializer saved successfully: {result}")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def put(self, request, pk=None):
        product = get_object_or_404(Product, pk=pk)
        
        # For a complete update, delete existing related data and recreate
        product.sizes.all().delete()  # This will cascade delete prices and dealers
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    def patch(self, request, pk=None):
        print(f"🔧 PATCH request for product ID: {pk}")
        print(f"📝 Request data: {request.data}")
        
        # Debug photo field specifically
        if 'photo' in request.data:
            photo_data = request.data['photo']
            print(f"📷 Photo field type: {type(photo_data)}")
            print(f"📷 Photo field value: {photo_data}")
            if isinstance(photo_data, (list, tuple)):
                print(f"📷 Photo is array/list with {len(photo_data)} items")
                if len(photo_data) > 0:
                    print(f"📷 First item type: {type(photo_data[0])}")
        
        product = get_object_or_404(Product, pk=pk)
        print(f"✅ Found product: {product.name}")
        
        # For PATCH, also do a complete replacement of nested data
        product.sizes.all().delete()  # This will cascade delete prices and dealers
        print(f"🗑️ Deleted existing sizes/prices/dealers for product {pk}")
        
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if not serializer.is_valid():
            print(f"❌ Serializer validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        serializer.save()
        print(f"💾 Successfully updated product {pk}")
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk=None):
        print(f"🗑️ DELETE request for product ID: {pk}")
        product = get_object_or_404(Product, pk=pk)
        print(f"✅ Found product to delete: {product.name}")
        product.delete()
        print(f"💀 Successfully deleted product {pk}")
        return Response({'message': 'Product deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
