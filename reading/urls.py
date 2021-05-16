from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views

app_name = 'reading'

router = DefaultRouter()
router.register('book', views.BookViewSet)
# router.register('exam-category', views.ManagerExamCategoryViewSet)
router.register('exam', views.ExamViewSet)
router.register('reading', views.ReadingViewSet)
router.register('comment', views.CommentViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('category/', views.CategoryListAPIView.as_view()),
    path('exam-result/', views.UserAnswerAPIView.as_view()),
]
