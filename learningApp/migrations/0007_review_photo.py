# Generated by Django 3.2.20 on 2023-09-07 18:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learningApp', '0006_course_instructor'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='photo',
            field=models.ImageField(null=True, upload_to='review_image/'),
        ),
    ]
