from rest_framework.serializers import ModelSerializer, SerializerMethodField
from .models import Perk, Experience
from medias import serializers as media_serializers
from users import serializers as user_serializers
from wishlists.models import Wishlist
from categories.serializers import CategorySerializer
class PerkSerializer(ModelSerializer):
    class Meta:
        model = Perk
        fields = "__all__"

class ExperienceDetailSerializer(ModelSerializer):
    host = user_serializers.TinyUserSerializer(read_only=True)
    total_time = SerializerMethodField()
    perks = PerkSerializer(read_only=True, many=True)
    category = CategorySerializer(read_only=True)
    rating = SerializerMethodField()
    is_owner = SerializerMethodField()
    is_liked = SerializerMethodField()
    video = media_serializers.VideoSerializer(read_only = True)

    class Meta:
        model = Experience
        fields = "__all__"
    
    def get_rating(self, experience):
        return experience.rating()
    def get_is_owner(self, experience):
        request = self.context["request"]
        return experience.host == request.user
    def get_is_liked(self, experience):
        request = self.context["request"]
        return Wishlist.objects.filter(user=request.user, experiences__pk=experience.pk).exists()
    def get_total_time(self, experience):
        return experience.total_time()

class ExperienceListSerializer(ModelSerializer):
    rating = SerializerMethodField()
    total_time = SerializerMethodField()
    is_owner = SerializerMethodField()
    video = media_serializers.VideoSerializer(read_only = True)

    class Meta:
        model = Experience
        # fields = (
        #     "pk",
        #     "name",
        #     "country",
        #     "city",
        #     "price",
        #     "rating",
        #     "is_owner",
        #     "video",
        # )
        fields = "__all__"
    
    def get_rating(self, experience):
        return experience.rating()
    def get_is_owner(self, experience):
        request = self.context["request"]
        return experience.host == request.user
    def get_total_time(self, experience):
        return experience.total_time()

