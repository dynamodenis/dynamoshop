from django.db import models
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model
from django_countries.fields import CountryField
from django.shortcuts import reverse
from django_countries.fields import CountryField
from django.dispatch import receiver
# Create your models here.

User = get_user_model()
# Select boxes
CATEGORY_CHOICES=(
    ('S','Shirt'),
    ('SW','Sport Wear'),
    ('OW','Outwear'),
    ('E', 'Electronic')
)

LABEL_CHOICES = (
    ('P', 'primary'),
    ('S', 'secondary'),
    ('D', 'danger')
)

ADDRESS_CHOICES = (
    ('B','Billing'),
    ('S', 'Shipping')
)
# Create the item class
class Item(models.Model):
    title = models.CharField(max_length=100)
    price = models.FloatField()
    discount_price = models.FloatField(blank=True, null = True)
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=2)
    label = models.CharField(choices=LABEL_CHOICES, max_length=1)
    slug = models.SlugField()
    description = models.TextField()
    image = models.ImageField(blank=True, upload_to='images/')
    
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse("product:product_detail", kwargs={
            'slug':self.slug
        })
        
    def get_add_to_cart(self):
        return reverse("product:add-to-cart", kwargs={
            'slug':self.slug
        })
        
    def remove_item_from_cart(self):
        return reverse("product:remove_item_from_cart", kwargs={
            'slug':self.slug
        })

#Create OrderItem()
class OrderItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ordered = models.BooleanField(default=False)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    
    def __str__(self):
        return f"{self.quantity} of {self.item.title}"
    
    def get_total_price(self):
        return self.quantity * self.item.price
    
    def get_total_discount_price(self):
        return self.quantity * self.item.discount_price
    
    # Get the user total savings on an item
    def get_savings(self):
        return self.get_total_price() - self.get_total_discount_price()
    
    # Get the total price for an item either discounted or priced
    def get_final_price(self):
        if self.item.discount_price:
            return self.get_total_discount_price()
        return self.get_total_price()
    
# Create the actual complete order of ordered items
class Order(models.Model):
    user = models.ForeignKey(User,
                             on_delete=models.CASCADE)
    ref_code = models.CharField(max_length=20, blank=True, null=True)
    items = models.ManyToManyField(OrderItem)
    start_date = models.DateTimeField(auto_now_add=True)
    ordered_date = models.DateTimeField()
    ordered = models.BooleanField(default=False)
    billing_address = models.ForeignKey('Address', related_name='billing_address', on_delete=models.SET_NULL, null=True, blank=True)
    shipping_address = models.ForeignKey('Address', related_name='shipping_address', on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, null=True, blank=True)
    being_delivered = models.BooleanField(default=False)
    received = models.BooleanField(default=False)
    refund_requested = models.BooleanField(default=False)
    refund_granted = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    # Get the total price of all your order
    def get_order_price(self):
        total=0
        for order_item in self.items.all():
            final_price = order_item.get_final_price()
            total  += final_price
        # Subtract the total from the coupon
        if self.coupon:
            total-=self.coupon.amount
        return total
    
    
# Billing address
class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    street_address = models.CharField(max_length=100)
    appartment_address = models.CharField(max_length=100, blank=True)
    country = CountryField(multiple=False)
    zip=models.CharField(max_length=100)
    address_type = models.CharField(max_length=2, choices=ADDRESS_CHOICES)
    default = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name_plural = 'Addresses'

# Payment method
class Payment(models.Model):
    stripe_charge_id = models.CharField(max_length=50)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, blank = True, null = True)
    timestamp = models.DateTimeField(auto_now_add=True)
    amount = models.FloatField()
    
    def __str__(self):
        return self.user.username

class Coupon(models.Model):
    code = models.CharField(max_length=50)
    amount = models.FloatField(default=0.0)
    
    def __str__(self):
        return  self.code
    
class Refund(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    reason = models.TextField()
    accepted = models.BooleanField(default=False)
    email = models.EmailField()
    
    def __str__(self):
        return self.order.user.username
        
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=50, blank=True, null=True)
    one_click_purchasing = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.username
    


@receiver(post_save,sender=User)
def create_profile(sender,instance,created,**kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        
@receiver(post_save,sender=User)
def save_profile(sender,instance,**kwargs):
    instance.userprofile.save()