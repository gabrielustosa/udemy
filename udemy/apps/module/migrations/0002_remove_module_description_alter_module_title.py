# Generated by Django 4.1.2 on 2022-10-22 14:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('module', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='module',
            name='description',
        ),
        migrations.AlterField(
            model_name='module',
            name='title',
            field=models.CharField(max_length=200, verbose_name='Title'),
        ),
    ]
