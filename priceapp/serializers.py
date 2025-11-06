from rest_framework import serializers
from .models import Product, ProductPrice, Dealer, ProductSize
# from drf_extra_fields.fields import Base64ImageField  # Commented out - using standard ImageField instead

class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        exclude = ('product_price',)  # exclude FK, will set in create()

class ProductPriceSerializer(serializers.ModelSerializer):
    dealers = DealerSerializer(many=True)

    class Meta:
        model = ProductPrice
        exclude = ('product_size',)  # exclude FK, will set in create()

    def create(self, validated_data):
        dealers_data = validated_data.pop('dealers', [])
        product_price = ProductPrice.objects.create(**validated_data)
        for dealer_data in dealers_data:
            Dealer.objects.create(product_price=product_price, **dealer_data)
        return product_price
    
# -------------------- PRODUCT SIZE SERIALIZER --------------------
class ProductSizeSerializer(serializers.ModelSerializer):
    prices = ProductPriceSerializer(many=True, required=False)

    class Meta:
        model = ProductSize
        exclude = ('product',)  # exclude FK, will set in create()

    def create(self, validated_data):
        prices_data = validated_data.pop('prices', [])
        product_size = ProductSize.objects.create(**validated_data)
        
        # Create Product Prices & Dealers for this size
        for price_data in prices_data:
            dealers_data = price_data.pop('dealers', [])
            product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
            for dealer_data in dealers_data:
                Dealer.objects.create(product_price=product_price, **dealer_data)
        
        return product_size

class ProductSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(required=False, allow_null=True, allow_empty_file=True)
    sizes = serializers.SerializerMethodField()  # Use method field for output

    class Meta:
        model = Product
        fields = '__all__'
    
    def get_sizes(self, obj):
        """Return properly serialized sizes for API responses"""
        return ProductSizeSerializer(obj.sizes.all(), many=True).data

    def validate(self, data):
        """Custom validation to preserve parsed sizes data"""
        # The parsed sizes data was added in to_internal_value but might be lost
        # Let's preserve it for create/update methods
        validated_data = super().validate(data)
        
        # If sizes_parsed exists in the original data, preserve it
        if hasattr(self, '_sizes_parsed_data'):
            validated_data['sizes_parsed'] = self._sizes_parsed_data
            print(f"✅ Preserved sizes_parsed in validate(): {len(validated_data['sizes_parsed'])} sizes")
        
        return validated_data

    def to_internal_value(self, data):
        import json
        
        print(f"🔧 ProductSerializer.to_internal_value() called")
        print(f"📝 Raw input data: {data}")
        
        # Convert FormData to mutable dict for processing
        if hasattr(data, 'getlist'):
            # Handle QueryDict from FormData
            processed_data = {}
            for key in data.keys():
                if key != 'sizes':  # Skip sizes since it's a method field
                    processed_data[key] = data.get(key)
        else:
            processed_data = dict(data)
            # Remove sizes from processed data since it's a method field
            processed_data.pop('sizes', None)
        
        print(f"📝 Processed data: {processed_data}")
        
        # Parse sizes JSON string if present and store separately for create/update
        if hasattr(data, 'get') and data.get('sizes'):
            sizes_str = data.get('sizes')
            print(f"📦 Raw sizes string: {sizes_str}")
            try:
                if isinstance(sizes_str, str):
                    self._sizes_parsed_data = json.loads(sizes_str)
                    print(f"📦 Parsed sizes successfully: {self._sizes_parsed_data}")
                else:
                    self._sizes_parsed_data = sizes_str
                    print(f"📦 Sizes already parsed: {self._sizes_parsed_data}")
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error for sizes: {e}")
                self._sizes_parsed_data = []
        else:
            self._sizes_parsed_data = []
            print(f"📦 No sizes data found, setting empty array")
        
        return super().to_internal_value(processed_data)

    def create(self, validated_data):
        print(f"🔧 ProductSerializer.create() called")
        print(f"📝 Raw validated_data: {validated_data}")
        
        # Get the parsed sizes data
        sizes_data = validated_data.pop('sizes_parsed', [])
        print(f"📦 Parsed sizes_data: {sizes_data} (count: {len(sizes_data)})")
        
        # Remove the original sizes string field if present
        validated_data.pop('sizes', None)
        
        product = Product.objects.create(**validated_data)
        print(f"✅ Created product: {product.name} (ID: {product.id})")

        # Create Product Sizes with their Prices & Dealers
        for size_index, size_data in enumerate(sizes_data):
            print(f"📏 Processing size {size_index + 1}: {size_data}")
            prices_data = size_data.pop('prices', [])
            print(f"💰 Found {len(prices_data)} prices for size: {size_data.get('size', 'Unknown')}")
            
            product_size = ProductSize.objects.create(product=product, **size_data)
            print(f"✅ Created size: {product_size.size} (ID: {product_size.id})")
            
            # Create Product Prices & Dealers for this size
            for price_index, price_data in enumerate(prices_data):
                print(f"💰 Processing price {price_index + 1}: {price_data}")
                dealers_data = price_data.pop('dealers', [])
                print(f"🤝 Found {len(dealers_data)} dealers for price")
                
                product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
                print(f"✅ Created price: {product_price.price} (ID: {product_price.id})")
                
                for dealer_index, dealer_data in enumerate(dealers_data):
                    print(f"🤝 Processing dealer {dealer_index + 1}: {dealer_data}")
                    Dealer.objects.create(product_price=product_price, **dealer_data)
                    print(f"✅ Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")

        print(f"🎉 Product creation completed: {product.name}")
        return product

    def update(self, instance, validated_data):
        print(f"🔧 ProductSerializer.update() called")
        print(f"📝 Raw validated_data: {validated_data}")
        
        # Get the parsed sizes data
        sizes_data = validated_data.pop('sizes_parsed', [])
        print(f"📦 Parsed sizes_data: {sizes_data} (count: {len(sizes_data)})")
        
        # Remove the original sizes string field if present
        validated_data.pop('sizes', None)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        print(f"✅ Updated product: {instance.name} (ID: {instance.id})")

        # Create Product Sizes with their Prices & Dealers (same logic as create)
        for size_index, size_data in enumerate(sizes_data):
            print(f"📏 Processing size {size_index + 1}: {size_data}")
            prices_data = size_data.pop('prices', [])
            print(f"💰 Found {len(prices_data)} prices for size: {size_data.get('size', 'Unknown')}")
            
            product_size = ProductSize.objects.create(product=instance, **size_data)
            print(f"✅ Created size: {product_size.size} (ID: {product_size.id})")
            
            # Create Product Prices & Dealers for this size
            for price_index, price_data in enumerate(prices_data):
                print(f"💰 Processing price {price_index + 1}: {price_data}")
                dealers_data = price_data.pop('dealers', [])
                print(f"🤝 Found {len(dealers_data)} dealers for price")
                
                product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
                print(f"✅ Created price: {product_price.price} (ID: {product_price.id})")
                
                for dealer_index, dealer_data in enumerate(dealers_data):
                    print(f"🤝 Processing dealer {dealer_index + 1}: {dealer_data}")
                    Dealer.objects.create(product_price=product_price, **dealer_data)
                    print(f"✅ Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")

        print(f"🎉 Product update completed: {instance.name}")
        return instance