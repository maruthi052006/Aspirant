from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User, Group
from .models import *
from exam.models import *
from main.models import *
import random

import string
from django.core.mail import send_mail



def index(request, user_id):
    user = get_object_or_404(User, id=user_id)
    return render(request, 'students/index.html', {'user': user})


def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def std_signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email')
        ph_no = request.POST.get('ph_no')
        reg_no = request.POST.get('reg_no')
        dep = request.POST.get('dep')
        year = request.POST.get('year')
        clg_name = request.POST.get('clg_name')
        course = request.POST.get('course')
        profile_pic = request.FILES.get('profile_pic')
        class_name = request.FILES.get('profile_pic')

        # Generate a unique username
        base_username = f"{first_name.lower()}{last_name.lower()}"
        username = base_username
        count = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{count}"
            count += 1

        # Generate a random password
        password = generate_password()

        if Student.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Try logging in.")
            return redirect('signup')
        # Create user
        user = User.objects.create_user(username=username, email=email, password=password)
        
        # Create student profile
        student = Student.objects.create(
            user=user,
            username=username,
            first_name=first_name,
            last_name=last_name,
            ph_no=ph_no,
            email=email,
            reg_no=reg_no,
            dep=dep,
            year=year,
            clg_name=clg_name,
            course=course,
            profile_pic=profile_pic,
            password=password,
            class_name=class_name,
        )

        # Add user to 'STUDENT' group
        student_group, created = Group.objects.get_or_create(name='STUDENT')
        student_group.user_set.add(user)

        # Send email with credentials
        subject = "Your Account Credentials - Online Test Platform"
        message = f"Hello {first_name},\n\nYour account has been created successfully.\n\nUsername: {username}\nPassword: {password}\n\nPlease log in and change your password after logging in.\n\nBest regards,\nAdmin Team"
        send_mail(subject, message, 'aspirantcbe@gmail.com', [email])

        return redirect('login')

    return render(request, 'students/std_signup.html')


from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib import messages

def std_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            messages.error(request, "Username and password are required.")
            return redirect('login')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('profile_update', user_id=user.id)
        else:
            messages.error(request, "Invalid username or password.")
            return redirect('login')

    return render(request, 'students/std_login.html')

@login_required
def std_update_profile(request, user_id):
    # if request.user.id != user_id:
    #     return HttpResponse("Unauthorized", status=403)

    user = get_object_or_404(User, id=user_id)
    student = get_object_or_404(Student, user=user)
    results = Result.objects.filter(student=student)

    if request.method == "POST":
        student.first_name = request.POST.get('first_name', student.first_name)
        student.last_name = request.POST.get('last_name', student.last_name)
        student.ph_no = request.POST.get('ph_no', student.ph_no)
        student.dep = request.POST.get('dep', student.dep)
        student.year = request.POST.get('year', student.year)
        student.clg_name = request.POST.get('clg_name', student.clg_name)
        student.course = request.POST.get('course', student.course)
        if 'profile_pic' in request.FILES:
            student.profile_pic = request.FILES['profile_pic']
        user.save()
        student.save()
        messages.success(request, "Profile updated successfully!")
        return redirect('profile_update', user_id=user.id)

    courses = Sources.objects.all()
    # return render(request, "students/std_base.html", {"courses": courses})

    return render(request, 'students/std_profile_update.html', {'user': user, 'student': student, 'results': results,'courses': courses})


def user_logout(request):
    logout(request)
    return redirect('login')


# @login_required
def select_course(request):
    # Get the teacher object for the logged-in user
    student = get_object_or_404(Student, user=request.user)

    # Filter students based on the teacher's college name
    clg = Student.objects.filter(clg_name=Student.clg_name)

    user = get_object_or_404(Student, user=request.user)

    # Filter courses based on students' courses
    courses = Course.objects.filter(course_group=user.course) 
    if request.method == 'POST':
        course_id = request.POST.get('course')
        num_questions = request.POST.get('num_questions')

        if not course_id or not num_questions.isdigit():
            messages.error(request, 'Invalid input')
            return render(request, 'exam/select_course.html', {
                'courses': courses,
            })

        return redirect('start_exam', course_id=course_id, num_questions=int(num_questions))

    return render(request, 'exam/select_course.html', {'courses': courses})



@login_required
def start_exam(request, course_id, num_questions):
    course = get_object_or_404(Course, id=course_id)

    if request.method == 'POST':
        questions = request.session.get('exam_questions', [])
        obtained_marks = 0
        correct_answers = []
        incorrect_answers = []

        for q_id in questions:
            question = Question.objects.get(id=q_id)
            selected_answer = request.POST.get(f"question_{question.id}")
            correct_answer = question.answer.strip().lower()
            explanation = getattr(question, 'explanation', "No explanation available.")

            if selected_answer and selected_answer.strip().lower() == correct_answer:
                obtained_marks += question.marks
                correct_answers.append(f"<b>{question.question}</b><br> Your Answer: <span class='text-success'>{selected_answer}</span> ✅")
            else:
                incorrect_answers.append(f"<b>{question.question}</b><br> Your Answer: <span class='text-danger'>{selected_answer if selected_answer else 'Not Answered'}</span> ❌<br>Correct Answer: <span class='text-success'>{question.answer}</span><br><i>Explanation: {explanation}</i>")

        return render(request, 'exam/exam_result.html', {
            "course": course,
            "obtained_marks": obtained_marks,
            "correct_answers": correct_answers,
            "incorrect_answers": incorrect_answers,
        })

    all_questions = list(Question.objects.filter(course=course))
    if len(all_questions) < int(num_questions):
        return render(request, 'exam/error.html', {'message': 'Not enough questions available for this exam.'})

    questions = random.sample(all_questions, int(num_questions))
    request.session['exam_questions'] = [q.id for q in questions]

    return render(request, 'exam/start_exam.html', {'questions': questions, 'course': course})

def available_courses(request):
    user = get_object_or_404(Student, user=request.user)
    # courses = Course.objects.filter(course=user.course)
    courses = Course.objects.filter(course_group=user.course) 
    return render(request, 'exam/available_courses.html', {'courses': courses})

def slt_start_exam(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    student = get_object_or_404(Student, user=request.user)

    # Check if student already submitted this exam
    if Result.objects.filter(student=student, exam=course).exists():
        messages.warning(request, "You have already submitted this exam.")
        return redirect('profile_update', user_id=request.user.id)

    if request.method == 'POST':
        question_ids = request.session.get('exam_questions', [])
        questions = Question.objects.filter(id__in=question_ids)

        obtained_marks = 0
        correct_answers, incorrect_answers = [], []

        for question in questions:
            selected_answer = request.POST.get(f"question_{question.id}", "").strip().casefold()
            correct_answer = question.answer.strip().casefold()
            reason = question.reason if question.reason else "No explanation provided."

            if selected_answer == correct_answer:
                obtained_marks += question.marks
                correct_answers.append(f"✅ {question.question}\nYour Answer: {selected_answer}\nReason: {reason}")
            else:
                incorrect_answers.append(
                    f"❌ {question.question}\nYour Answer: {selected_answer or 'Not Answered'}\n"
                    f"Correct Answer: {correct_answer}\nReason: {reason}"
                )

        # Store the result in the database
        Result.objects.create(student=student, exam=course, marks=obtained_marks)
        messages.success(request, "Your answers have been submitted successfully.")

        # Prepare and send email with reason
        subject = f"Exam Results for {course.course_name}"
        message = f"Hello {student.first_name},\n\nYou have completed the {course.course_name} exam.\nYour Score: {obtained_marks} Marks\n\n"

        if correct_answers:
            message += "✅ Correct Answers:\n" + "\n".join(correct_answers) + "\n\n"
        if incorrect_answers:
            message += "❌ Incorrect Answers:\n" + "\n".join(incorrect_answers) + "\n\n"

        message += "Best regards,\nAspirant'sTest Platform"
        send_mail(subject, message, 'admin@example.com', [student.user.email])

        return render(request, 'exam/exam_result.html', {
            'course': course,
            'correct_answers': correct_answers,
            'incorrect_answers': incorrect_answers,
            'obtained_marks': obtained_marks
        })

    # Select random questions for the exam
    all_questions = list(Question.objects.filter(course=course))
    if len(all_questions) < 3:
        messages.error(request, "Not enough questions available for this exam.")
        return redirect('profile_update', user_id=request.user.id)

    questions = random.sample(all_questions, 3)
    request.session['exam_questions'] = [q.id for q in questions]

    return render(request, 'exam/slt_start_exam.html', {'questions': questions, 'course': course})




from io import BytesIO
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie

def generate_report_card(request):
    results = Result.objects.filter(student__user=request.user)
    student = request.user

    total_marks = sum(result.marks for result in results)
    num_subjects = len(results)
    average = total_marks / num_subjects if num_subjects > 0 else 0
    cgpa = round(average / 10, 2)

    user = get_object_or_404(Student, user=request.user)
    clg_name = user.clg_name  # Extract college name

    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    p.setFont("Helvetica-Bold", 18)
    p.drawCentredString(width / 2, height - 50, clg_name)  # Use the extracted college name
    p.setFont("Helvetica", 12)
    p.drawCentredString(width / 2, height - 70, "Student Report Card")
    p.line(50, height - 80, width - 50, height - 80)

    p.setFont("Helvetica", 12)
    p.drawString(50, height - 110, f"Name: {student.username}")

    # Table Data
    data = [["Exam", "Marks", "Date"]]
    exam_names = []
    marks = []
    y_position = height - 150
    
    for result in results:
        data.append([result.exam.course_name[:20], str(result.marks), str(result.date)])
        exam_names.append(result.exam.course_name[:10])
        marks.append(result.marks)

    table = Table(data, colWidths=[180, 80, 240])  # Adjusted column widths
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ]))

    table.wrapOn(p, width, height)
    table.drawOn(p, 50, y_position - (len(results) * 20))

    # Total Marks, Average & CGPA
    y_text_position = y_position - (len(results) * 40)
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_text_position, f"Total Marks: {total_marks}")
    p.drawString(50, y_text_position - 20, f"Average Marks: {round(average, 2)}")
    p.drawString(50, y_text_position - 40, f"CGPA: {cgpa}")

    # Pie Chart
    if marks:
        d = Drawing(300, 200)
        pie = Pie()
        pie.x = 75
        pie.y = 50
        pie.width = 200
        pie.height = 200
        pie.data = marks
        pie.labels = exam_names
        pie.slices.strokeWidth = 0.5
        pie.slices[0].popout = 10
        d.add(pie)
        d.drawOn(p, width - 350, y_text_position - 250)
    
    p.showPage()
    p.save()

    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="report_card.pdf"'
    return response