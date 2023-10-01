# Generated by Django 4.2.5 on 2023-09-28 03:44

from django.db import migrations, models
import store.validators


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0011_customer_image'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='slug',
        ),
        migrations.AlterField(
            model_name='customer',
            name='image',
            field=models.ImageField(null=True, upload_to='store/images', validators=[store.validators.validate_file_size]),
        ),
    ]
