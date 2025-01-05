from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class EmailBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        UserModel = get_user_model()
        try:
            # Recherche de l'utilisateur par email
            user = UserModel.objects.get(email=username)
        except UserModel.DoesNotExist:
            return None

        # Vérifie le mot de passe
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        
        if not UserModel.objects.filter(email=username).exists():
            return None  # L'email n'existe pas

        return None

    def user_can_authenticate(self, user):
        """Vérifie si l'utilisateur est actif."""
        return getattr(user, 'is_active', False)
