from django.db import models

# Create your models here.
class Profile(models.Model):
    external_id = models.PositiveIntegerField(
        verbose_name='ID чата пользователя в Telegram',
        unique=True
    )
    username = models.CharField(
        verbose_name='Логин пользователя',
        max_length=50
    )

    name = models.CharField(
        verbose_name='Имя пользователя',
        max_length=100
    )
    program_type = models.CharField(
        verbose_name='Тип программы',
        max_length=50
    )
    gender = models.CharField(
        verbose_name='Пол',
        max_length=30
    )
    age = models.IntegerField(
        verbose_name='Возраст',
        default=0
    )
    weight = models.IntegerField(
        verbose_name='Вес (кг)',
        default=0
    )

    def __str__(self):
        return f'{self.external_id}--{self.username}'

    class Meta:
        verbose_name = 'Профиль'
        verbose_name_plural = 'Список профилей'

class Vitamin(models.Model):
    profile = models.ForeignKey(
        to = 'ugc.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        verbose_name='Время получения заявки',
        auto_now_add=True,
    )
    phys_loads = models.CharField(
        verbose_name='Нагрузка',
        max_length=150
    )
    stress = models.CharField(
        verbose_name='Стресс',
        max_length=15
    )
    weakness = models.CharField(
        verbose_name='Слабость',
        max_length=15
    )
    sun_frequency = models.CharField(
        verbose_name='Солнце',
        max_length=10
    )

    def __str__(self):
        return f'{self.profile}--VITAMINS'

    class Meta:
        verbose_name = 'Данные по программам витаминов'
        verbose_name_plural = 'Данные по программам витаминов'


class Training(models.Model):
    profile = models.ForeignKey(
        to = 'ugc.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        verbose_name='Время получения заявки',
        auto_now_add=True,
    )
    train_goal = models.CharField(
        verbose_name='Цель',
        max_length=20
    )
    how_much = models.CharField(
        verbose_name='Количество кг',
        max_length=10
    )
    sport_lvl = models.CharField(
        verbose_name='Уровень спортсмена',
        max_length=15
    )

    def __str__(self):
        return f'{self.profile}--TRAINING'

    class Meta:
        verbose_name = 'Данные по программам тренировок'
        verbose_name_plural = 'Данные по программам тренировок'


class Nutrition(models.Model):
    profile = models.ForeignKey(
        to = 'ugc.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        verbose_name='Время получения заявки',
        auto_now_add=True,
    )
    nutrition_goal = models.CharField(
        verbose_name='Цель',
        max_length=20
    )
    how_much = models.CharField(
        verbose_name='Количество кг',
        max_length=10
    )
    if_meat = models.CharField(
        verbose_name='Мясо',
        max_length=15
    )
    height = models.IntegerField(
        verbose_name='Рост (см)',
        default=0
    )
    phys_loads = models.CharField(
        verbose_name='Нагрузка',
        max_length=150
    )

    def __str__(self):
        return f'{self.profile}--NUTRITION'

    class Meta:
        verbose_name = 'Данные по программам питания'
        verbose_name_plural = 'Данные по программам питания'

class Payments(models.Model):
    profile = models.ForeignKey(
        to='ugc.Profile',
        verbose_name='Профиль',
        on_delete=models.PROTECT,
    )
    created_at = models.DateTimeField(
        verbose_name='Время получения платежа',
        auto_now_add=True,
    )

    key_succ = models.CharField(
        verbose_name='Ключ',
        max_length=200
    )

    is_activated = models.BooleanField(
        verbose_name='Активирован',
        default = 0
    )
    product_id = models.IntegerField(
        verbose_name='Product ID',
        max_length = 11
    )

    def __str__(self):
        return f'{self.profile}--Payments'

    class Meta:
        verbose_name = 'Данные по плате'
        verbose_name_plural = 'Данные по платежам'
