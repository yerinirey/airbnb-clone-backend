from typing import Any
from django.contrib import admin
from django.db.models.query import QuerySet
from .models import Review

# class WordFilter(admin.SimpleListFilter):
#     title = "Filter by words!"
#     parameter_name= "word"
#     def lookups(self, request, model_admin):
#         return [
#             ("good", "Good"), ("great", "Great"), ("awesome", "Awesome"),
#         ]
    
#     def queryset(self, request, reviews):
#         word = self.value()
#         print(word)
#         if word:
#             return reviews.filter(payload__contains=word)
#         else:
#             return reviews
        
class ScoreFilter(admin.SimpleListFilter):
    title = "Filter by score"
    parameter_name = "score"
    def lookups(self, request, model_admin):
        return [
            ("good", "Good"), ("bad", "Bad"),
        ]
    def queryset(self, request, reviews):
        param = self.value()
        print(param)
        if param=="good":
            return reviews.filter(rating__gte=3)
        elif param=="bad":
            return reviews.filter(rating__lt=3)
        else:
            return reviews


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = (
        "__str__",
        "payload"
    )
    list_filter = (
        ScoreFilter,
        # WordFilter,
        "rating",
        "user__is_host",
        "room__category",
        "room__pet_friendly",
    )