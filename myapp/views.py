# myapp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')

@login_required
def deepcut(request):
    return render(request, 'Deepcut/deepcut.html')

def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')
