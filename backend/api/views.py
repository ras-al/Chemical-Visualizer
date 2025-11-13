from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
import io
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404
from .models import Dataset
from .serializers import DatasetHistorySerializer, DatasetDetailSerializer
from .utils import process_csv_file

class FileUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "This is not a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            file_obj.seek(0)
            summary_data = process_csv_file(file_obj)
            
            file_obj.seek(0)
            dataset = Dataset.objects.create(
                filename=file_obj.name,
                summary_data=summary_data,
                original_file=file_obj
            )
            
            oldest_datasets = Dataset.objects.order_by('uploaded_at')
            if oldest_datasets.count() > 5:
                for old_dataset in oldest_datasets[:oldest_datasets.count() - 5]:
                    old_dataset.delete()
            
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class HistoryView(generics.ListAPIView):
    queryset = Dataset.objects.order_by('-uploaded_at')[:5]
    serializer_class = DatasetHistorySerializer

class SummaryDetailView(APIView):
    
    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        serializer = DatasetDetailSerializer(dataset)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        dataset.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class ReportView(APIView):

    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        summary = dataset.summary_data

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter # (612, 792)

        p.setFont("Helvetica-Bold", 16)
        p.drawString(1 * inch, height - 1 * inch, f"Report for: {dataset.filename}")
        
        p.setFont("Helvetica", 12)
        y = height - 1.5 * inch

        p.drawString(1 * inch, y, f"Total Equipment Count: {summary['total_count']}")
        y -= 0.5 * inch
        
        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, y, "Averages:")
        y -= 0.3 * inch
        
        p.setFont("Helvetica", 12)
        avg = summary['averages']
        p.drawString(1.2 * inch, y, f"Flowrate: {avg['flowrate_avg']}")
        y -= 0.3 * inch
        p.drawString(1.2 * inch, y, f"Pressure: {avg['pressure_avg']}")
        y -= 0.3 * inch
        p.drawString(1.2 * inch, y, f"Temperature: {avg['temperature_avg']} °C")
        y -= 0.5 * inch

        p.setFont("Helvetica-Bold", 14)
        p.drawString(1 * inch, y, "Equipment Distribution:")
        y -= 0.3 * inch

        p.setFont("Helvetica", 12)
        for eq_type, count in summary['type_distribution'].items():
            p.drawString(1.2 * inch, y, f"{eq_type}: {count}")
            y -= 0.3 * inch

        p.showPage()
        p.save()

        buffer.seek(0)
        return HttpResponse(
            buffer,
            content_type='application/pdf',
            headers={'Content-Disposition': f'attachment; filename="{dataset.filename}_report.pdf"'},
        )