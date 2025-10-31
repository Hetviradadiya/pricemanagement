from django.shortcuts import render
from django.http import FileResponse, Http404
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .forms import LoginForm
from .models import LoginRecord

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user is not None:
                login(request, user)

                # store login details
                LoginRecord.objects.create(
                    user=user,
                    ip_address=request.META.get('REMOTE_ADDR'),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )

                return redirect('product')
            else:
                return render(request, 'login.html', {
                    'form': form,
                    'error': 'Invalid email or password'
                })
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


def user_logout(request):
    logout(request)
    return redirect('login')

@login_required(login_url='login')
def price_dashboard(request):
    return render(request, 'products.html')

def cors_media_serve(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(file_path):
        raise Http404("File not found")

    response = FileResponse(open(file_path, 'rb'))
    # response["Access-Control-Allow-Origin"] = "https://radhe.co.in"
    response["Access-Control-Allow-Credentials"] = "true"
    return response


def csrf_failure(request, reason=""):
    return render(request, "403_csrf.html", status=403)