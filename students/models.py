from django.db import models
from django.contrib.auth.models import User

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True) 
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=150)
    username = models.CharField(max_length=150)
    email = models.EmailField(unique=True, null=False)
    ph_no = models.CharField(max_length=15)
    reg_no = models.CharField(max_length=15, unique=True)
    dep = models.CharField(max_length=255)
    year = models.CharField(max_length=255)
    clg_name = models.CharField(max_length=255)
    course = models.CharField(max_length=255, null=True)
    profile_pic = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    password = models.CharField(max_length=255)
    class_name = models.CharField(max_length=50, null=True, blank=True, default="Not Assigned") 

    def __str__(self):
        return self.first_name
    
class Attendance(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    date = models.DateField(auto_now_add=True)
    status = models.BooleanField(default=True)  # True = Present, False = Absent

    def __str__(self):
        return f"{self.student.first_name} - {self.date} - {'Present' if self.status else 'Absent'}"
