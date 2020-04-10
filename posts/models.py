from django.db import models
from django.contrib.auth import get_user_model
from django import forms

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(max_length=140, unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField()
    pub_date = models.DateTimeField("date published", auto_now_add=True, db_index=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="author_posts")
    group = models.ForeignKey(Group, blank=True, null=True, max_length=300, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/', blank=True, null=True)

    def __str__(self):
        return self.text


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE) 
    text = models.TextField()
    created = models.DateTimeField("DateCreated", auto_now_add=True)


class Follow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="follower") #подписчик
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="following") #подписуемый

    def __str__(self):
        return f'follower - {self.user} following - {self.author}'

