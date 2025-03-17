from django.urls import path
from . import views
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path('index/', views.index, name='student_index'),
    path('index/<int:user_id>/', views.index, name='index'),
    path('signup/', views.std_signup, name='signup'),
    path('', views.std_login, name='login'),  # Default page is login
    path('profile_update/', views.std_update_profile, name='profile_update'),
    path('profile_update/<int:user_id>/', views.std_update_profile, name='profile_update'),

    path('logout/', views.user_logout, name='user_logout'),

    path('select_course/', views.select_course, name='select_course'),
    # path('start_exam/<int:course_id>/<int:num_questions>/', views.start_exam, name='start_exam'),
    path('start_exam/<int:course_id>/<int:num_questions>/', views.start_exam, name='start_exam'),

    path('available_courses/', views.available_courses, name='available_courses'),
    path('slt_start_exam/<int:course_id>/', views.slt_start_exam, name='slt_start_exam'),

    # path('compiler', views.compiler, name='compiler'),
    # path('execute/', views.execute_code, name='execute_code'),

    path('generate_report_card/', views.generate_report_card, name='generate_report_card'),

]
    

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)