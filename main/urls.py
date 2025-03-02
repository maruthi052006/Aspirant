from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-logout/', views.admin_logout, name='admin_logout'),
    path('upload-pdf/', views.upload_pdf, name='upload_pdf'),
    path('view-pdfs/', views.view_pdfs, name='view_pdfs'),
    path('view_pdf/<int:file_id>/', view_pdf, name='view_pdf'),

    path('pdfs/', views.pdf_list, name='pdf_list'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

