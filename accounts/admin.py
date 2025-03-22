from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.utils.html import format_html
from .models import CustomUser, Channel, ChannelData
from django.core.paginator import Paginator

# Vue personnalisée pour afficher les utilisateurs et leurs canaux
def user_channels_view(request):
    users = CustomUser.objects.all()
    is_active_filter = request.GET.get('is_active')  # Récupère le filtre actif/inactif
    email_search = request.GET.get('email')  # Récupère le terme de recherche par email

    # Appliquer le filtre actif/inactif si nécessaire
    if is_active_filter in ['true', 'false']:
        users = users.filter(is_active=is_active_filter == 'true')

    # Appliquer la recherche par email si un terme est fourni
    if email_search:
        users = users.filter(email__icontains=email_search)

    # Pagination
    paginator = Paginator(users, 10)  # 10 utilisateurs par page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    user_data = []
    for user in page_obj:
        user_data.append({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'api_key': user.api_key,
            'is_active': user.is_active,
            'channels': user.channels.all(),
        })

    context = {
        'user_data': user_data,
        'page_obj': page_obj,  # Pour la pagination
        'total_users': users.count(),  # Nombre total d'utilisateurs
        'opts': CustomUser._meta
    }
    return render(request, 'admin/user_channels.html', context)

# Définition de l'admin personnalisé avec un onglet pour voir les utilisateurs et leurs canaux
class CustomAdminSite(admin.AdminSite):
    site_header = "Gestion de l'Administration"
    site_title = "Admin Personnalisé"
    index_title = "Accueil de l'administration"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('user-channels/', self.admin_view(user_channels_view), name="user_channels"),
        ]
        return custom_urls + urls

    def get_app_list(self, request):
        # Récupère la liste des applications et modèles existants
        app_list = super().get_app_list(request)

        # Ajoute un lien personnalisé sous l'onglet ACCOUNTS
        for app in app_list:
            if app['app_label'] == 'accounts':  # Remplace 'accounts' par le nom de ton application
                app['models'].append({
                    'name': 'Voir les utilisateurs',  # Nom du lien
                    'object_name': 'user_channels',  # Nom technique
                    'admin_url': '/admin/user-channels/',  # URL de la vue personnalisée
                    'view_only': True,  # Indique que ce n'est pas un modèle
                })

        return app_list

# Remplacement de l'admin par notre version personnalisée
admin_site = CustomAdminSite(name='custom_admin')

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'api_key', 'voir_channels')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('username', 'email')
    ordering = ('username',)

    def voir_channels(self, obj):
        return format_html('<a href="/admin/user-channels/">Voir les utilisateurs</a>')

    voir_channels.short_description = "Voir les utilisateurs et canaux"

@admin.register(Channel)
class ChannelAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'created_at')
    search_fields = ('name', 'user__username')
    list_filter = ('created_at',)

@admin.register(ChannelData)
class ChannelDataAdmin(admin.ModelAdmin):
    list_display = ('channel', 'timestamp', 'value')
    list_filter = ('channel',)
    search_fields = ('channel__name',)

# Enregistrement des modèles dans l'admin personnalisé
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(Channel, ChannelAdmin)
admin_site.register(ChannelData, ChannelDataAdmin)