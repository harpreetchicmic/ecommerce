# Generated by Django 3.2.18 on 2023-03-27 09:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_delete_asd'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='is_vendor',
            field=models.BooleanField(default=False),
        ),
    ]
