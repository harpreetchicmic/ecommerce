# Generated by Django 3.2.18 on 2023-03-28 10:01

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0004_alter_signup_is_vendor'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='cart',
            name='name',
        ),
        migrations.RemoveField(
            model_name='cart',
            name='photo',
        ),
    ]