from django.urls import path
from .views import PhotoDetail, VideoDetail, GetUploadURL, UploadPhoto
urlpatterns = [
    path("photos/get-url", GetUploadURL.as_view()),
    path("photos/upload-photo", UploadPhoto.as_view()),
    path("photos/<int:pk>", PhotoDetail.as_view()),
    path("videos/<int:pk>", VideoDetail.as_view())
]