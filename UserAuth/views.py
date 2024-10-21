from django.shortcuts import render, redirect

def home(request):
    return render(request,'UserAuth/index.html')

def login(request):
    return render(request, 'UserAuth/login.html')
