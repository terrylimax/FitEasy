# Generated by Django 2.2.7 on 2020-01-17 13:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0005_auto_20200113_1506'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='nutrition',
            name='if_milk',
        ),
        migrations.AddField(
            model_name='nutrition',
            name='height',
            field=models.IntegerField(default=0, verbose_name='Рост (см)'),
        ),
        migrations.AlterField(
            model_name='nutrition',
            name='how_much',
            field=models.CharField(max_length=10, verbose_name='Количество кг'),
        ),
        migrations.AlterField(
            model_name='training',
            name='how_much',
            field=models.CharField(max_length=10, verbose_name='Количество кг'),
        ),
    ]
