from django.shortcuts import render

# Create your views here.
def page(request):
    return render(request, 'home.html')

def log(request):
    return render(request, 'login.html')

def registration(request):
    return render(request, 'register.html')