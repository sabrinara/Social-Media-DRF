from django.http import HttpResponse
from django.shortcuts import render
from rest_framework import viewsets, status, generics
from rest_framework.views import APIView
from . import serializers
from . import models
from rest_framework.response import Response
from rest_framework.authtoken.models import Token

from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.shortcuts import redirect

# for generating token
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str

# for sending email
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib import messages

from rest_framework.permissions import IsAuthenticated

from rest_framework.decorators import api_view, permission_classes
from django.contrib.sites.shortcuts import get_current_site

from rest_framework.permissions import AllowAny
from rest_framework.authentication import TokenAuthentication


from django.middleware.csrf import get_token
from django.contrib.sessions.models import Session

from django.conf import settings

from rest_framework.authentication import SessionAuthentication, BasicAuthentication

class UserDetailView(APIView):
    # authentication_classes = [BasicAuthentication]
    # authentication_classes = [SessionAuthentication, BasicAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        user_details = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birth_date': user.AbstractUserDetails.birth_date if hasattr(user, 'AbstractUserDetails') else None,
            'gender': user.AbstractUserDetails.gender if hasattr(user, 'AbstractUserDetails') else None,
            'division': user.AbstractUserDetails.division if hasattr(user, 'AbstractUserDetails') else None,
            'district': user.AbstractUserDetails.district if hasattr(user, 'AbstractUserDetails') else None,
            'phone': user.AbstractUserDetails.phone if hasattr(user, 'AbstractUserDetails') else None,
            'profile_pic': str(user.AbstractUserDetails.profile_pic) if hasattr(user, 'AbstractUserDetails') and user.AbstractUserDetails.profile_pic else None,
        }

        # Get CSRF token
        csrf_token = get_token(request)
        # Get session ID
        session_id = request.session.session_key
        # print('csrf_token', csrf_token)
        # print("session_id", session_id)
        
        return Response(user_details, status=status.HTTP_200_OK)

# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def user_detail(request):
#     user = request.user
#     user_details = {
#         'email': user.email,
#         'first_name': user.first_name,
#         'last_name': user.last_name,
#         'birth_date': user.AbstractUserDetails.birth_date if hasattr(user, 'AbstractUserDetails') else None,
#         'gender': user.AbstractUserDetails.gender if hasattr(user, 'AbstractUserDetails') else None,
#         'division': user.AbstractUserDetails.division if hasattr(user, 'AbstractUserDetails') else None,
#         'district': user.AbstractUserDetails.district if hasattr(user, 'AbstractUserDetails') else None,
#         'phone': user.AbstractUserDetails.phone if hasattr(user, 'AbstractUserDetails') else None,
#         'profile_pic': str(user.AbstractUserDetails.profile_pic) if hasattr(user, 'AbstractUserDetails') and user.AbstractUserDetails.profile_pic else None,
#     }
#     return Response(user_details)

class UserDetailViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        user = self.request.user
        user_details = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'birth_date': user.AbstractUserDetails.birth_date if hasattr(user, 'AbstractUserDetails') else None,
            'gender': user.AbstractUserDetails.gender if hasattr(user, 'AbstractUserDetails') else None,
            'division': user.AbstractUserDetails.division if hasattr(user, 'AbstractUserDetails') else None,
            'district': user.AbstractUserDetails.district if hasattr(user, 'AbstractUserDetails') else None,
            'phone': user.AbstractUserDetails.phone if hasattr(user, 'AbstractUserDetails') else None,
            'profile_pic': str(user.AbstractUserDetails.profile_pic) if hasattr(user, 'AbstractUserDetails') and user.AbstractUserDetails.profile_pic else None,
        }
        return Response(user_details)

class UserRegistration(APIView):
    serializer_class = serializers.RegistrationSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Generate activation link with the correct domain
            current_site = get_current_site(request)

            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            # confirm_link = f'http://127.0.0.1:8000/accounts/activate/{uid}/{token}/'
            confirm_link = f'http://{current_site.domain}/accounts/activate/{uid}/{token}/'

            email_subject = 'Confirm your email'
            email_body = render_to_string(
                'accounts/email_templates/email_confirmation.html', {'confirm_link': confirm_link})
            email = EmailMultiAlternatives(
                email_subject, '', to=[user.email]
            )
            email.attach_alternative(email_body, 'text/html')
            email.send()

            return Response('Check your email for activation link')
        return Response(serializer.errors)


def activate(request, uid64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uid64))
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(
            request, "Your account has been activated. You can now log in.")
        # return redirect('login')
        # Redirect to the frontend login page
        return redirect('http://localhost:5173/login')
    else:
        messages.error(request, "Invalid activation link.")
        return redirect('register')



class UserLoginApiView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = serializers.UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        # print(f"Email: {email}, Password: {password}")

        user = User.objects.filter(email=email).first()
        # print(f"User: {user}")
        
        if user and user.check_password(password):
            token, _ = Token.objects.get_or_create(user=user)
            login(request, user)
            # print(f"Token: {token}")
            # print(f"Token key: {token.key}")
            # print('Login successful')
            # print(f"User: {user}")

            # Get CSRF token
            csrf_token = get_token(request)
            # Get session ID
            session_id = request.session.session_key
            # print('csrf_token', csrf_token)
            # print("session_id", session_id)

            return Response({'token': token.key, 'email': user.email, 'user_id': user.id, 'csrf_token': csrf_token, 'session_id': session_id}, status=status.HTTP_200_OK)
        else:
            return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class UserLogoutView(APIView):
    def get(self, request, *args, **kwargs):
        if request.auth:  # Check if authentication token exists
            request.auth.delete()  # Delete the authentication token
        logout(request)

        # return Response({'detail': 'Logout successful'}, status=status.HTTP_200_OK)

        # Delete CSRF token
        csrf_token = get_token(request)
        response = Response({'detail': 'Logout successful'},
                            status=status.HTTP_200_OK)
        response.delete_cookie(settings.CSRF_COOKIE_NAME)

        # Clear session
        request.session.clear()

        return response

# class UpdateUserView(generics.UpdateAPIView):
#     serializer_class = serializers.UpdateUserSerializer
#     permission_classes = [IsAuthenticated]

#     def get_object(self):
#         # print(self.request.user)
#         # return self.request.user.AbstractUserDetails

#         user = self.request.user

#         # Check if UserDetails exists for the user, create if not
#         if not hasattr(user, 'AbstractUserDetails'):
#             models.UserDetails.objects.create(user=user)

#         return user.AbstractUserDetails


class UpdateUserView(generics.RetrieveUpdateAPIView):
    serializer_class = serializers.UpdateUserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        user = self.request.user

        # Check if UserDetails exists for the user, create if not
        if not hasattr(user, 'AbstractUserDetails'):
            models.UserDetails.objects.create(user=user)

        return user.AbstractUserDetails

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)

        # Retrieve updated object data
        updated_instance = self.get_object()
        updated_serializer = self.get_serializer(updated_instance)
        print('updated_serializer', updated_serializer)

        return Response(updated_serializer.data, status=status.HTTP_200_OK)
