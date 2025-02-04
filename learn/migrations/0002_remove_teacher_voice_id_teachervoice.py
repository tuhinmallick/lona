# Generated by Django 5.1 on 2024-10-13 22:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learn', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='teacher',
            name='voice_id',
        ),
        migrations.CreateModel(
            name='TeacherVoice',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('voice_id', models.CharField(max_length=100)),
                ('description', models.CharField(blank=True, max_length=255)),
                ('subject', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='learn.subject')),
                ('teacher', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='voices', to='learn.teacher')),
            ],
        ),
    ]
