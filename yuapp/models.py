from django.contrib.auth.models import User, Group
from django.db import models, transaction
from django.forms import ValidationError
from django.core.validators import FileExtensionValidator
from utils.validators import validate_file_size
from utils.image_processing import resize_image
from django.utils import timezone
from decimal import Decimal
from django.db.models import F, Q
from datetime import timedelta
from django.db.models import Sum, F, Value, Subquery, OuterRef, Count
from django.db.models.functions import Coalesce
from geopy.distance import geodesic  # For proximity calculation
from django.utils.timezone import now
from django.core.mail import send_mail
from django.conf import settings
import random
import string
from simple_history.models import HistoricalRecords

class ActiveStatusModel(models.Model):
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

def validate_file_size(value):
    max_size_mb = 2  # 2 MB
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"Image file too large ( > {max_size_mb}MB )")
    
#email function
def send_email(username, password, recipient_email):
    subject = 'Your Account Information'
    message = f'Hello,\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\n\nThank you!'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [recipient_email]

    send_mail(subject, message, from_email, recipient_list)
            
# Model for Country
class Country(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Country'
        
    def __str__(self):
        return self.name

# Model for Region linked to Country
class Region(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GR" for Greater Accra
    country = models.ForeignKey(Country, on_delete=models.CASCADE)
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Region'
        
    def __str__(self):
        return f"{self.name}, {self.country.name}"

# Model for District linked to Region
class District(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GAW" for Ga West
    region = models.ForeignKey(Region, on_delete=models.CASCADE)
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'District'
        
    def __str__(self):    
        status = "Active" if self.active else "Inactive"
        return f"{self.name}, {self.region.name} - {status}"

# Model for City linked to District
class City(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "Ksi" for Kumasi
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'City'
        
    def __str__(self):
        status = "Active" if self.active else "Inactive"
        return f"{self.name}, {self.district.name} - {status}"
    



# Model for WaterTank
class WaterTank(ActiveStatusModel):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)  # Link to City
    capacity = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='watertanks/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Water Reservoir'
    
    def __str__(self):
        return f"{self.name}, {self.city.name}, - {self.city.district.region.name}, {self.city.district.region.country.name}"
    
# Model for MarketingCentre
class MarketingCentre(ActiveStatusModel):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    city = models.ManyToManyField(City, blank=True, verbose_name='Cluster/Sites')  # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Market Center'
        
    def __str__(self):
        return self.name

class Greenhouse(ActiveStatusModel):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True, verbose_name='City')  # Link to City
    water_tanks = models.ManyToManyField(WaterTank)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='greenhouse/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    description = models.TextField(null=True, blank=True)
    marketing_centres = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE, null=True, blank=True, verbose_name='marketcentre')  # Many-to-many relationship
    
    # New fields
    cost_component = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Total Construction Cost")
    number_of_rooms = models.PositiveIntegerField(verbose_name="Number of Rooms (Tunnels)", null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
   
    def shared_cost_per_room(self):
        #Calculate shared cost per room"""
        if self.number_of_rooms > 0:
            return self.cost_component / self.number_of_rooms
        return 0  # Avoid division by zero

    def __str__(self):
        return f"{self.name}, {self.city.name if self.city else 'No City'}, {self.city.district.region.country.name if self.city else 'No Country'}"

   
class GreenhouseRoom(ActiveStatusModel):
    room_name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='greenhouseroom/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    notes = models.TextField(null=True, blank=True)
    greenhouse = models.ForeignKey('Greenhouse', on_delete=models.CASCADE, related_name='rooms')  # One-to-many relationship
   
    #New field for shared cost
    shared_cost = models.DecimalField(max_digits=12, decimal_places=2, editable=False, null=True, blank=True, verbose_name="Shared Construction Cost")  

    assign = models.IntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
   
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Greenhouse Rooms'

    def clean(self):
        #Validate that no more rooms than allowed are created"""
        if self.greenhouse.rooms.count() >= self.greenhouse.number_of_rooms:
            raise ValidationError(f"Cannot add more rooms. Maximum of {self.greenhouse.number_of_rooms} already reached.")

    def save(self, *args, **kwargs):
        #Automatically assign shared cost before saving"""
        self.shared_cost = self.greenhouse.shared_cost_per_room()
        super().save(*args, **kwargs)
        
    def __str__(self):
        return f"{self.room_name} in {self.greenhouse.name} assigned to {self.beneficiary.full_name if hasattr(self, 'beneficiary') and self.beneficiary else 'None'}"


class MaintenanceCategory(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance Category'
        
    def __str__(self):
        return self.name

class Maintenance(ActiveStatusModel):
    REASON_FOR_RUN = [
        ('Pwr Outage', 'Pwr Outage'),
        ('Test', 'Test'),
        ('maintenance', 'Maintenance')
    ] 
    category = models.OneToOneField(MaintenanceCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='maintenance_category') 
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    is_tunnel = models.BooleanField(default=False)
    tunnel = models.OneToOneField(GreenhouseRoom, on_delete=models.CASCADE, null=True, blank=True, related_name='tunnel')    
    date = models.DateTimeField(default=timezone.now)
    last_fuel_filling_per_litre = models.DecimalField(max_digits=5, decimal_places=2)
    fuel_pecentage_level_before_run = models.DecimalField(max_digits=5, decimal_places=2)
    fuel_pecentage_level_after_run = models.DecimalField(max_digits=5, decimal_places=2)
    startTime = models.TimeField(blank=True, null=True)
    finishTime = models.TimeField(blank=True, null=True)
    operator_name = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    reason = models.CharField(max_length=20, choices=REASON_FOR_RUN, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance'
        
    def __str__(self):
        return f"{self.name} - {self.category.name}"
    
class SaleAgent(ActiveStatusModel):
    SALEAGENT_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ] 
    fullname = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='sale_agent')  # Allow null for now
    gender = models.CharField(max_length=20, choices=SALEAGENT_GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='saleagent/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Passport Photo'
    )
    nationalId = models.CharField(max_length=15, unique=True, null=True,  blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(
        upload_to='saleagent/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Ghana Card Picture'
    )   
    description = models.TextField(null=True,  blank=True)
    city = models.ManyToManyField(City, blank=True)  # Many-to-many relationship with Crop
    marketingcentre = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE,  null=True, blank=True, related_name='marketingcentre') # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saleagent_created_by')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Marketing & Sale Agents'
        
    def __str__(self):
        return self.fullname
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))

    #creation user credentials for beneficiary
      # Override the save method
     # Override the save method
    def save(self, *args, **kwargs):
        if not self.user:
            # Create user dynamically if not already assigned
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = True  # Optional if Sales Agent need staff access
            user.first_name = self.fullname.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.fullname.split(' ')[1:]) if len(self.fullname.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'EDO' group
            group, created = Group.objects.get_or_create(name='SALES')
            user.groups.add(group)

            # Assign the created user to the Supervisor
            self.user = user
            print(f'Sale Agent created with password: {password}')
            # Optional: Send email with login credentials

        super().save(*args, **kwargs)


class Finance(ActiveStatusModel):
    SALEAGENT_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ] 
    fullname = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name='finance')  # Allow null for now
    gender = models.CharField(max_length=20, choices=SALEAGENT_GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='finance/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Passport Photo'
    )
    nationalId = models.CharField(max_length=15, unique=True, null=True,  blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(
        upload_to='finance/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Ghana Card Picture'
    )   
    description = models.TextField(null=True,  blank=True)
    city = models.ManyToManyField(City, blank=True)  # Many-to-many relationship with Crop
    marketingcentre = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE,  null=True, blank=True, related_name='finance_marketingcentre') # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='finance_created_by')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Finance Team'
        
    def __str__(self):
        return self.fullname
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))

    #creation user credentials for beneficiary
      # Override the save method
     # Override the save method
    def save(self, *args, **kwargs):
        if not self.user:
            # Create user dynamically if not already assigned
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = True  # Optional if Sales Agent need staff access
            user.first_name = self.fullname.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.fullname.split(' ')[1:]) if len(self.fullname.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'EDO' group
            group, created = Group.objects.get_or_create(name='FINANCE')
            user.groups.add(group)

            # Assign the created user to the Supervisor
            self.user = user
            print(f'Finance Team member created with password: {password}')
            # Optional: Send email with login credentials

        super().save(*args, **kwargs)
              
# Model for Supervisors
class Supervisor(ActiveStatusModel):
    SUPERVISOR_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ] 
    fullname = models.CharField(max_length=255)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for now
    gender = models.CharField(max_length=20, choices=SUPERVISOR_GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)

    photo = models.ImageField(
        upload_to='edo/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Passport Picture'
    )
    nationalId = models.CharField(max_length=15, unique=True, null=True,  blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(
        upload_to='edo/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Ghana Card Picture'
    )   
    description = models.TextField(null=True,  blank=True)
    city = models.ManyToManyField(City, blank=True)  # Many-to-many relationship with Crop
    greenhouse = models.ManyToManyField(Greenhouse, blank=True)  # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='supervisor_created_by')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Enterprise Development Officer'
        
    def __str__(self):
        return self.fullname
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))

    #creation user credentials for beneficiary
      # Override the save method
     # Override the save method
    def save(self, *args, **kwargs):
        if not self.user:
            # Create user dynamically if not already assigned
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = True  # Optional if Supervisors need staff access
            user.first_name = self.fullname.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.fullname.split(' ')[1:]) if len(self.fullname.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'EDO' group
            group, created = Group.objects.get_or_create(name='EDO')
            user.groups.add(group)

            # Assign the created user to the Supervisor
            self.user = user
            print(f'Supervisor created with password: {password}')
            # Optional: Send email with login credentials

        super().save(*args, **kwargs)
    
class SupervisorAttendance(models.Model):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    login_latitude = models.FloatField()
    login_longitude = models.FloatField()
    login_time = models.DateTimeField(auto_now_add=True)
    is_valid = models.BooleanField(default=False)

    def validate_proximity(self):
        # Greenhouse location
        greenhouse_location = (self.greenhouse.latitude, self.greenhouse.longitude)
        # Supervisor's login location
        login_location = (self.login_latitude, self.login_longitude)
        # Calculate distance
        distance = geodesic(greenhouse_location, login_location).meters
        # Define a threshold (e.g., 100 meters)
        threshold = 100  # in meters
        self.is_valid = distance <= threshold
        return self.is_valid
    
    def __str__(self):
        return f"Attendance for {self.supervisor.fullname} at {self.timestamp} - Valid: {self.is_valid}"

     
# Model for Crops
class Crop(ActiveStatusModel):
    name = models.CharField(max_length=255)
    estimatedyield = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='crop/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Picture'
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        #return f"{self.name} - Estimated Yied => {self.estimatedyield}"
        return f"{self.name}"


class CropVariety(ActiveStatusModel):
    name = models.CharField(max_length=255)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, related_name='parent_crop') 
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='crop_variety/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Picture'
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Crop Variety'
        
    def __str__(self):
        #return f"{self.name} - Estimated Yied => {self.estimatedyield}"
        return f"{self.name} - {self.crop.name}"
    
# Model for Beneficiary with user identity for login
class Beneficiary(ActiveStatusModel):
    BENEFICIARY_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]

    gender = models.CharField(max_length=20, choices=BENEFICIARY_GENDER_CHOICES, null=True, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for now
    full_name = models.CharField(max_length=255)
    enterprise_name = models.CharField(max_length=255, verbose_name='Enterprise Name', null=True, blank=True)    
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='beneficiary/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Passport Picture'
    )
    nationalId = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(
        upload_to='beneficiary/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Ghana Card Picture'
    )
    description = models.TextField(null=True,  blank=True)
    assigned_tunnel = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE, null=True, related_name='beneficiary_tunnel') 
    assigned_edo = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, related_name='supervisor')
    crops = models.ManyToManyField(Crop, blank=True)  # Many-to-many relationship with Crop    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiary_created')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Beneficiary'
        
    def __str__(self):
        return self.full_name
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))

    #creation user credentials for beneficiary
    
     # Override the save method
    def save(self, *args, **kwargs):
        if not self.user:
            # Create user dynamically if not already assigned
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = False  # Optional if Beneficiaries don't need staff access
            user.first_name = self.full_name.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.full_name.split(' ')[1:]) if len(self.full_name.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'Beneficiary' group
            group, created = Group.objects.get_or_create(name='Beneficiary')
            user.groups.add(group)

            # Assign the created user to the Beneficiary
            self.user = user
            print(f'Beneficiary created with password: {password}')
            # Optional: Send email with login credentials

        super().save(*args, **kwargs)
        
class Grade(ActiveStatusModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='crop_grade_created')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Crop Production Grade'
        
    def __str__(self):
        return f"{self.name}"

class ProductUnit(ActiveStatusModel):
    name = models.CharField(max_length=255)
    expression = models.CharField(null=True,  blank=True, max_length=20, verbose_name='Measuring Unit')
    description = models.TextField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='crop_production_unit_created')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Crop Production Unit'
        
    def __str__(self):
        return f"{self.name}"


class PriceTable(ActiveStatusModel):
    market_center = models.ForeignKey(MarketingCentre, null=True, blank=True, on_delete=models.CASCADE, related_name='market_center_price')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, related_name='crop_price')
    cropvariety = models.ForeignKey(CropVariety, null=True, blank=True, on_delete=models.CASCADE, related_name='cropvariety_price')
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE, related_name='grade_price')
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, related_name='price_unit')
    price = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, null=True, blank=True)    
    selling_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    from_date = models.DateTimeField(default=timezone.now)
    to_date = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='price_table_created')
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Price Table'
        
    constraints = [
        models.UniqueConstraint(
            fields=['market_center', 'crop', 'grade', 'unit', 'from_date', 'to_date'], 
            name='unique_price_table'
        )
    ]
        
    def __str__(self):
        return f"Price Table For: {self.id} by {self.crop.name} - {self.grade.name} - {self.unit.name}  - {self.price} on  {self.from_date} - {self.to_date}"
    

     
# Model for beneficiary Workers
class WorkerRole(ActiveStatusModel):
    name = models.CharField(max_length=255)
    description = models.TextField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiary_worker_role_created')
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Beneficiary Woker Role'
        
    def __str__(self):
        return f"{self.name} ({self.description})"
    

# Model for beneficiary Workers
class Worker(ActiveStatusModel):
    BENEFICIARY_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ]
    full_name = models.CharField(max_length=255)     
    gender = models.CharField(max_length=20, choices=BENEFICIARY_GENDER_CHOICES, null=True, blank=True)
    role = models.ForeignKey(WorkerRole, on_delete=models.CASCADE)
    # beneficiary = models.ForeignKey('Beneficiary', on_delete=models.CASCADE, related_name='workers')
    beneficiary = models.ForeignKey(Beneficiary, null=True, blank=True, on_delete=models.CASCADE, related_name='workers')
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(
        upload_to='worker/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Passport Photo'
    )
    nationalId = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(
        upload_to='worker/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Ghana Card Picture'
    )
    from_date = models.DateTimeField(default=timezone.now)
    to_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    # created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Beneficiary Wokers'
        
    def __str__(self):
        return f"{self.full_name} - {self.role.name}"

#contract between Beneficiary and Worker
class Contract(ActiveStatusModel):
    CONTRACT_TYPE_CHOICES = [
        ('Temporary', 'Temporary'),
        ('Permanent', 'Permanent'),
        ('Casual', 'Casual'),
    ]
    
    CONTRACT_PAYMENT_CHOICES = [
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly'),
        ('Monthly', 'Monthly'),
    ]
     
    CONTRACT_STATUS_CHOICES = [
        ('Active', 'Active'),
        ('Ended', 'Ended'),
        ('Terminated', 'Terminated'),
    ]
    
    # Foreign keys to Beneficiary and Worker
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='contracts')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='contracts')
    # Contract details
    contract_type = models.CharField(max_length=50, choices=CONTRACT_TYPE_CHOICES)
    description = models.TextField(null=True, blank=True)
    from_date = models.DateTimeField(default=timezone.now)
    to_date = models.DateTimeField(null=True, blank=True)
    payment_mode_type = models.CharField(max_length=50, choices=CONTRACT_PAYMENT_CHOICES, null=True, blank=True)
    charge_per_day = models.DecimalField(max_digits=10, decimal_places=2)  # Assuming charge per day in currency
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    # Auto-calculated field for days between `from_date` and `to_date`
    @property
    def contract_duration_days(self):
        if self.to_date:
            return (self.to_date - self.from_date).days
        return 0
    
    # Contract status (active, terminated)
    status = models.CharField(max_length=20, choices=CONTRACT_STATUS_CHOICES, default='Active')
    # Date when the contract was created
    created_at = models.DateTimeField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if self.from_date and self.to_date:
            delta = self.to_date - self.from_date
            self.days = delta.days
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.worker.full_name} - {self.beneficiary.full_name} - {self.contract_type}"
    
    
# Model for TrendKnowledgeBank
class TrendKnowledgeBank(ActiveStatusModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='trendknowledgebank/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
   
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trend Knowledge Bank'
         
    def __str__(self):
        return self.title

# Model for TrendKnowledgeDiscussion linked to TrendKnowledgeBank
class TrendKnowledgeDiscussion(ActiveStatusModel):
    trend_knowledge_bank = models.ForeignKey(TrendKnowledgeBank, on_delete=models.CASCADE)
    discussion = models.TextField()
    photo = models.ImageField(
        upload_to='trendknowledgediscussion/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    tagged_beneficiaries = models.ManyToManyField(Beneficiary, related_name='discussions', blank=True)  # Tagging beneficiaries
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trend Knowledge Discussion'
        
    def __str__(self):
        return f"Discussion on {self.trend_knowledge_bank.title}"
       
# Model for CashAssigned with repayment period
class CashAssigned(ActiveStatusModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied')
    ]
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE,  related_name='cashloans')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_period_from = models.DateField()
    repayment_period_to = models.DateField()
    notes = models.TextField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigncash_created')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
   
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cash Bank'
    
    def __str__(self):
        return f"Cash Assigned to {self.beneficiary.full_name} - {self.amount}"

# Model for Repayment records
class Repayment(ActiveStatusModel):
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Denied', 'Denied')
    ]
    cash_assigned = models.ForeignKey(CashAssigned, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    bal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField()
    notes = models.TextField(null=True,  blank=True)
    photo = models.ImageField(
        upload_to='repayment/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Evidence'
    )
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cashcollection_created')
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cash Repayment'

    def __str__(self):
        return f"Repayment for {self.cash_assigned.beneficiary.full_name}"
        

# Model for StoreRoom
class StoreRoom(ActiveStatusModel):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    greenhouse = models.ForeignKey(Greenhouse, null=True, blank=True, on_delete=models.CASCADE, related_name='greenhouse')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='storeroom/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Upload Photo'
    )
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='storeroom_created')
   
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Store Room'
        
    def __str__(self):
        return f"{self.name} - {self.greenhouse.name if self.greenhouse.name else 'No Greenhouse Assign'}"


# Model for assigning StoreRoom to Beneficiaries
class StoreRoomAssign(ActiveStatusModel):
    storeroom = models.ForeignKey(StoreRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    assigned_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='storeroom_assign_created')
   
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Store Room Allocation'
        
    def __str__(self):
        return f"{self.storeroom.name} assigned to {self.beneficiary.full_name}"

# Model for ChangingRoom
class ChangingRoom(ActiveStatusModel):
    name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    greenhouse = models.ForeignKey(Greenhouse, null=True, blank=True, on_delete=models.CASCADE, related_name='green_house')
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='changingroom/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Upload Photo'
    )
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Changing Room'
        
    def __str__(self):
        return self.name

# Model for assigning ChangingRoom to Beneficiaries
class ChangingRoomAssign(ActiveStatusModel):
    changing_room = models.ForeignKey(ChangingRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    notes = models.TextField(null=True,  blank=True)
    assigned_at = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Changing Room Allocation'
    
    def __str__(self):
        return f"{self.changing_room.name} assigned to {self.beneficiary.full_name}"
 
### buyer and sales model
class Buyer(ActiveStatusModel):
    client_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, verbose_name='Contact Person')
    phone = models.CharField(max_length=15)  # Adjust the max length according to your needs
    email = models.EmailField(max_length=255)
    photo = models.ImageField(
        upload_to='buyer/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    shipping_address = models.TextField()
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)  # Track buyer balance
    city = models.ManyToManyField(City, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE,  null=True, blank=True, related_name='buyer_profile')
    notes = models.TextField(null=True, blank=True)
    market_center = models.ManyToManyField(MarketingCentre, blank=True)  # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='buyer_created')

    def __str__(self):
        return self.client_name
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))
 
    def save(self, *args, **kwargs):
        if not self.user:
            try:
                user = User.objects.get(email=self.email)
            except User.DoesNotExist:
                # Create user dynamically
                password = self.generate_random_password()
                user = User.objects.create_user(username=self.email.split('@')[0], email=self.email, password=password)
                user.first_name = self.client_name.split()[0]
                user.last_name = ' '.join(self.client_name.split()[1:])
                user.save()

                # Assign user to 'Buyer' group
                group, _ = Group.objects.get_or_create(name='Buyer')
                user.groups.add(group)

            self.user = user
        super().save(*args, **kwargs)
    
class AIC(ActiveStatusModel):
    person_incharge = models.CharField(max_length=255, verbose_name='In Charge')
    phone = models.CharField(max_length=15)  # Adjust the max length according to your needs
    email = models.EmailField(max_length=255)
    market_center = models.ManyToManyField(MarketingCentre, blank=True)  # Many-to-many relationship with Crop
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for now
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='aic_created')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'AIC'
    
    def __str__(self):
        return f"{self.person_incharge},- {self.market_center.name}"
    
    # Helper function to generate a random password
    def generate_random_password(self):
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choice(chars) for _ in range(8))

    #creation user credentials for beneficiary
    
     # Override the save method
    def save(self, *args, **kwargs):
        if not self.user:
            # Create user dynamically if not already assigned
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = False  # Optional if Beneficiaries don't need staff access
            user.first_name = self.person_incharge.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.person_incharge.split(' ')[1:]) if len(self.person_incharge.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'Beneficiary' group
            group, created = Group.objects.get_or_create(name='AIC')
            user.groups.add(group)

            # Assign the created user to the Beneficiary
            self.user = user
            print(f'AIC Rep created with password: {password}')
            # Optional: Send email with login credentials

        super().save(*args, **kwargs)



###<<<<<<<<<<<<<<<<<<<<<<<  SALES AND MARKETING MODULE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#####################
###<<<<<<<<<<<<<<<<<<<<<<<  SALES AND MARKETING MODULE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#####################
class Harvest(ActiveStatusModel):
    HARVEST_STATUS = [                
        ('Open', 'Open'),
        ('Confirmed', 'Confirmed'),
    ]

    HARVEST_REVIEW_STATUS = [ 
        ('Open', 'Open'),      
        ('Agree', 'Agree'),
        ('Disagree', 'Disagree'),
    ]
    confirmation = models.CharField(max_length=20, choices=HARVEST_STATUS, default='Open')
    date = models.DateTimeField(default=timezone.now)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    cropvariety = models.ForeignKey(CropVariety, on_delete=models.CASCADE, null=True, blank=True)
    unit = models.ForeignKey(ProductUnit, null=True, blank=True, on_delete=models.CASCADE)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE, null=True, blank=True)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE, null=True, blank=True)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, related_name='beneficiary_harvest')

    description = models.TextField(blank=True, default="")  
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='beneficiary_harvest_created')
    created_at = models.DateTimeField(default=timezone.now)
    price_record = models.ForeignKey(PriceTable, on_delete=models.SET_NULL, null=True, blank=True)

    status = models.CharField(max_length=10, default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='harvest_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)
    review_note = models.TextField(blank=True, default="")  
    reviewed_status = models.CharField(max_length=20, choices=HARVEST_REVIEW_STATUS, default='Open') 
    history = HistoricalRecords()
    class Meta:
        ordering = ['-date']
        verbose_name_plural = 'Crop Harvest Records'

    def __str__(self):
        return f"{self.date} ({self.crop}) ({self.description}) ({self.grade})"

    def calculate_price(self):
        if not self.crop or not self.grade or not self.unit:
            return None  # Avoid calculation if required fields are missing

        price_record = PriceTable.objects.filter(
            crop=self.crop,
            cropvariety = self.cropvariety,
            grade=self.grade,
            unit=self.unit,
            from_date__lte=self.date,
            to_date__gte=self.date
        ).order_by('-from_date').first()

        if price_record:
            self.price_record = price_record
            self.total_price = (self.quantity or 0) * price_record.selling_price
            self.save(update_fields=['price_record', 'total_price'])
            return self.total_price
        return None

    @classmethod
    def total_harvest_by_crop(cls, crop):
        return cls.objects.filter(crop=crop).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    @classmethod
    def total_harvest_by_greenhouse(cls, greenhouse):
        return cls.objects.filter(greenhouse=greenhouse).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    @classmethod
    def total_harvest_by_greenhouse_room(cls, greenhouse_room):
        return cls.objects.filter(greenhouse_room=greenhouse_room).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0

    @classmethod
    def total_harvest_by_beneficiary(cls, beneficiary):
        return cls.objects.filter(beneficiary=beneficiary).aggregate(total_quantity=Sum('quantity'))['total_quantity'] or 0
    
    def save(self, *args, **kwargs):
        is_new = self._state.adding  # Check if this is a new record
       #previous = None if is_new else Harvest.objects.get(pk=self.pk)

        super().save(*args, **kwargs)  # Save the record

        # Only trigger aggregation when it's a new record and already confirmed
        if is_new and self.confirmation == 'Confirmed':
            self.aggregate_harvest_stock()

    def aggregate_harvest_stock(self):
        if not self.greenhouse:
            return  

        market_centre = self.greenhouse.marketing_centres  
        harvest_date = self.date.date()  # Ensure we use the harvest record date

        with transaction.atomic():
            aggregate, created = HarvestStockAggregate.objects.get_or_create(
                market_centre=market_centre,
                crop=self.crop,
                grade=self.grade,
                unit=self.unit,
                unit_price = self.price_record,
                aggregation_date=harvest_date,  # Ensuring FIFO tracking
                defaults={'total_quantity': 0, 'total_value': 0}
                #created_at=self.created_by
            )

            aggregate.total_quantity += self.quantity or 0
            aggregate.total_value += self.total_price or 0
            aggregate.save()
                     

class HarvestStockAggregate(models.Model):
    market_centre = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE)
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    cropvariety = models.ForeignKey(CropVariety, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, null=True, blank=True)
    unit_price = models.ForeignKey(PriceTable, on_delete=models.CASCADE, null=True, blank=True)
    total_quantity = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    total_value = models.DecimalField(max_digits=15, decimal_places=2, default=0)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    aggregation_date = models.DateField(default=timezone.now, null=True, blank=True)
    history = HistoricalRecords()
    
    class Meta:
        ordering = ['aggregation_date']  # FIFO Order
        verbose_name_plural = 'Harvest Stock Aggregates'
        unique_together = ('market_centre', 'crop', 'grade', 'unit', 'aggregation_date')

    def __str__(self):
        return f"{self.aggregation_date} - {self.market_centre} - {self.crop} ({self.cropvariety}) ({self.grade}) ({self.unit})"

    def update_aggregate(self, quantity, value):
        with transaction.atomic():
            self.total_quantity += quantity or 0
            self.total_value += value or 0
            self.save(update_fields=['total_quantity', 'total_value'])
    
    def save(self, *args, **kwargs):
        if self.unit_price and self.total_quantity:
            self.total_value = self.total_quantity * self.unit_price.selling_price
        super().save(*args, **kwargs) 
            
class HarvestMovement(ActiveStatusModel):
    from_market_centre = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE, related_name='outgoing_movements_stock')
    to_market_centre = models.ForeignKey(MarketingCentre, on_delete=models.CASCADE, related_name='incoming_movements_stock')
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE)
    cropvariety= models.ForeignKey(CropVariety, on_delete=models.CASCADE, null=True, blank=True)
    grade = models.ForeignKey(Grade, on_delete=models.CASCADE)
    unit = models.ForeignKey(ProductUnit, on_delete=models.CASCADE, null=True, blank=True)  # Added for consistency
    quantity = models.DecimalField(max_digits=12, decimal_places=2)
    movement_date = models.DateTimeField(default=timezone.now)
    received = models.BooleanField(default=False)
    quantity_received = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    received_by = models.ForeignKey( 
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name='stock_movement_receivedby'
    )
    received_at = models.DateTimeField(null=True, blank=True)  # New: Timestamp for confirmation
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='stock_movement_createdby')
    created_at = models.DateTimeField(default=timezone.now)
    history = HistoricalRecords()
    class Meta:
        ordering = ['-movement_date']
        verbose_name_plural = 'Harvest Movements'

    def __str__(self):
        return f"Movement from {self.from_market_centre} to {self.to_market_centre} - {self.crop}, {self.cropvariety} ({self.grade})"

    def save(self, *args, **kwargs):
        #Ensures stock is deducted from `from_market_centre` and added to `to_market_centre` when received."""
        if not self.received:  # If movement is pending, validate available stock
            self.validate_stock_availability()
        
        super().save(*args, **kwargs)

    def validate_stock_availability(self):
        #Check if the source market centre has enough stock before movement."""
        available_stock = HarvestStockAggregate.objects.filter(
            market_centre=self.from_market_centre, 
            crop=self.crop, 
            cropvariety = self.cropvariety,
            grade=self.grade,
            unit=self.unit
        ).aggregate(total_quantity=Sum('total_quantity'))['total_quantity'] or 0

        if self.quantity > available_stock:
            raise ValueError(f"Insufficient stock at {self.from_market_centre}. Available: {available_stock}, Requested: {self.quantity}")

    def confirm_receipt(self, user):
        if self.received:
            raise ValueError("This movement has already been received.")

        with transaction.atomic():
            # Save timestamp early to ensure consistency
            self.received = True
            self.received_by = user
            self.received_at = timezone.now()
            self.save(update_fields=['received', 'received_by', 'received_at'])

            # 1. Fetch source stock
            source_stock = HarvestStockAggregate.objects.get(
                market_centre=self.from_market_centre,
                crop=self.crop,
                cropvariety=self.cropvariety,
                grade=self.grade,
                unit=self.unit
            )

            # 2. Calculate unit value safely
            unit_value = source_stock.total_value / source_stock.total_quantity if source_stock.total_quantity > 0 else 0

            # 3. Deduct from source
            source_stock.total_quantity -= self.quantity
            source_stock.total_value -= unit_value * self.quantity
            source_stock.save(update_fields=['total_quantity', 'total_value'])

            # 4. Add to destination
            destination_stock, created = HarvestStockAggregate.objects.get_or_create(
                market_centre=self.to_market_centre,
                crop=self.crop,
                cropvariety=self.cropvariety,
                grade=self.grade,
                unit=self.unit,
                aggregation_date=self.received_at.date(),  # ✅ this is key!
                defaults={
                    'total_quantity': 0,
                    'total_value': 0,
                    'created_by': user,
                }
            )

            # 5. Update quantity and value
            destination_stock.total_quantity += self.quantity
            destination_stock.total_value += unit_value * self.quantity
            destination_stock.save(update_fields=['total_quantity', 'total_value'])

            
##################################################################################################
#ORDER ORDER ITEMS, PAYMENTS, BALANCE FOR SALE ORDER PROCESSING
#############################################################################################################

class PaymentStatus(models.TextChoices):
    CASH = 'cash', 'Cash'
    CREDIT = 'credit', 'Credit Purchase'

class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    COMPLETED = 'completed', 'Completed'
    CANCELED = 'canceled', 'Cancelled'


class Order(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, related_name='orders')
    sales_agent = models.ForeignKey(SaleAgent, on_delete=models.SET_NULL, null=True, related_name='orders')
    order_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    sale_order_type = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.CASH, verbose_name="Sale Order Type")
    is_credit_approved = models.BooleanField(default=False)
    is_paid = models.BooleanField(default=False)

    notes = models.TextField(blank=True, null=True)
    total_items = models.PositiveIntegerField(default=0, blank=True, null=True, editable=False)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, blank=True, null=True, editable=False)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='orders_created')
    created_at = models.DateTimeField(auto_now_add=True)
    fulfilled_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='orders_fulfilled')
    fulfilled_at = models.DateTimeField(null=True, blank=True)
    delivery_date = models.DateField(default=timezone.now, null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    history = HistoricalRecords()
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Orders'
        indexes = [
            models.Index(fields=['order_date']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"Order #{self.pk} by {self.buyer.client_name if self.buyer else 'Unknown'} - {self.status.title()}"

    @property
    def total_paid(self):
        return self.payments.aggregate(total=models.Sum('amount_paid'))['total'] or 0

    @property
    def amount_due(self):
        return (self.total_amount or 0) - self.total_paid

    @property
    def is_fully_fulfilled(self):
        return all(item.is_delivered for item in self.order_items.all())

    @property
    def total_cost_sum(self):
        return sum(item.total_price for item in self.order_items.all())
      
    def update_totals(self):
        totals = self.order_items.aggregate(
            total_items=models.Count('id'),
            total_amount=Sum('total_price')
        )
        self.total_items = totals['total_items'] or 0
        self.total_amount = totals['total_amount'] or 0
        self.save(update_fields=['total_items', 'total_amount'])

    def update_payment_status(self):
        total_paid = self.total_paid
        total_amount = self.total_amount or 0
        
        if self.is_paid and self.is_fully_fulfilled:
           self.status = OrderStatus.COMPLETED
           self.save(update_fields=['status'])
        
        if total_paid >= total_amount:
            self.is_paid = True
            payment_status = PaymentStatusChoices.FULL
        elif total_paid > 0:
            self.is_paid = False
            payment_status = PaymentStatusChoices.PARTIAL
        else:
            self.is_paid = False
            payment_status = PaymentStatusChoices.UNPAID

        self.save(update_fields=['is_paid'])

        latest_payment = self.payments.last()
        
        if  latest_payment and latest_payment.payment_status != payment_status:
            latest_payment.payment_status = payment_status
            latest_payment.save(update_fields=['payment_status'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='order_items')
    harveststock = models.ForeignKey(HarvestStockAggregate, on_delete=models.CASCADE, related_name='order_items', null=True, blank=True)
    quantity = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_price = models.DecimalField(max_digits=15, decimal_places=2, editable=False, default=0)

    is_delivered = models.BooleanField(default=False)
    notes = models.TextField(default="", blank=True)

    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Order Items'
        unique_together = ('order', 'harveststock')

    def __str__(self):
        crop = self.harveststock.crop.name if self.harveststock else 'Unknown'
        grade = self.harveststock.grade.name if self.harveststock else ''
        return f"{crop} - {grade} - {self.quantity} units"

    def clean(self):
        if self.quantity <= 0:
            raise ValidationError("Quantity must be greater than zero.")
        if self.harveststock and self.harveststock.total_quantity < self.quantity:
            raise ValidationError("Insufficient stock for this item.")
    
    def get_price_from_pricetable(self):
        return PriceTable.objects.filter(
            crop=self.harveststock.crop,
            cropvariety=self.harveststock.cropvariety,  #review and correct stock aggregate to save cropvariety
            grade=self.harveststock.grade,
            unit=self.harveststock.unit,
            market_center=self.harveststock.market_centre
        ).order_by('-from_date').first()

        # price_entry = self.get_price_from_pricetable()
        # if not price_entry:
        #     raise ValidationError("No price entry found for the selected crop and grade.")
        # self.unit_price = price_entry.selling_price or 0

    def get_total_cost(self):
        return self.quantity * self.unit_price

    def adjust_stock(self, quantity_diff, price_diff):
        stock = self.harveststock
        if stock.total_quantity + quantity_diff < 0:
            raise ValueError("Insufficient stock to complete this operation.")
        stock.total_quantity += quantity_diff
        stock.total_value += price_diff
        stock.save(update_fields=['total_quantity', 'total_value'])
    
        if self.harveststock:
            if self.harveststock.total_quantity < self.quantity:
                raise ValidationError("Insufficient stock for this item.")


    def save(self, *args, **kwargs):
        if not self._state.adding and self.is_delivered:
                raise ValidationError("You cannot modify an item that has already been delivered.")
            
        with transaction.atomic():
            is_new = self._state.adding

            if self.harveststock:
                price_entry = self.get_price_from_pricetable()
                if price_entry:
                    self.unit_price = price_entry.selling_price or 0

            self.total_price = self.get_total_cost()
    
            # On new order item, reduce stock by quantity            
            if not is_new:
                old_item = OrderItem.objects.get(pk=self.pk)
                quantity_diff = self.quantity - old_item.quantity
                price_diff = self.total_price - old_item.total_price
            else:
                quantity_diff = -self.quantity  # subtract from stock
                price_diff = -self.total_price

            if self.harveststock:
                self.adjust_stock(quantity_diff, price_diff)

            super().save(*args, **kwargs)
            self.order.update_totals()



    
#SALE ORDER PAYMENTS and Approvals
class PaymentProvider(ActiveStatusModel):
    name = models.CharField(max_length=100)
    code = models.CharField(max_length=25)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        abstract = True
        ordering = ['-created_at']
        unique_together = ('name', 'code')

    def __str__(self):
        return f"{self.name} - {self.code}"

class MobilePayment(PaymentProvider):
    class Meta:
        verbose_name_plural = 'Mobile Money'

class BankPayment(PaymentProvider):
    class Meta:
        verbose_name_plural = 'Banks'
        
class ApprovalStatusChoices(models.TextChoices):
    PENDING = 'pending', 'Pending'
    APPROVED = 'approved', 'Approved'
    REJECTED = 'rejected', 'Rejected'

class PaymentMethod(models.TextChoices):
    CASH = 'cash', 'Cash'
    MOBILE_MONEY = 'mobile_money', 'Mobile Money'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'

class PaymentStatusChoices(models.TextChoices):
    UNPAID = 'unpaid', 'Unpaid'
    PARTIAL = 'partial_payment', 'Partial Payment'
    FULL = 'full_payment', 'Full Payment'


class Payment(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='payments')
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    payment_date = models.DateTimeField(default=timezone.now)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    payment_status = models.CharField(max_length=20, choices=PaymentStatusChoices.choices, default=PaymentStatusChoices.UNPAID)

    mobile_provider = models.ForeignKey(MobilePayment, on_delete=models.SET_NULL, null=True, blank=True, related_name='mobile_payments')
    bank_provider = models.ForeignKey(BankPayment, on_delete=models.SET_NULL, null=True, blank=True, related_name='bank_payments')

    reference_number = models.CharField(max_length=14, null=True, blank=True, verbose_name='Mobile/Bank Number')
    transaction_code = models.CharField(max_length=100, null=True, blank=True)
    paid_by = models.CharField(max_length=255, null=True, blank=True)
  
    payin_slip = models.ImageField(
        upload_to='payments/slips/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Proof of Payment'
    )
    
    notes = models.TextField(blank=True, default="")

    approval_status = models.CharField(
        max_length=10,
        choices=ApprovalStatusChoices.choices,
        default=ApprovalStatusChoices.PENDING,
        help_text="Admin approval required for Bank or Mobile payments."
    )
    approved_by = models.ForeignKey(
        User, on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='payments_approved',
        help_text="User who approved or rejected the payment"
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='payments_created')
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Payment'
        verbose_name_plural = 'Order Payments'

    # def __str__(self):
    #      return f"Payment for Order #{self.order.pk}" if self.order_id else "Unassigned Payment"


    def __str__(self):
         return f"Payment of {self.amount_paid} for Order #{self.order}" if self.order else f"Payment of {self.amount_paid} (No Order linked)"
    
    def clean(self):
        #super().clean()
        errors = {}
        if self.amount_paid <= 0:
            errors['amount_paid'] = "Payment amount must be greater than zero."

        if self.order and self.amount_paid > self.order.amount_due:
            errors['amount_paid'] = f"Payment exceeds amount due ({self.order.amount_due})."

        if self.payment_method == PaymentMethod.MOBILE_MONEY and not self.mobile_provider:
            errors['mobile_provider'] = "Please select a Mobile Money provider."

        if self.payment_method == PaymentMethod.BANK_TRANSFER and not self.bank_provider:
            errors['bank_provider'] = "Please select a Bank provider."

        if errors:
            raise ValidationError(errors)

        # if self.payment_method in [PaymentMethod.MOBILE_MONEY, PaymentMethod.BANK_TRANSFER]:
        #     if self.approval_status != ApprovalStatusChoices.APPROVED:
        #         raise ValidationError("This payment type requires approval before being processed.")


    def save(self, *args, **kwargs):
        if self.payin_slip:
            self.payin_slip = resize_image(self.payin_slip)


        super().save(*args, **kwargs)


#order payments balance by buyers
class Balance(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='balance')
    total_due = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    notes = models.TextField(blank=True, default="")
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='balances_created')
    created_at = models.DateTimeField(auto_now_add=True)
    history = HistoricalRecords()

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Order Payment Balance'
        verbose_name_plural = 'Order Payment Balances'
        constraints = [
            models.CheckConstraint(check=Q(amount_paid__gte=0), name='amount_paid_gte_0'),
            models.CheckConstraint(check=Q(total_due__gte=0), name='total_due_gte_0'),
        ]

    def __str__(self):
        return f"Balance for Order #{self.order.id if self.order_id else 'N/A'} - Due: {self.total_due}, Paid: {self.amount_paid}"

    def update_balance(self):
        if not self.order:
            return  # Safety check to avoid crashing if order is None
        self.total_due = self.order.total_amount or 0
        self.amount_paid = self.order.total_paid or 0
        self.save(update_fields=['total_due', 'amount_paid'])
   
   
        
class Fulfillment(ActiveStatusModel):
    order = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='fulfillments')
    delivered_quantity = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_date = models.DateTimeField(default=timezone.now)
    is_fulfilled = models.BooleanField(default=False)
    notes = models.TextField(default="")
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='fulfillment_created')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Purchase Order Fulfillments'

    def __str__(self):
        return f"{self.delivery_date}, - {self.order}, - {self.delivered_quantity}, for  {self.order.notes}"


class Spoilage(ActiveStatusModel):
    SPOILAGE_STATUS = [
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
    ]
    spoilage_date = models.DateTimeField(default=timezone.now)  
    orderitem = models.ForeignKey(OrderItem, on_delete=models.CASCADE, related_name='orderspoilage')
    quantity_spoiled = models.DecimalField(max_digits=10, decimal_places=2)
    photo_evidence = models.ImageField(
        upload_to='order/spoilage/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Evidence'
    )
    notes = models.TextField(default="")
    status = models.CharField(max_length=20, choices=SPOILAGE_STATUS, default='Pending') 
    reported_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='spoilage_created')
    confirmed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='spoilage_confirmation')
    confirmation_note = models.TextField(default="")
    confirmed_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    class Meta:
        ordering = ['-reported_at']
        verbose_name_plural = 'Purchase Order Spoilage'

    def __str__(self):
        return f"{self.orderitem}, - {self.quantity_spoiled} spoiled"
    

 ###<<<<<<<<<<<<<<<<<<<<<<< END OF SALES AND MARKETING MODULE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#####################
###<<<<<<<<<<<<<<<<<<<<<<<   END OF SALES AND MARKETING MODULE >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>#####################            
 
class Delivery(ActiveStatusModel):
    #transaction = models.ForeignKey(Transaction, on_delete=models.CASCADE, null=True, blank=True)
    order_item = models.ForeignKey(OrderItem, on_delete=models.CASCADE, null=True)
    volume_delivered = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_receive = models.PositiveIntegerField(null=True, blank=True, default=0) 
    delivery_date = models.DateTimeField(default=timezone.now, blank=True, null=True)
    date = models.DateField()   
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='delivery_created')
    confirm_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='delivery_confirmation')
    confirm_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Delivery'
    
    def __str__(self):
        return f"{self.order_item.order}, {self.volume_delivered}, - {self.created_by.first_name}, {self.created_by.last_name}"

class Transaction(ActiveStatusModel):
    CROP_PURCHASE = 'purchase'
    CROP_DELIVERY = 'delivery'

    TRANSACTION_TYPE = [
        (CROP_PURCHASE, 'Purchase'),
        (CROP_DELIVERY, 'Delivery'),
    ]

    date = models.DateField()
    order = models.ForeignKey(Order, on_delete=models.CASCADE, null=True, blank=True)
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True)
    aic = models.ForeignKey(AIC, on_delete=models.CASCADE, null=True, blank=True)
    buyer = models.ForeignKey(Buyer, on_delete=models.CASCADE, null=True, blank=True, related_name='order_by')
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    amount_bal = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='transaction_created')
    

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Transaction'

    def __str__(self):
        return f"{self.transaction_type}, {self.volume}, - {self.total_amount}"




class FinancialDistribution(models.Model):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    total_revenue = models.DecimalField(max_digits=10, decimal_places=2)
    aic_markup = models.DecimalField(max_digits=10, decimal_places=2)
    input_costs = models.DecimalField(max_digits=10, decimal_places=2)
    beneficiary_earnings = models.DecimalField(max_digits=10, decimal_places=2)

    def distribute_revenue(self):
        # Calculate markup (e.g., 20% of total revenue)
        self.aic_markup = self.total_revenue * Decimal('0.20')

        # Deduct input costs
        remaining_after_markup = self.total_revenue - self.aic_markup
        self.beneficiary_earnings = remaining_after_markup - self.input_costs

        # Save the distribution
        self.save()
        
class InputDealer(ActiveStatusModel):
    name = models.CharField(max_length=100)
    email = models.CharField(max_length=100, blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)
    contactperson = models.CharField(max_length=100, blank=True, null=True)
    telephone = models.CharField(max_length=15, blank=True, null=True)
    website = models.CharField(max_length=100, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='farminput/dealer/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    # cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farm Input Dealer'
        
    def __str__(self):
        return self.name
    
class FarmInputCategory(ActiveStatusModel):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(
        upload_to='farminput/category/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    ) 
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farm Input Category'
        
    def __str__(self):
        return self.name
    
class FarmInput(ActiveStatusModel):
    inputcategory = models.ForeignKey(FarmInputCategory, on_delete=models.CASCADE)
    inputdealer = models.ForeignKey(InputDealer, on_delete=models.CASCADE)
    description = models.TextField(blank=True, null=True)
    quantity_received = models.IntegerField(default=0)  # Remove 'max_length'
    cost_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    expiry_date = models.DateTimeField(null=True, blank=True)
    photo = models.ImageField(
        upload_to='farminput/photos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png']),
            validate_file_size
        ],
        verbose_name='Attach Photo'
    )
    confirmation = models.IntegerField(default=0)  # Remove 'max_length'
    confirm_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmed_farm_inputs')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_farm_inputs')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farm Input Receivable'

    def __str__(self):
         return f"{self.inputcategory.name} - {self.inputdealer.name} - {self.quantity_received}"

    @property
    def available_quantity(self):
        distributed_quantity = self.inputedodistribution_set.aggregate(Sum('quantity'))['quantity__sum'] or 0
        return self.quantity_received - distributed_quantity
    
    @property
    def available_quantity(self):
        distributed_quantity = InputEdoDistribution.objects.filter(
            farm_input=self
        ).aggregate(total_distributed=Sum('quantity'))['total_distributed'] or 0
        return self.quantity_received - distributed_quantity
class InputEdoDistribution(ActiveStatusModel):
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    farm_input = models.ForeignKey(FarmInput, on_delete=models.CASCADE)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    distributed_by = models.ForeignKey(AIC, on_delete=models.CASCADE)
    distribution_date = models.DateField(auto_now_add=True)
    confirmation = models.IntegerField(default=0)  # Remove 'max_length'
    confirm_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmed_edo_distributions')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_edo_distributions')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farm Input Edo Distribution'

    def save(self, *args, **kwargs):
        # Ensure farm input quantity is not over-allocated
        if self.farm_input.available_quantity < self.quantity:
            raise ValueError(f"Insufficient quantity in {self.farm_input} to distribute.")
        super().save(*args, **kwargs)
    
    # Calculate the total cost
        self.total_cost = self.quantity * self.farm_input.cost_per_unit

    @property
    def remaining_quantity(self):
        distributed = InputDistribution.objects.filter(
            farm_input=self.farm_input, distributed_by=self.supervisor
        ).aggregate(total_distributed=Sum('quantity'))['total_distributed'] or 0
        return self.quantity - distributed
    
    # def __str__(self):
    #     return f"{self.supervisor} - {self.farm_input.name} - {self.quantity}"  
    def __str__(self):
        # Customize the representation
        return f"{self.farm_input.inputcategory.name} - Quantity: {self.quantity}, Unit Cost: {self.unit_cost}" 
    
class InputDistribution(ActiveStatusModel):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    farm_input = models.ForeignKey(InputEdoDistribution, on_delete=models.CASCADE, related_name='edo_distributions')
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    distributed_by = models.ForeignKey(Supervisor, on_delete=models.CASCADE)
    distribution_date = models.DateField(auto_now_add=True)
    confirmation = models.IntegerField(default=0)  # Remove 'max_length'
    confirm_by = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='confirmed_distributions')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_distributions')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farm Input Distribution - Beneficiaries'

    # def save(self, *args, **kwargs):
    #     # Calculate total cost based on quantity and cost per unit
    #     self.total_cost = self.quantity * self.farm_input.cost_per_unit
    #     super().save(*args, **kwargs)
    
    def save(self, *args, **kwargs):
    # Ensure distributed_by is set before saving
        if not self.distributed_by:
            raise ValueError("The distributed_by field must be set before saving.")
        
        # Calculate the total cost
        self.total_cost = self.quantity * self.farm_input.unit_cost
         # Update supervisor's available quantity
        supervisor_distribution = InputEdoDistribution.objects.get(
            farm_input=self.farm_input.farm_input, supervisor=self.distributed_by
        )
        if supervisor_distribution.quantity < self.quantity:
            raise ValidationError("Insufficient quantity to distribute.")
        supervisor_distribution.quantity -= self.quantity
        supervisor_distribution.save()

        super().save(*args, **kwargs)


#AIC distributing Farm Input to Supervisor (EDO)  

#MOST OF THE SUPERVISOR MODULES
class NurseryData(models.Model):
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE)  # New field
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True)  # Many-to-many relationship with Crop 
    cropvariety = models.ForeignKey(CropVariety, on_delete=models.CASCADE, null=True, related_name='crop_variety') 
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)  # New field
    date_planted = models.DateTimeField(default=timezone.now)
    seeds_sown = models.IntegerField()
    seeds_germinated = models.IntegerField()
    seedlings_transplanted = models.IntegerField()
    avg_germination_rate = models.DecimalField(max_digits=5, decimal_places=2)
    avg_survival_rate = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Supervisor management fields
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='nurserydata_reviewed')  # Supervisor
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Nursery Data for {self.beneficiary.full_name} in {self.greenhouse_room}"

class SprayingMedthod(models.Model):
    method = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return self.method  # Or any other field that makes sense for display
    
class SprayingData(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True) 
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    date_sprayed = models.DateTimeField(default=timezone.now)
    chemical_used = models.CharField(max_length=100)
    dosage = models.DecimalField(max_digits=5, decimal_places=2)
    startTime = models.TimeField(blank=True, null=True)
    finishTime = models.TimeField(blank=True, null=True)
    sprayingMethod = models.ForeignKey(SprayingMedthod, on_delete=models.CASCADE, null=True, blank=True)
    sprayed_by = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True) 
    purpose = models.TextField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)    
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,related_name="sprayingdata_created")
    created_at = models.DateTimeField(default=timezone.now)
    
    # Supervisor management fields
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sprayingdata_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    #AIC Feedback management fields
    feedback = models.TextField(blank=True, null=True)
    feedback_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sprayingdata_feedback')
    feedback_at = models.DateTimeField(default=timezone.now)
    
    def __str__(self):
        return f"Spraying Data for {self.beneficiary.full_name} in {self.greenhouse_room}"

    

class TrellisingData(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True) 
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    date_trellised = models.DateField(default=timezone.now)
    method = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Supervisor management fields
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='trellisingdata_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Trellising Data for {self.beneficiary.full_name} in {self.greenhouse_room}"


class IrrigationData(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True) 
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    date_irrigated = models.DateField(default=timezone.now)    
    area_covered = models.DecimalField(max_digits=7, decimal_places=2, null=True, blank=True)
    water_quantity = models.DecimalField(max_digits=7, decimal_places=2)
    method = models.CharField(max_length=100)
    startTime = models.TimeField(blank=True, null=True)
    finishTime = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Supervisor management fields
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='irrigationdata_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Irrigation Data for {self.beneficiary.full_name} in {self.greenhouse_room}"
    
    def get_irrigation_records():
        records = IrrigationData.objects.all()
        for record in records:
            if record.startTime and record.finishTime:
                record.time_difference = record.finishTime - record.startTime
            else:
                record.time_difference = None
        return records

class HeightData(models.Model):
    crop = models.ForeignKey(Crop, on_delete=models.CASCADE, null=True, blank=True) 
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE)
    greenhouse_room = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE)
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    measurement_date = models.DateField(default=timezone.now)
    description = models.TextField(blank=True, null=True)
    average_height = models.DecimalField(max_digits=5, decimal_places=2)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=timezone.now)

    # Supervisor management fields
    status = models.CharField(max_length=10, choices=[('Pending', 'Pending'), ('Approved', 'Approved'), ('Denied', 'Denied')], default='Pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='heightdata_reviewed')
    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Height Data for {self.beneficiary.full_name} in {self.greenhouse_room}"

class Todo(ActiveStatusModel):
    TODOSTATE = [
        ('Open', 'Open'),
        ('Completed', 'Completed'),
        ('Cancel', 'Cancel'),
    ]
    description = models.TextField(blank=True, null=True)      
    todostate = models.CharField(max_length=20, choices=TODOSTATE, null=True, blank=True)
    expected_date = models.DateTimeField(default=now, null=True)
    days_left = models.IntegerField(null=True, blank=True)  # Removed max_length as it's invalid for IntegerField
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(default=now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Todo List'

    def __str__(self):
        return f"{self.description} - {self.created_at}"

    def save(self, *args, **kwargs):
        # Calculate the number of days left until the expected_date
        if self.expected_date:
            today = now().date()
            days_difference = (self.expected_date.date() - today).days
            self.days_left = days_difference
        else:
            self.days_left = None  # No expected date
        super().save(*args, **kwargs)


#<<<<<<<<<<<<<<<<<<<<<<<<<<<< ============== BILLING SYSTEMS MODELS ===============================>>>>>>>>>>>>>>>>>>

# Farm Season Model from the Front End, its known as the Farming Cycle
class FarmSeason(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, help_text="Record your farm season")
    description = models.TextField(blank=True, null=True)
    season_start_date = models.DateField(default=timezone.now)
    season_end_date = models.DateField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Farming Cycle'
        
    def __str__(self):
        return self.name

class BillableItem(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False, help_text="Enter the name of the billable item.")
    farmseason = models.ForeignKey(
        FarmSeason, null=True, blank=True, on_delete=models.CASCADE, 
        help_text="Select a farm season in which you want this billable item to be effected."
    )
    description = models.TextField(blank=True, null=True)
    is_public = models.BooleanField(default=False, help_text="If checked, accessible by all greenhouse locations")

    # Corrected ManyToManyField (removed on_delete)
    greenhouse = models.ManyToManyField(
        Greenhouse, blank=True, 
        help_text="Select applicable greenhouses (or leave empty if applies to all)."
    )
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Billable Items'
        
    def __str__(self):
        return self.name

# Cost Component for Billable Items
class BillableItemCost(models.Model):
    billable_item = models.ForeignKey(BillableItem, on_delete=models.CASCADE)
    greenhouse = models.ForeignKey('Greenhouse', null=True, blank=True, on_delete=models.CASCADE, help_text="If assigned, applies only to this greenhouse")
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Billable Item Cost'
        
    def __str__(self):
        return f"{self.billable_item.name} - {self.cost} ({'Global' if not self.greenhouse else self.greenhouse.name})"
    

class ServiceItem(models.Model):
    service_name = models.CharField(max_length=255) 
    farmseason = models.ForeignKey(FarmSeason, on_delete=models.CASCADE)   
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)      
    description = models.TextField(blank=True, null=True)   
    status = models.CharField(max_length=20, choices=[('Pending', 'Pending'), ('Under Review', 'Under Review'),('Completed', 'Completed')], default='Pending')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Service Items'
        
    def __str__(self):
        return f"{self.service_name} - {self.farmseason.name} - {self.created_at}" 

class ServiceRequest(models.Model):
    SERVICEREQUEST_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('canceled', 'Canceled'),
        ('under_review', 'Under Review'),  # New status
    ]
    supervisor = models.ForeignKey(Supervisor, on_delete=models.CASCADE, null=True, blank=True, related_name='edo_servicerequests')
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE, null=True, blank=True, related_name='edo_servicerequests_for_beneficiary')
    request_date = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=SERVICEREQUEST_STATUS_CHOICES, default='pending')
    description = models.TextField(null=True, blank=True)
    total_items = models.PositiveIntegerField(default=0, null=True, blank=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='servicerequest_created')
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    approve_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='servicerequest_fulfilled', blank=True)
    approve_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    approve_note = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Service Requests'
        
      
    def get_total_quantity(self):
        return sum(item.quantity for item in self.servicerequest_items.all())

    def get_total_cost(self):
        return sum(item.get_total_cost() for item in self.servicerequest_items.all())

    def update_totals(self):
        self.total_items = self.servicerequest_items.count()
        self.total_amount = self.get_total_cost()
        self.save()
        
    def is_fulfilled(self):
        return all(item.is_fulfilled for item in self.servicerequest_items.all())
    
    def __str__(self):
        return f"{self.description} - {self.supervisor.fullname} - {self.created_at}"
   # Service Request by Beneficiary
class ServiceRequestItem(models.Model):
    servicerequest = models.ForeignKey(ServiceRequest, on_delete=models.CASCADE, related_name='servicerequest_items')
    serviceitem = models.ForeignKey(ServiceItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(null=True, blank=True)
    unitcost = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    description = models.TextField(null=True, blank=True)
    is_fulfilled = models.BooleanField(default=False)  # New field to track delivery status
    created_at = models.DateTimeField(default=timezone.now, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='service_requestitem_created')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Service Request Items'
        
    def __str__(self):
        return f"{self.serviceitem.service_name} - {self.servicerequest.request_date} - {self.quantity} units"
    
    
    @property
    def total_cost(self):
        return self.quantity * self.unitcost
    
    def get_total_cost(self):
        return self.quantity * self.serviceitem.cost

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.servicerequest.update_totals()

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        self.servicerequest.update_totals()
    

# Invoice for Beneficiaries
class Invoice(models.Model):
    beneficiary = models.ForeignKey('Beneficiary', on_delete=models.CASCADE)
    farm_season = models.ForeignKey(FarmSeason, on_delete=models.CASCADE)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(default=timezone.now)
    status = models.CharField(max_length=20, choices=[('Unpaid', 'Unpaid'), ('Paid', 'Paid')], default='Unpaid')

    def generate_invoice(self):
        billable_items = BillableItem.objects.filter(applies_to_all=True) | BillableItem.objects.filter(greenhouse=self.beneficiary.assigned_tunnel.greenhouse)
        total_cost = sum(item.cost for item in billable_items)
        service_requests = ServiceRequest.objects.filter(beneficiary=self.beneficiary, status='Completed')
        service_total = sum(service.cost for service in service_requests)
        self.total_amount = total_cost + service_total
        self.save()

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Invoice'
        
    def __str__(self):
        return f"Invoice {self.id} - {self.beneficiary.full_name}"

# Payment Model
class InvoicePayment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(default=timezone.now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        total_paid = sum(payment.amount_paid for payment in Payment.objects.filter(invoice=self.invoice))
        if total_paid >= self.invoice.total_amount:
            self.invoice.status = 'Paid'
            self.invoice.save()

    def __str__(self):
        return f"Payment of {self.amount_paid} for Invoice {self.invoice.id}"
    
#<<<<<<<<<<<<<<<====================== END OF BILLING SYSTEMS MODELS ==================>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

   
class EquipmentCategory(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta: 
        ordering = ['-created_at']
        verbose_name_plural = 'Equipment Category'
        
    def __str__(self):
        return self.name
class Equipment(ActiveStatusModel):
    category = models.ForeignKey(EquipmentCategory, on_delete=models.CASCADE, null=True, blank=True, related_name='equipment_category') 
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta: 
        ordering = ['-created_at']
        verbose_name_plural = 'Equipments'
        
    def __str__(self):
        return self.name

class EquipmentPart(ActiveStatusModel):    
    equipment = models.ForeignKey(Equipment, on_delete=models.CASCADE, null=True, blank=True, related_name='equipment') 
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta: 
        ordering = ['-created_at']
        verbose_name_plural = 'Equipment Parts'
        
    def __str__(self):
        return self.name
class MaintenanceCode(ActiveStatusModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=10, unique=True)  # ISO country code, e.g., "GH" for Ghana
    description = models.TextField(null=True,  blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta: 
        ordering = ['created_at']
        verbose_name_plural = 'Maintenance Code'
        
    def __str__(self):
        return self.name


class EquipmentMaintenanceLog(ActiveStatusModel):
    REASON_FOR_RUN = [
        ('Pwr Outage', 'Pwr Outage'),
        ('Test', 'Test'),
        ('maintenance', 'Maintenance')
    ] 
    
    PART_USED = [
        ('replaced', 'Replaced'),
        ('repaired', 'Repaired'),
    ]
    REPAIR_STATUS = [
        ('completed', 'Completed'),
        ('in-progress', 'In Progress'),
    ] 
    TEST_STATUS = [
        ('resolved', 'Resolved'),
        ('not resolved', 'Not Resolved'),
    ] 
    date = models.DateTimeField(default=timezone.now)   
    code = models.ForeignKey(MaintenanceCode, on_delete=models.CASCADE, null=True, blank=True, related_name='maintenance_code')     
    part = models.ForeignKey(EquipmentPart, on_delete=models.CASCADE, null=True, blank=True, related_name='equipment_part') 
    part_use = models.CharField(max_length=20, choices=PART_USED, null=True, blank=True, verbose_name='Part Usage')
    status = models.CharField(max_length=20, choices=REPAIR_STATUS, null=True, blank=True, verbose_name='Repair Status')
    description = models.TextField(null=True,  blank=True)
    approved_by = models.CharField(max_length=255, verbose_name='Approved Person')
    performed_by = models.CharField(max_length=255, verbose_name='Engineer')
    performed_by_phone = models.CharField(max_length=15, verbose_name='Engineer Phone')
    tested_by = models.CharField(max_length=255, verbose_name='Tester')
    tested_by_phone = models.CharField(max_length=15, verbose_name='Tester Phone')
    test_feedback = models.CharField(max_length=20, choices=TEST_STATUS, verbose_name='Tester Feedback')
    maintenance_duration = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Maintenance Duration')
    maintenance_cost = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='Maintenance Cost')
    remarks = models.TextField(null=True,  blank=True, verbose_name='Remarks')
    created_at = models.DateTimeField(default=timezone.now)
        
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance Equipment Log'
        
    def __str__(self):
        return f"{self.date} - {self.code.name} {self.part.name}"