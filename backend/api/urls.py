from django.urls import path
from .views import FileUploadView, HistoryView, SummaryDetailView

urlpatterns = [
    # POST /api/upload/
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    
    # GET /api/history/
    path('history/', HistoryView.as_view(), name='history-list'),
    
    # GET /api/summary/<int:pk>/
    path('summary/<int:pk>/', SummaryDetailView.as_view(), name='summary-detail'),
]