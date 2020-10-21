from django.shortcuts import render, redirect
from .forms import RegisterUser
from django.contrib import messages


# Create your views here.
def register(request):
    if request.method == 'POST':
        form = RegisterUser(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data["username"]
            messages.success(request,"Account under "+ username + " has been successfully registered.")
            return redirect('accounts:login')
    else:
        form = RegisterUser()
            
    return render(request, 'account/register.html', {'form':form})