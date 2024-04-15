from rest_framework import serializers
from .models import MyUser, ApplicationDevice, Task, Reminder, Preference
from django.core.exceptions import ValidationError
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from .utils import Util



class UserRegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(style={'input_type':'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = '__all__'
        extra_kwargs={
            'password':{'write_only':True}
        }

    def validate(self, data):
        password = data.get('password')
        password2 = data.get('password2')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        return data
    
    def create(self, validate_data):
        return MyUser.objects.create_user(**validate_data)
    

class UserLoginSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = MyUser
        fields = ['email', 'password']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'name']

class UserChangePasswordSerializer(serializers.ModelSerializer):
    password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        model = MyUser
        fields = ['password', 'password2']

    def validate(self, attrs):
        password = attrs.get('password')
        password2 = attrs.get('password2')
        user = self.context.get('user')
        if password != password2:
            raise serializers.ValidationError("Password doesn't match")
        user.set_password(password)
        user.save()
        return attrs


class SendPasswordResetEmailSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = MyUser
        fields = ['email']

    def validate(self, attrs):
        email = attrs.get('email')
        if MyUser.objects.filter(email=email).exists():
            user = MyUser.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            link = 'http://localhost:3000/api/user/reset/'+uid+'/'+token
            # send email
            body = 'Click Following Link to Reset Your Password '+ link
            data = {
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise ValidationError("You are not Registered User")


class UserPasswordResetSerializer(serializers.ModelSerializer):
    try:
        password = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
        password2 = serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
        class Meta:
            model = MyUser
            fields = ['password', 'password2']

        def validate(self, attrs):
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')

            if password != password2:
                raise serializers.ValidationError("Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = MyUser.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise ValidationError("Token is not valid or expired")
            
            user.set_password(password)
            user.save()
            return attrs 
    except DjangoUnicodeDecodeError:
        PasswordResetTokenGenerator().check_token(user, token)
        raise ValidationError('Token is not valid or expired')

class MyUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = MyUser
        fields = ['id', 'email', 'name', 'is_active',]

class ApplicationDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicationDevice
        fields = ('id', 'name', 'api_key', 'user')  # Adjust fields as needed

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'created_at', 'due_at', 'user')

class ReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Reminder
        fields = ('id', 'message', 'trigger_at', 'user')

class PreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Preference
        fields = ['name', 'preferred_days', 'preferred_time']