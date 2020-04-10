from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path("follow/", views.follow_index, name="follow_index"),
    path("<username>/follow/", views.profile_follow, name="profile_follow"), 
    path("<username>/unfollow", views.profile_unfollow, name="profile_unfollow"),
    
    path('group/<slug:slug>', views.group_posts, name="group"),
    path('search/', views.search, name='search'),
    path('new/', views.new, name='new'),
    path("<username>/", views.profile, name="profile"),
    path("<username>/<int:post_id>/", views.post_view, name="post"),
    path("<username>/<int:post_id>/edit/", views.post_edit, name="post_edit"),
    path("<username>/<int:post_id>/comment/", views.add_comment, name="add_comment"),
    path('delete/<comment_id>', views.delete_comment, name='delete_comment'),
    path("", views.index, name="index"),

]
