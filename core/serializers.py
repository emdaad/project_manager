from rest_framework import serializers
from .models import Task, User, Project, Comment, membership, OTP
from django.contrib.auth import get_user_model, authenticate
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from django.core.exceptions import ValidationError as DjangoValidationError
from django.contrib.auth.password_validation import validate_password
from .utils import generate_otp

User = get_user_model()


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if not user:
            raise serializers.ValidationError("Invalid username or password.") 

        generate_otp(user)
        return {"user_id": user.id, "message":"OTP sent to your email"}


class VerifyOTPSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    code = serializers.CharField(max_length=6)

    def validate(self, data):
        try:
            otp = OTP.objects.filter(user_id=data['user_id'], code=data['code']).latest('created_at')
        except OTP.DoesNotExist:
            raise serializers.ValidationError("Invalid OTP")

        if not otp.is_valid():
            raise serializers.ValidationError("OTP expired")

        return data


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'password2', 'phone_number']

    def validate_password(self, value):
        """Run Django's password validators"""
        try:
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value

    def validate(self, attrs):
        """Ensure both passwords match"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            phone_number=validated_data.get('phone_number', '')
        )
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number']



class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)

    class Meta:
        model = Project
        fields = '__all__'


class TaskSerializer(TaggitSerializer,serializers.ModelSerializer):
    assignee = UserSerializer(read_only=True)
    tags = TagListSerializerField(required=False)

    class Meta:
        model = Task
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = '__all__'


class MembershipSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    project = serializers.PrimaryKeyRelatedField(queryset=Project.objects.all())

    class Meta:
        model = membership
        fields = '__all__'

    def create(self, validated_data):
        user = self.context['request'].user
        project = validated_data['project']

        membership_instance, created = membership.objects.get_or_create(
            user=user,
            project=project,
            defaults={'role': validated_data.get('role', 'member')}
        )
        return membership_instance
