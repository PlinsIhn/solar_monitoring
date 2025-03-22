from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from accounts.models import CustomUser
import re

class SignupForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Adresse email")

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password1', 'password2')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'placeholder': "Entrez votre nom d'utilisateur",
            'class': 'form-control'
        })
        self.fields['email'].widget.attrs.update({
            'placeholder': "Entrez votre adresse email",
            'class': 'form-control'
        })
        self.fields['password1'].widget.attrs.update({
            'placeholder': "Entrez votre mot de passe",
            'class': 'form-control'
        })
        self.fields['password2'].widget.attrs.update({
            'placeholder': "Confirmez votre mot de passe",
            'class': 'form-control'
        })

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if len(username) < 4:
            raise ValidationError("Le nom d'utilisateur doit contenir au moins 4 caractères.")
        if not re.match(r'^[a-zA-Z0-9_ ]+$', username):
            raise forms.ValidationError(
                "Le nom d'utilisateur ne peut contenir que des lettres, chiffres, underscores (_) et espaces."
            )
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Cet email est déjà utilisé. Veuillez en choisir un autre.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        if len(password) < 4:
            raise ValidationError("Le mot de passe doit contenir au moins 4 caractères.")
        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.is_active = False  # L'utilisateur reste inactif jusqu'à l'activation
        if commit:
            user.save()
        return user
    

from .models import Channel

class ChannelForm(forms.ModelForm):
    class Meta:
        model = Channel
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Exemple : Temperature', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)  # Récupère l'utilisateur
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data['name']
        if Channel.objects.filter(name=name, user=self.user).exists():
            raise forms.ValidationError("Vous avez déjà créé un canal avec ce nom.")
        return name