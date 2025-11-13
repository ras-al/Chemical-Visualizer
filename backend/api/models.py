from django.db import models
import os

class Dataset(models.Model):
    # We will store the original filename
    filename = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # This JSONField will store the summary from utils.py
    summary_data = models.JSONField()
    
    # Storing the file itself is optional but good for history
    original_file = models.FileField(upload_to='csv_uploads/', null=True, blank=True)

    def __str__(self):
        return self.filename

    def delete(self, *args, **kwargs):
        # Clean up the associated file when the record is deleted
        if self.original_file:
            if os.path.isfile(self.original_file.path):
                os.remove(self.original_file.path)
        super(Dataset, self).delete(*args, **kwargs)