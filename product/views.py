from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from .models import *
from django.views.generic import ListView,DetailView, View
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import CheckoutForm, CouponForm, RequestRefundForm, PaymentForm
import stripe
import string
import random

# regiater stripe
stripe.api_key = settings.STRIPE_API_KEY

# create a refrence code
def create_ref_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=15))

# Validating the checkout forms if they are valid or not
def is_valid_form(values):
    valid = True
    for field in values:
        if field == "":
            valid = False
    return valid



# Create your views here.
class HomeView(ListView):
    # items = Item.objects.all()
    model = Item
    paginate_by=10
    template_name = 'product/home-page.html'


class Checkout(View):
    def get(self, *args, **kwargs):
        form = CheckoutForm()
        coupon_form = CouponForm()
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {'form':form, 'order':order, 'coupon_form':coupon_form}
            # get the shippng address
            shipping_address_qs = Address.objects.filter(user = self.request.user, address_type = 'S', default=True)
            if shipping_address_qs.exists():
                context.update({'default_shipping_address': shipping_address_qs[0]})
            
            # Billing address
            billing_address_qs = Address.objects.filter(user = self.request.user, address_type = 'B', default=True)
            if billing_address_qs.exists():
                context.update({'default_billing_address': billing_address_qs[0]})
            return render(self.request, "product/checkout-page.html", context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "No active order.")
            return redirect("product:product_list")
    
    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():
                # -------------------------SHIPPING ADDRESS --------------------------------
                use_default_shipping = form.cleaned_data.get("use_default_shipping")
                if use_default_shipping:
                    print("Using the default shipping address")
                    address_qs = Address.objects.filter(user = self.request.user, address_type = 'S', default=True)
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(self.request, "No default shipping address available.")
                        return redirect("product:checkout")
                    
                else:
                    print("The user is inputting a shipping address")
                    
                    shipping_address = form.cleaned_data.get("shipping_address")
                    shipping_address2 = form.cleaned_data.get("shipping_address2")
                    shipping_country = form.cleaned_data.get("shipping_country")
                    shipping_zip = form.cleaned_data.get("shipping_zip")
                    
                    # same_billing_address = form.cleaned_data.get("same_billing_address")
                    # save_info = form.cleaned_data.get("save_info")
                    if is_valid_form([shipping_address, shipping_country, shipping_zip]):                 
                        shipping_address = Address(
                            user = self.request.user,
                            street_address = shipping_address,
                            appartment_address = shipping_address2,
                            country = shipping_country,
                            zip = shipping_zip,
                            address_type = 'S'
                        )
                        shipping_address.save()
                        
                        order.shipping_address = shipping_address
                        order.save()
                        # Set the default shipping address to true
                        set_default_shipping = form.cleaned_data.get("set_default_shipping")
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()
                                
                    else:
                        messages.info(self.request, "Please select the required address fields.")
                        
                        
                # ----------------------------BILLING ADDRESS -----------------------------
                 
                use_default_billing = form.cleaned_data.get("use_default_billing")
                same_billing_address = form.cleaned_data.get("same_billing_address")
                
                # If the billing address is the same as the shipping
                if same_billing_address:
                    billing_address = shipping_address
                    billing_address.pk = None
                    billing_address.save()
                    billing_address.address_type = 'B'
                    billing_address.save()
                    order.billing_address = billing_address
                    order.save()
                    
                # If the default is set
                elif use_default_billing:
                    print("Using the default billing address")
                    address_qs = Address.objects.filter(user = self.request.user, address_type = 'B', default=True)
                    if address_qs.exists():
                        billing_address = address_qs[0]
                        order.billing_address = billing_address
                        order.save()
                    else:
                        messages.info(self.request, "No default billing address available.")
                        return redirect("product:checkout")
                    
                else:
                    print("The user is inputting a billing address")
                    
                    billing_address = form.cleaned_data.get("billing_address")
                    billing_address2 = form.cleaned_data.get("billing_address2")
                    billing_country = form.cleaned_data.get("billing_country")
                    billing_zip = form.cleaned_data.get("billing_zip")
                    
                    # same_billing_address = form.cleaned_data.get("same_billing_address")
                    # save_info = form.cleaned_data.get("save_info")
                    if is_valid_form([billing_address, billing_country, billing_zip]):                 
                        billing_address = Address(
                            user = self.request.user,
                            street_address = billing_address,
                            appartment_address = billing_address2,
                            country = billing_country,
                            zip = billing_zip,
                            address_type = 'B'
                        )
                        billing_address.save()
                        
                        order.billing_address = billing_address
                        order.save()
                        # Set the default billing address to true
                        set_default_billing = form.cleaned_data.get("set_default_billing")
                        if set_default_billing:
                            billing_address.default = True
                            billing_address.save()
                                
                    else:
                        messages.info(self.request, "Please select the required address fields.")
                
                    
                payment_options = form.cleaned_data.get("payment_options")
                    
                # Checck the payment option
                if payment_options == 'S':
                    return redirect("product:payment", payment_option="stripe")
                elif payment_options =='P':
                    return redirect("product:payment", payment_option="paypal")
                
                else:
                    
                    messages.error(self.request,"Invalid Payment Option Selected")
                return redirect("product:checkout")
        except ObjectDoesNotExist:
            messages.error(self.request, "You dont have any order to process")
            return redirect("product:order-summary")
            
class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        if order.billing_address:
            return render(self.request, 'product/payment.html', {'order':order})
        else:
            messages.warning(self.request, "You dont have a billing address")
            return redirect("product:checkout")
    
    def post(self, *args, **kwargs):
        # GET the order
        order = Order.objects.get(user = self.request.user, ordered = False)
        token= self.request.POST.get("stripeToken")
        # form = PaymentForm(self.request.POST)
        userprofile = UserProfile.objects.get(user = self.request.user)
        
        # Handling Error
        try:
            # Use Stripe's library to make requests...
            charge = stripe.Charge.create(
                amount = int(order.get_order_price() * 100),
                currency='usd',
                
                source=token,
                )
            
            # Create the Payment
            payment = Payment()
            payment.stripe_charge_id = charge['id']
            payment.user = self.request.user
            payment.amount = order.get_order_price()
            payment.save()
            
            # After your payment is successful now u need to set the ordered in the order_item to true and save to clear that item
            order_items = order.items.all()
            order_items.update(ordered = True)
            for item in order_items:
                item.save()
            
            # Set the ordered to true,process payment and clear the order
            order.ordered = True;
            order.payment_method = payment
            order.ref_code = create_ref_code()
            order.save()
            
            messages.success(self.request, "Order Successfully Proccesed")
            return redirect("product:product_list")
        
        except stripe.error.CardError as e:
            # Since it's a decline, stripe.error.CardError will be caught
            body = e.json_body
            err = body.get('error',{})
            return redirect("product:checkout")
           
            messages.error(self.request, f"{err.get(message)}")
            print('Status is: %s' % e.http_status)
            print('Type is: %s' % e.error.type)
            print('Code is: %s' % e.error.code)
            # param is '' in this case
            print('Param is: %s' % e.error.param)
            print('Message is: %s' % e.error.message)
        except stripe.error.RateLimitError as e:
            # Too many requests made to the API too quickly
            messages.error(self.request, "Rate Limit Error")
            return redirect("product:checkout")
            
        except stripe.error.InvalidRequestError as e:
            # Invalid parameters were supplied to Stripe's API
            messages.error(self.request, "Invalid Request")
            return redirect("product:checkout")
            
        except stripe.error.AuthenticationError as e:
            # Authentication with Stripe's API failed
            # (maybe you changed API keys recently)
            messages.error(self.request, "Authentication Error")
            return redirect("product:checkout")
            
        except stripe.error.APIConnectionError as e:
            # Network communication with Stripe failed
            messages.error(self.request, "Network Error")
            return redirect("product:checkout")
            
        except stripe.error.StripeError as e:
            # Display a very generic error to the user, and maybe send
            # yourself an email
            
            messages.error(self.request, "Something went wrong. Please try again!")
            return redirect("product:checkout")
            
        except Exception as e:
            # Something else happened, completely unrelated to Stripe
            messages.error(self.request, "Something went wrong. We have been notified and working on it")
            return redirect("product:checkout")
            
    
# def product_detail(request):
#     return render(request, "product/product-page.html")
# ------------Product Detail View
class ProductDetailView(DetailView):
    model = Item
    template_name="product/product-page.html"
    
    
# add an item to cart
@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # Create an order item from the item
    order_item, created = OrderItem.objects.get_or_create(item = item, user=request.user, ordered=False)
    # get the order of the user
    order_query= Order.objects.filter(user= request.user, ordered=False)
    
    if order_query.exists():
        order = order_query[0]
        # Check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            
        else:
            order.items.add(order_item)
    # If no order yet create one 
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        
    return redirect('product:product_detail', slug=slug)

# Add single item from cart
@login_required
def add_single_item_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # Create an order item from the item
    order_item, created = OrderItem.objects.get_or_create(item = item, user=request.user, ordered=False)
    # get the order of the user
    order_query= Order.objects.filter(user= request.user, ordered=False)
    
    if order_query.exists():
        order = order_query[0]
        # Check if the orderitem is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            return redirect('product:order-summary')

        else:
            order.items.add(order_item)
            return redirect('product:oder-summary')

    # If no order yet create one 
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user=request.user, ordered_date = ordered_date)
        order.items.add(order_item)
        
        return redirect('product:order-summary')

# Remove items from cart
@login_required
def remove_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if you have an order
    order_query= Order.objects.filter(user = request.user, ordered= False)
    
    if order_query.exists():
        order = order_query[0]
        # check if the order contains any of the order items
        if order.items.filter(item__slug=item.slug).exists():
            # get the item
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            # remove the order item from order
            order.items.remove(order_item)
            order_item.delete()
            messages.info(request, "The item was removed from your order")
            return redirect("product:order-summary")
        else:
            messages.info(request, "The item does not exist in your order!")
            return redirect("product:product_detail", slug=slug)
        
    else:
        messages.info(request, "You don't have any active order")
        return redirect("product:product_detail", slug=slug)

# ADD single item

   
#Remove single item from cart
@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    # check if you have an order
    order_query= Order.objects.filter(user = request.user, ordered= False)
    
    if order_query.exists():
        order = order_query[0]
        # check if the order contains any of the order items
        if order.items.filter(item__slug=item.slug).exists():
            # get the item
            order_item = OrderItem.objects.filter(item=item, user=request.user, ordered=False)[0]
            # remove the order item from order
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            messages.info(request, "The item was removed from your order")
            return redirect("product:order-summary")
        else:
            messages.info(request, "The item does not exist in your order!")
            return redirect("product:product_detail", slug=slug)
        
    else:
        messages.info(request, "You don't have any active order")
        return redirect("product:product_detail", slug=slug)
            
            
# Create an order summary that is the cart
class OrderSummary(LoginRequiredMixin, View):
    def get(self, *args, **kwargs ):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            return render(self.request, "product/order-summary.html", {'order':order})
        
        except ObjectDoesNotExist:
            messages.error(self.request, "You dont have any cart!")
            return redirect("/")
        
def get_coupon(request, code):
    try:
        coupon = Coupon.objects.get(code = code)
        return coupon
    except ObjectDoesNotExist:
        messages.error(request, "The coupon does not exist, try a new one.")
        return redirect("product:checkout")
    
class ADD_COUPON(View):
    def post(self, *args, **kwargs):
        form = CouponForm(request.POST or None)
        if form.is_valid():
            # check if you have an order
            try:
                code = form.cleaned_data.get("code")
                order = Order.objects.get(user=request.user, ordered=False)
                coupon = get_coupon(request, code)
                # add the coupon to the order
                order.coupon = coupon
                order.save()
                messages.success(request,"Successfully added a coupon")
                return redirect("product:checkout")
            
            except ObjectDoesNotExist:
                messages.error(request, "You dont have any active order!")
                return redirect("product:checkout")

# Manage Refunds
class RequestRefund(View):
    def get(self, *args, **kwargs):
        form = RequestRefundForm()
        return render(self.request, 'product/request-refund.html', {'form':form})
    def post(self, *args, **kwargs):
        form = RequestRefundForm(self.request.POST)
        if form.is_valid():
            ref_code = form.cleaned_data.get('ref_code')
            message = form.cleaned_data.get('message')
            email = form.cleaned_data.get('email')
            # get the order by ref_code
            try:
                order = Order.objects.get(ref_code=ref_code)
                order.refund_requested = True
                order.save()
                
                # Create a refund table
                refund = Refund()
                refund.order = order
                refund.reason = message
                refund.email = email
                refund.save()
                messages.success(self.request, 'Refund was successfully processed.')
                return redirect("product:product_list")
                
            except ObjectDoesNotExist:
                messages.warning(self.request, 'Order does not exist!')
                return redirect("product:request_refund")
                