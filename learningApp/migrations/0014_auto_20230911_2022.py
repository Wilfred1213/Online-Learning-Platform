# Generated by Django 3.2.20 on 2023-09-11 19:22

from django.db import migrations
import embed_video.fields


class Migration(migrations.Migration):

    dependencies = [
        ('learningApp', '0013_replyreview_likes'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='lesson',
            name='order',
        ),
        migrations.AddField(
            model_name='lesson',
            name='video',
            field=embed_video.fields.EmbedVideoField(default='www'),
        ),
    ]
