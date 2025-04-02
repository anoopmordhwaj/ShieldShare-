from django import forms
from .models import *

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['name', 'file']


class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = [ 'name', 'parent' ]


class MoveFileForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['folder']

class FileShareForm(forms.ModelForm):
    class Meta:
        model = FileShare
        fields = ['user', 'permission']