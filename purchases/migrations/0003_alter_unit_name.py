# Generated by Django 5.0.6 on 2024-06-15 13:10

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0002_bankaccount_purchase_account'),
    ]

    operations = [
        migrations.AlterField(
            model_name='unit',
            name='name',
            field=models.CharField(max_length=20, unique=True),
        ),
    ]