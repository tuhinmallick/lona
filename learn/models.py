from django.conf import settings
from django.db import models

class Teacher(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    voice_id = models.CharField(max_length=100, blank=True, null=True)

class Subject(models.Model):
    name = models.CharField(max_length=100)

class Topic(models.Model):
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    content = models.TextField()

class LearningSession(models.Model):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    date = models.DateTimeField(auto_now_add=True)