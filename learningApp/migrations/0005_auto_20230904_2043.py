# Generated by Django 3.2.20 on 2023-09-04 19:43

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('learningApp', '0004_category_description'),
    ]

    operations = [
        migrations.RenameField(
            model_name='curriculum',
            old_name='lectures',
            new_name='course',
        ),
        migrations.RenameField(
            model_name='curriculum',
            old_name='sub_heading_intro1',
            new_name='sub_heading_intro',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='sub_heading2',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='sub_heading3',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='sub_heading_intro2',
        ),
        migrations.RemoveField(
            model_name='curriculum',
            name='sub_heading_intro3',
        ),
    ]
