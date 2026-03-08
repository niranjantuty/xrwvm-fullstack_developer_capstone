# from django.contrib import admin
# from .models import related models
from django.contrib import admin
from .models import CarMake, CarModel

# Registering models with their respective admins
admin.site.register(CarMake)
admin.site.register(CarModel)

# Register your models here.

# CarModelInline class

# CarModelAdmin class

# CarMakeAdmin class with CarModelInline

# Register models here
# Inline class for CarModel to be displayed within CarMake admin
class CarModelInline(admin.TabularInline):
    model = CarModel

# Admin class for CarMake with CarModelInline
class CarMakeAdmin(admin.ModelAdmin):
    inlines = [CarModelInline]
    list_display = ('name', 'country', 'founded_year')
    search_fields = ['name', 'country']

# Admin class for CarModel
class CarModelAdmin(admin.ModelAdmin):
    list_display = ('name', 'car_make', 'type', 'year', 'dealer_id')
    list_filter = ('car_make', 'type', 'year')
    search_fields = ['name', 'car_make__name']
