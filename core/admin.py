from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Donation, FoodRequest, Delivery, Feedback, Notification

class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('role', 'phone_number', 'address', 'is_approved')}),
    )
    list_display = ['username', 'email', 'role', 'is_approved', 'is_staff']

admin.site.register(User, CustomUserAdmin)
admin.site.register(Donation)
admin.site.register(FoodRequest)
admin.site.register(Delivery)
admin.site.register(Feedback)
admin.site.register(Notification)
