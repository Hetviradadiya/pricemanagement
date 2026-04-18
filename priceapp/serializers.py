from rest_framework import serializers
from .models import Product, ProductPrice, Dealer, ProductSize, UserAccount, Role
# from drf_extra_fields.fields import Base64ImageField  # Commented out - using standard ImageField instead

class DealerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dealer
        exclude = ('product_price',)  # exclude FK, will set in create()

class ProductPriceSerializer(serializers.ModelSerializer):
    price_date = serializers.DateField(required=False, allow_null=True)
    purchase_date = serializers.DateField(required=False, allow_null=True)
    dealers = DealerSerializer(many=True, required=False)

    class Meta:
        model = ProductPrice
        exclude = ('product_size',)  # exclude FK, will set in create()

    def to_internal_value(self, data):
        if hasattr(data, 'copy'):
            data = data.copy()

        for field_name in ('price_date', 'purchase_date'):
            if data.get(field_name) in ('', None):
                data[field_name] = None

        return super().to_internal_value(data)

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
            
            # Clean date fields
            for date_field in ['price_date', 'purchase_date']:
                if price_data.get(date_field) in ('', None):
                    price_data[date_field] = None
                    
            product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
            for dealer_data in dealers_data:
                # Clean date fields for dealer
                if dealer_data.get('purchase_date') in ('', None):
                    dealer_data['purchase_date'] = None
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
        import logging
        logger = logging.getLogger(__name__)
        
        # The parsed sizes data was added in to_internal_value but might be lost
        # Let's preserve it for create/update methods
        validated_data = super().validate(data)
        
        # If sizes_parsed exists in the original data, preserve it
        if hasattr(self, '_sizes_parsed_data'):
            validated_data['sizes_parsed'] = self._sizes_parsed_data
            try:
                print(f"✅ Preserved sizes_parsed in validate(): {len(validated_data['sizes_parsed'])} sizes")
                logger.info(f"Preserved sizes_parsed in validate(): {len(validated_data['sizes_parsed'])} sizes")
            except Exception as e:
                print(f"⚠️ Error logging sizes count: {e}")
                logger.error(f"Error logging sizes count: {e}")
        else:
            print(f"⚠️ No _sizes_parsed_data found in serializer instance")
            logger.warning("No _sizes_parsed_data found in serializer instance")
        
        return validated_data

    def to_internal_value(self, data):
        import json
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            print(f"🔧 ProductSerializer.to_internal_value() called")
            logger.info("ProductSerializer.to_internal_value() called")
            print(f"📝 Raw input data type: {type(data)}")
            logger.info(f"Raw input data type: {type(data)}")
            
            # Convert FormData to mutable dict for processing
            processed_data = {}
            sizes_raw = None
            
            if hasattr(data, 'getlist'):
                # Handle QueryDict from FormData
                print(f"📝 Processing QueryDict data")
                logger.info("Processing QueryDict data")
                for key in data.keys():
                    if key == 'sizes':
                        sizes_raw = data.get(key)
                    elif key != 'sizes':  # Skip sizes since it's a method field
                        processed_data[key] = data.get(key)
            elif hasattr(data, 'get'):
                # Handle dict-like data
                print(f"📝 Processing dict-like data")
                logger.info("Processing dict-like data")
                for key, value in data.items():
                    if key == 'sizes':
                        sizes_raw = value
                    elif key != 'sizes':
                        processed_data[key] = value
            else:
                # Fallback for other data types
                print(f"📝 Processing fallback data type")
                logger.info("Processing fallback data type")
                processed_data = dict(data) if data else {}
                sizes_raw = processed_data.pop('sizes', None)
            
            print(f"📝 Processed data keys: {list(processed_data.keys())}")
            logger.info(f"Processed data keys: {list(processed_data.keys())}")
            
            # Parse sizes JSON string if present
            if sizes_raw:
                print(f"📦 Found sizes data, type: {type(sizes_raw)}")
                logger.info(f"Found sizes data, type: {type(sizes_raw)}")
                try:
                    if isinstance(sizes_raw, str):
                        self._sizes_parsed_data = json.loads(sizes_raw)
                        print(f"📦 Successfully parsed {len(self._sizes_parsed_data)} sizes from JSON")
                        logger.info(f"Successfully parsed {len(self._sizes_parsed_data)} sizes from JSON")
                    elif isinstance(sizes_raw, (list, dict)):
                        self._sizes_parsed_data = sizes_raw
                        print(f"📦 Using pre-parsed sizes data")
                        logger.info("Using pre-parsed sizes data")
                    else:
                        print(f"⚠️ Unexpected sizes data type: {type(sizes_raw)}")
                        logger.warning(f"Unexpected sizes data type: {type(sizes_raw)}")
                        self._sizes_parsed_data = []
                except json.JSONDecodeError as e:
                    print(f"❌ JSON decode error for sizes: {e}")
                    logger.error(f"JSON decode error for sizes: {e}")
                    self._sizes_parsed_data = []
                except Exception as e:
                    print(f"❌ Unexpected error parsing sizes: {e}")
                    logger.error(f"Unexpected error parsing sizes: {e}")
                    self._sizes_parsed_data = []
            else:
                self._sizes_parsed_data = []
                print(f"📦 No sizes data found, setting empty array")
                logger.info("No sizes data found, setting empty array")
            
            return super().to_internal_value(processed_data)
            
        except Exception as e:
            print(f"❌ Critical error in to_internal_value: {e}")
            logger.error(f"Critical error in to_internal_value: {e}")
            self._sizes_parsed_data = []
            return super().to_internal_value({} if not data else data)

    def create(self, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            print(f"🔧 ProductSerializer.create() called")
            logger.info("ProductSerializer.create() called")
            print(f"📝 Raw validated_data keys: {list(validated_data.keys())}")
            logger.info(f"Raw validated_data keys: {list(validated_data.keys())}")
            
            # Get the parsed sizes data
            sizes_data = validated_data.pop('sizes_parsed', [])
            print(f"📦 Found sizes_parsed: {sizes_data is not None}")
            logger.info(f"Found sizes_parsed: {sizes_data is not None}")
            
            if sizes_data:
                print(f"📦 Sizes count: {len(sizes_data)}")
                logger.info(f"Sizes count: {len(sizes_data)}")
            else:
                print(f"⚠️ No sizes_parsed data found!")
                logger.warning("No sizes_parsed data found!")
                sizes_data = []
            
            # Remove the original sizes string field if present
            validated_data.pop('sizes', None)
            
            product = Product.objects.create(**validated_data)
            print(f"✅ Created product: {product.name} (ID: {product.id})")
            logger.info(f"Created product: {product.name} (ID: {product.id})")

            # Create Product Sizes with their Prices & Dealers
            for size_index, size_data in enumerate(sizes_data):
                print(f"📏 Processing size {size_index + 1}: {size_data}")
                logger.info(f"Processing size {size_index + 1}")
                prices_data = size_data.pop('prices', [])
                print(f"💰 Found {len(prices_data)} prices for size: {size_data.get('size', 'Unknown')}")
                
                product_size = ProductSize.objects.create(product=product, **size_data)
                print(f"✅ Created size: {product_size.size} (ID: {product_size.id})")
                logger.info(f"Created size: {product_size.size} (ID: {product_size.id})")
                
                # Create Product Prices & Dealers for this size
                for price_index, price_data in enumerate(prices_data):
                    print(f"💰 Processing price {price_index + 1}: {price_data}")
                    dealers_data = price_data.pop('dealers', [])
                    print(f"🤝 Found {len(dealers_data)} dealers for price")
                    
                    # Clean date fields
                    for date_field in ['price_date', 'purchase_date']:
                        if price_data.get(date_field) in ('', None):
                            price_data[date_field] = None
                    
                    product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
                    print(f"✅ Created price: {product_price.price} (ID: {product_price.id})")
                    logger.info(f"Created price: {product_price.price} (ID: {product_price.id})")
                    
                    for dealer_index, dealer_data in enumerate(dealers_data):
                        print(f"🤝 Processing dealer {dealer_index + 1}: {dealer_data}")
                        
                        # Clean date fields for dealer
                        if dealer_data.get('purchase_date') in ('', None):
                            dealer_data['purchase_date'] = None
                            
                        Dealer.objects.create(product_price=product_price, **dealer_data)
                        print(f"✅ Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")
                        logger.info(f"Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")

            print(f"🎉 Product creation completed: {product.name}")
            logger.info(f"Product creation completed: {product.name}")
            return product
            
        except Exception as e:
            print(f"❌ Critical error in create method: {e}")
            logger.error(f"Critical error in create method: {e}")
            # Still create the basic product even if nested data fails
            try:
                validated_data.pop('sizes', None)
                validated_data.pop('sizes_parsed', None)
                product = Product.objects.create(**validated_data)
                print(f"⚠️ Created basic product only: {product.name}")
                logger.warning(f"Created basic product only: {product.name}")
                return product
            except Exception as fallback_error:
                print(f"❌ Complete failure in create: {fallback_error}")
                logger.error(f"Complete failure in create: {fallback_error}")
                raise fallback_error

    def update(self, instance, validated_data):
        import logging
        logger = logging.getLogger(__name__)
        
        try:
            print(f"🔧 ProductSerializer.update() called")
            logger.info("ProductSerializer.update() called")
            print(f"📝 Raw validated_data keys: {list(validated_data.keys())}")
            logger.info(f"Raw validated_data keys: {list(validated_data.keys())}")
            
            # Get the parsed sizes data
            sizes_data = validated_data.pop('sizes_parsed', [])
            print(f"📦 Found sizes_parsed: {sizes_data is not None}")
            logger.info(f"Found sizes_parsed: {sizes_data is not None}")
            
            if sizes_data:
                print(f"📦 Sizes count: {len(sizes_data)}")
                logger.info(f"Sizes count: {len(sizes_data)}")
            else:
                print(f"⚠️ No sizes_parsed data found for update!")
                logger.warning("No sizes_parsed data found for update!")
                sizes_data = []
            
            # Remove the original sizes string field if present
            validated_data.pop('sizes', None)

            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            print(f"✅ Updated product: {instance.name} (ID: {instance.id})")
            logger.info(f"Updated product: {instance.name} (ID: {instance.id})")

            # Create Product Sizes with their Prices & Dealers (same logic as create)
            for size_index, size_data in enumerate(sizes_data):
                print(f"📏 Processing size {size_index + 1}: {size_data}")
                logger.info(f"Processing size {size_index + 1}")
                prices_data = size_data.pop('prices', [])
                print(f"💰 Found {len(prices_data)} prices for size: {size_data.get('size', 'Unknown')}")
                
                product_size = ProductSize.objects.create(product=instance, **size_data)
                print(f"✅ Created size: {product_size.size} (ID: {product_size.id})")
                logger.info(f"Created size: {product_size.size} (ID: {product_size.id})")
                
                # Create Product Prices & Dealers for this size
                for price_index, price_data in enumerate(prices_data):
                    print(f"💰 Processing price {price_index + 1}: {price_data}")
                    dealers_data = price_data.pop('dealers', [])
                    print(f"🤝 Found {len(dealers_data)} dealers for price")
                    
                    # Clean date fields
                    for date_field in ['price_date', 'purchase_date']:
                        if price_data.get(date_field) in ('', None):
                            price_data[date_field] = None
                    
                    product_price = ProductPrice.objects.create(product_size=product_size, **price_data)
                    print(f"✅ Created price: {product_price.price} (ID: {product_price.id})")
                    logger.info(f"Created price: {product_price.price} (ID: {product_price.id})")
                    
                    for dealer_index, dealer_data in enumerate(dealers_data):
                        print(f"🤝 Processing dealer {dealer_index + 1}: {dealer_data}")
                        
                        # Clean date fields for dealer
                        if dealer_data.get('purchase_date') in ('', None):
                            dealer_data['purchase_date'] = None
                            
                        Dealer.objects.create(product_price=product_price, **dealer_data)
                        print(f"✅ Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")
                        logger.info(f"Created dealer: {dealer_data.get('dlr_name', 'Unknown')}")

            print(f"🎉 Product update completed: {instance.name}")
            logger.info(f"Product update completed: {instance.name}")
            return instance
            
        except Exception as e:
            print(f"❌ Critical error in update method: {e}")
            logger.error(f"Critical error in update method: {e}")
            # Still update the basic product even if nested data fails
            try:
                validated_data.pop('sizes', None)
                validated_data.pop('sizes_parsed', None)
                for attr, value in validated_data.items():
                    setattr(instance, attr, value)
                instance.save()
                print(f"⚠️ Updated basic product only: {instance.name}")
                logger.warning(f"Updated basic product only: {instance.name}")
                return instance
            except Exception as fallback_error:
                print(f"❌ Complete failure in update: {fallback_error}")
                logger.error(f"Complete failure in update: {fallback_error}")
                raise fallback_error


# -------------------- USER ACCOUNT SERIALIZERS --------------------
class RoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Role
        fields = ['id', 'name', 'description']


class UserAccountSerializer(serializers.ModelSerializer):
    role_details = RoleSerializer(source='role', read_only=True)
    
    class Meta:
        model = UserAccount
        fields = [
            'id', 'username', 'full_name', 'email', 'mobile',
            'is_active', 'is_staff', 'is_superuser', 'date_joined',
            'address_line', 'city', 'state', 'country', 'postal_code',
            'role', 'role_details'
        ]
        read_only_fields = ['id', 'date_joined', 'is_superuser']
        extra_kwargs = {
            'email': {'required': False},
            'is_staff': {'read_only': True},
        }


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, min_length=6)
    confirm_password = serializers.CharField(required=True, write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Old password is incorrect.")
        return value

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError({"confirm_password": "New passwords do not match."})
        
        if data['old_password'] == data['new_password']:
            raise serializers.ValidationError({"new_password": "New password must be different from old password."})
        
        return data

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user