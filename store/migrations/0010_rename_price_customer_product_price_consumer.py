# Generated by Django 4.2.5 on 2023-09-18 03:35

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0009_customer_is_consumer'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='price_customer',
            new_name='price_consumer',
        ),
    ]