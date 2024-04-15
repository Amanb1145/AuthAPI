from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from .serializers import (UserRegistrationSerializer, UserLoginSerializer,
                           UserProfileSerializer, UserChangePasswordSerializer,
                           SendPasswordResetEmailSerializer, UserPasswordResetSerializer, PreferenceSerializer)
from rest_framework import viewsets, permissions
from .models import ApplicationDevice, Task, Reminder, Preference
from .serializers import ApplicationDeviceSerializer, TaskSerializer, ReminderSerializer
from django.contrib.auth import authenticate
from .rendersers import UserRenderers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated



def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

class UserRegistrationView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        token = get_tokens_for_user(user)
        return Response({'token':token,'msg':'Registration Success.'}, status=status.HTTP_201_CREATED)
    

class UserLoginView(APIView):
    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.data.get('email')
        password = serializer.data.get('password')
        user = authenticate(email=email, password=password)
        print(user)
        if user is not None:
            token = get_tokens_for_user(user)
            return Response({'token':token,'msg':'Login successfully'}, status=status.HTTP_200_OK)
        else:
            return Response({'errors':{'non_field_errors':['Email or Password is not Valid']}}, status=status.HTTP_404_NOT_FOUND)

class UserProfile(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)


class UserChangePassword(APIView):
    renderer_classes = [UserRenderers]
    permission_classes = [IsAuthenticated]

    def post(self, request, format=None):
        serializer = UserChangePasswordSerializer(data = request.data, context={'user':request.user})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Changed.'}, status=status.HTTP_200_OK)
    
class SendPasswordResetEmail(APIView):

    renderer_classes = [UserRenderers]

    def post(self, request, format=None):
        serializer = SendPasswordResetEmailSerializer(data= request.data)
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Sending Password Reset Email.'}, status=status.HTTP_200_OK)
    

class UserPasswordReset(APIView):
    renderer_classes = [UserRenderers]
    def post(self, request, uid, token, format=None):
        serializer = UserPasswordResetSerializer(data=request.data, context={'uid':uid, 'token':token})
        serializer.is_valid(raise_exception=True)
        return Response({'msg':'Password Reset Done.'}, status=status.HTTP_200_OK)

class ApplicationDeviceViewSet(viewsets.ModelViewSet):
    queryset = ApplicationDevice.objects.all()
    serializer_class = ApplicationDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return ApplicationDevice.objects.filter(user=self.request.user)

class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

class ReminderViewSet(viewsets.ModelViewSet):
    queryset = Reminder.objects.all()
    serializer_class = ReminderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Reminder.objects.filter(user=self.request.user)

class UserPreferencesAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        preferences = Preference.objects.filter(user=user).all()
        serializer = PreferenceSerializer(preferences, many=True)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = PreferenceSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=user)
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)