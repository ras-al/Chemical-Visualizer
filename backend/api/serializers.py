from rest_framework import serializers
from .models import Dataset

class DatasetHistorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at']

class DatasetDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = ['id', 'filename', 'uploaded_at', 'summary_data']