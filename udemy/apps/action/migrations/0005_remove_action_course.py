# Generated by Django 4.1.2 on 2022-11-08 15:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('action', '0004_action_course'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='action',
            name='course',
        ),
    ]
