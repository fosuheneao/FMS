from django.contrib import admin

from yuapp.models import Order

# Register your models here.
from .models import *
from django.utils.html import format_html
# Customize the admin site headers
admin.site.site_header = "ControlCentral - YuGEP App"
admin.site.site_title = "Admin Portal"
admin.site.index_title = "Welcome to YuGEP Admin Portal"

    
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
    list_display = ('name', 'city', 'latitude','longitude', 'active')  # Fields to display in list view
    list_filter = ('name', 'water_tanks')  # Filter sidebar options
    search_fields = ('name', 'water_tanks')  # Searchable fields
    ordering = ('name', 'water_tanks',)  # Default ordering
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
    list_display = ('room_name', 'greenhouse', 'latitude','longitude', 'active')  # Fields to display in list view
    list_filter = ('room_name', 'greenhouse')  # Filter sidebar options
    search_fields = ('room_name', 'greenhouse')  # Searchable fields
    ordering = ('room_name', 'greenhouse',)  # Default ordering
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
    
    list_display = ('name', 'description',)  # Fields to display in list view
    list_filter = ('name', 'description',)  # Filter sidebar options
    search_fields = ('name', 'description',)  # Searchable fields
    ordering = ('name', 'description',)  # Default ordering
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
    
    list_display = ('full_name', 'gender', 'enterprise_name', 'nationalId','active')  # Fields to display in list view
    list_filter = ('full_name', 'gender')  # Filter sidebar options
    search_fields = ('full_name', 'enterprise_name', 'gender')  # Searchable fields
    ordering = ('full_name','gender', 'enterprise_name')  # Default ordering
    list_display_links = ('full_name',)  # Only field2 will link to the objec
    
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(Beneficiary, BeneficiaryModelAdmin)

# admin.site.register(Worker)

class WorkerModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by','created_at')
    
    list_display = ('full_name', 'gender', 'role', 'nationalId', 'from_date','to_date', 'active')  # Fields to display in list view
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

# admin.site.register(Supervisor)
class MaintenanceModelAdmin(admin.ModelAdmin):
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
admin.site.register(Maintenance, MaintenanceModelAdmin)


# admin.site.register(MaintenanceCost)
class MaintenanceCostModelAdmin(admin.ModelAdmin):
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
admin.site.register(MaintenanceCost, MaintenanceCostModelAdmin)


# admin.site.register(MaintenanceCost)
class BeneficiaryMaintenanceShareModelAdmin(admin.ModelAdmin):
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
admin.site.register(BeneficiaryMaintenanceShare,BeneficiaryMaintenanceShareModelAdmin)

# admin.site.register(MaintenanceCost)
class BeneficiaryMaintenanceShareModelAdmin(admin.ModelAdmin):
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
admin.site.register(Order,BeneficiaryMaintenanceShareModelAdmin)

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


#Farm inputs and logics
class InputDealerModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name', 'email', 'address','contactperson','telephone', 'website', 'cost_per_unit', 'notes', 'active')  # Fields to display in list view
    list_filter = ('name', 'email', 'address','contactperson','telephone',)  # Filter sidebar options
    search_fields = ('name', 'email', 'address','contactperson','telephone',)  # Searchable fields
    ordering = ('name', 'contactperson')  # Default ordering
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(InputDealer, InputDealerModelAdmin)


class FarmInputCategoryModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('name',  'description','active')  # Fields to display in list view
    list_filter = ('name',  'description',)  # Filter sidebar options
    search_fields = ('name',  'description',)  # Searchable fields
    ordering = ('name', 'contactperson')  # Default ordering
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(FarmInputCategory, FarmInputCategoryModelAdmin)


class FarmInputModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('inputcategory', 'inputdealer', 'description', 'quantity_received', 'cost_per_unit', 'expiry_date', 'active')  # Fields to display in list view
    list_filter = ('inputcategory', 'inputdealer', 'expiry_date',)  # Filter sidebar options
    search_fields = ('inputcategory', 'inputdealer', 'expiry_date',)  # Searchable fields
    ordering = ('expiry_date', 'inputcategory')  # Default ordering
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(FarmInput, FarmInputModelAdmin)


class InputDistributionModelAdmin(admin.ModelAdmin):
    # Exclude the 'created_by' field from the admin form
    exclude = ('created_by',)
    
    list_display = ('beneficiary', 'farm_input', 'quantity', 'total_cost', 'distributed_by', 'distribution_date', 'confirmation', 'active')  # Fields to display in list view
    list_filter = ('beneficiary', 'farm_input',  'distribution_date',)  # Filter sidebar options
    search_fields = ('beneficiary', 'farm_input',  'distribution_date',)  # Searchable fields
    ordering = ('distribution_date', 'beneficiary')  # Default ordering
    class Media:
         css = {
             'all': ('admin/css/custom_admin.css',)  # Path to your custom CSS
         }
         
    def save_model(self, request, obj, form, change):
        # Set the current user as 'created_by' only when the object is newly created
        if not change:  # 'change' is False when adding a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
admin.site.register(InputDistribution, InputDistributionModelAdmin)  


