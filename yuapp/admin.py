from django.contrib import admin
from django.http import JsonResponse
from yuapp.forms import PriceTableAdminForm
from django.utils.html import format_html
# Register your models here.
from .models import *
from django.utils.timezone import localtime
from django.utils.html import format_html
# Customize the admin site headers
admin.site.site_header = "ControlCentral - YuGEP App"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to YuGEP Admin Portal"


#######################################3 READING HISTORICAL RECORDS #####################################
#After applying, you get automatic history tracking:
#Every create, update, or delete action is saved.
#You can access history like:

# payment = Payment.objects.get(id=1)
# for record in payment.history.all():
#     print(record.amount_paid, record.history_date, record.history_user)
    
# Register your models here.
# admin.site.register(Country)
class CountryModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_at',)
    
    list_display = ('name', 'code','latitude', 'longitude')  # Fields to display in list view
    list_filter = ('name', 'code',) # Filter sidebar options
    search_fields = ('name',)  # Searchable fields
    ordering = ('name', 'code',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
        
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Country, CountryModelAdmin)


# admin.site.register(Region)
class RegionModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_at',)
    
    list_display = ('name', 'code','country', 'latitude', 'longitude')  # Fields to display in list view
    list_filter = ('name', 'code','country') # Filter sidebar options
    search_fields = ('name','country',)  # Searchable fields
    ordering = ('name', 'code','country',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Region, RegionModelAdmin)

# admin.site.register(District)
class DistrictModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_at',)
    
    list_display = ('name', 'code','region', 'latitude', 'longitude')  # Fields to display in list view
    list_filter = ('name', 'code','region') # Filter sidebar options
    search_fields = ('name','region',)  # Searchable fields
    ordering = ('name', 'code','region',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(District, DistrictModelAdmin)

#admin.site.register(City)
class CityModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_at',)
    
    list_display = ('name', 'code','district', 'latitude', 'longitude', 'show_map', 'created_at')  # Fields to display in list view
    list_filter = ('name', 'code','district') # Filter sidebar options
    search_fields = ('name','district',)  # Searchable fields
    ordering = ('name', 'code','district',)  # Default ordering
    
    # list_display = ('name', 'show_map')

    def show_map(self, obj):
        # Creates a clickable link with city name that opens a modal
        return format_html(
            '<a href="#" class="show-map" data-lat="{}" data-lng="{}">View Map</a>',
            obj.latitude, obj.longitude
        )
    show_map.short_description = "City Map"
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def created_at_date(self, obj):
        return obj.created_at.date()  # Extract only the date part

    created_at_date.short_description = 'Created At'  # Change column name in the list view
    
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(City, CityModelAdmin)

# admin.site.register(MarketingCentre)
class MarketingCentreModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    list_display = ('name', 'location', 'active')  # Fields to display in list view
    list_filter = ('name', 'city')  # Filter sidebar options
    search_fields = ('name', 'location')  # Searchable fields
    ordering = ('name', 'location',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(MarketingCentre, MarketingCentreModelAdmin)

#buyer auto created by
# admin.site.register(GreenhouseRoom)
class GreenhouseModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    list_display = ('name', 'city', 'latitude','longitude', 'cost_component', 'number_of_rooms', 'marketing_centres', 'active')  # Fields to display in list view
    list_filter = ('name', 'water_tanks','number_of_rooms', 'marketing_centres',)  # Filter sidebar options
    search_fields = ('name', 'water_tanks', 'marketing_centres',)  # Searchable fields
    ordering = ('name', 'water_tanks','cost_component','number_of_rooms','marketing_centres',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Greenhouse, GreenhouseModelAdmin)

#buyer auto created by
# admin.site.register(GreenhouseRoom)
class GreenhouseRoomModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    list_display = ('room_name', 'greenhouse', 'latitude','longitude', 'shared_cost', 'assign', 'active')  # Fields to display in list view
    list_filter = ('room_name', 'greenhouse','shared_cost',)  # Filter sidebar options
    search_fields = ('room_name', 'greenhouse')  # Searchable fields
    ordering = ('room_name', 'greenhouse','shared_cost',)  # Default ordering
    list_display_links = ('room_name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(GreenhouseRoom, GreenhouseRoomModelAdmin)


#buyer auto created by
# admin.site.register(WaterTank)
class WaterTankModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    list_display = ('name', 'capacity', 'city', 'latitude','longitude', 'active')  # Fields to display in list view
    list_filter = ('name', 'capacity', 'city')  # Filter sidebar options
    search_fields = ('name', 'capacity', 'city')  # Searchable fields
    ordering = ('name', 'capacity', 'city')  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(WaterTank, WaterTankModelAdmin)


# admin.site.register(TrendKnowledgeBank)
class TrendKnowledgeBankModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','created_at')
    
    list_display = ('title', 'description','latitude', 'longitude', 'created_at')  # Fields to display in list view
    list_filter = ('title', 'description','created_at') # Filter sidebar options
    search_fields = ('title',)  # Searchable fields
    ordering = ('title', 'description',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def created_at_date(self, obj):
        return obj.created_at.date()  # Extract only the date part

    created_at_date.short_description = 'Created At'  # Change column name in the list view


    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(TrendKnowledgeBank, TrendKnowledgeBankModelAdmin)


# admin.site.register(TrendKnowledgeDiscussion)
class TrendKnowledgeDiscussionModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','created_at')
    
    list_display = ('trend_knowledge_bank', 'discussion',)  # Fields to display in list view
    list_filter = ('trend_knowledge_bank', 'discussion',)  # Filter sidebar options
    search_fields = ('trend_knowledge_bank', 'discussion',)  # Searchable fields
    ordering = ('trend_knowledge_bank', 'discussion',)  # Default ordering
    list_display_links = ('trend_knowledge_bank',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(TrendKnowledgeDiscussion, TrendKnowledgeDiscussionModelAdmin)


class CropModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'description', 'estimatedyield',)  # Fields to display in list view
    list_filter = ('name', 'description','estimatedyield',)  # Filter sidebar options
    search_fields = ('name', 'description',)  # Searchable fields
    ordering = ('name', 'description', 'estimatedyield',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Crop, CropModelAdmin)

class CropVarietyModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'crop', 'description',)  # Fields to display in list view
    list_filter = ('name', 'crop', 'description',)  # Filter sidebar options
    search_fields = ('name', 'crop',)  # Searchable fields
    ordering = ('name', 'crop',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(CropVariety, CropVarietyModelAdmin)

#buyer auto created by
class BuyerModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    list_display = ('client_name', 'location', 'contact_person', 'phone','email', 'active')  # Fields to display in list view
    list_filter = ('client_name', 'location', 'contact_person')  # Filter sidebar options
    search_fields = ('client_name', 'location', 'contact_person')  # Searchable fields
    ordering = ('client_name', 'location', 'contact_person')  # Default ordering
    list_display_links = ('client_name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Buyer, BuyerModelAdmin)

# admin.site.register(Crop)
#admin.site.register(Beneficiary)
class BeneficiaryModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','user') # Exclude the user field since it's created dynamically
    
    list_display = ('full_name', 'gender', 'enterprise_name', 'nationalId','assigned_tunnel','active')  # Fields to display in list view
    list_filter = ('full_name', 'gender','assigned_tunnel',)  # Filter sidebar options
    search_fields = ('full_name', 'enterprise_name', 'gender','assigned_tunnel',)  # Searchable fields
    ordering = ('full_name','gender', 'enterprise_name','assigned_tunnel',)  # Default ordering
    list_display_links = ('full_name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
            
            # Check if a greenhouse room is assigned and update the corresponding record
            assigned_greenhouse_room = form.cleaned_data.get('assigned_greenhouse_room')  # Adjust this field name as necessary
            if assigned_greenhouse_room:
                # Set assign to 0 in the corresponding GreenhouseRoom record
                greenhouse_room = GreenhouseRoom.objects.get(id=assigned_greenhouse_room.id)  # Fetch the greenhouse room
                greenhouse_room.assign = 0  # Set assign to 0
                greenhouse_room.save()  # Save the updated greenhouse room

        super().save_model(request, obj, form, change)

admin.site.register(Beneficiary, BeneficiaryModelAdmin)       
#     def save_model(self, request, obj, form, change):
#         # Set the current user as 'created_by' only when the object is newly created
#         if not change:  # 'change' is False when adding a new object
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
# admin.site.register(Beneficiary, BeneficiaryModelAdmin)

# admin.site.register(Worker)

class WorkerModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','created_at')
    
    list_display = ('full_name', 'gender', 'role', 'nationalId', 'from_date','to_date', 'active', 'created_by')  # Fields to display in list view
    list_filter = ('full_name', 'gender')  # Filter sidebar options
    search_fields = ('full_name', 'role', 'gender')  # Searchable fields
    ordering = ('full_name','gender', 'role')  # Default ordering
    list_display_links = ('full_name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def from_at_date(self, obj):
        return obj.from_date.date()  # Extract only the date part

    from_at_date.short_description = 'Engaged From'  # Change column name in the list view
    
    def to_at_date(self, obj):
        return obj.to_date.date()  # Extract only the date part

    to_at_date.short_description = 'Engaged To'  # Change column name in the list view
    
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Worker, WorkerModelAdmin)


class WorkerRoleModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','created_at')
    
    list_display = ('name', 'description','active')  # Fields to display in list view
    list_filter = ('name', )  # Filter sidebar options
    search_fields = ('name', 'description')  # Searchable fields
    ordering = ('name', 'description')  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(WorkerRole, WorkerRoleModelAdmin)

# admin.site.register(CashAssigned)
class CashAssignedModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by', 'created_at')
    
    list_display = ('beneficiary', 'amount', 'repayment_period_from', 'repayment_period_to', 'notes', 'created_at', 'active')  # Fields to display in list view
    list_filter = ('beneficiary',)  # Filter sidebar options
    search_fields = ('beneficiary',)  # Searchable fields
    ordering = ('beneficiary',)  # Default ordering
    list_display_links = ('beneficiary',)  # Only field2 will link to the objec

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(CashAssigned, CashAssignedModelAdmin)

# admin.site.register(Repayment)
class RepaymentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by', 'created_at')
    
    list_display = ('cash_assigned', 'amount_paid', 'bal_amount', 'date_paid', 'notes', 'created_at', 'active')  # Fields to display in list view
    list_filter = ('cash_assigned',)  # Filter sidebar options
    search_fields = ('cash_assigned',)  # Searchable fields
    ordering = ('cash_assigned',)  # Default ordering
    list_display_links = ('cash_assigned',)  # Only field2 will link to the objec

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Repayment, RepaymentModelAdmin)



# admin.site.register(StoreRoomAssign)
#store room auto created by
class StoreRoomModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'location', 'greenhouse','active')  # Fields to display in list view
    list_filter = ('name', )  # Filter sidebar options
    search_fields = ('name', 'description')  # Searchable fields
    ordering = ('name', 'description')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
    # fieldsets = (
    #     (None, {
    #         'fields': ('name',)
    #     }),
    #     ('Advanced options', {
    #         'classes': ('collapse',),
    #         'fields': ('greenhouse',),
    #     }),
    # )
    list_display_links = ('name',)  # Only field2 will link to the objec

    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(StoreRoom, StoreRoomModelAdmin)


#storeroom assign auto created by
class StoreRoomAssignModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('storeroom', 'beneficiary', 'assigned_at','active')  # Fields to display in list view
    list_filter = ('storeroom', )  # Filter sidebar options
    search_fields = ('storeroom', 'beneficiary')  # Searchable fields
    ordering = ('storeroom', 'beneficiary')  # Default ordering
    
    def created_at_date(self, obj):
        return obj.assigned_at.date()  # Extract only the date part

    created_at_date.short_description = 'Assigned on'  # Change column name in the list view
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(StoreRoomAssign, StoreRoomAssignModelAdmin)


#store room auto created by
class ChangingRoomModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'location', 'greenhouse','active')  # Fields to display in list view
    list_filter = ('name', 'location',)  # Filter sidebar options
    search_fields = ('name', 'location')  # Searchable fields
    ordering = ('name', 'location')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ChangingRoom, ChangingRoomModelAdmin)

# admin.site.register(ChangingRoomAssign)
class ChangingRoomAssignModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('changing_room', 'beneficiary', 'assigned_at','active')  # Fields to display in list view
    list_filter = ('changing_room', 'beneficiary',)  # Filter sidebar options
    search_fields = ('changing_room', 'beneficiary')  # Searchable fields
    ordering = ('changing_room', 'beneficiary')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ChangingRoomAssign, ChangingRoomAssignModelAdmin)

# admin.site.register(Supervisor)
class SupervisorAssignModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Supervisor, SupervisorAssignModelAdmin)

class SaleAgentAssignModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('fullname', 'nationalId', 'gender', 'age', 'marketingcentre', 'active')  # Fields to display in list view
    list_filter = ('fullname', 'nationalId', 'gender', 'marketingcentre',)  # Filter sidebar options
    search_fields = ('fullname', 'nationalId', 'gender', 'marketingcentre')  # Searchable fields
    ordering = ('fullname', 'nationalId', 'gender', 'marketingcentre',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(SaleAgent, SaleAgentAssignModelAdmin)


class FinanceModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('fullname', 'nationalId', 'gender', 'age', 'marketingcentre', 'active')  # Fields to display in list view
    list_filter = ('fullname', 'nationalId', 'gender', 'marketingcentre',)  # Filter sidebar options
    search_fields = ('fullname', 'nationalId', 'gender', 'marketingcentre')  # Searchable fields
    ordering = ('fullname', 'nationalId', 'gender', 'marketingcentre',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Finance, FinanceModelAdmin)

# admin.site.register(MaintenanceCost)
class GradeModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'description', 'active')  # Fields to display in list view
    list_filter = ('name', 'description',)  # Filter sidebar options
    search_fields = ('name', 'description')  # Searchable fields
    ordering = ('name', 'description')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Grade, GradeModelAdmin)


class HarvestModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('formatted_date', 'crop', 'grade', 'quantity', 'beneficiary', 'active', 'confirmation')  # Fields to display in list view
    list_filter = ('date', 'crop', 'grade', 'confirmation')  # Filter sidebar options
    search_fields = ('date', 'crop', 'grade')  # Searchable fields
    ordering = ('-date', 'crop', 'grade')  # Default ordering (most recent first)

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }

    def formatted_date(self, obj):
       #Format date as 'dd-mm-YYYY'."""
        return localtime(obj.date).strftime('%d-%m-%Y')

    formatted_date.short_description = "Date"  # Custom column header

    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Harvest, HarvestModelAdmin)


class ProductUnitModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'expression', 'description', 'active')  # Fields to display in list view
    list_filter = ('name', 'expression', 'description', 'active',)  # Filter sidebar options
    search_fields = ('name', 'expression', 'description', 'active')  # Searchable fields
    ordering = ('name', 'expression', 'description', 'active')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ProductUnit, ProductUnitModelAdmin)


# admin.site.register(MaintenanceCost)
# class BeneficiaryMaintenanceShareModelAdmin(admin.ModelAdmin):
#     # Exclude the 'created_by' field from the admin form
#     exclude = ('created_by',)
    
#     class Media:
#          css = {
#              'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
#          }
         
#     def save_model(self, request, obj, form, change):
#         # Set the current user as 'created_by' only when the object is newly created
#         if not change:  # 'change' is False when adding a new object
#             obj.created_by = request.user
#         super().save_model(request, obj, form, change)
# admin.site.register(BeneficiaryMaintenanceShare,BeneficiaryMaintenanceShareModelAdmin)





# Customize the admin index to include collapsible sections
class CustomAdminSite(admin.AdminSite):
    site_header = "My Custom Admin"
    
    def index(self, request, extra_context=None):
        # Call the default index view
        response = super().index(request, extra_context)
        
        # Add collapsible section header classes to the context
        response.context_data['model_list'] = format_html(
            '<div class="model-section-header">Models</div>'
            '<div class="model-section-items">'
            '{{ model_list }}'
            '</div>'
        )
        return response

# Use the custom admin site
admin_site = CustomAdminSite(name='custom_admin')


class AICModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('person_incharge', 'phone', 'email', 'active')  # Fields to display in list view
    list_filter = ('person_incharge', 'phone', 'email', 'active',)  # Filter sidebar options
    search_fields = ('person_incharge','active')  # Searchable fields
    ordering = ('person_incharge', 'active')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(AIC, AICModelAdmin)

class TransactionModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('date', 'order', 'supervisor', 'aic', 'buyer', 'volume', 'total_amount', 'amount_paid', 'amount_bal', 'transaction_type', 'active')  # Fields to display in list view
    list_filter = ('date', 'order', 'supervisor', 'aic', 'buyer', 'active',)  # Filter sidebar options
    search_fields = ('date', 'order', 'supervisor', 'aic', 'buyer', 'active')  # Searchable fields
    ordering = ('date', 'order', 'supervisor', 'aic', 'buyer', 'active')  # Default ordering
   
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Transaction, TransactionModelAdmin)

class DeliveryModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('date', 'order_item', 'volume_delivered', 'active')  # Fields to display in list view
    list_filter = ('date', 'order_item', 'volume_delivered', 'active',)  # Filter sidebar options
    search_fields = ('date', 'order_item', 'volume_delivered', 'active')  # Searchable fields
    ordering = ('date', 'order_item', 'volume_delivered', 'active')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Delivery, DeliveryModelAdmin)


class OrderModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ['buyer', 'order_date', 'status', 'is_paid', 'sale_order_type']
    list_filter = ['status', 'is_paid', 'sale_order_type']
    
    search_fields = ('buyer', 'order_date', 'notes', 'status', 'sale_order_type')  # Searchable fields
    ordering = ('buyer', 'order_date', 'notes', 'status', 'sale_order_type')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Order, OrderModelAdmin)


class SpoilageModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('reported_at',)
    
    list_display = ['spoilage_date', 'orderitem', 'quantity_spoiled', 'status', 'reported_by', 'confirmed_by']
    list_filter = ['status', 'reported_by', 'confirmed_by']
    
    search_fields = ('spoilage_date', 'status', 'reported_by', 'confirmed_by')  # Searchable fields
    ordering = ('spoilage_date', 'status', 'reported_by', 'confirmed_by')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.reported_at = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Spoilage, SpoilageModelAdmin)


class OrderItemModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('id', 'order', 'harveststock', 'quantity', 'unit_price', 'get_total_price')  # Fields to display in list view
    list_filter = ('order','created_at', 'harveststock')  # Filter sidebar options
    search_fields = ('order', 'harveststock')  # Searchable fields
    ordering = ('-created_at', 'harveststock') # Default ordering
   
    def get_total_price(self, obj):
        return obj.quantity * obj.unit_price
    get_total_price.short_description = 'Total Price'
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(OrderItem, OrderItemModelAdmin)


@admin.action(description="Approve selected payments")
def approve_payments(modeladmin, request, queryset):
    queryset.update(
        approval_status=ApprovalStatusChoices.APPROVED,
        approved_by=request.user,
        approved_at=timezone.now()
    )    
class PaymentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('order', 'payment_date', 'amount_paid', 'payment_method', 'approval_status', 'payin_slip_preview')  # notes Fields to display in list view
    
    list_filter = ('order', 'payment_date', 'amount_paid','payment_method', 'approval_status')  # Filter sidebar options
    search_fields = ('order', 'payment_date', 'amount_paid', 'payment_method', 'approval_status')  # Searchable fields
    ordering = ('order', 'payment_date', 'amount_paid','payment_method', 'approval_status')  # Default ordering
    
    actions = [approve_payments]
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
    
    def payin_slip_preview(self, obj):
        if obj.payin_slip:
            return format_html(f'<img src="{obj.payin_slip.url}" style="max-height: 60px;" />')
        return "No Image"
    payin_slip_preview.short_description = 'Slip Preview'
      
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Payment, PaymentModelAdmin)

class FulfillmentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('order', 'delivered_quantity', 'delivery_date','is_fulfilled', 'active')  # notes Fields to display in list view
    list_filter = ('order', 'delivered_quantity', 'delivery_date','is_fulfilled', 'active',)  # Filter sidebar options
    search_fields = ('order', 'delivered_quantity', 'delivery_date','is_fulfilled', 'active',)  # Searchable fields
    ordering = ('order', 'delivered_quantity', 'delivery_date','is_fulfilled', 'active')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Fulfillment, FulfillmentModelAdmin)

class BalanceModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('order', 'total_due', 'amount_paid', 'notes')  # notes Fields to display in list view
    list_filter = ('order', 'total_due', 'amount_paid', 'notes')  # Filter sidebar options
    search_fields = ('order', 'total_due', 'amount_paid', 'notes')  # Searchable fields
    ordering = ('order', 'total_due', 'amount_paid', 'notes')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Balance, BalanceModelAdmin)


class MobilePaymentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'code', 'description', 'active')  # notes Fields to display in list view
    list_filter = ('name', 'code', 'active')  # Filter sidebar options
    search_fields = ('name', 'code', 'active')  # Searchable fields
    ordering = ('name', 'code',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(MobilePayment, MobilePaymentModelAdmin)


class BankPaymentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'code', 'description', 'active')  # notes Fields to display in list view
    list_filter = ('name', 'code', 'active')  # Filter sidebar options
    search_fields = ('name', 'code', 'active')  # Searchable fields
    ordering = ('name', 'code',)  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(BankPayment, BankPaymentModelAdmin)

class PriceTableModelAdmin(admin.ModelAdmin):
    #form = PriceTableAdminForm
    exclude = ('created_by',)
    
    list_display = ('market_center', 'crop', 'cropvariety', 'grade', 'unit', 'price', 'selling_price', 'from_date', 'to_date', 'active')
    list_filter = ('market_center','crop', 'cropvariety', 'grade', 'unit', 'from_date', 'to_date', 'active',)
    search_fields = ('market_center','crop', 'cropvariety', 'grade', 'unit', 'price', 'from_date', 'to_date','active',)
    ordering = ('market_center','crop', 'cropvariety', 'grade', 'unit', 'active')

    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)
         }
        # js = ('admin/js/jquery.init.js', 'admin/js/dependent_crop_variety.js',)

    def save_model(self, request, obj, form, change):
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)

admin.site.register(PriceTable, PriceTableModelAdmin)

class ContractModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('worker', 'beneficiary', 'contract_type', 'from_date', 'to_date', 'charge_per_day', 'status', 'active',)
    search_fields = ('worker__full_name', 'beneficiary__full_name', 'active')
    list_filter = ('contract_type', 'status', 'active')
    ordering = ('contract_type', 'status')  # Default ordering
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Contract, ContractModelAdmin)


class FarmSeasonModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(FarmSeason, FarmSeasonModelAdmin)

class BillableItemModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(BillableItem, BillableItemModelAdmin)


class ServiceItemModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    #exclude = ('created_by',)  
    list_display = ('service_name', 'farmseason', 'cost','description', 'status', 'created_by','created_at',)  # Fields to display in list view
    list_filter = ('service_name', 'farmseason', 'cost','description', 'status', 'created_by',)  # Filter sidebar options
    search_fields = ('service_name', 'farmseason', 'cost','description', 'status',)  # Searchable fields
    ordering = ('service_name', 'farmseason', 'cost','description', 'status',)  # Default ordering
    list_display_links = ('service_name',)  # Only field2 will link to the objec
      
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ServiceItem, ServiceItemModelAdmin)

class ServiceRequestModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    #exclude = ('created_by',)  
    list_display = ('supervisor', 'total_items', 'total_amount','description', 'status', 'created_by','request_date',)  # Fields to display in list view
    list_filter = ('supervisor', 'total_items', 'total_amount','description', 'status', 'created_by','request_date',)  # Filter sidebar options
    search_fields = ('supervisor', 'total_items', 'total_amount','status',)  # Searchable fields
    ordering = ('supervisor', 'total_items', 'total_amount','status',)  # Default ordering
    list_display_links = ('description',)  # Only field2 will link to the objec
      
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ServiceRequest, ServiceRequestModelAdmin)

class ServiceRequestItemModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    #exclude = ('created_by',)  
    list_display = ('servicerequest', 'serviceitem', 'quantity','unitcost','description', 'is_fulfilled','created_by',)  # Fields to display in list view
    list_filter = ('servicerequest', 'serviceitem', 'quantity','unitcost', 'is_fulfilled','created_by')  # Filter sidebar options
    search_fields = ('servicerequest', 'serviceitem','is_fulfilled','created_by')  # Searchable fields
    ordering = ('servicerequest', 'serviceitem','is_fulfilled','created_by')  # Default ordering
    list_display_links = ('servicerequest','serviceitem',)  # Only field2 will link to the objec
      
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(ServiceRequestItem, ServiceRequestItemModelAdmin)

class MaintenanceCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'description')  # Fields to display in list view
    list_filter = ('name', 'code',)  # Filter sidebar options
    search_fields = ('name', 'code',)  # Searchable fields
    ordering = ('name', 'code',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(MaintenanceCategory, MaintenanceCategoryModelAdmin)


class MaintenanceModelAdmin(admin.ModelAdmin):
    list_display = ('date','category', 'name', 'code', 'description', 'is_tunnel', 'tunnel', 'last_fuel_filling_per_litre','fuel_pecentage_level_before_run','fuel_pecentage_level_after_run','startTime','finishTime','operator_name','department','reason',)  # Fields to display in list view
    list_filter = ('date','category', 'name', 'code', 'description', 'is_tunnel', 'tunnel','reason', 'department')  # Filter sidebar options
    search_fields = ('date','category', 'name', 'code', 'description', 'is_tunnel', 'tunnel','reason', 'department')  # Searchable fields
    ordering = ('date', 'category', 'is_tunnel','reason', 'department')  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Maintenance, MaintenanceModelAdmin)

########################################### MAINTENANCE MODULE#############################################
#equipment
class EquipmentModelAdmin(admin.ModelAdmin):
    list_display = ('name','category', 'description',  'code',)  # Fields to display in list view
    list_filter = ('name', 'category', 'code',)  # Filter sidebar options
    search_fields = ('name', 'category',  'code',)  # Searchable fields
    ordering = ('name', 'category', 'code',)  # Default ordering
    list_display_links = ('name', 'category', )  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Equipment, EquipmentModelAdmin)

#maintenanceCode
class MaintenanceCodeModelAdmin(admin.ModelAdmin):
    list_display = ('name','description',  'code',)  # Fields to display in list view
    list_filter = ('name','code',)  # Filter sidebar options
    search_fields = ('name', 'code',)  # Searchable fields
    ordering = ('name','code',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(MaintenanceCode, MaintenanceCodeModelAdmin)

#EquipmentPart
class EquipmentPartModelAdmin(admin.ModelAdmin):
    list_display = ('name','equipment','description',  'code',)  # Fields to display in list view
    list_filter = ('name', 'equipment','code',)  # Filter sidebar options
    search_fields = ('name', 'equipment', 'code',)  # Searchable fields
    ordering = ('name', 'equipment','code',)  # Default ordering
    list_display_links = ('name', 'equipment',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(EquipmentPart, EquipmentPartModelAdmin)


#EquipMaintenanceLogCategory
class EquipmentCategoryModelAdmin(admin.ModelAdmin):
    list_display = ('name','description',  'code',)  # Fields to display in list view
    list_filter = ('name','code',)  # Filter sidebar options
    search_fields = ('name', 'code',)  # Searchable fields
    ordering = ('name','code',)  # Default ordering
    list_display_links = ('name',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(EquipmentCategory, EquipmentCategoryModelAdmin)


#EquipMaintenanceLog
class EquipMaintenanceLogModelAdmin(admin.ModelAdmin):
    list_display = ('date', 'code', 'part', 'part_use','status','approved_by','performed_by','tested_by','maintenance_duration', 'maintenance_cost',)  # Fields to display in list view
    list_filter = ('date', 'code', 'part', 'part_use','status',)  # Filter sidebar options
    search_fields = ('date', 'code', 'part', 'part_use','status','approved_by','performed_by','tested_by',)  # Searchable fields
    ordering = ('date', 'code', 'part', 'part_use','status',)  # Default ordering
    list_display_links = ('date', 'code', 'part',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(EquipmentMaintenanceLog, EquipMaintenanceLogModelAdmin)
######################################################### MAINTENANCE MODULE ############################################################

class TodoModelAdmin(admin.ModelAdmin):
    list_display = ('description', 'todostate', 'expected_date','days_left','created_by',)  # Fields to display in list view
    list_filter = ('description','todostate', 'expected_date','days_left','created_by',)  # Filter sidebar options
    search_fields = ('description','todostate', 'expected_date','days_left',)  # Searchable fields
    ordering = ('todostate', 'expected_date','days_left','created_by',)  # Default ordering
    list_display_links = ('description',)  # Only field2 will link to the objec    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Todo, TodoModelAdmin)



class InvoiceModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Invoice, InvoiceModelAdmin)


class InvoicePaymentModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(InvoicePayment, InvoicePaymentModelAdmin)





################################## ADMIN PANEL VIEWS ####################################################
@admin.site.admin_view
def get_cropvarieties(request):
    crop_id = request.GET.get('crop_id')
    results = []
    if crop_id:
        crop_varieties = CropVariety.objects.filter(crop_id=crop_id)
        results = [{'id': cv.id, 'name': cv.name} for cv in crop_varieties]
    return JsonResponse({'results': results})
################################## END OF ADMIN PANEL VIEWS ####################################################