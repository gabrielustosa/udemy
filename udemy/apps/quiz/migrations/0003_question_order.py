# Generated by Django 4.1.2 on 2022-11-21 18:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0002_question_max_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='question',
            name='order',
            field=models.PositiveIntegerField(null=True),
        ),
    ]
