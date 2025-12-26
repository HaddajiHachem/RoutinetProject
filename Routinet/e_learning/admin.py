from django.contrib import admin
from .models import Cours, Module, Ressource, Devoir, Soumission, Inscription, Message, Notification, Evenement

class ModuleInline(admin.TabularInline):
    model = Module
    extra = 1
    classes = ('collapse',)

class RessourceInline(admin.TabularInline):
    model = Ressource
    extra = 1
    classes = ('collapse',)

class DevoirInline(admin.TabularInline):
    model = Devoir
    extra = 1
    classes = ('collapse',)

class InscriptionInline(admin.TabularInline):
    model = Inscription
    extra = 1
    classes = ('collapse',)

@admin.register(Cours)
class CoursAdmin(admin.ModelAdmin):
    list_display = ('titre', 'enseignant', 'statut', 'date_debut', 'date_fin', 'created_at')
    list_filter = ('statut', 'created_at', 'enseignant')
    search_fields = ('titre', 'description', 'enseignant__username')
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ModuleInline, DevoirInline, InscriptionInline]
    
    fieldsets = (
        ('Informations générales', {
            'fields': ('titre', 'description', 'enseignant', 'image')
        }),
        ('Statut et dates', {
            'fields': ('statut', 'date_debut', 'date_fin')
        }),
        ('Dates techniques', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Module)
class ModuleAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'ordre', 'created_at')
    list_filter = ('cours', 'created_at')
    search_fields = ('titre', 'description', 'cours__titre')
    inlines = [RessourceInline]

@admin.register(Ressource)
class RessourceAdmin(admin.ModelAdmin):
    list_display = ('nom', 'module', 'type', 'ordre', 'created_at')
    list_filter = ('type', 'module__cours', 'created_at')
    search_fields = ('nom', 'description', 'module__titre')

@admin.register(Devoir)
class DevoirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'module', 'date_limite', 'note_max', 'created_at')
    list_filter = ('cours', 'module', 'date_limite')
    search_fields = ('titre', 'description', 'cours__titre')
    readonly_fields = ('created_at',)

@admin.register(Soumission)
class SoumissionAdmin(admin.ModelAdmin):
    list_display = ('devoir', 'etudiant', 'note', 'date_depot', 'est_en_retard')
    list_filter = ('devoir__cours', 'date_depot', 'note')
    search_fields = ('etudiant__username', 'devoir__titre')
    readonly_fields = ('date_depot',)
    
    def est_en_retard(self, obj):
        return obj.est_en_retard
    est_en_retard.boolean = True
    est_en_retard.short_description = 'En retard'

@admin.register(Inscription)
class InscriptionAdmin(admin.ModelAdmin):
    list_display = ('etudiant', 'cours', 'statut', 'date_inscription')
    list_filter = ('statut', 'cours', 'date_inscription')
    search_fields = ('etudiant__username', 'cours__titre')

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('expediteur', 'destinataire', 'date_envoi', 'lu')
    list_filter = ('date_envoi', 'lu')
    search_fields = ('expediteur__username', 'destinataire__username', 'contenu')
    readonly_fields = ('date_envoi',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'titre', 'type', 'lu', 'date_heure')
    list_filter = ('type', 'lu', 'date_heure')
    search_fields = ('utilisateur__username', 'titre', 'contenu')
    readonly_fields = ('date_heure',)

@admin.register(Evenement)
class EvenementAdmin(admin.ModelAdmin):
    list_display = ('titre', 'cours', 'type', 'date_debut', 'date_fin')
    list_filter = ('type', 'cours', 'date_debut')
    search_fields = ('titre', 'description', 'cours__titre')