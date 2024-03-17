from django.utils import timezone
from rest_framework.serializers import ModelSerializer
from rest_framework import serializers
from .models import Booking

class CreateExperienceBookingSerializer(ModelSerializer):
    experience_time = serializers.DateTimeField()
    class Meta:
        model = Booking
        fields = (
            "experience_time",
            "guests",
        )

    def validate_experience_time(self, value):
        ex_start_time = self.context["experience"].start
        ex_end_time = self.context["experience"].end
        now = timezone.localtime(timezone.now())
        if value < now:
            raise serializers. ValidationError("Can't book in the past.")
        if Booking.objects.filter(experience_time__date=value.date()).exists():
            raise serializers.ValidationError("There are already someone's reservation for that date.")
        if value.time() <= ex_start_time or value.time() >= ex_end_time:
            raise serializers.ValidationError("Please book at a valid time.")
        return value
    

class CreateRoomBookingSerializer(ModelSerializer): 
    check_in = serializers.DateField()
    check_out = serializers.DateField()
    class Meta:
        model = Booking
        fields = (
            "check_in",
            "check_out",
            "guests",
        )

    def validate_check_in(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past.")
        return value

    def validate_check_out(self, value):
        now = timezone.localtime(timezone.now()).date()
        if now > value:
            raise serializers.ValidationError("Can't book in the past.")
        return value

    def validate(self, data):
        room = self.context.get("room")
        if data['check_out'] <= data['check_in']:
            raise serializers.ValidationError("Check in should be smaller than check out.")
        if Booking.objects.filter(
            room=room,
            check_in__lte=data["check_out"], 
            check_out__gte=data["check_in"],
            ).exists():
            raise serializers.ValidationError("Those (or some of those) dates are already taken.")
        return data

class PublicBookingSerializer(ModelSerializer):

    class Meta:
        model = Booking
        fields = (
            "pk",
            "check_in",
            "check_out",
            "experience_time",
            "guests",
        )

class PrivateBookingSerializer(ModelSerializer):
    class Meta:
        model = Booking
        fields = "__all__"