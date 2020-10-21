from django import forms
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget

PAYMENT_CHOICES = (
    ('S', 'Stripe'),
    ('P', 'PayPal')
)
class CheckoutForm(forms.Form):
    # Shipping Fields
    shipping_address = forms.CharField(required=False)
    shipping_address2 = forms.CharField(required=False)
    shipping_country = CountryField(blank_label='select country').formfield( required = False, widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100 form-control',
    }))
    shipping_zip=forms.CharField(required=False)
    same_billing_address = forms.BooleanField( required=False)
    set_default_shipping = forms.BooleanField( required=False)
    use_default_shipping = forms.BooleanField( required=False)
    
    # Billing Fields
    billing_address = forms.CharField(required=False)
    billing_address2 = forms.CharField(required=False)
    billing_country = CountryField(blank_label='select country').formfield( required = False, widget=CountrySelectWidget(attrs={
        'class':'custom-select d-block w-100 form-control',
    }))
    billing_zip=forms.CharField(required=False)
    same_shipping_address = forms.BooleanField( required=False)
    set_default_billing = forms.BooleanField( required=False)
    use_default_billing = forms.BooleanField( required=False)
    
    payment_options = forms.ChoiceField(widget=forms.RadioSelect, choices=PAYMENT_CHOICES)
    
# coupon form
class CouponForm(forms.Form):
    code = forms.CharField(widget = forms.TextInput(attrs={
        'class':'form-control',
        'placeholder':'Promo Code',
        'aria-label':"Recipient's username", 
        'aria-describedby':"basic-addon2"
    }))
    
# Request refunds
class RequestRefundForm(forms.Form):
    ref_code = forms.CharField(widget = forms.TextInput(attrs={
        'class':'form-control'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class':'md-textarea form-control',
        'rows':2
    }))
    email = forms.EmailField(widget = forms.TextInput(attrs={
        'class':'form-control'
    }))
    

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)