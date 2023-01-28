# Generated by Django 4.1.5 on 2023-01-25 16:09

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='TmpUser',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('MBTI', models.CharField(max_length=10)),
                ('ennear_ans', models.CharField(max_length=10)),
                ('ennear_res', models.CharField(max_length=10)),
                ('prefer_movie_id', models.IntegerField()),
                ('recommended_character_id', models.IntegerField()),
                ('create_time', models.DateTimeField()),
            ],
        ),
    ]