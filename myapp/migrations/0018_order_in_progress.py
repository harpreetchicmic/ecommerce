# Generated by Django 3.2.18 on 2023-04-12 05:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0017_alter_productreview_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='in_progress',
            field=models.BooleanField(default=False),
        ),
    ]
