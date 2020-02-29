# Generated by Django 3.0.3 on 2020-02-14 20:22

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('ugc', '0007_auto_20200121_2017'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payments',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Время получения платежа')),
                ('key_succ', models.CharField(max_length=20, verbose_name='Ключ')),
                ('is_activated', models.BooleanField(default=0, verbose_name='Активирован')),
                ('product_id', models.IntegerField(max_length=11, verbose_name='Product ID')),
                ('profile', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='ugc.Profile', verbose_name='Профиль')),
            ],
            options={
                'verbose_name': 'Данные по плате',
                'verbose_name_plural': 'Данные по программам питания',
            },
        ),
    ]
