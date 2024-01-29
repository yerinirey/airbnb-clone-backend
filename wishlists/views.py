from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound, ParseError
from rest_framework.status import HTTP_200_OK
from .models import Wishlist
from rooms.models import Room
from experiences.models import Experience
from .serializers import WishlistSerializer
class Wishlists(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):
        all_wishlists = Wishlist.objects.filter(user=request.user)
        serializer = WishlistSerializer(all_wishlists, many=True,
                                        context={"request": request},)
        return Response(serializer.data)
    def post(self, request):
        serializer = WishlistSerializer(data=request.data)
        if serializer.is_valid():
            rooms = request.data.get("rooms")
            experiences = request.data.get("experiences")
            try:
                with transaction.atomic():
                    wishlist = serializer.save(
                        user=request.user
                    )
                    if rooms:
                        for room_pk in rooms:
                            room = Room.objects.get(pk=room_pk)
                            wishlist.rooms.add(room)
                    if experiences:
                        for experience_pk in experiences:
                            experience = Experience.objects.get(pk=experience_pk)
                            wishlist.experiences.add(experience)   
            except Room.DoesNotExist:
                raise ParseError("Room Not Found")
            except Experience.DoesNotExist:
                raise ParseError("Experience Not Found")
            except Exception as e:
                raise ParseError(e)
            serializer = WishlistSerializer(wishlist, context={"request": request})
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class WishlistDetail(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound

    def get(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(wishlist, context={"request": request},)
        return Response(serializer.data)
    
    def delete(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        wishlist.delete()
        return Response(status=HTTP_200_OK)
    
    def put(self, request, pk):
        wishlist = self.get_object(pk, request.user)
        serializer = WishlistSerializer(wishlist, data=request.data, partial=True)
        if serializer.is_valid():
            wishlist = serializer.save()
            serializer = WishlistSerializer(wishlist, context={"request": request},)
            return Response(serializer.data)
        else:
            return Response(serializer.errors)

class WishlistRoomToggle(APIView):
    def get_list(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound
    def get_room(self, pk):
        try:
            return Room.objects.get(pk=pk)
        except Room.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, room_pk):
        wishlist = self.get_list(pk, request.user)
        room = self.get_room(room_pk)
        if wishlist.rooms.filter(pk=room.pk).exists():
            wishlist.rooms.remove(room)
        else:
            wishlist.rooms.add(room)
        return Response(status=HTTP_200_OK)
    
class WishlistExperienceToggle(APIView):
    def get_list(self, pk, user):
        try:
            return Wishlist.objects.get(pk=pk, user=user)
        except Wishlist.DoesNotExist:
            raise NotFound
    def get_experience(self, pk):
        try:
            return Experience.objects.get(pk=pk)
        except Experience.DoesNotExist:
            raise NotFound
        
    def put(self, request, pk, experience_pk):
        wishlist = self.get_list(pk, request.user)
        experience = self.get_experience(experience_pk)
        if wishlist.experiences.filter(pk=experience.pk).exists():
            wishlist.experiences.remove(experience)
        else:
            wishlist.experiences.add(experience)
        return Response(status=HTTP_200_OK)