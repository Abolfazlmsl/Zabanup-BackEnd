from ckeditor.fields import RichTextField
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.db import models


person_id_checker = RegexValidator(
    regex=r'^[0-9]*$',
    message="یک کد ملی معتبر وارد کنید."
)

credit_cart_checker = RegexValidator(
    regex=r'^[0-9]*$',
    message="یک شماره کارت معتبر وارد کنید."
)

postal_code_checker = RegexValidator(
    regex=r'^[0-9]*$',
    message="یک کدپستی معتبر وارد کنید."
)


def validate_phone_number(value):
    if value and is_number(value) and\
            is_valid_phone_number(value) and\
            len(value) == 11:
        return value
    else:
        raise ValidationError("یک شماره تلفن معتبر وارد کنید.")


def is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def is_valid_phone_number(number):
    if number[0] == '0' and number[1] == '9':
        return True
    else:
        return False


def reading_counter(exam):
    if Reading.objects.filter(exam_id=exam).count() >= 3:
        raise ValidationError('شما نمی توانید بیش از 3 متن ریدینگ در یک آزمون ذخیره نمایید.')


class UserManager(BaseUserManager):

    def create_user(self, phone_number, password, email=None,
                    **extra_fields):
        """Create and save a new user"""
        if phone_number and \
                is_number(phone_number) and \
                is_valid_phone_number(phone_number) and \
                len(phone_number) == 11:
            pass
        else:
            raise ValueError('Phone number is invalid!')
        if email:
            email = self.normalize_email(email)
        user = self.model(
            phone_number=phone_number,
            email=email,
            **extra_fields
        )
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, phone_number, password):
        """create and save new super user"""
        user = self.create_user(phone_number, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)

        return user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user model that support email instead of username"""
    GENDER = [
        ('male', 'Male'),
        ('female', 'Female'),
    ]
    phone_number = models.CharField(
        validators=[validate_phone_number],
        max_length=11,
        unique=True,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField(
        max_length=255,
        unique=True,
        blank=True,
        null=True,
    )
    generated_token = models.IntegerField(
        blank=True,
        null=True,
    )
    picture = models.ImageField(
        upload_to='uploads/profile/',
        null=True,
        blank=True
    )
    gender = models.CharField(max_length=128, choices=GENDER)
    favorite_question = models.ManyToManyField('Question', blank=True, null=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'phone_number'


class Book(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_on = models.DateField(auto_now_add=True)
    image = models.ImageField(upload_to='uploads/book/', null=True, blank=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    CHOICES = (
        ('difficulty', 'Difficulty'),
        ('type', 'Type'),
        ('question', 'Question'),
        ('subject', 'Subject'),
    )
    name = models.CharField(max_length=255)
    sub_name = models.CharField(max_length=255, null=True, blank=True)
    type = models.CharField(max_length=255, choices=CHOICES)

    class Meta:
        unique_together = ('name', 'sub_name',)

    def __str__(self):
        return f'{self.name}, {self.type}, {self.id}'


class Exam(models.Model):
    # exam_code = models.CharField(max_length=64)
    title = models. CharField(max_length=255, blank=True, null=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    difficulty = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    rate = models.CharField(max_length=1, blank=True, null=True)
    test_taken = models.IntegerField(default=0)

    @property
    def passages(self):
        return self.reading_set.all()

    def __str__(self):
        return f'{self.id}, {self.book}, {self.difficulty}'


class Reading(models.Model):
    title = models.CharField(max_length=255, unique=True)
    text = RichTextField()
    image = models.ImageField(upload_to='uploads/reading/', null=True, blank=True)
    exam = models.ForeignKey(Exam, on_delete=models.SET_NULL, null=True, blank=True, validators=(reading_counter,))
    priority = models.PositiveIntegerField(null=True, blank=True)
    subject = models.ManyToManyField(Category, related_name='subject')
    passage_type = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='passage_type')

    def __str__(self):
        return self.title

    @property
    def question_description(self):
        return self.questiondescription_set.all()

    @property
    def book(self):
        if self.exam:
            return self.exam.book
        return None


class QuestionDescription(models.Model):
    text = RichTextField(null=False, blank=False)
    number_of_choices = models.PositiveIntegerField(null=True, blank=True)
    priority = models.PositiveIntegerField(null=True, blank=True)
    passage = models.ForeignKey(Reading, on_delete=models.CASCADE)
    type = models.ForeignKey(Category, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.passage}, {self.type}'

    @property
    def questions(self):
        return self.question_set.all()


class Question(models.Model):
    description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
    text = RichTextField()
    priority = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.text}, {self.description.passage.title}, {self.id}'

    @property
    def answers(self):
        return self.answer_set.all()


# class CompletionQuestion(models.Model):
#     CHOICES = (
#         ('summary', 'Summary Completion'),
#         ('sentence', 'Sentence Completion'),
#     )
#     description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
#     text = RichTextField()
#     type = models.CharField(max_length=127, choices=CHOICES)
#     priority = models.PositiveIntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.text}, {self.description.passage.title}, {self.id}'
#
#
# class MapQuestion(models.Model):
#     description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
#     text = RichTextField()
#     priority = models.PositiveIntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.text}, {self.description.passage.title}, {self.id}'
#
#
# class MultipleQuestion(models.Model):
#     description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
#     text = RichTextField()
#     priority = models.PositiveIntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.text}, {self.description.passage.title}, {self.id}'
#
#
# class ShortQuestion(models.Model):
#     description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
#     text = RichTextField()
#     priority = models.PositiveIntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.text}, {self.description.passage.title}, {self.id}'
#
#
# class TrueFalseQuestion(models.Model):
#     CHOICES = (
#         ('true-false', 'True False'),
#         ('yes-no', 'Yes No'),
#     )
#     description = models.ForeignKey(QuestionDescription, on_delete=models.CASCADE)
#     text = RichTextField()
#     type = models.CharField(max_length=127, choices=CHOICES)
#     priority = models.PositiveIntegerField(null=True, blank=True)
#
#     def __str__(self):
#         return f'{self.text}, {self.description.passage.title}, {self.id}'


class Answer(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, null=True, blank=True)
    # completion_question = models.ForeignKey(CompletionQuestion, on_delete=models.CASCADE, null=True, blank=True)
    # map_question = models.ForeignKey(MapQuestion, on_delete=models.CASCADE, null=True, blank=True)
    # multiple_question = models.ForeignKey(MultipleQuestion, on_delete=models.CASCADE, null=True, blank=True)
    # short_question = models.ForeignKey(ShortQuestion, on_delete=models.CASCADE, null=True, blank=True)
    # true_false_question = models.ForeignKey(TrueFalseQuestion, on_delete=models.CASCADE, null=True, blank=True)
    text = models.CharField(max_length=255)
    truth = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.id}, {self.question.text}, {self.text}'


class UserAnswer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    answer = models.TextField()
    grade = models.FloatField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user}, {self.exam}, {self.grade}, {self.created_on}'


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    text = models.TextField()
    like = models.PositiveIntegerField(default=0)
    created_on = models.DateTimeField(auto_now_add=True)

    @property
    def children(self):
        return self.comment_set.all().order_by('-created_on')

    def __str__(self):
        return f'{self.id}, {self.user}, {self.text}, {self.parent_id}'


class Ticket(models.Model):
    CHOICES = [
        ('practice', 'تمرین و آموزش'),
        ('exam', 'آزمون'),
        ('support', 'پشتیبانی'),
        ('Sale', 'فروش'),
    ]
    title = models.CharField(max_length=255)
    staff = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='staff', null=True)
    student = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='student', null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    relate_unit = models.CharField(max_length=255, choices=CHOICES)

    @property
    def message_set(self):
        return self.ticketmessage_set.all().order_by('created_on')

    def __str__(self):
        return f'{self.title}, {self.relate_unit}, {self.staff}, {self.student}'


class TicketMessage(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField(blank=False)
    created_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.ticket}, {self.text}'


class Chat(models.Model):
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='sender', null=True)
    receiver = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='receiver', null=True)
    date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.sender}, {self.receiver}, {self.id}'


class ChatMessage(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    text = models.TextField(blank=False)
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.chat}, {self.sender}, {self.text}'
