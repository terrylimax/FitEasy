# Generated by Django 2.2.7 on 2020-01-21 17:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0006_auto_20200117_1653'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nutrition',
            name='username',
        ),
        migrations.RemoveField(
            model_name='training',
            name='username',
        ),
        migrations.RemoveField(
            model_name='vitamin',
            name='username',
        ),
        migrations.AlterField(
            model_name='nutrition',
            name='nutrition_goal',
            field=models.CharField(max_length=20, verbose_name='Цель'),
        ),
        migrations.AlterField(
            model_name='nutrition',
            name='phys_loads',
            field=models.CharField(max_length=150, verbose_name='Нагрузка'),
        ),
        migrations.AlterField(
            model_name='training',
            name='train_goal',
            field=models.CharField(max_length=20, verbose_name='Цель'),
        ),
        migrations.AlterField(
            model_name='vitamin',
            name='phys_loads',
            field=models.CharField(max_length=150, verbose_name='Нагрузка'),
        ),
    ]