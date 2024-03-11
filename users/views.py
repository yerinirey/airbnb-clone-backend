import requests
from django.contrib.auth import authenticate, login, logout
from django.conf import settings
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.exceptions import ParseError, NotFound
from rest_framework.permissions import IsAuthenticated
import jwt
from . import serializers
from .models import User
class Me(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)
    
    def put(self, request):
        user = request.user
        serializer = serializers.PrivateUserSerializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)
        
class Users(APIView):
    def post(self, request):
        password = request.data.get('password')
        if not password:
            raise ParseError
        serializer = serializers.PrivateUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            user.set_password(password)
            user.save()
            serializer = serializers.PrivateUserSerializer(user)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class PublicUser(APIView):

    def get(self, request, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise NotFound
        serializer = serializers.PrivateUserSerializer(user)
        return Response(serializer.data)
    
class ChangePassword(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request):
        user = request.user
        old_password = request.data.get("old_password")
        new_password = request.data.get("new_password")
        if not old_password or not new_password:
            raise ParseError
        if user.check_password(old_password):
            user.set_password(new_password)
            user.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class LogIn(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            raise ParseError
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return Response({"ok": "Logged In!"})
        else:
            return Response({"error":"Wrong Password"},
                            status=status.HTTP_400_BAD_REQUEST,)
        
class LogOut(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)
        return Response({"ok": "byebye"})
    
class JWTLogin(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if not username or not password:
            raise ParseError
        user = authenticate(request, username=username, password=password)
        if user:
            token = jwt.encode({"pk": user.pk}, settings.SECRET_KEY, algorithm="HS256",)
            return Response({"token": token})
        else:
            return Response({"error":"Wrong Password"})
class GithubLogIn(APIView):
    def post(self, request):
        try:
            code = request.data.get("code")
            access_token = requests.post(f"https://github.com/login/oauth/access_token?code={code}&client_id=7adf462274f7c5a31ed2&client_secret={settings.GH_SECRET}", 
                headers={
                    "Accept":"application/json",
                },
            )
            access_token = access_token.json().get('access_token')
            user_data = requests.get("https://api.github.com/user", headers={
                "Authorization": f"Bearer {access_token}",
                "Accept":"application/json",
            })
            user_data = user_data.json()
            user_emails = requests.get("https://api.github.com/user/emails", headers={
                "Authorization": f"Bearer {access_token}",
                "Accept":"application/json",
            })
            user_emails = user_emails.json()
            try:
                user = User.objects.get(email= user_emails[0]["email"])
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user = User.objects.create(
                    username=user_data.get('login'),
                    email=user_emails[0]['email'],
                    name=user_data.get('name'),
                    avatar=user_data.get('avatar_url'),
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class KakaoLogIn(APIView):
    def post(self, request):
        try:
            code = request.data.get('code')
            access_token = requests.post("https://kauth.kakao.com/oauth/token",
                                         headers={
                                             "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
                                         },
                                        data={
                                            "grant_type": "authorization_code",
                                            "client_id": "b85462c423a2ff377d3dd60ce0ebc5ba",
                                            "redirect_uri": "http://127.0.0.1:3000/social/kakao",
                                            "code": code,
                                        },
                                        )
            access_token = access_token.json().get("access_token")
            user_data = requests.get("https://kapi.kakao.com/v2/user/me",
                                     headers={
                                         "Authorization": f"Bearer ${access_token}",
                                         "Content-type": "application/x-www-form-urlencoded;charset=utf-8"
                                     })
            user_data = user_data.json()
            kakao_account = user_data.get("kakao_account")
            profile = kakao_account.get("profile")
            try:
                user = User.objects.get(username=profile.get("nickname"))
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            except User.DoesNotExist:
                user= User.objects.create(
                    email = "cannotget@kakao.com",
                    username = profile.get("nickname"),
                    name=profile.get('nickname'),
                    avatar=profile.get("profile_image_url"),
                )
                user.set_unusable_password()
                user.save()
                login(request, user)
                return Response(status=status.HTTP_200_OK)
            # try:
            #     user = User.objects.get(email=kakao_account.get("email"))
            #     login(request, user)
            #     return Response(status=status.HTTP_200_OK)
            # except User.DoesNotExist:
            #     user= User.objects.create(
            #         email=kakao_account.get("email"),
            #         username = profile.get("nickname"),
            #         name=profile.get('nickname'),
            #         avatar=profile.get("profile_image_url"),
            #     )
            #     user.set_unusable_password()
            #     user.save()
            #     login(request, user)
            #     return Response(status=status.HTTP_200_OK)
        except Exception:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        
class SignUp(APIView):
    def post(self, request):
        try:
            name = request.data.get("name")
            email = request.data.get("email")
            username = request.data.get("username")
            password = request.data.get("password")
            if User.objects.filter(username=username):
                return Response({
                    "Failed": "The username is already used. Please use another username."
                }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email):
                return Response({
                    "Failed": "This email has already been used."
                }, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(
                email = email,
                username = username,
                name = name
            )

            user.set_password(password)
            user.save()
            login(request, user)
            return Response({
                "Success": "Signed Up!!!"
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({
                "Failed": f"{e}"
            }, status=status.HTTP_400_BAD_REQUEST)
        