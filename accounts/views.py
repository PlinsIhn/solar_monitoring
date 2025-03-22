
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.conf import settings
from .tokens import account_activation_token  
from .forms import SignupForm, ChannelForm
from .models import CustomUser, Channel
from django.contrib.auth.tokens import default_token_generator

def home(request):
    return render(request, 'home.html')

def signup_view(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = False  # L'utilisateur est inactif jusqu'à l'activation
            user.save()

            # Génération de l'UID et du jeton
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)

            # Préparation de l'e-mail
            domain = request.get_host()
            activation_link = f"http://{domain}/accounts/activate/{uid}/{token}/"
            message = f"Bonjour {user.username},\n\nCliquez sur ce lien pour activer votre compte : {activation_link}"
            user.email_user("Activation de compte", message)

            messages.success(request, "Un e-mail d'activation a été envoyé.")
            return redirect('signup')
    else:
        form = SignupForm()

    return render(request, 'registration/signup.html', {'form': form})

def activate_view(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = get_object_or_404(get_user_model(), pk=uid)
    except (TypeError, ValueError, OverflowError, get_user_model().DoesNotExist):
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return render(request, 'accounts/activation_success.html', {'user': user})
    else:
        messages.error(request, "Le lien d'activation est invalide ou a expiré.")
        return redirect('signup')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            user = CustomUser.objects.get(email=email)
            if user.check_password(password):
                if user.is_active:
                    user.backend = 'django.contrib.auth.backends.ModelBackend'
                    login(request, user)
                    return redirect('profile')
                else:
                    messages.error(request, 'Votre compte est inactif.')
            else:
                messages.error(request, 'Mot de passe incorrect.')
        except CustomUser.DoesNotExist:
            messages.error(request, "Aucun utilisateur n'a été trouvé avec cet email.")

    return render(request, 'accounts/login.html')



# Logout
def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def profile_view(request):
    user = request.user  # Utilisateur connecté
    context = {
        'username': user.username,
        'email': user.email,
        'api_key': user.api_key,
        'date_joined': request.user.date_joined,# Assurez-vous que le champ existe
        # Vous pouvez ajouter d'autres données ici si nécessaire
    }
    return render(request, 'profile.html', context)


@login_required
def channel_view(request):
    
    # Récupération des canaux de l'utilisateur connecté
    channels = Channel.objects.filter(user=request.user)

    # Gestion du formulaire d'ajout de canal
    if request.method == 'POST':
        form = ChannelForm(request.POST, user=request.user)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.user = request.user
            channel.save()
            messages.success(request, "Canal ajouté avec succès.")
            return redirect('channel')
        else:
            messages.error(request, "Ce canal est déjà ajouté")
    else:
        form = ChannelForm(user=request.user)

    return render(request, 'channel.html', {'channels': channels, 'form': form})

@login_required
def delete_channel(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, user=request.user)
    if request.method == 'POST':
        channel.delete()
        messages.success(request, "Canal supprimé avec succès.")
        return redirect('channel')

    return render(request, 'accounts/delete_channel.html', {'channel': channel})


from django.shortcuts import render, get_object_or_404
from .models import Channel, ChannelData
from django.http import JsonResponse

@login_required
def dashboard_view(request):
    if not request.user.is_authenticated:
        return redirect('login')

    channels = Channel.objects.filter(user=request.user)
    return render(request, 'dashboard.html', {'channels': channels})

from datetime import datetime
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Channel, ChannelData

def get_channel_data(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, user=request.user)

    # Récupérer les dates de début et de fin à partir des paramètres de requête
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Convertir les dates en objets datetime si elles sont présentes
    if start_date:
        start_date = datetime.strptime(start_date, '%Y-%m-%d')
    if end_date:
        end_date = datetime.strptime(end_date, '%Y-%m-%d')

    # Filtrer les données en fonction des dates
    data = ChannelData.objects.filter(channel=channel)

    if start_date:
        data = data.filter(timestamp__gte=start_date)
    if end_date:
        data = data.filter(timestamp__lte=end_date)

    # Trier les données par timestamp et limiter à 40 valeurs
    data = data.order_by('-timestamp')[:50]
    data = list(reversed(data))  # Remettre les données dans l'ordre chronologique

    labels = [entry.timestamp.strftime("%Y-%m-%d %H:%M:%S") for entry in data]
    values = [entry.value for entry in data]

    return JsonResponse({'labels': labels, 'values': values})











from django.http import JsonResponse
from django.contrib.auth import get_user_model
from .models import Channel, ChannelData
import json
from django.views.decorators.csrf import csrf_exempt
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

@csrf_exempt
def receive_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            api_key = data.get("api_key")
            entries = data.get("entries")

            if not isinstance(entries, list):
                return JsonResponse({"error": "Entries must be a list of data points"}, status=400)

            try:
                user = User.objects.get(api_key=api_key)
            except User.DoesNotExist:
                return JsonResponse({"error": "Invalid API key"}, status=403)

            channel_layer = get_channel_layer()

            for entry in entries:
                channel_name = entry.get("channel_name")
                value = entry.get("value")

                try:
                    channel = Channel.objects.get(user=user, name=channel_name)
                except Channel.DoesNotExist:
                    return JsonResponse({"error": f"Channel '{channel_name}' not found"}, status=404)

                # Sauvegarde en base de données
                new_data = ChannelData.objects.create(channel=channel, value=value)

                # 🔥 Envoi des données en temps réel via WebSocket
                async_to_sync(channel_layer.group_send)(
                    "sensor_data",
                    {
                        "type": "send_sensor_data",
                        "data": {
                            "channel": channel.id,
                            "channel_name": channel.name,
                            "value": new_data.value,
                            "timestamp": new_data.timestamp.strftime("%H:%M:%S"),
                        },
                    },
                )

            return JsonResponse({"message": "All data received successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)



from django.http import JsonResponse
from .models import ChannelData, Channel

def get_latest_data(request, channel_id):
    """Renvoie les dernières données du canal demandé"""
    channel = Channel.objects.filter(id=channel_id).first()
    if not channel:
        return JsonResponse({"error": "Canal introuvable"}, status=404)

    # Récupérer les 10 dernières valeurs
    latest_entries = ChannelData.objects.filter(channel=channel).order_by("-timestamp")[:10]
    
    labels = [entry.timestamp.strftime("%H:%M:%S") for entry in latest_entries]
    values = [entry.value for entry in latest_entries]

    return JsonResponse({"labels": labels[::-1], "values": values[::-1]})  # Inverser pour avoir le bon ordre



from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import ChannelData, Channel

@csrf_exempt  # Permet d'envoyer des requêtes POST sans token CSRF (si AJAX)
def test_graph(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)  # Récupérer les données JSON envoyées
            for key, value in data.items():
                if key.startswith("channel-"):
                    channel_id = key.split("-")[1]  # Extraire l'ID du canal
                    channel = Channel.objects.get(id=channel_id)
                    
                    # Enregistrer la donnée de test dans la base
                    ChannelData.objects.create(channel=channel, value=value)

            return JsonResponse({"success": True, "message": "Données enregistrées avec succès !"})
        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)})

    return JsonResponse({"success": False, "error": "Requête invalide"})


from django.http import JsonResponse
from accounts.models import ChannelData, Channel  # Importer les bons modèles

def get_latest_temperature(request):
    latest_temp = ChannelData.objects.filter(channel__name="temperature_ps").order_by('-timestamp').first()
    
    if latest_temp:
        return JsonResponse({"temperature_ps": latest_temp.value})  # Utilisation de `value`
    else:
        return JsonResponse({"temperature_ps": None})  # Aucune donnée trouvée


# views.py
from django.shortcuts import render
from .models import ChannelData


from django.shortcuts import render
from .models import ChannelData, Channel
from django.utils.dateparse import parse_date
@login_required
def historique(request):
    user = request.user  # Récupère l'utilisateur connecté
    channel_id = request.GET.get('channel')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # Filtrer les canaux de l'utilisateur connecté
    channels = Channel.objects.filter(user=user)

    # Filtrer les données en fonction des critères
    historique_data = ChannelData.objects.filter(channel__user=user).order_by('-timestamp')

    if channel_id:
        historique_data = historique_data.filter(channel_id=channel_id)

    if start_date:
        historique_data = historique_data.filter(timestamp__date__gte=parse_date(start_date))

    if end_date:
        historique_data = historique_data.filter(timestamp__date__lte=parse_date(end_date))

    

    return render(request, 'historique.html', {
        'historique_data': historique_data,
        'channels': channels,  # Liste filtrée des canaux de l'utilisateur
    })







from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib import messages
@login_required
def aide_support(request):
    if request.method == "POST":
        user_email = request.user.email  # Récupère l'email du user connecté
        user_name = request.user.username  # Récupère le nom du user
        subject = request.POST.get("subject", "Support Request")
        message = request.POST.get("message", "")

        if not message.strip():
            messages.error(request, "Le message ne peut pas être vide.")
            return redirect("aide_support")  # Redirige vers la page support

        full_message = f"De : {user_name} ({user_email})\n\n{message}"

        send_mail(
            subject,
            full_message,
            user_email,  # L'email de l'utilisateur qui envoie
            ['hrpirkt@gmail.com'],  # Destinataire
            fail_silently=False,
        )

        messages.success(request, "Votre message a été envoyé avec succès !")
        return redirect("aide_support")  # Redirige après l'envoi

    return render(request, "aide_support.html")


