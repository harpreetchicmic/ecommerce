# Generated by Django 3.2.18 on 2023-03-31 05:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0008_recently_viewed'),
    ]

    operations = [
        migrations.AddField(
            model_name='addproduct',
            name='quantity',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
