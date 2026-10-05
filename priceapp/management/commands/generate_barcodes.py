import uuid
from io import BytesIO
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import barcode
from barcode.writer import ImageWriter
from priceapp.models import Product


class Command(BaseCommand):
    help = 'Generate barcodes and barcode image files for existing products missing them.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Regenerate barcode and barcode images for ALL products, even if they already have one.',
        )

    def handle(self, *args, **options):
        force = options['force']
        
        if force:
            products = Product.objects.all()
            self.stdout.write(self.style.WARNING(f'Force mode active: checking all {products.count()} products...'))
        else:
            # Only pick products where barcode or barcode_image is empty
            products = Product.objects.filter(barcode__isnull=True) | Product.objects.filter(barcode='') | Product.objects.filter(barcode_image='')
            products = products.distinct()

        total = products.count()
        if total == 0:
            self.stdout.write(self.style.SUCCESS('All products already have barcodes and images. Nothing to do!'))
            return

        self.stdout.write(f'Found {total} products needing barcodes. Starting generation...')

        code128_class = barcode.get_barcode_class('code128')
        writer = ImageWriter()
        writer.set_options({'write_text': True, 'module_height': 12.0})

        updated_count = 0

        for product in products:
            # 1. Assign barcode string if missing or forced
            if not product.barcode or force:
                product.barcode = f"RT{uuid.uuid4().hex[:10].upper()}"

            # 2. Generate barcode PNG image if missing or forced
            if not product.barcode_image or force:
                bc = code128_class(product.barcode, writer=writer)
                buffer = BytesIO()
                bc.write(buffer)
                
                filename = f"barcode_{product.barcode}.png"
                product.barcode_image.save(filename, ContentFile(buffer.getvalue()), save=False)

            # Save product record without triggering extra signals or resets
            product.save(update_fields=['barcode', 'barcode_image'])
            updated_count += 1

            self.stdout.write(f'[{updated_count}/{total}] Processed: {product.name} -> Barcode: {product.barcode}')

        self.stdout.write(self.style.SUCCESS(f'\nSuccessfully generated barcodes for {updated_count} products!'))