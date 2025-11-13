from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, generics
from rest_framework.parsers import MultiPartParser, FormParser
from django.shortcuts import get_object_or_404

from .models import Dataset
from .serializers import DatasetHistorySerializer, DatasetDetailSerializer
from .utils import process_csv_file # This is our new, correct util

class FileUploadView(APIView):
    """
    Handles file upload, analysis, and saving to the database.
    Manages the "last 5" history rule.
    """
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        file_obj = request.FILES.get('file')
        
        if not file_obj:
            return Response({"error": "No file provided"}, status=status.HTTP_400_BAD_REQUEST)
        
        if not file_obj.name.endswith('.csv'):
            return Response({"error": "This is not a CSV file."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 1. Analyze the data using our corrected util
            # We must reset the file pointer after reading it
            file_obj.seek(0)
            summary_data = process_csv_file(file_obj)
            
            # 2. Save the new dataset
            file_obj.seek(0)
            dataset = Dataset.objects.create(
                filename=file_obj.name,
                summary_data=summary_data,
                original_file=file_obj
            )
            
            # 3. Enforce "last 5" history rule
            oldest_datasets = Dataset.objects.order_by('uploaded_at')
            if oldest_datasets.count() > 5:
                for old_dataset in oldest_datasets[:oldest_datasets.count() - 5]:
                    old_dataset.delete() # Our model's delete() handles file removal
            
            # 4. Return the summary of the new upload
            serializer = DatasetDetailSerializer(dataset)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({"error": f"An unexpected error occurred: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

class HistoryView(generics.ListAPIView):
    """
    Provides a list of the last 5 uploaded datasets.
    """
    queryset = Dataset.objects.order_by('-uploaded_at')[:5]
    serializer_class = DatasetHistorySerializer

# --- MODIFIED CLASS ---
class SummaryDetailView(APIView):
    """
    Retrieves (GET) or Deletes (DELETE) the summary_data 
    for a single dataset by its ID.
    """
    def get(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        # Return only the JSON summary data
        return Response(dataset.summary_data, status=status.HTTP_200_OK)

    # --- ADD THIS NEW METHOD ---
    def delete(self, request, pk):
        dataset = get_object_or_404(Dataset, pk=pk)
        dataset.delete() # This will trigger our model's custom delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    # --------------------------