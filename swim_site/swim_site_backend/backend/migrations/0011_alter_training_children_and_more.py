# Generated by Django 4.2.11 on 2024-03-16 15:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0010_alter_training_children'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='children',
            field=models.ManyToManyField(blank=True, to='backend.child', verbose_name='Дети'),
        ),
        migrations.AlterField(
            model_name='training',
            name='training_status',
            field=models.CharField(choices=[('1', 'Open'), ('2', 'Closed')], default='Open', max_length=255, verbose_name='Статус тренировки'),
        ),
    ]
