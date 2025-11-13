from django.urls import path
from .views import FileUploadView, HistoryView, SummaryDetailView, ReportView

urlpatterns = [
    path('upload/', FileUploadView.as_view(), name='file-upload'),
    path('history/', HistoryView.as_view(), name='history-list'),
    path('summary/<int:pk>/', SummaryDetailView.as_view(), name='summary-detail'),
    path('summary/<int:pk>/report/', ReportView.as_view(), name='summary-report'),

]