from django.shortcuts import render
from django.http import FileResponse, Http404
import os
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import TokenError
from django.utils import timezone
from .forms import LoginForm
from .models import LoginRecord

# def user_login(request):
def user_login(request):
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


class LoginAPIView(APIView):
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        if not email or not password:
            return Response({'status' : False,'detail': 'Email and password are required.'}, status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=email, password=password)
        if user is None:
            return Response({'status' : False,'detail': 'Invalid credentials.'}, status=status.HTTP_401_UNAUTHORIZED)

        login(request, user)

        refresh = RefreshToken.for_user(user)

        try:
            LoginRecord.objects.create(
                user=user,
                ip_address=request.META.get('REMOTE_ADDR'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        except Exception:
            pass

        return Response({
            'status' : True,
            'access': str(refresh.access_token),
            'refresh': str(refresh),

            "user": {
                "id": user.id,
                "username" : user.username,
                "name": user.full_name,
                "email": user.email,
                "phone": user.mobile,
                "is_staff": user.is_staff,
            }
        }, status=status.HTTP_200_OK)


class LogoutAPIView(APIView):
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get('refresh') or request.COOKIES.get('refresh')

        # Try to blacklist a single provided refresh token first
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                logout(request)
                return Response({'status' : True,'detail': 'Logged out and refresh token blacklisted'}, status=status.HTTP_200_OK)
            except TokenError as te:
                # Token is invalid/expired
                logout(request)
                return Response({'status' : False,'detail': 'Logged out (invalid refresh token)', 'error': str(te)}, status=status.HTTP_200_OK)
            except Exception as e:
                logout(request)
                return Response({'status' : False,'detail': 'Logged out (error blacklisting refresh token)', 'error': str(e)}, status=status.HTTP_200_OK)

        # If no specific refresh provided, attempt to blacklist all outstanding tokens for the user
        try:
            from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken

            outstanding = OutstandingToken.objects.filter(user=request.user)
            blacklisted_count = 0
            for out in outstanding:
                try:
                    # Create BlacklistedToken for each OutstandingToken (idempotent via get_or_create)
                    BlacklistedToken.objects.get_or_create(token=out)
                    blacklisted_count += 1
                except Exception:
                    # ignore per-token errors
                    pass

            logout(request)
            return Response({'status' : True,'detail': 'Logged out', 'blacklisted': blacklisted_count}, status=status.HTTP_200_OK)

        except Exception as e:
            logout(request)
            return Response({'status' : False,'detail': 'Logged out (error during blacklisting)', 'error': str(e)}, status=status.HTTP_200_OK)