from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from .models import Profile

class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profil'
    fk_name = 'user'

class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'get_role', 'is_staff')
    list_select_related = ('profile',)
    
    def get_role(self, instance):
        return instance.profile.role
    get_role.short_description = 'Rôle'
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'telephone', 'created_at')
    list_filter = ('role', 'created_at')
    search_fields = ('user__username', 'user__first_name', 'user__last_name', 'telephone')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Informations utilisateur', {
            'fields': ('user', 'role')
        }),
        ('Informations personnelles', {
            'fields': ('telephone', 'date_naissance', 'photo_profil', 'biographie')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

# Désenregistrer l'admin User par défaut et réenregistrer avec notre admin personnalisé
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)