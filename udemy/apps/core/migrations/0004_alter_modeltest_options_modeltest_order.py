# Generated by Django 4.1.2 on 2022-12-03 17:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_modeltest_num'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='modeltest',
            options={'ordering': ('order',)},
        ),
        migrations.AddField(
            model_name='modeltest',
            name='order',
            field=models.PositiveIntegerField(null=True),
        ),
    ]