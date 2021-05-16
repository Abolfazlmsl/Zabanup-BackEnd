import secrets
import string
from random import randint

from django.contrib.auth import get_user_model
from kavenegar import KavenegarAPI, APIException, HTTPException
from rest_framework import generics, status, viewsets, mixins
from rest_framework.generics import UpdateAPIView, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated

from Web_zabanup.settings import KAVENEGAR_APIKEY
from core import models
from . import serializers, permissions


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class CreateUserView(generics.CreateAPIView):
    """Create a new user in system"""
    serializer_class = serializers.UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = serializers.UserSerializer(data=self.request.data)
        if serializer.is_valid():
            serializer.validated_data['generated_token'] = randint(100000, 999999)
            if serializer.validated_data['email'] == '':
                serializer.validated_data['email'] = None
            serializer.save()
        try:
            api = KavenegarAPI(KAVENEGAR_APIKEY)
            # print("phone", serializer.validated_data['phone_number'])
            params = {'sender': '10008445', 'receptor': serializer.validated_data['phone_number'],
                      'message': 'زبان آپ\n' + 'کد تایید:' + str(serializer.validated_data['generated_token'])}
            api.sms_send(params)
            return Response({"message": "ثبت نام با موفقیت انجام شد. کد تایید به تلفن همراه شما ارسال شد."}, status=status.HTTP_201_CREATED)

        except KeyError:
            return Response({"message": "ثبت نام با مشکل مواجه شده است! لطفا مجدد تلاش کنید"}, status=status.HTTP_400_BAD_REQUEST)

        except APIException:
            return Response(
                {
                    'error': 'ارسال کد تایید با مشکل مواجه شده است',
                    'type': 'APIException'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except HTTPException:
            return Response(
                {
                    'error': 'ارسال کد تایید با مشکل مواجه شده است',
                    'type': 'HTTPException'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class ManageUserView(generics.RetrieveUpdateAPIView):
    """manage the authenticated user"""
    serializer_class = serializers.UserDetailSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        """Retrieve and return authenticated user"""
        return self.request.user


class UserPhoneRegisterAPIView(APIView):

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        if user:
            serializer = serializers.UserPhoneRegisterSerializer(user, data=data)
            if serializer.is_valid():
                if serializer.data['generated_token'] == int(data.get("generated_token")):
                    user.is_verified = True
                    user.save()
                    return Response({"user": "verified successfully"})
                else:
                    return Response(
                        {'error': 'The entered token is invalid'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(UpdateAPIView):
    """
    An endpoint for changing password.
    """
    serializer_class = serializers.ChangePasswordSerializer
    model = get_user_model()
    permission_classes = (IsAuthenticated,)

    def get_object(self, queryset=None):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid():
            # Check old password
            if not self.object.check_password(serializer.data.get("old_password")):
                return Response({"old_password": ["رمز عبور فعلی نادرست میباشد!"]}, status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
            response = {
                'status': 'success',
                'code': status.HTTP_200_OK,
                'message': 'Password updated successfully',
                'data': []
            }

            return Response(response)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ResendSignUpTokenAPIView(APIView):
    """
    User verification via sms
    """

    def put(self, request):
        data = request.data
        user = get_object_or_404(get_user_model(), phone_number=data['phone_number'])
        print(user)
        if user:
            serializer = serializers.ResendSignUpTokenSerializer(user, data=data)
            if serializer.is_valid():
                serializer.validated_data['generated_token'] = randint(100000, 999999)
                user.save()
                try:
                    api = KavenegarAPI(KAVENEGAR_APIKEY)
                    params = {'sender': '10008445', 'receptor': serializer.validated_data['phone_number'],
                              'message': 'زبان آپ\n' + 'کد تایید:' + str(serializer.validated_data['generated_token'])}
                    response = api.sms_send(params)
                    return Response({"message": "کاربر با موفقیت ثبت نام شد."})

                except APIException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'APIException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
                except HTTPException:
                    return Response(
                        {
                            'error': 'ارسال کد تایید با مشکل مواجه شده است',
                            'type': 'HTTPException'
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            return Response({"user": "چنین کاربری وجود ندارد"})


class ForgetPasswordAPIView(APIView):
    # serializer_class = serializers.UserForgetSerializer
    # queryset = models.User.objects.all()

    def post(self, request):
        phone_number = request.data['phone_number']
        print(phone_number)
        alphabet = string.ascii_letters + string.digits
        password = ''.join(secrets.choice(alphabet) for i in range(8))
        try:
            user = get_user_model().objects.get(phone_number=str(phone_number))
        except get_user_model().DoesNotExist:
            return Response(
                {
                    'message': 'شماره مورد نظر یافت نشد',
                },
                status=status.HTTP_404_NOT_FOUND
            )
        try:
            api = KavenegarAPI(KAVENEGAR_APIKEY)
            params = {'sender': '10008445', 'receptor': phone_number,
                      'message': 'زبان آپ\n' + 'رمزعبور جدید شما:' + password}
            api.sms_send(params)
            user.set_password(password)
            user.save()
            return Response(
                {
                    'message': 'رمز عبور به شماره موبایل وارد شده ارسال گردید',
                },
                status=status.HTTP_200_OK
            )
        except APIException:
            return Response(
                {
                    'error': 'ارسال رمز عبور با مشکل مواجه شده است',
                    'type': 'APIException'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except HTTPException:
            return Response(
                {
                    'error': 'ارسال رمز عبور با مشکل مواجه شده است',
                    'type': 'HTTPException'
                },
                status=status.HTTP_400_BAD_REQUEST
            )


class UserAnswerViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    serializer_class = serializers.UserAnswerSerializer
    permission_classes = (IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)
    queryset = models.UserAnswer.objects.all()

    def get_queryset(self):
        queryset = models.UserAnswer.objects.filter(user=self.request.user)
        return queryset


class TicketViewSet(viewsets.GenericViewSet,
                    mixins.ListModelMixin,
                    mixins.RetrieveModelMixin,
                    mixins.CreateModelMixin,):
    """Manage ticket in database"""

    serializer_class = serializers.TicketListSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    queryset = models.Ticket.objects.all()

    def get_queryset(self):
        return self.queryset.filter(staff=self.request.user)

    def get_serializer_class(self):
        if self.action == 'list':
            return self.serializer_class
        elif self.action == 'create':
            return serializers.TicketCreateSerializer
        else:
            return serializers.TicketDetailSerializer

    def perform_create(self, serializer):
        """Save authenticated user"""
        serializer.save(student=self.request.user)


class TicketMessageAPIView(generics.CreateAPIView):
    serializer_class = serializers.TicketMessageSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsTicketMessageOwner)
    pagination_class = StandardResultsSetPagination
    queryset = models.TicketMessage.objects.all()

    def perform_create(self, serializer):
        """Save authenticated user"""
        serializer.save(sender=self.request.user)


class CommentViewSet(viewsets.GenericViewSet,
                     mixins.ListModelMixin,
                     mixins.RetrieveModelMixin):
    serializer_class = serializers.CommentSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated, permissions.IsTicketMessageOwner)
    pagination_class = StandardResultsSetPagination
    queryset = models.Comment.objects.all()

    def get_queryset(self):
        return models.Comment.objects.filter(user=self.request.user)