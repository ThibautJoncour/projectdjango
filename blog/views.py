from django.shortcuts import render

# Create your views here.

def interface(request):
    return render(request, "blog/interface.html")
# views.py


def login_page(request):
    return render(request, "blog/login.html")



