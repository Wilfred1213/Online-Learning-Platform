# Generated by Django 3.2.20 on 2023-09-03 15:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learningApp', '0003_auto_20230903_1606'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='description',
            field=models.TextField(default='description', max_length=10000),
        ),
    ]
