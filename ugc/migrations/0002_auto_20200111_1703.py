# Generated by Django 2.2.7 on 2020-01-11 12:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='weight',
            field=models.IntegerField(default=1, verbose_name='Вес (кг)'),
        ),
    ]