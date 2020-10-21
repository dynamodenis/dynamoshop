from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm

User = get_user_model()
class RegisterUser(UserCreationForm):
    def __init__(self,*args,**kwargs):
        super(RegisterUser,self).__init__(*args,**kwargs)
        for fieldname in ['username','email','password1']:
            self.fields[fieldname].help_text=None
            
    email=forms.EmailField()
    
    class Meta:
        model=User
        fields=['username','email','password1']