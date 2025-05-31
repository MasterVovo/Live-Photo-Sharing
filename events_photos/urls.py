from django.urls import path
from . import views

urlpatterns = [
    path('welcome/', views.welcome_view, name='welcome'),
    path('upload/', views.upload_photo_view, name='upload_photo'),
    path('gallery/', views.photo_gallery_view, name='photo_gallery'),
    path('edit/<int:photo_id>/edit', views.edit_photo_view, name='edit_photo'),
    path('delete/<int:photo_id>/delete/', views.delete_photo_view, name='delete_photo'),
]
