# Generated by Django 3.2.20 on 2023-09-24 18:30

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('learningApp', '0038_auto_20230923_2310'),
    ]

    operations = [
        migrations.CreateModel(
            name='subscriptionNewsletter',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('email', models.EmailField(max_length=254)),
            ],
        ),
    ]
