from django.shortcuts import render
from django.db.models import Q, F
from store.models import Product, Subscription
from django.db.models.aggregates import Count

# Create your views here.


def say_hello(request):
    # Product subscribed
    result = Subscription.objects.aggregate(count=Count('id'))
    queryset = Subscription.objects.annotate(
        amount=F('quantity') * F('product__price_customer') * 3).select_related(
        'product').select_related('customer').order_by('quantity').all()

    return render(
        request, 'hello.html',
        context={'subscriptions': list(
            queryset), 'result': result}
    )
