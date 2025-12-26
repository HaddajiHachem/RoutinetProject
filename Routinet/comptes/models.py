from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

class Profile(models.Model):
    """
    Modèle de profil étendant l'utilisateur Django
    """
    ROLE_CHOICES = [
        ('etudiant', 'Étudiant'),
        ('enseignant', 'Enseignant'),
        ('admin', 'Administrateur'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='etudiant')
    telephone = models.CharField(max_length=20, blank=True)
    date_naissance = models.DateField(null=True, blank=True)
    photo_profil = models.ImageField(upload_to='profils/', blank=True, null=True)
    biographie = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Profil"
        verbose_name_plural = "Profils"
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    def is_etudiant(self):
        return self.role == 'etudiant'
    
    def is_enseignant(self):
        return self.role == 'enseignant'
    
    def is_admin(self):
        return self.role == 'admin'
    
    def get_full_name(self):
        return self.user.get_full_name() or self.user.username

# Signal pour créer automatiquement un profil lors de la création d'un utilisateur
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()