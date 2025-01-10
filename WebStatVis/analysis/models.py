from django.db import models

# Create your models here.

from django.db import models

class UploadedFile(models.Model):

    '''
    Here, a new class UploadedFile is defined, which inherits from models.Model. 
    This means it will be treated as a database table.
    '''
    name = models.CharField(max_length=255)  # This creates a character field for storing the name of the uploaded file, with a maximum length of 255 characters.
    file = models.FileField(upload_to='uploads/')  # File storage path/ This creates a file field that allows users to upload files. The upload_to argument specifies that uploaded files will be stored in the uploads/ directory.
    uploaded_at = models.DateTimeField(auto_now_add=True)  # Timestamp of upload /This creates a date and time field that automatically records the timestamp when the file is uploaded.

    def __str__(self):
        return self.name
    '''
    This method defines how the UploadedFile object is represented as a string. 
    When you print an instance of this model, it will return the file name.
    '''
    
'''
In summary, the UploadedFile model captures the name, file, and upload timestamp of files uploaded by users,
and it stores this information in a database for later retrieval and management.
'''