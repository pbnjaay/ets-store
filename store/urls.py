from django.urls import path, include
from . import views
from rest_framework_nested.routers import DefaultRouter, NestedDefaultRouter

router = DefaultRouter()

router.register('subscriptions', views.SubscriptionViewSet,
                basename='subscription')
router.register('products', views.ProductViewSet, basename='product')
router.register('customers', views.CostumerViewSet, basename='customer')
router.register('orders', views.OrderViewSet, basename='order')
router.register('instalments', views.InstalmentViewSet, basename='instalment')
orders_router = NestedDefaultRouter(router, 'orders', lookup='order')
orders_router.register('items', views.OrderItemViewSet, basename='order-items')


urlpatterns = router.urls + orders_router.urls
