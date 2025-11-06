#!/usr/bin/env python
"""
Debug script for testing ProductSerializer on PythonAnywhere
Run this to test if the serializer works correctly in production environment
"""
import os
import sys
import django
from django.conf import settings

# Add the project directory to the path
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(project_dir)

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pricemanagement.settings')
django.setup()

from priceapp.serializers import ProductSerializer
import json

def test_serializer():
    """Test the ProductSerializer with sample data"""
    print("🔍 Testing ProductSerializer...")
    
    # Sample data like what comes from FormData
    test_data = {
        'name': 'Test Product',
        'sizes': json.dumps([
            {
                "size": "32",
                "code": "TP32", 
                "hsn": "TP001",
                "mrp": 100,
                "prices": [
                    {
                        "payment_type": "bill",
                        "price": 50,
                        "discount": 10,
                        "discount_price": 45,
                        "tax": 5,
                        "tax_price": 47.25,
                        "box": 20,
                        "box_discount": 5,
                        "box_discount_price": 900,
                        "box_tax": 5,
                        "box_tax_price": 945,
                        "dealers": [
                            {
                                "dlr_name": "Test Dealer",
                                "slol": "TD001",
                                "purchase_date": "2025-11-06",
                                "purchase_price": 40,
                                "purchase_discount": 5,
                                "purchase_discount_price": 38,
                                "purchase_tax": 3,
                                "purchase_tax_price": 39.14,
                                "purchase_box": 15,
                                "purchase_box_discount": 2,
                                "purchase_box_discount_price": 588,
                                "purchase_box_tax": 3,
                                "purchase_box_tax_price": 605.64
                            }
                        ]
                    }
                ]
            }
        ])
    }
    
    print(f"📝 Test data: {test_data}")
    
    try:
        # Test serializer creation
        serializer = ProductSerializer(data=test_data)
        print(f"✅ Serializer created successfully")
        
        # Test validation
        is_valid = serializer.is_valid()
        print(f"📋 Serializer is_valid(): {is_valid}")
        
        if not is_valid:
            print(f"❌ Validation errors: {serializer.errors}")
            return False
            
        # Test save (create)
        print(f"💾 Attempting to save...")
        product = serializer.save()
        print(f"✅ Product saved successfully: {product.name} (ID: {product.id})")
        
        # Check if nested data was created
        sizes_count = product.sizes.count()
        print(f"📦 Created {sizes_count} sizes")
        
        if sizes_count > 0:
            size = product.sizes.first()
            prices_count = size.prices.count()
            print(f"💰 Created {prices_count} prices for first size")
            
            if prices_count > 0:
                price = size.prices.first()
                dealers_count = price.dealers.count()
                print(f"🤝 Created {dealers_count} dealers for first price")
                
        return True
        
    except Exception as e:
        print(f"❌ Error testing serializer: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🚀 Starting ProductSerializer debug test...")
    success = test_serializer()
    
    if success:
        print("🎉 Serializer test PASSED! The nested data should work on PythonAnywhere.")
    else:
        print("💥 Serializer test FAILED! Check the errors above.")