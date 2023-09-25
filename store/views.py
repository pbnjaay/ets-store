from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.filters import SearchFilter
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from store.pagination import DefaultPagination
from store.permissions import IsAdminOrReadOnly

from .models import (Customer, Instalment, Order, OrderItem, Product,
                     Subscription)
from .serializers import (CustomerSerializer, InstalmentCreateSerializer,
                          InstalmentSerializer, OrderCreateSerializer,
                          OrderItemCreateSeriazer, OrderItemSerializer,
                          OrderItemUpdateSerializer, OrderSerializer,
                          OrderUpdateSerializer, ProductSerializer,
                          SubscriptionCreateSerializer, SubscriptionSerializer)


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]


class CostumerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    filter_backends = [SearchFilter]
    search_fields = ['first_name', 'last_name']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]


class SubscriptionViewSet(ModelViewSet):
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer', 'product']
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        queryset = Subscription.objects \
            .select_related('product') \
            .select_related('customer').all()

        product_id = self.request.query_params.get('product_id')

        if product_id is not None:
            queryset = queryset.filter(product_id=product_id)

        return queryset

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return SubscriptionSerializer
        return SubscriptionCreateSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def create(self, request):
        serializer = SubscriptionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        customer_id = serializer.validated_data.get('customer').id
        product_id = serializer.validated_data.get('product').id
        subscription = Subscription.objects \
            .filter(customer__id=customer_id, product__id=product_id) \
            .first()

        if subscription is not None:
            return Response(
                {'detail': 'This customer already has a subscription to this product'},
                status=status.HTTP_409_CONFLICT
            )

        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.prefetch_related('items__product') \
                            .select_related('customer') \
                            .all()

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer']
    pagination_class = DefaultPagination
    serializer_class = OrderCreateSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderSerializer
        elif self.request.method == 'POST':
            return OrderCreateSerializer
        return OrderUpdateSerializer

    def create(self, request, *args, **kwargs):
        serializer = OrderCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)

        return Response(serializer.data)


class OrderItemViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_order(self):
        order = Order.objects \
            .filter(pk=self.kwargs['order_pk']) \
            .select_related('customer').first()

        return order

    def create(self, request, *args, **kwargs):
        order = self.get_order()

        if order is not None:
            serializer = OrderItemCreateSeriazer(
                data=request.data,
                context={
                    'order_id': self.kwargs['order_pk'],
                    'is_consumer': order.customer.is_consumer,
                    'customer_id': order.customer.id
                }
            )
            serializer.is_valid(raise_exception=True)
            order_item = serializer.save()
            serializer = OrderItemSerializer(order_item)

            return Response(serializer.data)

        return Response(
            {'detail': 'This order with the given id does not exist'},
            status=status.HTTP_404_NOT_FOUND
        )

    def list(self, request, *args, **kwargs):
        order = self.get_order()
        if order is not None:
            queryset = OrderItem.objects \
                .filter(order_id=self.kwargs['order_pk']) \
                .select_related('product') \
                .all()
            serializer = OrderItemSerializer(queryset, many=True)
            return Response(serializer.data)

        return Response(
            {'detail': 'Not found.'},
            status=status.HTTP_404_NOT_FOUND
        )

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return OrderItemSerializer
        elif self.request.method == 'POST':
            return OrderItemCreateSeriazer
        return OrderItemUpdateSerializer

    def get_queryset(self):
        return OrderItem.objects.filter(order_id=self.kwargs['order_pk']).all()


class InstalmentViewSet(ModelViewSet):
    queryset = Instalment.objects.select_related('customer').all()
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['customer']
    pagination_class = DefaultPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return InstalmentSerializer
        return InstalmentCreateSerializer
