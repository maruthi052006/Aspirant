from django.db import models

from students.models import Student
class Course(models.Model):
    COURSE_GROUPS = [
        ('Aptitude', 'Aptitude'),
        ('Soft Skill', 'Soft Skill'),
        ('Technical', 'Technical'),
    ]
    course_group = models.CharField(max_length=20, choices=COURSE_GROUPS, default='Aptitude')
    course_name = models.CharField(max_length=50)
    question_number = models.PositiveIntegerField()
    total_marks = models.PositiveIntegerField()
    is_approved = models.BooleanField(default=False)
    

    def __str__(self):
        return f"{self.course_name} ({self.course_group})"

class Question(models.Model):
    course=models.ForeignKey(Course,on_delete=models.CASCADE)
    marks=models.PositiveIntegerField()
    question=models.CharField(max_length=600)
    option1=models.CharField(max_length=200)
    option2=models.CharField(max_length=200)
    option3=models.CharField(max_length=200)
    option4=models.CharField(max_length=200)
    cat=(('Option1','Option1'),('Option2','Option2'),('Option3','Option3'),('Option4','Option4'))
    answer=models.CharField(max_length=200,choices=cat)
    reason = models.TextField(default="No explanation provided.", blank=True, null=True)

class Result(models.Model):
    student = models.ForeignKey(Student,on_delete=models.CASCADE)
    exam = models.ForeignKey(Course,on_delete=models.CASCADE)
    marks = models.PositiveIntegerField()
    date = models.DateTimeField(auto_now=True)
