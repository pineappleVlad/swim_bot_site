# Generated by Django 4.2.11 on 2024-04-02 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0013_balanceoperations'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='trainers',
            name='city',
        ),
        migrations.AddField(
            model_name='trainers',
            name='club',
            field=models.CharField(blank=True, max_length=255, null=True, verbose_name='Клуб'),
        ),
    ]
