from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import CustomerForm, NewPackageForm, CustomerSignupForm, NewTransportForm, PackageForm, TransportForm, AdminLoginForm, NewTransportForm, TransportLoginForm
from .models import Customer, Package, DamagedOrLostPackages, DeliveredPackages, Transport, AvailableTransport, InTransitTransport,User, PackageStatus, Warehouse, Route, PackagesInSystem, PackagesDelivered, PackagesInTransit
from django.views.decorators.csrf import csrf_exempt

from tracking import models



def index(request):
    return render(request, 'tracking/index.html')


# Utility function to handle user login
def handle_login(request, form_class, redirect_url, error_message):
    if request.method == 'POST':
        form = form_class(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect(redirect_url)
            else:
                return render(request, 'tracking/login.html', {'form': form, 'error': error_message})
    else:
        form = form_class()
    return render(request, 'tracking/login.html', {'form': form})


# Add Package View
def add_package(request):
    if request.method == "POST":
        form = NewPackageForm(request.POST)  # Use NewPackageForm for the form
        if form.is_valid():
            package = form.save()  # Save the package instance
            # Automatically create an entry in PackagesInSystem
            PackagesInSystem.objects.create(package=package)
            original_package = Package.objects.get(package = package)
            PackageStatus.objects.create(
                package_id=original_package.package_id,
                location='Registered'
            )
            return redirect('package_list')  # Redirect to the package list

        else:
            return render(request, 'tracking/add_package.html', {'form': form, 'error': 'Form submission failed.'})
    else:
        form = NewPackageForm()  # Initialize form for GET request
    return render(request, 'tracking/add_package.html', {'form': form}) 

# Add Transport View
def add_transport(request):
    if request.method == "POST":
        form = TransportForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('transport_list')
        else:
            return render(request, 'tracking/add_transport.html', {'form': form, 'error': 'Form submission failed.'})
    else:
        form = TransportForm()
    return render(request, 'tracking/add_transport.html', {'form': form})

# Add Customer View
def add_customer(request):
    if request.method == "POST":
        form = CustomerForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_list')
        else:
            return render(request, 'tracking/add_customer.html', {'form': form, 'error': 'Form submission failed.'})
    else:
        form = CustomerForm()
    return render(request, 'tracking/add_customer.html', {'form': form})


# Admin Login View
@csrf_exempt
def admin_login(request):
    return handle_login(request, AdminLoginForm, 'admin_dashboard', 'Invalid admin credentials.')

# Logout View
def logout_view(request):
    logout(request)
    return redirect('customer_login')

# Admin Dashboard - requires login and admin access

@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        return redirect('admin_login')

    packages = Package.objects.order_by('estimated_delivery_date')
    customers = Customer.objects.all()
    transports = Transport.objects.all()
    packagesintransit = PackagesInTransit.objects.all()
    packagesinsystem = PackagesInSystem.objects.all()
    damagedorlost = DamagedOrLostPackages.objects.all()
    deliveredpackages = DeliveredPackages.objects.all()
    packagestatus = PackageStatus.objects.all()
    available_transports = AvailableTransport.objects.all()
    warehouses = Warehouse.objects.all()
    routes = Route.objects.all()
    intransit_transports = InTransitTransport.objects.all()

    if request.method == 'POST':
        form = NewTransportForm(request.POST)
        if form.is_valid():
            vehicle_type = request.POST.get('vehicle_type')
            max_capacity = request.POST.get('max_capacity')
            number_plate = request.POST.get('number_plate')
            driver_name = request.POST.get('driver_name')

        transport = Transport.objects.create(
            vehicle_type=vehicle_type,
            max_capacity=max_capacity,
            number_plate=number_plate,
            driver_name=driver_name
        )

        AvailableTransport.objects.create(
            vehicle_type=vehicle_type,
            max_capacity=max_capacity,
            number_plate=number_plate,
            driver_name=driver_name
        )

        return redirect('admin_dashboard') # Redirect to the dashboard after successful creation
    else:
        form = NewPackageForm()

    context = {
        'packages': packages,
        'customers': customers,
        'transports': transports,
        'packagesintransit': packagesintransit,
        'packagesinsystem': packagesinsystem,
        'damagedorlost': damagedorlost,
        'deliveredpackages': deliveredpackages,
        'packagestatus': packagestatus,
        'available_transports': available_transports,
        'warehouses': warehouses,
        'routes': routes,
        'intransit_transports': intransit_transports,
        'form': form  # Include the form for new transport
    }

    return render(request, 'tracking/admin_dashboard.html', context)

# Transport Driver Dashboard - requires transport session
def driver_dashboard(request):
    transport_id = request.session.get('transport_id')
    if not transport_id:
        return redirect('transport_login')

    transport = Transport.objects.get(transport_id=transport_id)
    assigned_packages = transport.packagetransport_set.all()

    return render(request, 'tracking/driver_dashboard.html', {'assigned_packages': assigned_packages})


def transport_register(request):
    if request.method == 'POST':
        vehicle_type = request.POST.get('vehicle_type')
        max_capacity = request.POST.get('max_capacity')
        number_plate = request.POST.get('number_plate')
        driver_name = request.POST.get('driver_name')

        transport = Transport.objects.create(
            vehicle_type=vehicle_type,
            max_capacity=max_capacity,
            number_plate=number_plate,
            driver_name=driver_name
        )
        return redirect('admin_dashboard')


def customer_signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        address = request.POST.get('address')
        phone_number = request.POST.get('phone_number')
        email_address = request.POST.get('email_address')

        user = User.objects.create_user(username=username, password=password)
        customer = Customer.objects.create(
            user=user,
            first_name=first_name,
            last_name=last_name,
            address=address,
            phone_number=phone_number,
            email_address=email_address
        )
        login(request, user)
        return redirect('customer_dashboard')

    return render(request, 'tracking/customer_signup.html')

def customer_dashboard(request):
    customer = Customer.objects.get(user=request.user)
    packages = Package.objects.filter(customer=customer)
    transit_packages = PackagesInTransit.objects.filter(customer=customer)
    delivered_packages = DeliveredPackages.objects.filter(customer=customer)
    # Create mappings for package statuses
    package_status_map = {
        package.package_id: PackageStatus.objects.filter(package_id=package.package_id)
        for package in packages
    }
    transit_package_status_map = {
        transit_package.package_id: PackageStatus.objects.filter(package_id=transit_package.package_id)
        for transit_package in transit_packages
    }

    if request.method == 'POST':
        form = NewPackageForm(request.POST)
        if form.is_valid():
            new_package = form.save(commit=False)
            new_package.customer = customer
            new_package.save()
            PackagesInSystem.objects.create(
                package_id=new_package.package_id,  # Use the same package ID
                customer=new_package.customer,
                type=new_package.type,
                weight=new_package.weight,
                height=new_package.height,
                width=new_package.width,
                length=new_package.length,
                dispatch_location=new_package.dispatch_location,
                delivery_location=new_package.delivery_location,
            )

            return redirect('customer_dashboard')  # Redirect to the dashboard after successful creation
    else:
        form = NewPackageForm()

    return render(request, 'tracking/customer_dashboard.html', {
        'packages': packages,
        'form': form,
        'transit_packages': transit_packages,
        'package_status_map': package_status_map,
        'transit_package_status_map': transit_package_status_map,
        'delivered_packages': delivered_packages,
    })


def customer_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('customer_dashboard')  # Redirect after successful login
        else:
            return render(request, 'tracking/customer_login.html', {'error_message': 'Invalid credentials'})

    return render(request, 'tracking/customer_login.html')

from django.shortcuts import render, redirect
from .forms import TransportLoginForm
from .models import Transport
from django.contrib import messages

def transport_login(request):
    if request.method == 'POST':
        form = TransportLoginForm(request.POST)
        if form.is_valid():
            number_plate = form.cleaned_data.get('number_plate')
            driver_name = form.cleaned_data.get('driver_name')

            try:
                # Retrieve the transport instance using the number plate and driver name
                transport = Transport.objects.get(number_plate=number_plate, driver_name=driver_name)

                # Store the number plate in the session for later retrieval
                request.session['number_plate'] = transport.number_plate

                # Redirect to the transport dashboard after successful login
                return redirect('transport_dashboard')

            except Transport.DoesNotExist:
                messages.error(request, "Invalid number plate or driver name.")
                return render(request, 'tracking/transport_login.html', {'form': form})

    else:
        form = TransportLoginForm()

    return render(request, 'tracking/transport_login.html', {'form': form})

from django.shortcuts import render

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Package, Transport, PackageStatus

from .models import Package, Transport, Route, Warehouse
from django.shortcuts import render, redirect
from django.contrib import messages


from django.shortcuts import render, redirect
from .models import Warehouse, Transport, Package, PackagesInTransit, PackagesInSystem
from decimal import Decimal

def assign_route(request):
    return render(request, 'tracking/assign_route.html')  # Template with the three buttons

def assign_warehouse_to_warehouse(request):
    if request.method == 'POST':
        transport_id = request.POST.get('transport_id')
        from_warehouse_name = request.POST.get('from_warehouse_name')
        to_warehouse_name = request.POST.get('to_warehouse_name')
        package_ids = request.POST.getlist('package_ids')

        try:
            # Retrieve Transport instance
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        except AvailableTransport.DoesNotExist:
            messages.error(request, "Invalid transport ID. Please select a valid transport.")
            return redirect('assign_warehouse_to_warehouse')  # Redirect to form

        # Calculate total weight of selected packages
        total_package_weight = float(sum(Package.objects.get(package_id=package_id).weight for package_id in package_ids))

        # Check if assigning packages would exceed max capacity
        if transport_instance.current_load + Decimal(str(total_package_weight)) > transport_instance.max_capacity:
            messages.error(request, 'Assignment failed: Transport load capacity exceeded.')
            return redirect('assign_warehouse_to_warehouse')

        transport_instance.current_load += Decimal(str(total_package_weight))
        transport_instance.save()

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        transport_obj = Transport.objects.get(transport_id=transport_instance.transport_id)
        Route.objects.create(
            transport = transport_obj,
            type = 'WTW',
            end_location = to_warehouse_name,
            start_location = from_warehouse_name,
        )

        for package_id in package_ids:
            # Get the package from PackagesInSystem
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
            warehouse_instance = Warehouse.objects.get(warehouse_name = from_warehouse_name)
            # Access the original Package instance
            original_package = PackagesInSystem.objects.get(package_id = package_id) # This accesses the related Package

            # Add to PackagesInTransit
            PackagesInTransit.objects.create(
                package_id=original_package.package_id, 
                transport_id = transport_instance.transport_id,
                warehouse_id = warehouse_instance.warehouse_id,
                type = original_package.type,
                weight = original_package.weight,
                height = original_package.height,
                width = original_package.width,
                length = original_package.length,
                dispatch_location = original_package.dispatch_location,
                delivery_location = original_package.delivery_location,
                customer = original_package.customer,

            )
            PackageStatus.objects.create(
                package_id=original_package.package_id,
                location=warehouse_instance.warehouse_name,
                #status=PackageStatus.status_type.REGISTERED,

            )

            original_package.delete()  # Deletes the PackagesInSystem entry

    #add to Route
        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        InTransitTransport.objects.create(
            transport_id = transport_instance.transport_id,
            vehicle_type=transport_instance.vehicle_type,
            max_capacity=transport_instance.max_capacity,
            number_plate=transport_instance.number_plate,
            driver_name=transport_instance.driver_name
        )
        transport_instance.delete()



    # Load packages in system, warehouses, and transports for form
    context = {
        'packages': PackagesInSystem.objects.all(),  # Fetch from PackagesInSystem
        'warehouses': Warehouse.objects.all(),
        'transports': AvailableTransport.objects.all()
    }
    return render(request, 'tracking/assign_warehouse_to_warehouse.html', context)




def assign_warehouse_to_delivery(request):
    if request.method == 'POST':
        transport_id = request.POST.get('transport_id')
        warehouse_name = request.POST.get('warehouse_name')
        package_ids = request.POST.getlist('package_ids')

        try:
            # Retrieve Transport instance
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        except AvailableTransport.DoesNotExist:
            messages.error(request, "Invalid transport ID. Please select a valid transport.")
            return redirect('assign_warehouse_to_delivery')  # Redirect to form

        # Calculate total weight of selected packages
        total_package_weight = float(sum(Package.objects.get(package_id=package_id).weight for package_id in package_ids))

        # Check if assigning packages would exceed max capacity
        if transport_instance.current_load + Decimal(str(total_package_weight)) > transport_instance.max_capacity:
            messages.error(request, 'Assignment failed: Transport load capacity exceeded.')
            return redirect('assign_warehouse_to_delivery')

        # Update transport's current load (assuming all packages are assigned successfully)
        transport_instance.current_load += Decimal(str(total_package_weight))
        transport_instance.save()

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        transport_obj = Transport.objects.get(transport_id=transport_instance.transport_id)

        Route.objects.create(
            transport = transport_obj,
            type = 'WTD',
            end_location = 'Delivery',
            start_location = warehouse_name,
        )


        # Move selected packages from PackagesInSystem to P
        for package_id in package_ids:
            # Get the package from PackagesInSystem
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
            warehouse_instance = Warehouse.objects.get(warehouse_name = warehouse_name)
            # Access the original Package instance
            original_package = PackagesInSystem.objects.get(package_id = package_id) # This accesses the related Package

            # Add to PackagesInTransit
            PackagesInTransit.objects.create(
                package_id=original_package.package_id, 
                transport_id = transport_instance.transport_id,
                warehouse_id = warehouse_instance.warehouse_id,
                type = original_package.type,
                weight = original_package.weight,
                height = original_package.height,
                width = original_package.width,
                length = original_package.length,
                dispatch_location = original_package.dispatch_location,
                delivery_location = original_package.delivery_location,
                customer = original_package.customer,

            )
            PackageStatus.objects.create(
                package_id=original_package.package_id,
                location=warehouse_instance.warehouse_name,
                #status=PackageStatus.status_type.REGISTERED,

            )

            original_package.delete()  # Deletes the PackagesInSystem entry

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        InTransitTransport.objects.create(
            transport_id = transport_instance.transport_id,
            vehicle_type=transport_instance.vehicle_type,
            max_capacity=transport_instance.max_capacity,
            number_plate=transport_instance.number_plate,
            driver_name=transport_instance.driver_name
        )
        transport_instance.delete()
    #add to Route
    
    # Load packages in system, warehouses, and transports for form
    context = {
        'packages': PackagesInSystem.objects.all(),
        'warehouses': Warehouse.objects.all(),
        'transports': AvailableTransport.objects.all()
    }
    return render(request, 'tracking/assign_warehouse_to_delivery.html', context)


def assign_dispatch_to_warehouse(request):
    if request.method == 'POST':
        transport_id = request.POST.get('transport_id')
        warehouse_name = request.POST.get('warehouse_name')
        package_ids = request.POST.getlist('package_ids')

        try:
            # Retrieve Transport instance
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        except AvailableTransport.DoesNotExist:
            messages.error(request, "Invalid transport ID. Please select a valid transport.")
            return redirect('assign_dispatch_to_warehouse')  # Redirect to form

        # Calculate total weight of selected packages
        total_package_weight = float(sum(Package.objects.get(package_id=package_id).weight for package_id in package_ids))

        # Check if assigning packages would exceed max capacity
        if transport_instance.current_load + Decimal(str(total_package_weight)) > transport_instance.max_capacity:
            messages.error(request, 'Assignment failed: Transport load capacity exceeded.')
            return redirect('assign_dispatch_to_warehouse')

        # Update transport's current load (assuming all packages are assigned successfully)
        transport_instance.current_load += Decimal(str(total_package_weight))
        transport_instance.save()

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        transport_obj = Transport.objects.get(transport_id=transport_instance.transport_id)

        Route.objects.create(
            transport = transport_obj,
            type = 'DTW',
            end_location = warehouse_name,
            start_location = 'Dispatch',
        )


        # Move selected packages from PackagesInSystem to PackagesInTransit
        for package_id in package_ids:
            # Get the package from PackagesInSystem
            transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
            warehouse_instance = Warehouse.objects.get(warehouse_name = warehouse_name)
            # Access the original Package instance
            original_package = PackagesInSystem.objects.get(package_id = package_id) # This accesses the related Package

            # Add to PackagesInTransit
            PackagesInTransit.objects.create(
                package_id=original_package.package_id, 
                transport_id = transport_instance.transport_id,
                #warehouse_id = warehouse_instance.warehouse_id,
                type = original_package.type,
                weight = original_package.weight,
                height = original_package.height,
                width = original_package.width,
                length = original_package.length,
                dispatch_location = original_package.dispatch_location,
                delivery_location = original_package.delivery_location,
                customer = original_package.customer,

            )
            PackageStatus.objects.create(
                package_id=original_package.package_id,
                location=original_package.dispatch_location,
                #status=PackageStatus.status_type.REGISTERED

            )
            package = PackagesInSystem.objects.get(package_id = package_id)
            package.delete()
            #original_package.delete()  # Deletes the PackagesInSystem entry

        transport_instance = AvailableTransport.objects.get(transport_id=transport_id)
        InTransitTransport.objects.create(
            transport_id = transport_instance.transport_id,
            vehicle_type=transport_instance.vehicle_type,
            max_capacity=transport_instance.max_capacity,
            number_plate=transport_instance.number_plate,
            driver_name=transport_instance.driver_name
        )
        transport_instance.delete()
    #add to Route
    
    # Load packages in system, warehouses, and transports for form
    context = {
        'packages': PackagesInSystem.objects.all(),  # Fetch from PackagesInSystem
        'warehouses': Warehouse.objects.all(),
        'transports': AvailableTransport.objects.all()
    }
    return render(request, 'tracking/assign_dispatch_to_warehouse.html', context)


def transport_dashboard(request):
    # Retrieve the number plate from the session
    number_plate = request.session.get('number_plate')

    # Check if number plate exists in session
    if not number_plate:
        messages.error(request, "Please log in to access the dashboard.")
        return redirect('transport_login')

    try:
        # Get the transport instance using the number plate from the session
        transport = Transport.objects.get(number_plate=number_plate)
    except Transport.DoesNotExist:
        messages.error(request, "Transport record not found.")
        return redirect('transport_login')

    assigned_packages = PackagesInTransit.objects.filter(transport=transport.transport_id)

    # Get the latest assigned route (adjust as needed)
    try:
        latest_route = Route.objects.filter(transport=transport.transport_id).latest('route_id')
    except Route.DoesNotExist:
        latest_route = None  # No route found

    return render(request, 'tracking/transport_dashboard.html', {
        'transport': transport,
        'assigned_packages': assigned_packages,
        'assigned_route': latest_route,
    })


from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.db import transaction

def complete_route(request, route_id):
    route = get_object_or_404(Route, route_id=route_id)
    packages_in_transit = PackagesInTransit.objects.filter(transport=route.transport)

    if request.method == 'POST':
        with transaction.atomic():
            for package in packages_in_transit:
                final_status = request.POST.get(f'package_{package.package_id}_status')
                
                if not final_status:
                    messages.error(request, f"Status for package {package.package_id} is missing.")
                    return redirect('transport_dashboard')

                # Move packages based on final status
                if final_status == 'delivered_to_warehouse':
                    # Create entry in PackagesInSystem
                    PackagesInSystem.objects.create(
                        package_id=package.package_id,
                        customer=package.customer,
                        type=package.type,
                        weight=package.weight,
                        height=package.height,
                        width=package.width,
                        length=package.length,
                        dispatch_location=package.dispatch_location,
                        delivery_location=package.delivery_location,
                    )
                elif final_status in ['damaged', 'lost']:
                    # Create entry in DamagedOrLostPackages
                    DamagedOrLostPackages.objects.create(
                        package_id=package.package_id,
                        customer=package.customer,
                        type=package.type,
                        weight=package.weight,
                        height=package.height,
                        width=package.width,
                        length=package.length,
                        dispatch_location=package.dispatch_location,
                        delivery_location=package.delivery_location,
                    )
                    PackageStatus.objects.create(
                        package_id=package.package_id,
                        location='Lost/Damaged',
                        #status=PackageStatus.status_type.REGISTERED
                    )
                elif final_status == 'delivered_to_final_location':
                    # Create entry in DeliveredPackages
                    DeliveredPackages.objects.create(
                        package_id=package.package_id,
                        customer=package.customer,
                        type=package.type,
                        weight=package.weight,
                        height=package.height,
                        width=package.width,
                        length=package.length,
                        dispatch_location=package.dispatch_location,
                        delivery_location=package.delivery_location,
                    )
                    PackageStatus.objects.create(
                        package_id=package.package_id,
                        location=package.delivery_location,
                        #status=PackageStatus.status_type.REGISTERED
                    )
                    original_package = Package.objects.filter(package_id=package.package_id)
                    original_package.delete()

                
                # Remove package from PackagesInTransit
                package.delete()

            # Transfer transport to AvailableTransport and remove from InTransitTransport
            transport_instance = get_object_or_404(InTransitTransport, transport_id=route.transport.transport_id)
            AvailableTransport.objects.create(
                transport_id=transport_instance.transport_id,
                vehicle_type=transport_instance.vehicle_type,
                max_capacity=transport_instance.max_capacity,
                number_plate=transport_instance.number_plate,
                driver_name=transport_instance.driver_name,
                current_load=0  # Reset current load
            )
            transport_instance.delete()

            route_instance = get_object_or_404(Route, route_id = route_id)
            # Delete the completed route from the Route table
            route_instance.delete()

            messages.success(request, "Route completed and packages updated successfully.")
            return redirect('transport_dashboard')
    
    return render(request, 'tracking/complete_route.html', {
        'route': route,
        'packages_in_transit': packages_in_transit,
    })
