from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)


class FAQ(models.Model):
    intent = models.CharField(max_length=100)
    question = models.TextField()
    answer = models.JSONField() 

    def __str__(self):
        return self.intent


class ChatLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    confidence = models.FloatField(default=0.0)
    timestamp = models.DateTimeField(auto_now_add=True)


class Feedback(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='users_feedback')
    message = models.TextField()
    response = models.TextField()
    rating = models.IntegerField(choices=[(1, 'Poor'), (2, 'Fair'), (3, 'Good'), (4, 'Very Good'), (5, 'Excellent')])
    comments = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
