# Generated by Django 3.2.20 on 2023-09-02 17:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentications', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customuser',
            name='is_instructor',
            field=models.BooleanField(default=False, verbose_name='is_student'),
        ),
        migrations.AlterField(
            model_name='customuser',
            name='is_student',
            field=models.BooleanField(default=False, verbose_name='is_instructor'),
        ),
    ]