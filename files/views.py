from django.shortcuts import render, redirect, HttpResponse
from django.shortcuts import get_object_or_404
from .forms import FileUploadForm, FolderForm, FileShareForm
from .models import *
from django.http import FileResponse
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from .models import User
from django.contrib.auth import authenticate, logout, login




# Create your views here.

def Logout(request):
    logout(request)
    return redirect('Login')
    
def Login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not User.objects.filter(username = username).exists():
            return HttpResponse("<script>alert('Invalid Username! Enter correct username.'); window.location='/Login/';</script>")
        
        user = authenticate(username = username, password = password)

        if user is None:
            return HttpResponse("<script>alert('Invalid Credentials! Enter correct password.'); window.location='/Login/';</script>")

        else:
            login(request, user)
            return HttpResponse("<script>alert('Login successfully!.'); window.location='/';</script>")

    return render(request, 'login.html')


def Signup(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        user = User.objects.filter(username__icontains = username)

        if user.exists():
            return HttpResponse("<script>alert('This Username is already registered with other user. Try different username.'); window.location='/Signup/';</script>")
        
        user = User.objects.create(email = email,username = username)

        if password == confirm_password:
            user.set_password(password)
            user.save()
            return HttpResponse("<script>alert('User created seccusfully.'); window.location='/';</script>")
        else:
            return HttpResponse("<script>alert('Entered Wrong Password! Re-confirm your password.'); window.location='/Signup/';</script>")

    return render(request, 'signup.html')



@login_required(login_url='/Login/')
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

@login_required(login_url='/Login/')
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

@login_required(login_url='/Login/')
def dashboard(request):
    folders = Folder.objects.filter(owner = request.user, parent = None)
    files = File.objects.filter(uploaded_by = request.user, folder = None)
    shared_files = File.objects.filter(shared_with__user = request.user)

    return render(request, 'dashboard.html', {"folders": folders,"files": files , "shared_files": shared_files})

@login_required(login_url='/Login/')
def view_folder(request, folder_id):
    folder = Folder.objects.get(id=folder_id, owner=request.user)
    subfolders = folder.subfolders.all()  # Fetch subfolders
    files = folder.files.all()  # Fetch files in this folder
    return render(request, 'folder_view.html', {'folder': folder, 'subfolders': subfolders, 'files': files})

    
@login_required(login_url='/Login/')
def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id)

    # Check permission
    if file.uploaded_by != request.user:
        file_share = FileShare.objects.filter(file=file, user=request.user, permission='delete').exists()
        if not file_share:
            return redirect('dashboard')  # No permission
        
    file.delete()
    return redirect('dashboard')

@login_required(login_url='/Login/')
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


@login_required(login_url='/Login/')
def share_file(request, file_id):
    expiring_link = None
    
    file = get_object_or_404(File,id = file_id ,uploaded_by = request.user)
    print(file)

    if request.method == 'POST':
        form = FileShareForm(request.POST)
        if form.is_valid():
            file_share  = form.save(commit=False)
            file_share.file = file
            file_share.save()
            

            expiring_link = generate_expiring_link(file)

            return render(request, 'share_success.html', {'expiring_link': expiring_link, 'file': file})
    else:
        form = FileShareForm()
    return render(request, 'share_file.html', {"form": form, "file": file})


@login_required(login_url='/Login/')
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

    token = uuid.uuid4().hex[:8] 

    link = ExpiringLink.objects.create(file=file, token=token)
    link.save()
    
    return token