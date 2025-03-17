from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate,logout
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.utils.timezone import now
from django.db.models import Count, Q, Avg
import json

# Import models explicitly
from django.contrib.auth.models import User, Group
from teachers.models import *
from students.models import *
from exam.models import *


def teacher_signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        password = request.POST.get('password')
        email = request.POST.get('email')
        college_name = request.POST.get('college_name')
        course = request.POST.get('course')
        profile_pic = request.FILES.get('profile_pic')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists!")
            return redirect('teacher_signup')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return redirect('teacher_signup')

        user = User.objects.create_user(username=username, first_name=first_name, last_name=last_name, password=password)
        teacher = Teacher.objects.create(user=user, email=email, college_name=college_name, course=course, profile_pic=profile_pic)

        # Assign user to the TEACHER group
        my_teacher_group, created = Group.objects.get_or_create(name='TEACHER')
        my_teacher_group.user_set.add(user)

        messages.success(request, "Signup successful! Wait for admin approval.")
        return redirect('teacherlogin')

    return render(request, 'teachers/teachersignup.html')


def teacher_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is not None:
            teacher = Teacher.objects.filter(user=user).first()
            if teacher and teacher.is_approved:
                login(request, user)
                return redirect('teacher_dashboard')  # Redirect to teacher index page
            else:
                messages.error(request, "Your account is pending admin approval.")
                return redirect('teacherlogin')
        else:
            messages.error(request, "Invalid credentials!")
    
    return render(request, 'teachers/teacherlogin.html')

from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def approve_teachers(request):
    pending_teachers = Teacher.objects.filter(is_approved=False)
    
    if request.method == "POST":
        teacher_id = request.POST.get('teacher_id')
        teacher = Teacher.objects.get(id=teacher_id)
        teacher.is_approved = True
        teacher.save()
        messages.success(request, f"{teacher.user.first_name} is now approved.")
        return redirect('approve_teachers')  # Refresh after approval

    return render(request, 'admin/approve_teachers.html', {'pending_teachers': pending_teachers})


from django.contrib.auth.decorators import login_required

from django.shortcuts import render, redirect, get_object_or_404
from .models import Teacher, Clg, Syllabus  # Ensure your models are correctly imported


import json
from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q, Avg
# from .models import Teacher, Student, Attendance, Result, Clg, Syllabus

@login_required
def teacher_dashboard(request):
    teacher = get_object_or_404(Teacher, user=request.user)

    if not teacher.is_approved:
        return redirect('teacherlogin')

    syllabus_data = {}
    colleges = Clg.objects.filter(clg_name=teacher.college_name)

    for college in colleges:
        syllabus_data[college.clg_name] = Syllabus.objects.filter(clg=college).order_by("day")

    today = date.today()
    selected_class = request.GET.get('class_name', None)

    attendance_query = Student.objects.values('class_name')
    if selected_class:
        attendance_query = attendance_query.filter(class_name=selected_class)

    attendance_summary = (
        attendance_query.annotate(
            total_students=Count('id'),
            present=Count('attendance', filter=Q(attendance__date=today, attendance__status=True)),
            absent=Count('attendance', filter=Q(attendance__date=today, attendance__status=False)),
        )
    )

    attendance_data = []
    class_names = []
    attendance_percentages = []

    for record in attendance_summary:
        total = record['total_students']
        present = record['present']
        percentage = (present / total * 100) if total > 0 else 0

        attendance_data.append({
            'class_name': record['class_name'],
            'total_students': total,
            'present': present,
            'absent': record['absent'],
            'attendance_percentage': round(percentage, 2)
        })

        class_names.append(record['class_name'])
        attendance_percentages.append(round(percentage, 2))

    # Exam results (average marks per class)
    exam_query = Result.objects.values('student__class_name')
    if selected_class:
        exam_query = exam_query.filter(student__class_name=selected_class)

    exam_results = exam_query.annotate(avg_marks=Avg('marks'))

    exam_class_names = []
    exam_avg_marks = []

    for result in exam_results:
        exam_class_names.append(result['student__class_name'])
        exam_avg_marks.append(round(result['avg_marks'], 2))

    context = {
        "syllabus_data": syllabus_data,
        "attendance_data": attendance_data,
        "class_names": json.dumps(class_names),
        "attendance_percentages": json.dumps(attendance_percentages),
        "exam_class_names": json.dumps(exam_class_names),
        "exam_avg_marks": json.dumps(exam_avg_marks),
        "selected_class": selected_class
    }

    return render(request, 'teachers/dashboard.html', context)



@login_required
def student_list(request):
    teacher = get_object_or_404(Teacher, user=request.user)  # Get the logged-in teacher
    students = Student.objects.filter(clg_name=teacher.college_name) 
    return render(request, 'teachers/students_list.html', {'students': students})

@login_required
def syllabus_view(request):
    if request.method == "POST":
        clg_id = request.POST.get("clg")  # Get College ID
        day = request.POST.get("day")  # Get Day
        topic = request.POST.get("topic")  # Get Topic
        trainer_name = request.POST.get("trainer_name")  # Get Trainer Name

        if clg_id and day and topic and trainer_name:
            clg = Clg.objects.get(id=clg_id)  # Fetch the college object
            # Save syllabus entry
            Syllabus.objects.create(clg=clg, day=day, topic=topic, trainer_name=trainer_name)
            return redirect("syllabus")  # Redirect to avoid duplicate submissions

    # Retrieve all syllabus items grouped by college
    syllabus_data = {}
    colleges = Clg.objects.all()

    for college in colleges:
        syllabus_data[college.clg_name] = Syllabus.objects.filter(clg=college).order_by("day")

    return render(request, "admin/dashboard.html", {"syllabus_data": syllabus_data, "colleges": colleges})


from datetime import date
from django.shortcuts import render, get_object_or_404, redirect
# from .models import Attendance, Student, Teacher

def mark_attendance(request):
    teacher = get_object_or_404(Teacher, user=request.user)  # Get the logged-in teacher
    students = Student.objects.filter(clg_name=teacher.college_name)  # Fetch students from the same college
    today = date.today()  # Get the current date

    if request.method == "POST":
        for key, value in request.POST.items():
            if key.startswith("student_"):  
                student_id = key.replace("student_", "")  # Extract student ID
                student = students.filter(id=student_id).first()  # Ensure only valid students are processed
                
                if student:
                    status = True if value.lower() == "present" else False
                    
                    # Check if an attendance record already exists for this student and date
                    attendance = Attendance.objects.filter(student=student, date=today).first()

                    if attendance:
                        attendance.status = status  # Update status
                        attendance.save()
                    else:
                        Attendance.objects.create(student=student, date=today, status=status)  # Create new record

        return redirect('class_wise_attendance')  # Redirect after submission

    return render(request, 'admin/mark_attendance.html', {'students': students})


from django.shortcuts import render
from django.db.models import Count, Avg, Q
from datetime import date
import json

def class_wise_attendance(request):
    today = date.today()
    selected_class = request.GET.get('class_name', None)  # Get selected class from request

    # Fetch attendance data
    attendance_query = Student.objects.values('class_name')
    if selected_class:
        attendance_query = attendance_query.filter(class_name=selected_class)

    attendance_summary = (
        attendance_query.annotate(
            total_students=Count('id'),
            present=Count('attendance', filter=Q(attendance__date=today, attendance__status=True)),
            absent=Count('attendance', filter=Q(attendance__date=today, attendance__status=False)),
        )
    )

    attendance_data = []
    class_names = []
    attendance_percentages = []

    for record in attendance_summary:
        total = record['total_students']
        present = record['present']
        percentage = (present / total * 100) if total > 0 else 0

        attendance_data.append({
            'class_name': record['class_name'],
            'total_students': total,
            'present': present,
            'absent': record['absent'],
            'attendance_percentage': round(percentage, 2)
        })

        class_names.append(record['class_name'])
        attendance_percentages.append(round(percentage, 2))

    # Fetch exam result data (average marks per class)
    exam_query = Result.objects.values('student__class_name')
    if selected_class:
        exam_query = exam_query.filter(student__class_name=selected_class)

    exam_results = exam_query.annotate(avg_marks=Avg('marks'))

    exam_class_names = []
    exam_avg_marks = []

    for result in exam_results:
        exam_class_names.append(result['student__class_name'])
        exam_avg_marks.append(round(result['avg_marks'], 2))

    context = {
        'attendance_data': attendance_data,
        'class_names': json.dumps(class_names),  
        'attendance_percentages': json.dumps(attendance_percentages),
        'exam_class_names': json.dumps(exam_class_names),
        'exam_avg_marks': json.dumps(exam_avg_marks),
        'selected_class': selected_class
    }

    return render(request, 'teachers/dashboard.html', context)

def exam_performance(request):
    exam_results = (
        Result.objects
        .values('student__class_name', 'exam__course_name')  # Match your Course model field
        .annotate(avg_marks=Avg('marks'))
        .order_by('student__class_name', 'exam__course_name')
    )

    class_data = {}
    exam_labels = set()

    for result in exam_results:
        class_name = result['student__class_name']
        exam_name = result['exam__course_name']  # Match your Course model
        avg_marks = round(result['avg_marks'], 2)

        exam_labels.add(exam_name)

        if class_name not in class_data:
            class_data[class_name] = []
        
        class_data[class_name].append(avg_marks)

    chart_series = [{"name": cls, "data": marks} for cls, marks in class_data.items()]

    context = {
        'chart_series': json.dumps(chart_series),
        'exam_labels': json.dumps(list(exam_labels)),
    }

    return render(request, 'teachers/dashboard.html', context)

def view_profile(request, user_id):

    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, user=user)
    results = Result.objects.filter(student=student)

    return render(request, 'admin/std_profile.html', {'user': user, 'student': student, 'results': results})

def user_logout(request):
    logout(request)
    return redirect('login')