from django.db import models
from django.shortcuts import render
from django.core.validators import FileExtensionValidator

class FileUpload(models.Model):
    folder_path = models.CharField(max_length=255)  # Store full folder path
    file = models.FileField(upload_to='uploads/')  # File storage
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.folder_path}/{self.file.name}"

class Sources(models.Model):
   course_name = models.CharField(max_length=50)
   def __str__(self):
        return self.course_name

class Source_file(models.Model):
    course=models.ForeignKey(Sources,on_delete=models.CASCADE)
    file = models.FileField(
        upload_to="uploads/",
        validators=[FileExtensionValidator(['pdf', 'docx'])]
    )
    title = models.CharField(max_length=255, blank=True) 
    uploaded_at = models.DateTimeField(auto_now_add=True)


from django.db import models

class Clg(models.Model):
    COURSE_CHOICES = [
        ('Aptitude', 'Aptitude'),
        ('SoftSkill', 'Soft Skill'),
        ('Technical', 'Technical'),
    ]

    clg_name = models.CharField(max_length=100, unique=True)
    course_name = models.CharField(max_length=100, choices=COURSE_CHOICES, default='Aptitude')

    def __str__(self):
        return self.clg_name

