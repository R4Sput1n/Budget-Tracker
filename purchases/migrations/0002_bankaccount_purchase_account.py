# Generated by Django 5.0.6 on 2024-06-15 13:08

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('purchases', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BankAccount',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=10, unique=True)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
        ),
        migrations.AddField(
            model_name='purchase',
            name='account',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='purchases.bankaccount'),
        ),
    ]
