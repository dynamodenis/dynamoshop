from django.contrib import admin
from .models import  *
# Register your models here.

admin.site.site_title="DynamoShop"
admin.site.site_header="DynamoShop"

# Create a custom action to change the refund from requested to accepted
def make_refund_accepted(modeladmin, request, queryset):
    queryset.update(refund_granted = True)
make_refund_accepted.short_description = "Update Refund To Accepted"

class OrderAdmin(admin.ModelAdmin):
    list_display = ['user', 'ordered','being_delivered', 'received', 'refund_requested', 'refund_granted', 'billing_address', 'shipping_address', 'payment_method','coupon']
    list_filter = ['ordered','being_delivered', 'received', 'refund_requested', 'refund_granted']
    # this creates links to the list wth foreign keys
    list_display_links = ['billing_address','shipping_address',  'payment_method','coupon']
    # search by
    search_fields = ['user__username','ref_code']
    # register your custom actions make_refund_accepted
    actions = [make_refund_accepted]
    
class AddressAdmin(admin.ModelAdmin):
    list_display = ['user','street_address','appartment_address', 'country', 'zip', 'address_type', 'default']
    list_filter = ['default', 'address_type','country']
    search_fields = ['user', 'street_address', 'appartment_address', 'zip']
    
admin.site.register(Item)
admin.site.register(OrderItem)
admin.site.register(Order, OrderAdmin)
admin.site.register(Payment)
admin.site.register(Coupon)
admin.site.register(Refund)
admin.site.register(Address, AddressAdmin)
admin.site.register(UserProfile)