from datetime import timedelta
from django.utils import timezone

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Folder(models.Model):
    name = models.CharField(max_length=255)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='subfolders')
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='uploads/')  # Saves files in /media/uploads/
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, null=True, blank=True, related_name='files')

    def __str__(self):
        return self.name


class FileShare(models.Model):
    PERMISSION_CHOICES = [
        ('view', 'View Only'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]
    file = models.ForeignKey(File, on_delete=models.CASCADE, related_name='shared_with')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    permission = models.CharField(max_length=10, choices=PERMISSION_CHOICES)
    shared_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.permission} - {self.file.name}"
    



class ExpiringLink(models.Model):
    file = models.ForeignKey(File, on_delete=models.CASCADE)
    token = models.CharField(max_length=70, unique=True)
    expires_at = models.DateTimeField(default=timezone.now() + timedelta(hours=1))

    def __str__(self):
        return self.token


