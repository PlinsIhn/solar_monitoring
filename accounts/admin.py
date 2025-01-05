
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Channel, ChannelData

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    # Champs à afficher dans la liste des utilisateurs
    list_display = ('username', 'email', 'api_key', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    # Champs à afficher dans le formulaire d'édition
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal info', {'fields': ('email', 'api_key')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )

    # Champs affichés lors de la création d'un utilisateur
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active'),
        }),
    )

class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user')  # Affiche le nom et l'utilisateur dans l'interface admin
    search_fields = ('name', 'user__username')  # Permet de chercher par nom ou utilisateur

class ChannelDataAdmin(admin.ModelAdmin):
    list_display = ('channel', 'timestamp', 'value')  # Affiche les données importantes
    list_filter = ('channel',)  # Permet de filtrer par canal
    search_fields = ('channel__name',)  # Recherche par nom de canal

admin.site.register(Channel, ChannelAdmin)
admin.site.register(ChannelData, ChannelDataAdmin)
