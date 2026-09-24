from django.db import models

class FAQ(models.Model):
    question = models.TextField()
    answer = models.TextField()
    category = models.CharField(max_length=100)

    def __str__(self):
        return self.question
