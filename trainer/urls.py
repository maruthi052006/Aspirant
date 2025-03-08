from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *

urlpatterns = [
    path('trainer-signup/', views.trainer_signup, name='trainer_signup'),
    path('', views.trainer_login, name='trainer_login'),
    path('trainer-dashboard/', views.trainer_dashboard, name='trainer_dashboard'),
    path('pdf/<int:pdf_id>/', view_pdf, name='view_pdf'),
    path('logout/', views.user_logout, name='user_logout'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


