# Generated by Django 4.2.11 on 2024-03-16 09:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0007_rename_child_name_childid_name'),
    ]

    operations = [
        migrations.RenameField(
            model_name='childid',
            old_name='current_id',
            new_name='parent_chat_id',
        ),
    ]
