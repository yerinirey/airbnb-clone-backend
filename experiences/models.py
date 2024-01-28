from django.db import models
from common.models import CommonModel

class Experience(CommonModel):

    """ Experience Model Definition """
    country = models.CharField(max_length=50, default="한국")
    city = models.CharField(max_length=80, default="서울")
    name = models.CharField(max_length=250)
    host = models.ForeignKey("users.User", on_delete=models.CASCADE, related_name="experiences",)
    price = models.PositiveIntegerField()
    address = models.CharField(max_length=250)
    start = models.TimeField()
    end = models.TimeField()
    description = models.TextField()
    perks = models.ManyToManyField("experiences.Perk", related_name="experiences",)
    category = models.ForeignKey(
        "categories.Category",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="experiences",
    )
    def __str__(self):
        return self.name
    def rating(self):
        count = self.reviews.count()
        if count == 0:
            return 0.0
        else:
            total_rating = 0
            for review in self.reviews.all().values("rating"):
                total_rating += review["rating"]
            return round(total_rating/count, 2)
    def total_time(self):
        seconds = (self.end.hour * 3600 + self.end.minute * 60 + self.end.second) - (
            self.start.hour * 3600 + self.start.minute * 60 + self.start.second
        )
        hours, remainder = divmod(seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        return f"{hours}H {minutes}M"


class Perk(CommonModel):

    """ What is included on an Experience """
    name = models.CharField(max_length=100)
    details = models.CharField(max_length=250, blank=True, null=True)
    explanation = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name
    
    