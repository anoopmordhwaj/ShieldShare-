

from django.contrib import admin
from django.urls import path, include
from files import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('upload/', views.upload_file, name='upload_file'),
    path('', views.dashboard, name='dashboard'),

    path('Login/', views.Login, name='Login'),
    path('Signup/', views.Signup, name='Signup'),
    path('Logout/', views.Logout, name='Logout'),

    path('create_folder/', views.create_folder, name='create_folder'),
    path('folder/<int:folder_id>/', views.view_folder, name='view_folder'),
    path('rename_file/<int:file_id>/', views.rename_file, name='rename_file'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('share_file/<int:file_id>/', views.share_file, name='share_file'),
    path('download_link/<str:token>/', views.download_link, name='download_link'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
