# Generated by Django 5.0.4 on 2024-04-22 23:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0003_alter_answer_is_correct'),
    ]

    operations = [
        migrations.AddField(
            model_name='result',
            name='date',
            field=models.DateTimeField(blank=True, null=True, verbose_name='дата и время прохождения'),
        ),
    ]
