from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import get_object_or_404
from .forms import FileUploadForm, FolderForm, FileShareForm
from .models import *
from django.http import FileResponse
from django.utils.timezone import now



# Create your views here.

def upload_file(request):
    
    if request.method == 'POST':
        form = FileUploadForm(request.POST, request.FILES)
        
        if form.is_valid():
            form_instance = form.save(commit=False)
            form_instance.uploaded_by = request.user
            form_instance.save()
            return redirect('dashboard')

    else:
        form = FileUploadForm() 
   
    return render(request, 'upload.html', {'form': form})

def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.owner = request.user
            folder.save()
            return redirect('dashboard')
    else:
        form = FolderForm()
    
    return render(request, 'folder.html', {"form": form})

def dashboard(request):
    folders = Folder.objects.filter(owner = request.user, parent = None)
    files = File.objects.filter(uploaded_by = request.user, folder = None)
    shared_files = File.objects.filter(shared_with__user = request.user)

    return render(request, 'dashboard.html', {"folders": folders,"files": files , "shared_files": shared_files})


def view_folder(request, folder_id):
    folder = Folder.objects.get(id=folder_id, owner=request.user)
    subfolders = folder.subfolders.all()  # Fetch subfolders
    files = folder.files.all()  # Fetch files in this folder
    return render(request, 'folder_view.html', {'folder': folder, 'subfolders': subfolders, 'files': files})

    

def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)

    # Check permission
    if file.uploaded_by != request.user:
        file_share = FileShare.objects.filter(file=file, user=request.user, permission='delete').exists()
        if not file_share:
            return redirect('dashboard')  # No permission
        
    file.delete()
    return redirect('dashboard')


def rename_file(request, file_id):
    file = get_object_or_404(File, id = file_id)

    # Check permission
    if file.uploaded_by != request.user:
        file_share = FileShare.objects.filter(file=file, user=request.user, permission='edit').exists()
        if not file_share:
            return redirect('dashboard')


    if request.method == 'POST':
        file.name = request.POST['new_name']
        file.save()
        return redirect('dashboard')
    return render(request, 'rename.html', {'file': file})


def share_file(request, file_id):
    expiring_link = None
    file = get_object_or_404(File,id = file_id ,uploaded_by = request.user)

    if request.method == 'POST':
        form = FileShareForm(request.POST)
        if form.is_valid():
            file_share  = form.save(commit=False)
            file_share.file = file
            file_share.save()
            

            expiring_link = generate_expiring_link(file)

            return render(request, 'share_success.html', {'expiring_link': expiring_link})
    else:
        form = FileShareForm()
    return render(request, 'share_file.html', {"form": form, "file": file})



def download_link(request, token):
    link = get_object_or_404(ExpiringLink, token = token)

    if link.expires_at < now():
        return HttpResponse("The link has expired.")
    
    return FileResponse(link.file.file, as_attachment=True)


import uuid
from django.utils.timezone import now
import random
import string

def generate_expiring_link(file):
    """Generates an expiring link for a file."""

    # token = 123456789023
    token = ''.join(random.choice(string.ascii_letters) for i in range(6))

    link = ExpiringLink.objects.create(file=file, token=token)
    link.save()
    
    
    return token