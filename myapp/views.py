# myapp/views.py
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def post_wrap(request):
    return render(request, 'myapp/post_wrap.html')

def view_wraps(request):
    return render(request, 'myapp/view_wraps.html')
