# Generated by Django 4.2.5 on 2023-09-23 08:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0007_alter_orderitem_quantity_subscribed'),
    ]

    operations = [
        migrations.AddField(
            model_name='orderitem',
            name='amount_paid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='quantity_subscribed',
            field=models.PositiveIntegerField(default=0),
            preserve_default=False,
        ),
    ]
