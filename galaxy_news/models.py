from django.db import models
from django.contrib.auth.models import User


class News(models.Model):
    title = models.CharField(max_length=130)
    text = models.TextField()
    image = models.ImageField(upload_to='images/', null=True, blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


class GmailConfirm(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)

    def __str__(self):
        return f"{self.user.username}: {self.code}"