from django.db import models

from django.contrib.auth.models import BaseUserManager, AbstractBaseUser


class MyUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, password2=None, is_active=True, is_admin=False):
        """
        Creates and saves a User with the given email, date of
        birth and password.
        """
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            name=name,
        )

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None):
        """
        Creates and saves a superuser with the given email, date of
        birth and password.
        """
        user = self.create_user(
            email,
            password=password,
            name=name,

        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class MyUser(AbstractBaseUser):
    email = models.EmailField(
        verbose_name="email address",
        max_length=255,
        unique=True,
    )

    name = models.CharField(max_length=100)
    is_admin = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = MyUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name",]

    def __str__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return self.is_admin

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_admin

class Preference(models.Model):
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE, related_name='preference')
    name = models.CharField(max_length=100)
    preferred_days = models.CharField(max_length=255, null=True, blank=True)  # Store preferred days as a comma-separated string
    preferred_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.email}'s preferences"

class ApplicationDevice(models.Model):
    name = models.CharField(max_length=255)
    api_key = models.CharField(max_length=255, blank=True, null=True)  # Optional for API integration
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)  # Link to user who owns it

    def __str__(self):
        return self.name

class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_time = models.TimeField(blank=True, null=True)
    due_at = models.DateTimeField(blank=True, null=True)
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

class Reminder(models.Model):
    message = models.CharField(max_length=255)
    trigger_at = models.DateTimeField()
    user = models.ForeignKey(MyUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.message

