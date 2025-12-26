from django.urls import path
from . import views

app_name = 'e_learning'

urlpatterns = [
    # Pages principales
    path('', views.index, name='index'),
    path('cours/', views.cours_list, name='cours_list'),
    path('mes-cours/', views.mes_cours, name='mes_cours'),
    path('contact/', views.contact, name='contact'),
    path('mes-devoirs/', views.mes_devoirs, name='mes_devoirs'),
    path('offres/', views.offres, name='offres'),
    path('evenements/', views.evenements_admin, name='evenements_admin'),
    path('evenements/creer/', views.evenement_create, name='evenement_create'),
    path('evenements/<int:pk>/modifier/', views.evenement_update, name='evenement_update'),
    path('evenements/<int:pk>/supprimer/', views.evenement_delete, name='evenement_delete'),
    
    # Gestion des cours
    path('cours/creer/', views.cours_create, name='cours_create'),
    path('cours/<int:pk>/', views.cours_detail, name='cours_detail'),
    path('cours/<int:pk>/modifier/', views.cours_update, name='cours_update'),
    path('cours/<int:pk>/supprimer/', views.cours_delete, name='cours_delete'),
    
    # Inscriptions
    path('cours/<int:pk>/inscription/', views.inscription_cours, name='inscription_cours'),
    path('cours/<int:pk>/desinscription/', views.desinscription_cours, name='desinscription_cours'),
    
    # Modules
    path('cours/<int:cours_pk>/module/creer/', views.module_create, name='module_create'),
    
    # Devoirs
    path('devoir/creer/', views.devoir_create_global, name='devoir_create_global'),
    path('cours/<int:cours_pk>/devoir/creer/', views.devoir_create, name='devoir_create'),
    path('devoir/<int:devoir_pk>/soumettre/', views.devoir_submit, name='devoir_submit'),
    
    # Communication
    path('notifications/', views.notifications, name='notifications'),
    path('messagerie/', views.messagerie, name='messagerie'),
]