# Generated by Django 4.1.5 on 2023-01-26 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('test_rec', '0002_alter_tmpuser_mbti_alter_tmpuser_ennear_ans_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tmpuser',
            name='prefer_movie_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
        migrations.AlterField(
            model_name='tmpuser',
            name='recommended_character_id',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
