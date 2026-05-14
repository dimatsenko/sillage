import pytest
from django.urls import reverse
from .models import CustomUser

@pytest.mark.django_db
def test_create_custom_user():
    user = CustomUser.objects.create_user(
        username='testuser', 
        email='test@example.com', 
        password='testpassword123',
        phone_number='+380501234567'
    )
    assert user.username == 'testuser'
    assert user.email == 'test@example.com'
    assert user.phone_number == '+380501234567'
    assert user.check_password('testpassword123') is True

@pytest.mark.django_db
def test_login_view(client):
    user = CustomUser.objects.create_user(
        username='testuser', 
        password='testpassword123'
    )
    url = reverse('users:login')
    response = client.post(url, {'username': 'testuser', 'password': 'testpassword123'})
    
    # Check if redirect happened to the core-home (login success)
    assert response.status_code == 302
    assert response.url == reverse('core-home')
    
    # Logout before next test
    client.logout()
    
    # Check if login fails with wrong password
    response_fail = client.post(url, {'username': 'testuser', 'password': 'wrongpassword'})
    assert response_fail.status_code == 200 # stays on login page

@pytest.mark.django_db
def test_register_view(client):
    url = reverse('users:register')
    data = {
        'username': 'newuser',
        'email': 'new@test.com',
        'phone_number': '123456',
        # UserCreationForm requires pass and pass confirmation, but we will test just a simple GET response first
    }
    response = client.get(url)
    assert response.status_code == 200
    assert 'form' in response.context

