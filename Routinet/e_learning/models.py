from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse

class Cours(models.Model):
    """
    Modèle représentant un cours
    """
    STATUT_CHOICES = [
        ('brouillon', 'Brouillon'),
        ('publie', 'Publié'),
        ('archive', 'Archivé'),
    ]
    
    titre = models.CharField(max_length=200)
    description = models.TextField()
    enseignant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cours_enseignes')
    fichier = models.FileField(upload_to='cours/', blank=True, null=True)
    image = models.ImageField(upload_to='cours_images/', blank=True, null=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='brouillon')
    date_debut = models.DateField(blank=True, null=True)
    date_fin = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Cours"
        verbose_name_plural = "Cours"
        ordering = ['-created_at']
    
    def __str__(self):
        return self.titre
    
    def get_absolute_url(self):
        return reverse('e_learning:cours_detail', kwargs={'pk': self.pk})
    
    @property
    def nombre_etudiants(self):
        return self.inscriptions.filter(statut='active').count()
    
    @property
    def nombre_modules(self):
        return self.modules.count()


class Inscription(models.Model):
    """
    Inscription d'un étudiant à un cours
    """
    STATUT_CHOICES = [
        ('active', 'Active'),
        ('terminee', 'Terminée'),
        ('en_attente', 'En attente'),
        ('annulee', 'Annulée'),
    ]
    
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inscriptions')
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='inscriptions')
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='active')
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Inscription"
        verbose_name_plural = "Inscriptions"
        unique_together = ['etudiant', 'cours']
        ordering = ['-date_inscription']
    
    def __str__(self):
        return f"{self.etudiant.username} - {self.cours.titre}"


class Module(models.Model):
    """
    Module/Chapitre d'un cours
    """
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='modules')
    titre = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Module"
        verbose_name_plural = "Modules"
        ordering = ['ordre', 'created_at']
    
    def __str__(self):
        return f"{self.cours.titre} - {self.titre}"


class Ressource(models.Model):
    """
    Ressource pédagogique (PDF, vidéo, lien, image)
    """
    TYPE_CHOICES = [
        ('pdf', 'PDF'),
        ('video', 'Vidéo'),
        ('lien', 'Lien'),
        ('image', 'Image'),
    ]
    
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='ressources')
    nom = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    url = models.URLField(blank=True, null=True)
    fichier = models.FileField(upload_to='ressources/', blank=True, null=True)
    description = models.TextField(blank=True)
    ordre = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Ressource"
        verbose_name_plural = "Ressources"
        ordering = ['ordre', 'created_at']
    
    def __str__(self):
        return self.nom


class Devoir(models.Model):
    """
    Devoir assigné aux étudiants
    """
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='devoirs')
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name='devoirs', blank=True, null=True)
    titre = models.CharField(max_length=200)
    description = models.TextField()
    fichier_devoir = models.FileField(upload_to='devoirs/', blank=True, null=True)
    date_limite = models.DateTimeField()
    note_max = models.DecimalField(max_digits=5, decimal_places=2, default=20.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Devoir"
        verbose_name_plural = "Devoirs"
        ordering = ['-date_limite']
    
    def __str__(self):
        return f"{self.cours.titre} - {self.titre}"
    
    @property
    def est_en_retard(self):
        return timezone.now() > self.date_limite


class Soumission(models.Model):
    """
    Soumission d'un devoir par un étudiant
    """
    devoir = models.ForeignKey(Devoir, on_delete=models.CASCADE, related_name='soumissions')
    etudiant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='soumissions')
    fichier_soumission = models.FileField(upload_to='soumissions/')
    commentaire = models.TextField(blank=True)
    date_depot = models.DateTimeField(auto_now_add=True)
    note = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)
    commentaire_enseignant = models.TextField(blank=True)
    date_notation = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        verbose_name = "Soumission"
        verbose_name_plural = "Soumissions"
        unique_together = ['devoir', 'etudiant']
        ordering = ['-date_depot']
    
    def __str__(self):
        return f"{self.etudiant.username} - {self.devoir.titre}"
    
    @property
    def est_en_retard(self):
        return self.date_depot > self.devoir.date_limite


class Message(models.Model):
    """
    Messagerie interne entre utilisateurs
    """
    expediteur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_envoyes')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages_recus')
    contenu = models.TextField()
    date_envoi = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"
        ordering = ['-date_envoi']
    
    def __str__(self):
        return f"De {self.expediteur.username} à {self.destinataire.username}"


class Notification(models.Model):
    """
    Notifications système pour les utilisateurs
    """
    TYPE_CHOICES = [
        ('cours', 'Nouveau cours'),
        ('devoir', 'Nouveau devoir'),
        ('message', 'Nouveau message'),
        ('inscription', 'Inscription'),
        ('note', 'Nouvelle note'),
    ]
    
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    titre = models.CharField(max_length=200)
    contenu = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    lien = models.CharField(max_length=200, blank=True)
    lu = models.BooleanField(default=False)
    date_heure = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_heure']
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.titre}"


class Evenement(models.Model):
    """
    Événements liés aux cours (examens, séances, etc.)
    """
    TYPE_CHOICES = [
        ('examen', 'Examen'),
        ('seance', 'Séance'),
        ('conference', 'Conférence'),
        ('autre', 'Autre'),
    ]
    
    cours = models.ForeignKey(Cours, on_delete=models.CASCADE, related_name='evenements')
    titre = models.CharField(max_length=200)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    date_debut = models.DateTimeField()
    date_fin = models.DateTimeField()
    lieu = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Événement"
        verbose_name_plural = "Événements"
        ordering = ['date_debut']
    
    def __str__(self):
        return f"{self.cours.titre} - {self.titre}"