from django.contrib.auth import get_user_model
from rest_framework import generics, viewsets, mixins
from rest_framework.pagination import PageNumberPagination
from rest_framework_simplejwt.authentication import JWTAuthentication

from core import models
from manager_panel import serializers, permissions


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ManagerInfoView(generics.RetrieveUpdateAPIView):
    """Show detailed of manager user"""
    serializer_class = serializers.UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    queryset = get_user_model().objects.all()

    def get_object(self):
        """Retrieve anr return authenticated user"""
        return self.request.user


class ManagerUserViewSet(viewsets.GenericViewSet,
                         mixins.ListModelMixin,
                         mixins.RetrieveModelMixin):
    """user for manager"""

    serializer_class = serializers.UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = get_user_model().objects.all()

    def get_queryset(self):
        """Filter user that doesn't show admin or staff"""
        return self.queryset.filter(
            is_superuser=False, is_staff=False
        ).exclude(groups__name='Manager')

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        else:
            return serializers.UserDetailSerializer


class ManagerBookViewSet(viewsets.ModelViewSet):
    """Manage books in database"""

    serializer_class = serializers.BookSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Book.objects.all()


class ManagerCategoryViewSet(viewsets.ModelViewSet):
    """Manage exams in database"""

    serializer_class = serializers.CategorySerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Category.objects.all()


class ManagerExamViewSet(viewsets.ModelViewSet):
    """Manage exams in database"""

    serializer_class = serializers.ExamSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Exam.objects.all()


class ManagerReadingViewSet(viewsets.ModelViewSet):
    """Manage reading in database"""

    serializer_class = serializers.ReadingSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Reading.objects.all()


class ManagerQuestionViewSet(viewsets.ModelViewSet):
    """Manage question in database"""

    serializer_class = serializers.QuestionSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Question.objects.all()


class ManagerAnswerViewSet(viewsets.ModelViewSet):
    """Manage question in database"""

    serializer_class = serializers.AnswerSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Answer.objects.all()


class ManagerUserAnswerViewSet(viewsets.GenericViewSet,
                               mixins.ListModelMixin,
                               mixins.RetrieveModelMixin):
    """Manage user answer in database"""

    serializer_class = serializers.UserAnswerSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.UserAnswer.objects.all()


class ManagerCommentViewSet(viewsets.GenericViewSet,
                            mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            mixins.DestroyModelMixin):
    """Manage comment in database"""

    serializer_class = serializers.CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Comment.objects.all()


class ManagerTicketViewSet(viewsets.GenericViewSet,
                           mixins.ListModelMixin,
                           mixins.RetrieveModelMixin):
    """Manage ticket in database"""

    serializer_class = serializers.TicketSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (permissions.IsManager,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Ticket.objects.all()

    def get_queryset(self):
        return self.queryset.filter(staff=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        else:
            return serializers.TicketDetailSerializer


class ManagerTicketMessageAPIView(generics.CreateAPIView):
    """Manage ticket message in database"""

    serializer_class = serializers.TickerMessageSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (
        permissions.IsManager,
        permissions.IsTicketMessageOwner
    )
    pagination_class = StandardResultsSetPagination
    queryset = models.TicketMessage.objects.all()

    def perform_create(self, serializer):
        """Save authenticated user"""
        serializer.save(sender=self.request.user)
