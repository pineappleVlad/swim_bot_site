# Generated by Django 4.2.11 on 2024-03-16 15:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0009_alter_childid_parent_chat_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='training',
            name='children',
            field=models.ManyToManyField(blank=True, null=True, to='backend.child', verbose_name='Дети'),
        ),
    ]
