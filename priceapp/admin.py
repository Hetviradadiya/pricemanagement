import nested_admin
from django.contrib import admin
from .models import Product, ProductPrice, Dealer, ProductSize
from import_export.admin import ImportExportModelAdmin

# ----------------- Dealer Inline (Nested) -----------------
class DealerInline(nested_admin.NestedTabularInline):
    model = Dealer
    extra = 1
    fields = (
        "dlr_name", "slol", "purchase_date",
        "purchase_price", "purchase_discount", "purchase_discount_price",
        "purchase_tax", "purchase_tax_price",
        "purchase_box", "purchase_box_discount",
        "purchase_box_discount_price", "purchase_box_tax", "purchase_box_tax_price",
    )


# ----------------- ProductPrice Inline (Nested) -----------------
class ProductPriceInline(nested_admin.NestedTabularInline):
    model = ProductPrice
    extra = 1
    inlines = [DealerInline]
    fields = (
        "payment_type", "price", "discount", "discount_price",
        "tax", "tax_price", "box", "box_discount",
        "box_discount_price", "box_tax", "box_tax_price"
    )

@admin.register(ProductPrice)
class ProductPriceAdmin(ImportExportModelAdmin):
    list_display = ("product_size", "payment_type", "price", "discount", "tax")
    search_fields = ("product_size__product__name", "payment_type")


@admin.register(ProductSize)
class ProductSizeAdmin(ImportExportModelAdmin):
    list_display = ("product", "size", "code", "hsn", "mrp")
    search_fields = ("product__name", "size", "code", "hsn")
    list_filter = ("product__name",)
    inlines = [ProductPriceInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('product')


@admin.register(Dealer)
class DealerAdmin(ImportExportModelAdmin):
    list_display = ("dlr_name", "slol", "product_price", "purchase_date", "purchase_price")
    search_fields = ("dlr_name", "slol", "product_price__product_size__product__name")
    list_filter = ("purchase_date", "dlr_name")
    date_hierarchy = "purchase_date"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'product_price__product_size__product'
        )

class ProductSizeInline(nested_admin.NestedTabularInline):
    model = ProductSize
    extra = 1
    inlines = [ProductPriceInline]  # ProductPrice now belongs to ProductSize
    fields = ['size', 'code', 'hsn', 'mrp']
    
# ----------------- Product Admin (Nested) -----------------
@admin.register(Product)
class ProductAdmin(nested_admin.NestedModelAdmin, ImportExportModelAdmin):
    list_display = ("id", "photo", "name")
    search_fields = ("name",)
    inlines = [ProductSizeInline]  # ProductSize belongs to Product

    class Media:
        css = {"all": ("admin/css/custom_admin.css",)}
