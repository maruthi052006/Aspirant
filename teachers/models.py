from django.db import models
from django.contrib.auth.models import User

class Teacher(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Teacher/', null=True, blank=True)
    status = models.BooleanField(default=False)  # Active or Inactive
    email = models.EmailField(unique=True)
    college_name = models.CharField(max_length=255)
    course = models.CharField(max_length=255)
    is_approved = models.BooleanField(default=False)  # Approval from Superuser

    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.user.first_name

class Clg(models.Model):
    clg_name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.clg_name

class Syllabus(models.Model):
    clg = models.ForeignKey(Clg, on_delete=models.CASCADE)  # Link syllabus to a specific college
    day = models.IntegerField()  # Day number
    topic = models.CharField(max_length=255)  # Syllabus topic
    trainer_name = models.CharField(max_length=100)  # Trainer conducting the session

    class Meta:
        unique_together = ('clg', 'day')  # Ensures no duplicate day entries for the same college

    def __str__(self):
        return f"{self.clg.clg_name} - Day {self.day}: {self.topic} (Trainer: {self.trainer_name})"


