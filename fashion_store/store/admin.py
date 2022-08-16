from django.contrib import admin
from django.db.models import Sum, DateTimeField, Min, Max
from django.db.models.functions import Trunc

from .models import *

admin.site.register(Category)
admin.site.register(Customer)
# admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Payment)
admin.site.register(ShippingAddress)
admin.site.register(Testimonials)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    change_form_template = "admin/product_management.html"

@admin.register(OrderSummary)
class OrderSummaryAdmin(admin.ModelAdmin):
    change_list_template = 'admin/sale_summary_change_list.html'
    date_hierarchy = 'paymentOrder__datePayment'

    def changelist_view(self, request, extra_context=None):
        response = super().changelist_view(
            request,
            extra_context=extra_context,
        )

        try:
            qs = response.context_data['cl'].queryset
        except (AttributeError, KeyError):
            return response

        metrics = {
            'total': Sum('itemOrdered__totalProductOrder'),
            'total_sales': Sum('paymentOrder__pricePayment'),
        }

        response.context_data['summary'] = list(
            qs
            .values('itemOrdered__transactionOrder', 'paymentOrder__datePayment', 'itemOrdered__id', 'paymentOrder__methodPayment')
            .annotate(**metrics)
            .order_by('-paymentOrder__datePayment')
        )

        response.context_data['summary_total'] = dict(
            qs.aggregate(**metrics)
        )

        return response
