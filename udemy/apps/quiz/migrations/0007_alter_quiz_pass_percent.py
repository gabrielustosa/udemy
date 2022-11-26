# Generated by Django 4.1.2 on 2022-11-25 18:44

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('quiz', '0006_question_course'),
    ]

    operations = [
        migrations.AlterField(
            model_name='quiz',
            name='pass_percent',
            field=models.PositiveIntegerField(validators=[django.core.validators.MaxValueValidator(100)]),
        ),
    ]