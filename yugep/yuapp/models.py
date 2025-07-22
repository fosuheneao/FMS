from django.contrib.auth.models import User, Group
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
import random
import string

class ActiveStatusModel(models.Model):
    active = models.BooleanField(default=True)

    class Meta:
        abstract = True

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
    
# Model for TrendKnowledgeBank
class TrendKnowledgeBank(ActiveStatusModel):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True,  blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='trendknowledgebank/photos/', null=True, blank=True,  verbose_name="Attach Photo")
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
    photo = models.ImageField(upload_to='trendknowledgediscussion/photos/', null=True, blank=True,  verbose_name="Attach Photo")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Trend Knowledge Discussion'
        
    def __str__(self):
        return f"Discussion on {self.trend_knowledge_bank.title}"


# Model for WaterTank
class WaterTank(ActiveStatusModel):
    name = models.CharField(max_length=255)
    city = models.ForeignKey(City, on_delete=models.CASCADE, null=True, blank=True)  # Link to City
    capacity = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='watertanks/photos/', null=True, blank=True,  verbose_name="Attach Photo")
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
    photo = models.ImageField(upload_to='greenhouse/photos/', null=True, blank=True, verbose_name="Attach Photo")
    description = models.TextField(null=True, blank=True)
    marketing_centres = models.ManyToManyField(MarketingCentre, blank=True)  # Many-to-many relationship
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
   

    def __str__(self):
        return f"{self.name}, {self.city.name if self.city else 'No City'}, {self.city.district.region.country.name if self.city else 'No Country'}"

   
class GreenhouseRoom(ActiveStatusModel):
    room_name = models.CharField(max_length=255)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    photo = models.ImageField(upload_to='greenhouseroom/photos/', null=True, blank=True, verbose_name="Attach Photo")
    notes = models.TextField(null=True, blank=True)
    greenhouse = models.ForeignKey('Greenhouse', on_delete=models.CASCADE, related_name='rooms')  # One-to-many relationship
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
   
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Greenhouse Rooms'

    def __str__(self):
        return f"{self.room_name} in {self.greenhouse.name} assigned to {self.beneficiary.full_name if hasattr(self, 'beneficiary') and self.beneficiary else 'None'}"


# Model for Supervisors
class Supervisor(ActiveStatusModel):
    BENEFICIARY_GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female')
    ] 
    fullname = models.CharField(max_length=255)
    gender = models.CharField(max_length=20, choices=BENEFICIARY_GENDER_CHOICES, null=True, blank=True)
    age = models.PositiveIntegerField(verbose_name="Age", null=True, blank=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    photo = models.ImageField(upload_to='worker/photos/', null=True, blank=True, verbose_name='Passport Picture')
    nationalId = models.CharField(max_length=15, unique=True, null=True,  blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(upload_to='worker/photos/', null=True, blank=True,  verbose_name="Ghana Card Picture")   
    description = models.TextField(null=True,  blank=True)
    city = models.ManyToManyField(City, blank=True)  # Many-to-many relationship with Crop
    greenhouse = models.ManyToManyField(Greenhouse, blank=True)  # Many-to-many relationship with Crop
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Enterprise Development Officer'
        
    def __str__(self):
        return self.fullname
    
# Model for Crops
class Crop(ActiveStatusModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    photo = models.ImageField(upload_to='crop/photos/', null=True, blank=True,  verbose_name="Attach Picture")
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.name
    
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
    photo = models.ImageField(upload_to='beneficiary/photos/', null=True, blank=True,  verbose_name="Passport Picture")
    nationalId = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(upload_to='beneficiary/photos/', null=True, blank=True,  verbose_name="Ghana Card Picture")
    description = models.TextField(null=True,  blank=True)
    assigned_tunnel = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE, null=True, related_name='beneficiaries') 
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
        # Create user dynamically if not already assigned
        if not self.user:
            username = self.email.split('@')[0]
            password = self.generate_random_password()  # Generate random password
            is_staff = 1
            user = User.objects.create_user(username=username, email=self.email, password=password)
            user.is_staff = True 
            user.first_name = self.full_name.split(' ')[0]  # Set first name
            user.last_name = ' '.join(self.full_name.split(' ')[1:]) if len(self.full_name.split(' ')) > 1 else ''  # Set last name
            user.save()

            # Add the user to the 'beneficiary' group
            group, created = Group.objects.get_or_create(name='beneficiary')
            user.groups.add(group)

            # Assign the created user to the beneficiary
            self.user = user
            print({password})
            # Send email with login credentials
            # subject = 'Your Beneficiary Account Information'
            # message = f'Hello {self.full_name},\n\nYour account has been created.\nUsername: {username}\nPassword: {password}\n\nThank you!'
            # send_mail(subject, message, 'no-reply@alldayhost.com', [self.email])

        super().save(*args, **kwargs)
        
        
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
    photo = models.ImageField(upload_to='worker/photos/', null=True, blank=True,  verbose_name="Passport Picture")
    nationalId = models.CharField(max_length=15, unique=True, null=True, blank=True, verbose_name='Ghana Card')
    cardphoto = models.ImageField(upload_to='worker/photos/', null=True, blank=True,  verbose_name="Ghana Card Picture")
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
        return f"{self.full_name} ({self.role})"
    
# Model for CashAssigned with repayment period
class CashAssigned(ActiveStatusModel):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    repayment_period_from = models.DateField()
    repayment_period_to = models.DateField()
    notes = models.TextField(null=True,  blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigncash_created')
    created_at = models.DateTimeField(default=timezone.now)
   
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Cash Bank'
    
    def __str__(self):
        return f"Cash Assigned to {self.beneficiary.full_name}"

# Model for Repayment records
class Repayment(ActiveStatusModel):
    cash_assigned = models.ForeignKey(CashAssigned, on_delete=models.CASCADE)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2)
    bal_amount = models.DecimalField(max_digits=10, decimal_places=2)
    date_paid = models.DateField()
    notes = models.TextField(null=True,  blank=True)
    photo = models.ImageField(upload_to='repayment/photos/', null=True, blank=True, verbose_name='Attach Evidence')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='cashcollection_created')
    created_at = models.DateTimeField(default=timezone.now)
    
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
    photo = models.ImageField(upload_to='storeroom/photos/', null=True, blank=True, verbose_name='Upload Photo')
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
    photo = models.ImageField(upload_to='changingroom/photos/', null=True, blank=True, verbose_name='Upload Photo')
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


class Maintenance(ActiveStatusModel):
    MAINTENANCE_CHOICES = [
        ('watertank', 'Water Reservoir'),
        ('greenhouse', 'Greenhouse'),
        ('greenhouseroom', 'Greenhouse Room'),
        ('changingroom', 'Changing Room'),
        ('storeroom', 'Store Room')
    ]

    maintenance_type = models.CharField(max_length=20, choices=MAINTENANCE_CHOICES)
    watertank = models.ForeignKey(WaterTank, on_delete=models.CASCADE, null=True, blank=True)
    greenhouse = models.ForeignKey(Greenhouse, on_delete=models.CASCADE, null=True, blank=True)
    greenhouseroom = models.ForeignKey(GreenhouseRoom, on_delete=models.CASCADE, null=True, blank=True)
    changingroom = models.ForeignKey(ChangingRoom, on_delete=models.CASCADE, null=True, blank=True)
    storeroom = models.ForeignKey(StoreRoom, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    photo = models.ImageField(upload_to='maintenance/photos/', null=True, blank=True, verbose_name='Attach Photo')
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance'
        
    def __str__(self):
        return f"{self.get_maintenance_type_display()} Maintenance from {self.start_date}"

class MaintenanceCost(ActiveStatusModel):
    maintenance = models.ForeignKey(Maintenance, on_delete=models.CASCADE)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2)
    date_incurred = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance Cost'
        
    def __str__(self):
        return f"Cost for {self.maintenance} - {self.total_cost}"


class BeneficiaryMaintenanceShare(ActiveStatusModel):
    beneficiary = models.ForeignKey(Beneficiary, on_delete=models.CASCADE)
    maintenance_cost = models.ForeignKey(MaintenanceCost, on_delete=models.CASCADE)
    share_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Maintenance Cost Distribution'
        
    def __str__(self):
        return f"{self.beneficiary.name} Share for {self.maintenance_cost.maintenance}"


### buyer and sales model
class Buyer(ActiveStatusModel):
    client_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    contact_person = models.CharField(max_length=255, verbose_name='Contact Person')
    phone = models.CharField(max_length=15)  # Adjust the max length according to your needs
    email = models.EmailField(max_length=255)
    photo = models.ImageField(upload_to='buyers/photos/', null=True, blank=True, verbose_name='Upload Photo')  # Make sure you have the correct MEDIA settings
    shipping_address = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Buyer'
        
    def __str__(self):
        return self.client_name

