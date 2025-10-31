from django.db import models

# -------------------- PRODUCT --------------------
class Product(models.Model):
    photo = models.ImageField(upload_to="products/", blank=True, null=True)
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name
    
class ProductSize(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="sizes")
    size = models.CharField(max_length=50, blank=True, null=True)
    code = models.CharField(max_length=50, blank=True, null=True)
    hsn = models.CharField(max_length=50, blank=True, null=True)
    mrp = models.FloatField(default=0,blank=True, null=True)

    def __str__(self):
        return f"{self.product.name} {(self.size)}"


# -------------------- PAYMENT TYPE --------------------
PAYMENT_TYPE_CHOICES = [
    ("cash", "Cash"),
    ("bill", "Bill"),
    ("sale_cash", "Sale Cash"),
    ("sale_bill", "Sale Bill"),
    ("frd_cash", "Frd Cash"),
    ("frd_bill", "Frd Bill"),
]


# -------------------- PRODUCT PRICE --------------------
class ProductPrice(models.Model):
    product_size = models.ForeignKey(ProductSize, on_delete=models.CASCADE, related_name="prices",null=True,blank=True)
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPE_CHOICES)

    # --- Selling Price Fields ---
    price = models.FloatField(default=0)
    discount = models.FloatField(default=0)
    discount_price = models.FloatField(default=0)
    tax = models.FloatField(default=0)
    tax_price = models.FloatField(default=0)

    box = models.FloatField(default=0)
    box_discount = models.FloatField(default=0)
    box_discount_price = models.FloatField(default=0)
    box_tax = models.FloatField(default=0)
    box_tax_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.product_size.product.name} - {self.product_size.size} ({self.payment_type})"

    @property
    def final_price(self):
        subtotal = self.price - (self.price * self.discount / 100)
        return subtotal + (subtotal * self.tax / 100)


# -------------------- DEALER --------------------
class Dealer(models.Model):
    product_price = models.ForeignKey(ProductPrice, on_delete=models.CASCADE, related_name="dealers")

    # --- Dealer Info ---
    dlr_name = models.CharField(max_length=100,blank=True, null=True)
    slol = models.CharField(max_length=100, blank=True, null=True)

    # --- Dealer-specific Purchase Fields ---
    purchase_date = models.DateField(blank=True, null=True)
    purchase_price = models.FloatField(default=0)
    purchase_discount = models.FloatField(default=0)
    purchase_discount_price = models.FloatField(default=0)
    purchase_tax = models.FloatField(default=0)
    purchase_tax_price = models.FloatField(default=0)

    purchase_box = models.FloatField(default=0)
    purchase_box_discount = models.FloatField(default=0)
    purchase_box_discount_price = models.FloatField(default=0)
    purchase_box_tax = models.FloatField(default=0)
    purchase_box_tax_price = models.FloatField(default=0)

    def __str__(self):
        return f"{self.dlr_name} ({self.slol}) - {self.product_price.product_size.product.name}"

    @property
    def final_purchase_price(self):
        subtotal = self.purchase_price - (self.purchase_price * self.purchase_discount / 100)
        return subtotal + (subtotal * self.purchase_tax / 100)
    
from django.db import models
from django.contrib.auth.models import User,AbstractUser,Group,Permission,BaseUserManager
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone

# Create your models here.
class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True

class AccountManager(BaseUserManager):
    use_in_migrations = True
 
    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)  # This hashes the password
        user.save(using=self._db)
        return user
 
    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)
 
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', Role.objects.get_or_create(name='Admin')[0])
 
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
 
        return self._create_user(email, password, **extra_fields)
 
class Role(BaseModel):     
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return self.name
 
 
class Module(BaseModel):   
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
 
    def __str__(self):
        return self.name
   
 
class UserAccount(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=20, unique=True, blank=True, null=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(verbose_name="email_address", max_length=255, unique=True)
    mobile = models.CharField(max_length=20,unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    address_line = models.TextField(blank=True, null=True)
    city = models.CharField(blank=True, null=True, max_length=255)
    state = models.CharField(blank=True, null=True, max_length=255)
    country = models.CharField(blank=True, null=True, max_length=255)
    postal_code = models.CharField(blank=True, null=True, max_length=255)
    role = models.ForeignKey(Role, null=True, blank=True, on_delete=models.SET_NULL)
    created_by = models.ForeignKey(
        'self', null=True, blank=True, on_delete=models.SET_NULL, related_name='created_users'
    )
   
    objects = AccountManager()
 
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['full_name','mobile']
 
    def __str__(self):
        return self.full_name
 
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

class LoginRecord(models.Model):
    user = models.ForeignKey(UserAccount, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    login_time = models.DateTimeField(auto_now_add=True)
    user_agent = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.ip_address} at {self.login_time}"