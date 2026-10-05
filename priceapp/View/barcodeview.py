import io
import uuid
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.graphics.barcode import code128
from reportlab.lib.units import mm

from ..models import Product
from ..serializers import ProductSerializer

# 1. SCAN API: Look up product by barcode string
class ProductBarcodeScanView(APIView):
    def get(self, request):
        code = request.query_params.get('barcode', '').strip()
        if not code:
            return Response({'error': 'Barcode parameter required'}, status=status.HTTP_400_BAD_REQUEST)

        product = Product.objects.filter(barcode__iexact=code).first()
        if not product:
            return Response({'error': f'Product with barcode "{code}" not found.'}, status=status.HTTP_404_NOT_FOUND)

        serializer = ProductSerializer(product, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class GenerateBulkBarcodePdfView(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        select_all = data.get('all', False)
        product_ids = data.get('product_ids', [])
        
        try:
            copies = int(data.get('copies', 1))
            if copies < 1:
                copies = 1
        except (ValueError, TypeError):
            copies = 1

        print(f">>> Processing: select_all={select_all}, product_ids={product_ids}, copies={copies}")

        if select_all:
            products = list(Product.objects.all().order_by('id'))
        elif product_ids:
            products = list(Product.objects.filter(id__in=product_ids).order_by('id'))
        else:
            print(">>> ERROR: No products selected")
            return Response({
                'status': False,
                'message': 'No products selected for barcode PDF generation.',
                'file_url': None
            }, status=status.HTTP_400_BAD_REQUEST)

        if not products:
            print(">>> ERROR: No matching products found in database")
            return Response({
                'status': False,
                'message': 'No matching products found in database.',
                'file_url': None
            }, status=status.HTTP_404_NOT_FOUND)

        # Build list multiplied by copies
        items_to_print = []
        for prod in products:
            for _ in range(copies):
                items_to_print.append(prod)

        print(f">>> Total sticker items to render: {len(items_to_print)}")

        # Create PDF layout
        buffer = io.BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)
        page_width, page_height = A4

        label_w = 60 * mm
        label_h = 32 * mm
        margin_x = 10 * mm
        margin_y = 15 * mm
        cols = 3
        gap_x = 4 * mm
        gap_y = 3 * mm

        x = margin_x
        y = page_height - margin_y - label_h
        col_count = 0

        for prod in items_to_print:
            barcode_val = prod.barcode or f"PRD{prod.id:06d}"

            # Label box outline
            pdf.setStrokeColorRGB(0.82, 0.82, 0.82)
            pdf.setLineWidth(0.6)
            pdf.roundRect(x, y, label_w, label_h, 2.5 * mm, stroke=1, fill=0)

            # Product Name
            pdf.setFont("Helvetica-Bold", 8)
            pdf.setFillColorRGB(0.12, 0.12, 0.12)
            pdf.drawString(x + 3 * mm, y + label_h - 5 * mm, str(prod.name)[:24])

            # Company / VP
            pdf.setFont("Helvetica", 7)
            pdf.setFillColorRGB(0.35, 0.35, 0.35)
            comp_vp = f"{prod.company_name or ''} {f'({prod.vp_name})' if prod.vp_name else ''}".strip()
            if comp_vp:
                pdf.drawString(x + 3 * mm, y + label_h - 8.5 * mm, comp_vp[:28])

            # Barcode
            try:
                barcode_obj = code128.Code128(barcode_val, barWidth=0.25 * mm, barHeight=9.5 * mm)
                barcode_obj.drawOn(pdf, x + 3 * mm, y + 6.5 * mm)
            except Exception as e:
                print(f">>> Barcode draw warning for {barcode_val}: {e}")

            # Barcode Text
            pdf.setFont("Helvetica-Bold", 7)
            pdf.setFillColorRGB(0.1, 0.1, 0.1)
            pdf.drawCentredString(x + (label_w / 2), y + 2.5 * mm, barcode_val)

            col_count += 1
            if col_count % cols == 0:
                x = margin_x
                y -= label_h + gap_y
            else:
                x += label_w + gap_x

            if y < margin_y:
                pdf.showPage()
                y = page_height - margin_y - label_h
                x = margin_x

        pdf.save()
        buffer.seek(0)

        # Save PDF to media storage
        filename = f"barcodes_batch_{uuid.uuid4().hex[:8]}.pdf"
        file_path = f"barcodes_pdf/{filename}"

        saved_path = default_storage.save(file_path, ContentFile(buffer.getvalue()))
        file_url = request.build_absolute_uri(settings.MEDIA_URL + saved_path)

        print(f">>> [SUCCESS] PDF Generated at: {file_url}")
        print("="*50 + "\n")

        return Response({
            'status': True,
            'message': f'Generated {len(items_to_print)} barcodes successfully.',
            'total_barcodes': len(items_to_print),
            'file_url': file_url
        }, status=status.HTTP_200_OK)