from django import forms
from .models import Customer, Package, Transport
from django import forms
from django.core.validators import RegexValidator
from .models import Customer

class CustomerForm(forms.ModelForm):
    phone_number = forms.CharField(
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )

    class Meta:
        model = Customer
        fields = ['first_name', 'last_name', 'address', 'phone_number', 'email_address']


class PackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['customer', 'type', 'weight', 'height', 'width', 'length', 'dispatch_location', 'delivery_location']


class TransportForm(forms.ModelForm):
    class Meta:
        model = Transport
        fields = ['vehicle_type', 'max_capacity', 'number_plate', 'driver_name']


class AdminLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomerLoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class CustomerSignupForm(forms.Form):
    username = forms.CharField(max_length=150)
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            raise forms.ValidationError("Passwords do not match.")
        return cleaned_data


class TransportLoginForm(forms.Form):
    number_plate = forms.CharField(max_length=15)
    driver_name = forms.CharField(max_length=100)

class NewPackageForm(forms.ModelForm):
    class Meta:
        model = Package
        fields = ['type','weight','height','width','length','dispatch_location', 'delivery_location'] 
        type = forms.ChoiceField(choices=Package.Type.choices, label='Package Type') # Customize the fields as needed

class NewTransportForm(forms.Form):
    class Meta: 
        model = Transport
        fields = ['vehicle_type','max_capacity','number_plate','driver_name']
