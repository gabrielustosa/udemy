# Generated by Django 4.1.2 on 2022-12-01 21:10

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelrelatedobject',
            name='model_test',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='model_related', to='core.modeltest'),
        ),
    ]
