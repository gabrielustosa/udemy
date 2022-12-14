# Generated by Django 4.1.2 on 2022-11-18 22:46

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('module', '0002_alter_module_options'),
        ('course', '0009_course_image'),
    ]

    operations = [
        migrations.CreateModel(
            name='Quiz',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modification Date and Time')),
                ('order', models.PositiveIntegerField(null=True)),
                ('title', models.CharField(max_length=200, verbose_name='Title')),
                ('description', models.TextField(verbose_name='Description')),
                ('is_published', models.BooleanField(default=False)),
                ('is_draft', models.BooleanField(default=True)),
                ('is_timed', models.BooleanField(default=False)),
                ('pass_percent', models.PositiveIntegerField()),
                ('course', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='course.course')),
                ('module', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='quizzes', to='module.module')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='Question',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='Creation Date and Time')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='Modification Date and Time')),
                ('question', models.TextField()),
                ('feedback', models.TextField()),
                ('answers', django.contrib.postgres.fields.ArrayField(base_field=models.TextField(), size=None)),
                ('correct_response', models.IntegerField()),
                ('quiz', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='quiz.quiz')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
