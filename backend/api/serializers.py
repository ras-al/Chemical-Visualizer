from rest_framework import serializers
from .models import Dataset

# Serializer for the history list (less data)
class DatasetHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        # We only need basic info for the list
        fields = ['id', 'filename', 'uploaded_at']

# Serializer for the main upload response (includes the summary)
class DatasetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        # Show all fields, including the summary
        fields = ['id', 'filename', 'uploaded_at', 'summary_data']