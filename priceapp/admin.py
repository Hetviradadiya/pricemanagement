import nested_admin
from django.contrib import admin
from .models import Product, ProductPrice, Dealer, ProductSize, UserAccount, Role, Module, LoginRecord
from import_export.admin import ImportExportModelAdmin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django import forms

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


# ----------------- Role Admin -----------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


# ----------------- Module Admin -----------------
@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "created_at", "updated_at")
    search_fields = ("name", "description")
    list_filter = ("created_at",)


# ----------------- LoginRecord Admin -----------------
@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    list_display = ("user", "ip_address", "login_time", "user_agent")
    search_fields = ("user__full_name", "user__email", "ip_address")
    list_filter = ("login_time",)
    readonly_fields = ("user", "ip_address", "login_time", "user_agent")
    date_hierarchy = "login_time"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# ----------------- UserAccount Forms -----------------
class UserAccountChangeForm(forms.ModelForm):
    """Form for updating users. Includes all fields but replaces password with admin's password hash display field."""
    password = ReadOnlyPasswordHashField(
        label="Password",
        help_text=(
            "Raw passwords are not stored, so there is no way to see this "
            "user's password, but you can change the password using "
            '<a href="../password/">this form</a>.'
        ),
    )

    class Meta:
        model = UserAccount
        fields = '__all__'

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial.get("password")


class UserAccountCreationForm(forms.ModelForm):
    """Form for creating new users. Includes all required fields plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = UserAccount
        fields = ('email', 'full_name', 'mobile', 'username')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


# ----------------- UserAccount Admin -----------------
@admin.register(UserAccount)
class UserAccountAdmin(BaseUserAdmin):
    form = UserAccountChangeForm
    add_form = UserAccountCreationForm
    
    list_display = ("email", "full_name", "mobile", "role", "is_active", "is_staff", "is_superuser", "date_joined")
    list_filter = ("is_active", "is_staff", "is_superuser", "role", "date_joined")
    search_fields = ("email", "full_name", "mobile", "username")
    ordering = ("-date_joined",)
    
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("username", "full_name", "mobile")}),
        ("Address", {"fields": ("address_line", "city", "state", "country", "postal_code")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "role", "groups", "user_permissions")}),
        ("Important Dates", {"fields": ("date_joined", "last_login")}),
        ("Metadata", {"fields": ("created_by",)}),
    )
    
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "mobile", "password1", "password2", "role", "is_staff", "is_active"),
        }),
    )
    
    readonly_fields = ("date_joined", "last_login")
    filter_horizontal = ("groups", "user_permissions")
