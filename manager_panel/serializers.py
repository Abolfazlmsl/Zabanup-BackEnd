from rest_framework import serializers
from django.contrib.auth import get_user_model
from core import models


class UserSerializer(serializers.ModelSerializer):
    """Serialize user model"""

    class Meta:
        model = get_user_model()
        fields = (
            'id',
            'name',
            'phone_number',
        )


class UserDetailSerializer(UserSerializer):
    """Serialize user detail model"""

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + (
            (
                'gender',
                'email',
                'is_verified',
            )
        )


class BookSerializer(serializers.ModelSerializer):
    """Serialize book model"""

    class Meta:
        model = models.Book
        fields = '__all__'
        read_only_fields = ('id', 'test_taken', 'created_on', 'rate')


class CategorySerializer(serializers.ModelSerializer):
    """Serialize exam model"""

    class Meta:
        model = models.Category
        fields = '__all__'
        read_only_fields = ('id',)


class ExamSerializer(serializers.ModelSerializer):
    """Serialize exam model"""

    class Meta:
        model = models.Exam
        fields = '__all__'
        read_only_fields = ('id',)


class ReadingSerializer(serializers.ModelSerializer):
    """Serialize reading model"""

    class Meta:
        model = models.Reading
        fields = '__all__'
        read_only_fields = ('id',)


class QuestionSerializer(serializers.ModelSerializer):
    """Serialize question model"""

    class Meta:
        model = models.Question
        fields = '__all__'
        read_only_fields = ('id',)


class AnswerSerializer(serializers.ModelSerializer):
    """Serialize answer model"""

    class Meta:
        model = models.Answer
        fields = '__all__'
        read_only_fields = ('id',)


class UserAnswerSerializer(serializers.ModelSerializer):
    """Serialize user answer model"""

    class Meta:
        model = models.UserAnswer
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    """Serialize comment model"""

    class Meta:
        model = models.Comment
        fields = '__all__'


class TickerMessageSerializer(serializers.ModelSerializer):
    """Serialize ticket message model"""

    class Meta:
        model = models.TicketMessage
        fields = '__all__'
        read_only_fields = ('id', 'sender')


class TicketSerializer(serializers.ModelSerializer):
    """Serialize ticket model"""
    staff = UserSerializer(many=False)
    student = UserSerializer(many=False)

    class Meta:
        model = models.Ticket
        fields = '__all__'


class TicketDetailSerializer(TicketSerializer):
    """Serialize detail ticket model"""
    message_set = TickerMessageSerializer(many=True)
