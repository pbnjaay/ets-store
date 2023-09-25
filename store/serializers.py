from django.db import transaction
from rest_framework import serializers

from store.models import (Customer, Instalment, Order, OrderItem, Product,
                          Subscription)


class BaseProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price_supplier', 'price_consumer']


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'inventory', 'slug',
                  'price_supplier', 'price_consumer']


class BaseCustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name']


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'first_name', 'last_name',
                  'is_consumer', 'email', 'phone_number', 'birth_date', 'image']


class SubscriptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Subscription
        fields = fields = ['id', 'quantity', 'customer', 'product']


class SubscriptionSerializer(serializers.ModelSerializer):
    customer = BaseCustomerSerializer()
    product = BaseProductSerializer()

    class Meta:
        model = Subscription
        fields = ['id', 'quantity', 'customer', 'product']


class OrderItemCreateSeriazer(serializers.ModelSerializer):
    unit_price = serializers.IntegerField(read_only=True)
    quantity_subscribed = serializers.IntegerField(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price',
                  'product', 'quantity_subscribed', 'retour']

    def save(self, **kwargs):
        subscription = Subscription.objects \
            .filter(customer_id=self.context['customer_id'], product_id=self.validated_data['product'].id) \
            .first()
        self.instance = OrderItem.objects.create(
            order_id=self.context['order_id'],

            unit_price=self.validated_data['product'].price_consumer
            if self.context['is_consumer']
            else self.validated_data['product'].price_supplier,

            product=self.validated_data['product'],
            quantity=self.validated_data['quantity'],
            quantity_subscribed=subscription.quantity if subscription else 0,
            retour=self.validated_data['retour']
        )
        return self.instance


class OrderItemUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = ['quantity', 'retour']


class OrderItemSerializer(serializers.ModelSerializer):
    unit_price = serializers.IntegerField(read_only=True)
    product = BaseProductSerializer()
    total_price = serializers.SerializerMethodField()

    def get_total_price(self, item: OrderItem):
        return item.unit_price * (item.quantity - item.quantity_subscribed - item.retour)

    class Meta:
        model = OrderItem
        fields = ['id', 'quantity', 'unit_price',
                  'product', 'quantity_subscribed', 'retour', 'total_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)
    customer = CustomerSerializer()
    total_price = serializers.SerializerMethodField()
    amount_remaining = serializers.SerializerMethodField()

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'customer',
                  'items', 'amount_paid', 'total_price', 'amount_remaining']

    def get_total_price(self, order: Order):
        return sum([
            item.unit_price *
            (item.quantity - item.quantity_subscribed - item.retour)
            for item in order.items.all()
        ])

    def get_amount_remaining(self, order: Order):
        return self.get_total_price(order) - order.amount_paid


class OrderUpdateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Order
        fields = ['amount_paid']


class OrderCreateSerializer(serializers.ModelSerializer):
    items = OrderItemCreateSeriazer(many=True)

    class Meta:
        model = Order
        fields = ['customer', 'items', 'placed_at']

    def save(self, **kwargs):
        with transaction.atomic():
            validated_data = self.validated_data

            customer = validated_data['customer']

            order = Order.objects \
                .filter(customer=customer, placed_at=validated_data['placed_at']) \
                .first()

            if order is None:
                order = Order.objects.create(
                    customer_id=customer.id,
                    placed_at=validated_data['placed_at']
                )

            order_items = []
            for item in validated_data['items']:
                subscription = Subscription.objects \
                    .filter(customer_id=customer.id, product_id=item['product'].id) \
                    .first()
                order_items.append(
                    OrderItem(
                        order=order,
                        product=item['product'],

                        unit_price=item['product'].price_consumer
                        if customer.is_consumer
                        else item['product'].price_supplier,

                        quantity=item['quantity'],
                        quantity_subscribed=subscription.quantity if subscription else 0,
                        retour=item.retour
                    )
                )

            OrderItem.objects.bulk_create(order_items)

            return order


class InstalmentSerializer(serializers.ModelSerializer):
    customer = BaseCustomerSerializer()

    class Meta:
        model = Instalment
        fields = ['id', 'customer', 'amount', 'date']


class InstalmentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Instalment
        fields = ['customer', 'amount', 'date']
