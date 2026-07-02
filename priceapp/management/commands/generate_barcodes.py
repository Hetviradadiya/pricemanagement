from django.core.management.base import BaseCommand
from django.utils import timezone
from django.db.models import Q
from django.core.files.base import File
from io import BytesIO
import barcode
from barcode.writer import ImageWriter
from priceapp.models import Product  # Adjust 'priceapp' if your app name is different

class Command(BaseCommand):
    help = 'Generates missing barcode numbers and images for existing products.'

    def handle(self, *args, **kwargs):
        # Find products missing either the barcode string OR the barcode image
        products_missing_barcodes = Product.objects.filter(
            Q(barcode__isnull=True) | Q(barcode__exact='') |
            Q(barcode_image__isnull=True) | Q(barcode_image__exact='')
        )
        
        total_found = products_missing_barcodes.count()
        
        if total_found == 0:
            self.stdout.write(self.style.WARNING('No products found missing barcodes or images. You are all set!'))
            return

        self.stdout.write(f"Found {total_found} products needing barcode updates. Generating now...")
        
        current_year = timezone.now().year
        success_count = 0

        for product in products_missing_barcodes:
            try:
                # 1. Generate the Barcode Number if it doesn't exist yet
                if not product.barcode:
                    product.barcode = f"{current_year}{product.id:06d}"
                
                # 2. Generate the Barcode Image (Code128 format)
                CODE128 = barcode.get_barcode_class('code128')
                bc = CODE128(product.barcode, writer=ImageWriter())
                
                # Save it to memory
                buffer = BytesIO()
                bc.write(buffer, options={'write_text': False, 'module_height': 10.0})
                
                # 3. Save the image file to the Django ImageField
                file_name = f"barcode_{product.barcode}.png"
                product.barcode_image.save(file_name, File(buffer), save=False)
                
                # 4. Save both the string and the image to the database
                product.save(update_fields=['barcode', 'barcode_image'])
                success_count += 1
                
                # Print progress to the terminal
                self.stdout.write(self.style.SUCCESS(f'Successfully generated barcode & image for {product.name} ({product.barcode})'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed to update product ID {product.id}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS(f'\nFinished! Successfully updated {success_count} products.'))