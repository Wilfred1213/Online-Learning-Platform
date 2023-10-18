from django.shortcuts import render, redirect
from authentications.forms import *

from django.contrib import messages
from django.contrib.auth.models import auth
from django.contrib.auth import authenticate, login,logout
from learningApp.models import Instructor, upcomingEvent

# Create your views here.
def register_user(request):
    instructors = Instructor.objects.all().order_by('-post_date')[:4]
    events = upcomingEvent.objects.all()[:3]
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, request.FILES)
        if form.is_valid():   
            form.save() 
            return redirect('authentications:loggin')
    else:
        form = UserRegistrationForm()
    return render(request, 'authentications/signup.html', {'form': form, 'events':events, 'instructors':instructors})


def loggin(request):
    events = upcomingEvent.objects.all()[:3]
    instructors = Instructor.objects.all().order_by('-post_date')[:4]
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None and user.is_student:
                login(request, user)
                messages.info(request, 'Login successful')
                return redirect('index')
            elif user is not None and user.is_instructor:
                login(request, user)
                messages.info(request, 'Login successful')
                return redirect('index')
            
            messages.info(request, 'Invalid data')
            return redirect('authentications:loggin')
    else:
        form = LoginForm(request)
    return render(request, 'authentications/signin.html', {'form': form, 'events':events, 'instructors':instructors})

def logout(request):
    auth.logout(request)
    messages.success(request, 'You logout! Loging again?')
    return redirect('authentications:loggin')