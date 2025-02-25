# Generated by Django 5.0.7 on 2025-02-23 04:50

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bank', '0005_alter_loan_timestamp_alter_transactions_timestamp'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='billpayment',
            name='status',
        ),
        migrations.AlterField(
            model_name='loan',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 23, 4, 50, 52, 368020, tzinfo=datetime.timezone.utc)),
        ),
        migrations.AlterField(
            model_name='transactions',
            name='timestamp',
            field=models.DateTimeField(default=datetime.datetime(2025, 2, 23, 4, 50, 52, 368020, tzinfo=datetime.timezone.utc)),
        ),
    ]
