# Generated by Django 3.1.2 on 2020-12-22 13:28

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('catalog', '0013_auto_20201222_2125'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='id_number',
            field=models.BigIntegerField(blank=True, null=True, validators=[django.core.validators.MaxLengthValidator(8), django.core.validators.MinLengthValidator(0)]),
        ),
    ]
