from django.db import models
from django.contrib.auth.models import User
import os
from django.utils.timezone import now, timedelta
from main.models import *

class Trainer(models.Model):
    SPECIALIZATION_CHOICES = [
        ('Aptitude', 'Aptitude'),
        ('Soft Skill', 'Soft Skill'),
        ('Technical', 'Technical'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    ph_no = models.CharField(max_length=15)
    specialization = models.CharField(max_length=50, choices=SPECIALIZATION_CHOICES, default='Technical')
    clg = models.OneToOneField(Clg, on_delete=models.CASCADE, null=True, blank=True, related_name="trainer")
    profile_pic = models.ImageField(upload_to='trainer_profiles/', blank=True, null=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.specialization}"

class TrainingPDF(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    pdf = models.FileField(upload_to='training_pdfs/')
    created_at = models.DateTimeField(auto_now_add=True)

    def is_expired(self):
        return self.created_at < now() - timedelta(days=1)  # Expires after 24 hours

    def delete_if_expired(self):
        if self.is_expired():
            if self.pdf:
                os.remove(self.pdf.path)  # Delete file from storage
            self.delete()

    def __str__(self):
        return f"Training PDF by {self.trainer} on {self.created_at.strftime('%Y-%m-%d')}"
