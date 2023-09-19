from django.contrib import admin

from store.models import Customer, Product, Subscription

# Register your models here.


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price_supplier',
                    'price_consumer', 'inventory_status']
    list_per_page = 10

    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory < 10:
            return 'LOW'
        return 'OK'


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name',
                    'phone_number', 'birth_date', 'email']
    list_per_page = 10
    search_fields = ['first_name', 'last_name']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['customer', 'product', 'quantity']
    list_per_page = 10
