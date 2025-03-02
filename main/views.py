from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from .models import FileUpload
import os
from django.conf import settings
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Source_file, Sources
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

# Admin Login View (without using Django forms)
def admin_login(request):
    if request.user.is_authenticated and request.user.is_superuser:
        return redirect('upload_pdf')  # Redirect if already logged in
    
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_superuser:
            login(request, user)
            return redirect('index')  # Redirect to upload page
        else:
            messages.error(request, "Invalid Credentials or Not a Superuser")
    
    return render(request, 'admin/admin_login.html')

# Admin Logout View
@login_required
def admin_logout(request):
    logout(request)
    return redirect('admin_login')

# Check if user is a superuser
def superuser_required(user):
    return user.is_superuser

# View to upload PDF (only for superusers)
@login_required
@user_passes_test(superuser_required)
def upload_pdf(request):
    if request.method == 'POST':
        course_id = request.POST.get('course')
        pdf_file = request.FILES.get('file')
        file_title = request.POST.get('title')  # Get title from form input

        if course_id and pdf_file:
            course = Sources.objects.get(id=course_id)
            Source_file.objects.create(course=course, file=pdf_file, title=file_title)
            return redirect('view_pdfs')

    courses = Sources.objects.all()
    return render(request, 'admin/upload_pdf.html', {'courses': courses})

# View to display PDFs (accessible to all users)
from django.http import HttpResponse
import mimetypes
def view_pdfs(request):
    files = Source_file.objects.all()
    return render(request, 'admin/view_pdfs.html', {'files': files})


from django.shortcuts import get_object_or_404
from django.http import FileResponse

def view_pdf(request, file_id):
    pdf_file = get_object_or_404(Source_file, id=file_id)
    response = FileResponse(pdf_file.file.open(), content_type='application/pdf')
    response['Content-Disposition'] = 'inline'  # Ensure it opens in browser
    return response

def pdf_list(request):
    pdfs = Source_file.objects.all()
    return render(request, 'pdf_list.html', {'pdfs': pdfs})