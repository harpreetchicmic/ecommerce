# Generated by Django 3.2.18 on 2023-03-28 05:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0003_alter_signup_is_vendor'),
    ]

    operations = [
        migrations.AlterField(
            model_name='signup',
            name='is_vendor',
            field=models.BooleanField(default=False, null=True),
        ),
    ]
