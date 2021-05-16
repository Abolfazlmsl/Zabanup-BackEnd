from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'user'
router = DefaultRouter()
router.register('user-answer', views.UserAnswerViewSet),
router.register('ticket', views.TicketViewSet),
router.register('comment', views.CommentViewSet),

urlpatterns = [
    path('', include(router.urls)),
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path('verify-user/', views.UserPhoneRegisterAPIView.as_view(), name='verify-user'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change-password'),
    path('resend/', views.ResendSignUpTokenAPIView.as_view(), name='resend-token'),
    path('forget-password/', views.ForgetPasswordAPIView.as_view(), name='forget-password'),
    path('ticket-message/', views.TicketMessageAPIView.as_view(), name='ticket-message'),
]
