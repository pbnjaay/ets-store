from django.db import models
from django.core.validators import MinValueValidator


class Product(models.Model):
    title = models.CharField(max_length=255)
    price_supplier = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    price_consumer = models.PositiveIntegerField(
        validators=[MinValueValidator(1)])
    inventory = models.PositiveIntegerField()
    slug = models.SlugField()
    last_update = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return self.title

    class Meta:
        indexes = [models.Index(fields=['title'])]
        ordering = ['title']


class Customer(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=15)
    birth_date = models.DateField(null=True)
    email = models.EmailField(null=True, unique=True)
    is_consumer = models.BooleanField(default=True)
    image = models.ImageField(upload_to='store/images', null=True)

    def __str__(self) -> str:
        return f'{self.first_name} {self.last_name}'

    class Meta:
        indexes = [models.Index(fields=['first_name', 'last_name'])]


class Order(models.Model):
    placed_at = models.DateField()
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    amount_paid = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_order_per_day',
                fields=['customer', 'placed_at']
            )
        ]


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order, on_delete=models.CASCADE, related_name='items')
    quantity = models.IntegerField(validators=[MinValueValidator(1)])
    unit_price = models.PositiveIntegerField()
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity_subscribed = models.PositiveIntegerField()
    retour = models.PositiveBigIntegerField(default=0)


class Instalment(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.PROTECT)
    amount = models.PositiveIntegerField()
    date = models.DateTimeField()


class Subscription(models.Model):
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                name='unique_subscription',
                fields=['customer', 'product']
            )
        ]
