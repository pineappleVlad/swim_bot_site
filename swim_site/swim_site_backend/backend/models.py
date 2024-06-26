from django.db import models


class Child(models.Model):
    name = models.CharField(max_length=255, verbose_name='Фио ребёнка', unique=True)
    paid_training_count = models.IntegerField(default=0, verbose_name='Кол-во оплаченных занятий')
    parent_chat_id = models.IntegerField(blank=True, null=True, verbose_name='Айди чата родителя')

    def __str__(self):
        return f'{self.name} | Баланс: {self.paid_training_count}'
    class Meta:
        verbose_name = 'Ребёнок'
        verbose_name_plural = 'Дети'



class Trainers(models.Model):
    name = models.CharField(max_length=255, verbose_name='Фио тренера')
    city = models.CharField(max_length=255, verbose_name='Город')

    def __str__(self):
        return f'{self.name} {self.city}'

    class Meta:
        verbose_name = 'Тренер'
        verbose_name_plural = 'Тренеры'


class Training(models.Model):
    POOL_CHOICES = (
        ('1', 'Большой бассейн'),
        ('2', 'Малый бассейн')
    )

    STATUS_CHOICES = (
        ('1', 'Open'),
        ('2', 'Closed')
    )

    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    training_status = models.CharField(max_length=255, choices=STATUS_CHOICES, default='Open', verbose_name='Статус тренировки')
    pool_type = models.CharField(max_length=255, choices=POOL_CHOICES, verbose_name='Тип бассейна')
    trainer = models.ForeignKey(Trainers, on_delete=models.CASCADE, verbose_name='Тренер')
    children = models.ManyToManyField('Child', verbose_name='Дети', blank=True)

    def __str__(self):
        return f'{self.date} {self.time} {self.training_status} {self.pool_type} {self.trainer}'
    class Meta:
        verbose_name = 'Тренировка'
        verbose_name_plural = 'Тренировки'


class ChildId(models.Model):
    name = models.CharField(max_length=255, verbose_name='Имя ребенка', unique=True)
    parent_chat_id = models.IntegerField(verbose_name='Нынешний айди', unique=True)


class BalanceOperations(models.Model):
    date = models.DateField(verbose_name='Дата')
    time = models.TimeField(verbose_name='Время')
    child_name = models.CharField(max_length=255, verbose_name='ФИО ребенка')
    add_trainings_count = models.IntegerField(verbose_name='Добавленные тренировки')
