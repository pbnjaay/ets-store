from django.db import transaction
from rest_framework import serializers

from store.models import (Customer, Instalment, Order, OrderItem, Product,
                          Subscription)


class ProductSerializer(serializers.ModelSerializer):

    class Meta:
        model = Product
        fields = ['id', 'title', 'inventory', 'slug',
                  'price_supplier', 'price_consumer']


class CustomerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name',
                  'is_consumer', 'email', 'phone_number', 'birth_date']


class CreateSubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = fields = ['id', 'quantity', 'customer', 'product']


class SubscriptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = ['id', 'quantity', 'customer', 'product']

    customer = serializers.PrimaryKeyRelatedField(
        queryset=Subscription.objects.all()
    )
    product = serializers.HyperlinkedRelatedField(
        view_name='product-detail',
        queryset=Product.objects.all()
    )


class CreateOrderItemSeriazer(serializers.ModelSerializer):
    unit_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price', 'product']

    def save(self, **kwargs):
        self.instance = OrderItem.objects.create(
            order_id=self.context['order_id'],

            unit_price=self.validated_data['product'].price_consumer
            if self.context['is_consumer']
            else self.validated_data['product'].price_supplier,

            product=self.validated_data['product'],
            quantity=self.validated_data['quantity']
        )
        return self.instance


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.IntegerField(read_only=True)
    product = ProductSerializer()

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price', 'product']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer()

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'customer', 'items']


class UpdateOrderSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['customer']


class CreateOrderSerializer(serializers.ModelSerializer):
    items = CreateOrderItemSeriazer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'items']

    def save(self, **kwargs):
        with transaction.atomic():
            customer = self.validated_data['customer']
            order = Order.objects.create(
                customer_id=customer.id
            )
            order_items = [
                OrderItem(
                    order=order,
                    product=item['product'],
                    unit_price=item['product'].price_consumer if customer.is_consumer else item['product'].price_supplier,
                    quantity=item['quantity']
                )
                for item in self.validated_data['items']
            ]

            OrderItem.objects.bulk_create(order_items)

            return order


class BaseCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name']


class InstalmentSerializer(serializers.ModelSerializer):
    customer = BaseCustomerSerializer()

    class Meta:
        model = Instalment
        fields = ['id', 'customer', 'amount', 'date']


class CreateInstalmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instalment
        fields = ['customer', 'amount', 'date']
