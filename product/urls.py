from django.urls import path,include
from .views import *
from django.conf import settings
from django.conf.urls.static import static

app_name="product"
urlpatterns = [
    path('',HomeView.as_view(), name="product_list"),
    path('checkout/', Checkout.as_view(), name='checkout'),
    path('product_detail/<slug>/', ProductDetailView.as_view(), name='product_detail'),
    path('add-to-cart/<slug>/', add_to_cart, name="add-to-cart"),
    path('add-single-item/<slug>/', add_single_item_cart, name="add_single_item_cart"),
    path('remove_item_from_cart/<slug>', remove_item_from_cart, name='remove_item_from_cart'),
    path('remove-item/<slug>/', remove_single_item_from_cart, name="remove-single-item"),
    path('order-summary/', OrderSummary.as_view(), name="order-summary"),
    path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    path('coupon/', ADD_COUPON.as_view(), name="coupon"),
    path('request-refund/', RequestRefund.as_view(),name='request_refund'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.MEDIA_ROOT)
