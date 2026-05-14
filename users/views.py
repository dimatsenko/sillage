from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from .forms import CustomUserCreationForm, UserProfileUpdateForm
from django.contrib import messages

def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Реєстрація пройшла успішно!')
            return redirect('core-home') # Will create a dummy home url later
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/register.html', {'form': form})

class CustomLoginView(LoginView):
    template_name = 'users/login.html'
    redirect_authenticated_user = True
    
    def get_success_url(self):
        return reverse_lazy('core-home') # Default redirect after login

class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('users:login')

@login_required
def profile_view(request):
    orders = request.user.orders.all().prefetch_related('items__product')
    return render(request, 'users/profile.html', {'orders': orders})

@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        form = UserProfileUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Ваші дані успішно оновлено!')
            return redirect('users:profile')
    else:
        form = UserProfileUpdateForm(instance=request.user)
    return render(request, 'users/profile_edit.html', {'form': form})

