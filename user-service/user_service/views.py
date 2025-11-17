from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from Core.authentication import GatewayHeaderAuthentication
from Core.messaging import publisher

from .serializers import (
    UserSerializer, 
    RegisterSerializer,
    LoginSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer
)

User = get_user_model()
token_generator = PasswordResetTokenGenerator()


#  Register 
class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user.is_active:
            publisher.publish_user_created(
                user_uuid=str(user.id),
                email=user.email,
                is_active=user.is_active
            )
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data
        }, status=status.HTTP_201_CREATED)


#  Login 

class LoginView(APIView):
    serializer_class = LoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        return Response({
            "uuid": str(user.id),
            "email": user.email
        }, status=status.HTTP_200_OK)



#  Logout 
class LogoutView(APIView):

    def post(self, request):
        # JWT blacklisting artıq servisdə yoxdursa, sadəcə cavab qaytara bilərsən
        return Response({"detail": "Logged out successfully"}, status=status.HTTP_205_RESET_CONTENT)


# User Profile
class UserProfileView(APIView):
    authentication_classes = [GatewayHeaderAuthentication]
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    def put(self, request): 
        serializer = UserSerializer(request.user, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)

    def patch(self, request):
        serializer = UserSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=400)


# Password Reset Request
class PasswordResetRequestView(APIView):

    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({"detail": "Bərpa linki göndərildi."})

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        frontend_base = getattr(settings, "FRONTEND_PASSWORD_RESET_URL", "http://127.0.0.1:3000/reset-password")
        reset_link = f"{frontend_base}?uid={uid}&token={token}"

        subject = "Şifrənin bərpası üçün keçid"
        message = f"""
Salam {user.first_name or 'istifadəçi'},

Şifrənizi sıfırlamaq üçün bu linkə klikləyin:
👉 {reset_link}

Hörmətlə,
Maestro komandası
        """

        from_email = settings.DEFAULT_FROM_EMAIL
        send_mail(subject, message.strip(), from_email, [user.email], fail_silently=False)

        return Response({"detail": "Əgər bu e-mail ilə hesab varsa, bərpa linki göndərildi."}, status=status.HTTP_200_OK)


# Password Reset Confirm
class PasswordResetConfirmView(APIView):

    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data['user']
        new_password = serializer.validated_data['new_password']
        user.set_password(new_password)
        user.save()

        return Response({"detail": "Şifrəniz uğurla yeniləndi."}, status=status.HTTP_200_OK)
