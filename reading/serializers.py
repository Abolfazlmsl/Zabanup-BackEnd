from django.contrib.auth import get_user_model
from rest_framework import serializers
from core import models


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Book
        fields = '__all__'


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Answer
        fields = (
            'id',
            'text'
        )


class QuestionSerializer(serializers.ModelSerializer):
    answers = AnswerSerializer(many=True)

    class Meta:
        model = models.Question
        exclude = ['description']
        depth = 1


class ExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Exam
        fields = '__all__'
        depth = 1


class ReadingSerializer(serializers.ModelSerializer):
    book = serializers.CharField(max_length=255)

    class Meta:
        model = models.Reading
        fields = (
            'id',
            'title',
            'image',
            'passage_type',
            'subject',
            'book'
        )
        depth = 1


class QuestionDescriptionSerializer(serializers.ModelSerializer):
    questions = QuestionSerializer(many=True)

    class Meta:
        model = models.QuestionDescription
        exclude = ['passage']
        depth = 1


class ReadingWithQuestionsSerializer(serializers.ModelSerializer):
    question_description = QuestionDescriptionSerializer(many=True)

    class Meta:
        model = models.Reading
        fields = '__all__'
        depth = 1


class UserAnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = models.UserAnswer
        fields = '__all__'
        read_only_fields = (
            'id',
            'user',
            'grade',
            'created_on'
        )


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = models.Category
        fields = '__all__'


class ExamRetrieveSerializer(serializers.ModelSerializer):
    passages = ReadingWithQuestionsSerializer(many=True)

    class Meta:
        model = models.Exam
        fields = '__all__'
        depth = 1


class CommentChildrenSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        fields = '__all__'


class CommentSerializer(serializers.ModelSerializer):
    children = CommentChildrenSerializer(many=True, read_only=True)

    class Meta:
        model = models.Comment
        fields = '__all__'
        read_only_fields = (
            'id',
            'user',
            'created_on',
            'like',
            'children'
        )


