from django.db import models
from django.contrib.auth.models import User


from django.core.validators import RegexValidator
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

class Customer(models.Model):
    customer_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    address = models.TextField()
    
    # Phone number validation
    phone_number = models.CharField(
        max_length=20,
        validators=[RegexValidator(
            regex=r'^\+?1?\d{9,15}$',
            message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
        )]
    )

    # Email address validation (requires @ symbol)
    email_address = models.EmailField(
        max_length=100,
        unique=True,
        validators=[RegexValidator(
            regex=r'^[\w\.-]+@[\w\.-]+\.\w{2,}$',
            message="Please enter a valid email address with '@'."
        )]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


from django.db import models
from datetime import timedelta
from django.utils import timezone

class Package(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)
    estimated_delivery_date = models.DateField(blank=True, null=True)  # New field for estimated delivery date

    def save(self, *args, **kwargs):
        # Calculate estimated delivery date based on package type
        if self.type == self.Type.PERISHABLE:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=1)
        elif self.type == self.Type.LIVE:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=2)
        elif self.type == self.Type.PRIORITY:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=3)
        elif self.type == self.Type.FRAGILE:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=5)
        elif self.type == self.Type.BULK:
            self.estimated_delivery_date = timezone.now().date() + timedelta(days=7)

        super().save(*args, **kwargs)  # Call the original save method

    def __str__(self):
        return f"{self.package_id}"


class Transport(models.Model):
    transport_id = models.AutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=50)
    max_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    number_plate = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    #for trigger:
    current_load = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Curr

    def __str__(self):
        return f"Transport {self.number_plate} - Driver: {self.driver_name}"


class AvailableTransport(models.Model):
    transport_id = models.AutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=50)
    max_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    number_plate = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    #for trigger:
    current_load = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Curr

    def __str__(self):
        return f"Transport {self.number_plate} - Driver: {self.driver_name}"


class InTransitTransport(models.Model):
    transport_id = models.AutoField(primary_key=True)
    vehicle_type = models.CharField(max_length=50)
    max_capacity = models.DecimalField(max_digits=10, decimal_places=2)
    number_plate = models.CharField(max_length=20, unique=True)
    driver_name = models.CharField(max_length=100)
    #for trigger:
    current_load = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # Curr

    def __str__(self):
        return f"Transport {self.number_plate} - Driver: {self.driver_name}"


class Warehouse(models.Model):
    warehouse_id = models.AutoField(primary_key=True)
    warehouse_name = models.TextField(max_length=100)
    address = models.TextField()

    def __str__(self):
        return self.warehouse_id

class Route(models.Model):
    route_id = models.AutoField(primary_key=True)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    start_location = models.CharField(max_length = 100)
    end_location = models.CharField(max_length=100)

    class route_type(models.TextChoices):
        DISPATCHTOWAREHOUSE = 'DTW'
        WAREHOUSETOWAREHOUSE = 'WTW'
        WAREHOUSETODELIVERY = 'WTD'

    type = models.CharField(max_length=70, choices=route_type.choices, default=route_type.WAREHOUSETOWAREHOUSE)
    def __str__(self):
        return f"Route {self.route_id} Transport {self.transport}"
    

class CompletedRoute(models.Model):
    route_id = models.AutoField(primary_key=True)
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    start_location = models.ForeignKey(Warehouse, related_name='start_warehouse', on_delete=models.CASCADE)
    end_location = models.ForeignKey(Warehouse, related_name='end_warehouse', on_delete=models.CASCADE)
    delivery_addresses = models.TextField(blank=True, null=True)  # For final delivery addresses

    class route_type(models.TextChoices):
        DISPATCHTOWAREHOUSE = 'DTW'
        WAREHOUSETOWAREHOUSE = 'WTW'
        WAREHOUSETODELIVERY = 'WTD'

    type = models.CharField(max_length=70, choices=route_type.choices, default=route_type.WAREHOUSETOWAREHOUSE)
    def __str__(self):
        return f"Route {self.route_id} Transport {self.transport}"
    


class PackagesInTransit(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    transport = models.ForeignKey(Transport, on_delete=models.CASCADE)
    warehouse_id = models.ForeignKey(Warehouse, on_delete = models.CASCADE, default = 1)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)

    def __str__(self):
        return f"Package {self.package_id} for {self.customer} )"



class PackagesDelivered(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)

    def __str__(self):
        return f"Package {self.package_id} for {self.customer} )"



class PackagesInSystem(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)

    def __str__(self):
        return f"Package {self.package_id} for {self.customer}"


class PackageStatus(models.Model):
    class StatusType(models.TextChoices):
        REGISTERED = 'Registered'
        DELIVEREDTOWAREHOUSE = 'Delivered to Warehouse'
        LOST = 'Lost'
        DAMAGED = 'Damaged'
        DELIVEREDTOFINAL = 'Delivery Complete'
        
    # Foreign key to the Package model
    package = models.ForeignKey('Package', on_delete=models.CASCADE, related_name='packagestatus_set')
    
    status_date = models.DateField(auto_now_add=True)
    location = models.CharField(max_length=200)
    status = models.CharField(max_length=70, choices=StatusType.choices, default=StatusType.REGISTERED)

    def __str__(self):
        return f"Package {self.package.package_id} at Location {self.location} on {self.status_date}"


class DeliveredPackages(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.package_id}"


class DamagedOrLostPackages(models.Model):
    class Type(models.TextChoices):
        FRAGILE = 'FR', 'Fragile'
        BULK = 'BK', 'Bulk'
        PRIORITY = 'PR', 'Priority'
        PERISHABLE = 'PE', 'Perishable'
        LIVE = 'LI', 'Live'

    package_id = models.AutoField(primary_key=True) 
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    type = models.CharField(max_length=70, choices=Type.choices, default=Type.FRAGILE)
    weight = models.FloatField()
    height = models.FloatField()
    width = models.FloatField()
    length = models.FloatField()
    dispatch_location = models.CharField(max_length=255)
    delivery_location = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.package_id}"
