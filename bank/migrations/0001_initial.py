# Generated by Django 5.0.7 on 2025-02-14 15:19

import datetime
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Supports',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='', max_length=20)),
                ('email', models.EmailField(max_length=40)),
                ('issue', models.CharField(default='', max_length=300)),
            ],
        ),
        migrations.CreateModel(
            name='User_reg',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone', models.IntegerField(default=0)),
                ('account_number', models.CharField(max_length=20, unique=True)),
                ('email', models.EmailField(max_length=30)),
                ('gender', models.CharField(max_length=20)),
                ('account_type', models.CharField(max_length=40)),
                ('balance', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('address', models.CharField(default='', max_length=500)),
                ('image', models.ImageField(default='', null=True, upload_to='User/Images')),
                ('Pan', models.CharField(default='', max_length=50)),
                ('aadhaar', models.CharField(default='', max_length=50)),
                ('DoB', models.CharField(default='', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Transactions',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('transaction_type', models.CharField(choices=[('DEPOSIT', 'Deposit'), ('WITHDRAW', 'Withdraw'), ('TRANSFER', 'Transfer')], max_length=20)),
                ('timestamp', models.DateTimeField(default=datetime.datetime(2025, 2, 14, 15, 19, 45, 352624, tzinfo=datetime.timezone.utc))),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('about', models.CharField(max_length=100)),
                ('receiptent', models.DecimalField(decimal_places=2, max_digits=10, null=True)),
                ('receiptent_no', models.CharField(default='', max_length=30, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='bank.user_reg')),
            ],
        ),
    ]
