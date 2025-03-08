import random
import string
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User, Group
from django.core.mail import send_mail
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from main.models import *
from .models import *

def generate_password():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=8))

def trainer_signup(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name').strip()
        last_name = request.POST.get('last_name').strip()
        email = request.POST.get('email')
        ph_no = request.POST.get('ph_no')
        specialization = request.POST.get('specialization')
        clg_id = request.POST.get('clg')
        profile_pic = request.FILES.get('profile_pic')

        base_username = f"{first_name.lower()}{last_name.lower()}"
        username = base_username
        count = 1

        while User.objects.filter(username=username).exists():
            username = f"{base_username}{count}"
            count += 1

        password = generate_password()

        if Trainer.objects.filter(email=email).exists():
            messages.error(request, "This email is already registered. Try logging in.")
            return redirect('trainer_signup')

        user = User.objects.create_user(username=username, email=email, password=password)
        clg = Clg.objects.get(id=clg_id) if clg_id else None

        trainer = Trainer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            ph_no=ph_no,
            email=email,
            specialization=specialization,
            clg=clg,
            profile_pic=profile_pic,
        )

        trainer_group, created = Group.objects.get_or_create(name='TRAINER')
        trainer_group.user_set.add(user)

        subject = "Trainer Account Created"
        message = f"Hello {first_name},\n\nYour trainer account has been created successfully.\n\nUsername: {username}\nPassword: {password}\n\nBest regards,\nAdmin Team"
        send_mail(subject, message, 'aspirantcbe@gmail.com', [email])

        return redirect('trainer_login')

    colleges = Clg.objects.all()
    return render(request, 'trainers/trainer_signup.html', {'colleges': colleges})

def trainer_login(request):
    if request.method == "POST":
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None and hasattr(user, 'trainer'):
            login(request, user)
            return redirect('trainer_dashboard')  # Redirect to dashboard
        else:
            messages.error(request, "Invalid credentials or not a trainer account.")

    return render(request, 'trainers/trainer_login.html')

@login_required
def trainer_dashboard(request):
    trainer = Trainer.objects.get(user=request.user)
    pdfs = TrainingPDF.objects.filter(trainer=trainer)

    return render(request, 'trainers/trainer_dashboard.html', {'trainer': trainer, 'pdfs': pdfs})


import mimetypes
from django.http import HttpResponse, FileResponse
from django.shortcuts import get_object_or_404

from django.shortcuts import get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required

@login_required
def view_pdf(request, pdf_id):
    pdf = get_object_or_404(TrainingPDF, id=pdf_id, trainer__user=request.user)

    if pdf.is_expired():
        pdf.delete_if_expired()
        return HttpResponse("This PDF has expired.", status=403)

    return render(request, 'trainers/view_pdf.html', {'pdf_url': pdf.pdf.url})

def user_logout(request):
    logout(request)
    return redirect('login')