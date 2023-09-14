from django.db import models


class Product(models.Model):
    title = models.CharField(max_length=255)
    price_supplier = models.IntegerField()
    slug = models.SlugField()
    price_customer = models.IntegerField()
    inventory = models.IntegerField()
    last_update = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [models.Index(fields=['title'])]


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    birth_date = models.DateField(null=True)
    email = models.EmailField(null=True, unique=True)

    class Meta:
        indexes = [models.Index(fields=['first_name', 'last_name'])]


class Order(models.Model):
    placed_at = models.DateTimeField(auto_now_add=True)
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    product = models.OneToOneField(Product, on_delete=models.PROTECT)


class Subscription(models.Model):
    quantity = models.IntegerField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    is_paid = models.BooleanField(default=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['customer', 'product']
            )
        ]
