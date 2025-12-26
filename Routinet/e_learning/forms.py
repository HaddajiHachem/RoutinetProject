from django import forms
from .models import Cours, Module, Ressource, Devoir, Soumission, Message, Evenement

class CoursForm(forms.ModelForm):
    """
    Formulaire de création/modification de cours
    """
    class Meta:
        model = Cours
        fields = ['titre', 'description', 'image', 'fichier', 'statut', 'date_debut', 'date_fin']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du cours'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Description détaillée du cours'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'statut': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_debut': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'date_fin': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }


class ModuleForm(forms.ModelForm):
    """
    Formulaire de création/modification de module
    """
    class Meta:
        model = Module
        fields = ['titre', 'description', 'ordre']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du module'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Description du module'
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }


class RessourceForm(forms.ModelForm):
    """
    Formulaire de création/modification de ressource
    """
    class Meta:
        model = Ressource
        fields = ['nom', 'type', 'url', 'fichier', 'description', 'ordre']
        widgets = {
            'nom': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nom de la ressource'
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'URL (pour vidéos ou liens)'
            }),
            'fichier': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3
            }),
            'ordre': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0
            }),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        type_ressource = cleaned_data.get('type')
        url = cleaned_data.get('url')
        fichier = cleaned_data.get('fichier')
        
        if type_ressource in ['video', 'lien'] and not url:
            raise forms.ValidationError("Une URL est requise pour les vidéos et les liens.")
        
        if type_ressource in ['pdf', 'image'] and not fichier and not url:
            raise forms.ValidationError("Un fichier est requis pour les PDFs et images.")
        
        return cleaned_data


class DevoirForm(forms.ModelForm):
    """
    Formulaire de création/modification de devoir
    """
    class Meta:
        model = Devoir
        fields = ['titre', 'description', 'module', 'fichier_devoir', 'date_limite', 'note_max']
        widgets = {
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du devoir'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Instructions du devoir'
            }),
            'module': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fichier_devoir': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'date_limite': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'note_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
        }


class DevoirGlobalForm(forms.ModelForm):
    """Formulaire de création de devoir avec choix du cours (création globale)."""

    class Meta:
        model = Devoir
        # On inclut explicitement le cours pour que l'enseignant puisse le choisir
        fields = ['cours', 'titre', 'description', 'module', 'fichier_devoir', 'date_limite', 'note_max']
        widgets = {
            'cours': forms.Select(attrs={
                'class': 'form-control'
            }),
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre du devoir'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Instructions du devoir'
            }),
            'module': forms.Select(attrs={
                'class': 'form-control'
            }),
            'fichier_devoir': forms.FileInput(attrs={
                'class': 'form-control'
            }),
            'date_limite': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'note_max': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
        }


class SoumissionForm(forms.ModelForm):
    """
    Formulaire de soumission de devoir par l'étudiant
    """
    class Meta:
        model = Soumission
        fields = ['fichier_soumission', 'commentaire']
        widgets = {
            'fichier_soumission': forms.FileInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'commentaire': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Commentaires ou notes pour l\'enseignant (optionnel)'
            }),
        }


class NotationForm(forms.ModelForm):
    """
    Formulaire de notation par l'enseignant
    """
    class Meta:
        model = Soumission
        fields = ['note', 'commentaire_enseignant']
        widgets = {
            'note': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 0,
                'step': '0.01'
            }),
            'commentaire_enseignant': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Commentaires et feedback pour l\'étudiant'
            }),
        }


class MessageForm(forms.ModelForm):
    """
    Formulaire d'envoi de message
    """
    class Meta:
        model = Message
        fields = ['destinataire', 'contenu']
        widgets = {
            'destinataire': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contenu': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 5,
                'placeholder': 'Votre message...'
            }),
        }


class EvenementForm(forms.ModelForm):
    """
    Formulaire de création d'événement
    """
    class Meta:
        model = Evenement
        fields = ['cours', 'titre', 'description', 'type', 'date_debut', 'date_fin', 'lieu']
        widgets = {
            'cours': forms.Select(attrs={
                'class': 'form-control'
            }),
            'titre': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Titre de l\'événement'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'date_debut': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'date_fin': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            }),
            'lieu': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Lieu de l\'événement'
            }),
        }