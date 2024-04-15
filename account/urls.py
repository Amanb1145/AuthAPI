from django.urls import path, include
from . import views

from rest_framework import routers
from .views import (
    ApplicationDeviceViewSet, TaskViewSet, ReminderViewSet, UserPreferencesAPIView
)

router = routers.DefaultRouter()

# Application/Device Integration
router.register(r'applications', ApplicationDeviceViewSet, basename='applicationdevice')

# Recommendations - Not implemented in provided code
# router.register(r'recommendations', RecommendationViewSet, basename='recommendation')

# Tasks
router.register(r'tasks', TaskViewSet, basename='task')

# Reminders
router.register(r'reminders', ReminderViewSet, basename='reminder')

urlpatterns = [
    path('register/', views.UserRegistrationView.as_view()),
    path('login/', views.UserLoginView.as_view()),
    path('profile/', views.UserProfile.as_view()),
    path('changepass/', views.UserChangePassword.as_view()),
    path('send-email-rest-password/', views.SendPasswordResetEmail.as_view()),
    path('rest-password/<uid>/<token>/', views.UserPasswordReset.as_view()),
    path('api/', include(router.urls)),
    path('api/preferences/', UserPreferencesAPIView.as_view(), name='user-preferences'),

]
