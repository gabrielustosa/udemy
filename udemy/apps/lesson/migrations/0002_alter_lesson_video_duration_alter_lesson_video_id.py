# Generated by Django 4.1.2 on 2022-11-16 18:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('lesson', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lesson',
            name='video_duration',
            field=models.FloatField(null=True),
        ),
        migrations.AlterField(
            model_name='lesson',
            name='video_id',
            field=models.CharField(max_length=100, null=True),
        ),
    ]
