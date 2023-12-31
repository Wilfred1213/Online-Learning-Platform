# Generated by Django 3.2.20 on 2023-09-21 20:48

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('learningApp', '0028_cumulativescore_quiz'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='cumulativescore',
            unique_together={('user', 'course')},
        ),
        migrations.RemoveField(
            model_name='cumulativescore',
            name='quiz',
        ),
        migrations.RemoveField(
            model_name='cumulativescore',
            name='quiz_score',
        ),
    ]
