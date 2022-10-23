# Generated by Django 4.1.2 on 2022-10-23 02:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0002_lessonrelation'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='video_duration',
            field=models.FloatField(default=1),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video_id',
            field=models.CharField(max_length=100),
        ),
    ]
