
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
        form = ChannelForm(request.POST)
        if form.is_valid():
            channel = form.save(commit=False)
            channel.user = request.user
            channel.save()
            messages.success(request, "Canal ajouté avec succès.")
            return redirect('channel')
        else:
            messages.error(request, "Erreur lors de l'ajout du canal.")
    else:
        form = ChannelForm()

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

def get_channel_data(request, channel_id):
    channel = get_object_or_404(Channel, id=channel_id, user=request.user)
    data = ChannelData.objects.filter(channel=channel).order_by('timestamp')
    
    labels = [entry.timestamp.strftime("%H:%M:%S") for entry in data]
    values = [entry.value for entry in data]
    
    return JsonResponse({'labels': labels, 'values': values})







@login_required
def historique_view(request):
    # Logique pour afficher l'historique des données
    return render(request, 'historique.html')

@login_required
def aide_support_view(request):
    # Logique pour afficher l'aide et le support
    return render(request, 'aide_support.html')


from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import APIKey, Channel, ChannelData
import json

@csrf_exempt
def receive_data(request):
    if request.method == "POST":
        try:
            data = json.loads(request.body)
            api_key = data.get("api_key")
            channel_name = data.get("channel_name")
            value = data.get("value")

            # Valider la clé d'API
            try:
                api_key_instance = APIKey.objects.get(key=api_key)
                user = api_key_instance.user
            except APIKey.DoesNotExist:
                return JsonResponse({"error": "Invalid API key"}, status=403)

            # Valider le canal
            try:
                channel = Channel.objects.get(user=user, name=channel_name)
            except Channel.DoesNotExist:
                return JsonResponse({"error": "Channel not found"}, status=404)

            # Enregistrer les données
            ChannelData.objects.create(channel=channel, value=value)
            return JsonResponse({"message": "Data received successfully"}, status=200)

        except Exception as e:
            return JsonResponse({"error": str(e)}, status=400)

    return JsonResponse({"error": "Invalid request method"}, status=405)
