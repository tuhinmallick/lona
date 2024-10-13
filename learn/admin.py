from django.contrib import admin
from .models import Teacher, Subject, Topic, LearningSession

# Register your models here.
admin.site.register(Teacher)
admin.site.register(Subject)
admin.site.register(Topic)
admin.site.register(LearningSession)
