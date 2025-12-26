from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.contrib.auth.models import User
from .models import Cours, Module, Ressource, Devoir, Soumission, Inscription, Message, Notification, Evenement
from .forms import CoursForm, ModuleForm, RessourceForm, DevoirForm, DevoirGlobalForm, SoumissionForm, MessageForm, EvenementForm
from comptes.models import Profile


def _normalize_name(s):
    """Normalize a name: collapse whitespace, strip, lowercase.
    
    Examples:
        '  Iyed   Iyed ' -> 'iyed iyed'
        'IYED IYED' -> 'iyed iyed'
    """
    if not s:
        return ''
    return ' '.join(s.split()).strip().lower()


def _get_instructor_courses(user):
    """Fetch all courses where the enseignant (FK) matches the logged-in user's full name.
    
    Compares normalized instructor full names:
    - Logged-in user: get_full_name() or username
    - Course enseignant: enseignant.get_full_name() or enseignant.username
    
    Both normalized: whitespace collapsed, lowercased.
    """
    user_norm = _normalize_name(user.get_full_name() or user.username)
    
    # Get all courses with enseignant pre-fetched
    all_courses = Cours.objects.select_related('enseignant').all()
    matches = []
    
    for c in all_courses:
        enseignant = c.enseignant
        if enseignant:
            enseignant_norm = _normalize_name(enseignant.get_full_name() or enseignant.username)
            # Match if normalized names are equal
            if enseignant_norm == user_norm:
                matches.append(c)
    
    return matches


def index(request):
    """
    Page d'accueil
    """
    from comptes.models import Profile
    cours_publies_qs = Cours.objects.filter(statut='publie')
    cours_publies = cours_publies_qs.annotate(
        nb_etudiants=Count('inscriptions', filter=Q(inscriptions__statut='active'))
    )[:6]
    cours_publies_count = cours_publies_qs.count()
    enseignant_count = Profile.objects.filter(role='enseignant').count()
    etudiant_count = Profile.objects.filter(role='etudiant').count()
    context = {
        'cours_publies': cours_publies,
        'cours_publies_count': cours_publies_count,
        'enseignant_count': enseignant_count,
        'etudiant_count': etudiant_count,
    }
    
    if request.user.is_authenticated:
        if request.user.profile.is_etudiant():
            context['mes_cours'] = Cours.objects.filter(
                inscriptions__etudiant=request.user,
                inscriptions__statut='active'
            )[:4]
        elif request.user.profile.is_enseignant():
            context['mes_cours'] = _get_instructor_courses(request.user)[:4]
    
    return render(request, 'e_learning/index.html', context)


def cours_list(request):
    """
    Liste de tous les cours publiés
    """
    cours = Cours.objects.filter(statut='publie').annotate(
        nb_etudiants=Count('inscriptions', filter=Q(inscriptions__statut='active'))
    )
    
    # Recherche
    query = request.GET.get('q')
    if query:
        cours = cours.filter(
            Q(titre__icontains=query) | 
            Q(description__icontains=query) |
            Q(enseignant__first_name__icontains=query) |
            Q(enseignant__last_name__icontains=query)
        )
    
    context = {
        'cours_list': cours,
        'query': query
    }
    return render(request, 'e_learning/cours_list.html', context)


@login_required
def cours_detail(request, pk):
    """
    Détails d'un cours
    """
    cours = get_object_or_404(Cours, pk=pk)
    
    # Vérifier si l'utilisateur est inscrit ou est l'enseignant
    est_enseignant = cours.enseignant == request.user
    est_inscrit = False
    
    if request.user.profile.is_etudiant():
        est_inscrit = Inscription.objects.filter(
            etudiant=request.user,
            cours=cours,
            statut='active'
        ).exists()
    
    # Seuls les inscrits ou l'enseignant peuvent voir le contenu
    peut_voir_contenu = est_enseignant or est_inscrit or cours.statut == 'publie'
    
    modules = cours.modules.all().prefetch_related('ressources', 'devoirs')
    devoirs = cours.devoirs.all()
    
    context = {
        'cours': cours,
        'modules': modules,
        'devoirs': devoirs,
        'est_enseignant': est_enseignant,
        'est_inscrit': est_inscrit,
        'peut_voir_contenu': peut_voir_contenu,
    }
    
    return render(request, 'e_learning/cours_detail.html', context)


@login_required
def cours_create(request):
    """
    Créer un nouveau cours (enseignants uniquement)
    """
    if not request.user.profile.is_enseignant():
        messages.error(request, "Vous devez être enseignant pour créer un cours.")
        return redirect('e_learning:index')
    
    if request.method == 'POST':
        form = CoursForm(request.POST, request.FILES)
        if form.is_valid():
            cours = form.save(commit=False)
            cours.enseignant = request.user
            cours.save()
            messages.success(request, f"Le cours '{cours.titre}' a été créé avec succès.")
            return redirect('e_learning:cours_detail', pk=cours.pk)
    else:
        form = CoursForm()
    
    return render(request, 'e_learning/cours_form.html', {'form': form, 'action': 'Créer'})


@login_required
def cours_update(request, pk):
    """
    Modifier un cours (enseignant propriétaire uniquement)
    """
    cours = get_object_or_404(Cours, pk=pk)
    
    if cours.enseignant != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à modifier ce cours.")
    
    if request.method == 'POST':
        form = CoursForm(request.POST, request.FILES, instance=cours)
        if form.is_valid():
            form.save()
            messages.success(request, f"Le cours '{cours.titre}' a été mis à jour.")
            return redirect('e_learning:cours_detail', pk=cours.pk)
    else:
        form = CoursForm(instance=cours)
    
    return render(request, 'e_learning/cours_form.html', {'form': form, 'action': 'Modifier', 'cours': cours})


@login_required
def cours_delete(request, pk):
    """
    Supprimer un cours
    """
    cours = get_object_or_404(Cours, pk=pk)
    
    if not (cours.enseignant == request.user or getattr(request.user.profile, 'is_admin')()):
        return HttpResponseForbidden("Vous n'êtes pas autorisé à supprimer ce cours.")
    
    if request.method == 'POST':
        titre = cours.titre
        cours.delete()
        messages.success(request, f"Le cours '{titre}' a été supprimé.")
        return redirect('e_learning:mes_cours')
    
    return render(request, 'e_learning/cours_confirm_delete.html', {'cours': cours})

@login_required
def evenements_admin(request):
    """
    Liste des évènements (réservée à l'administrateur)
    """
    if not getattr(request.user.profile, 'is_admin')():
        return HttpResponseForbidden("Accès réservé à l'administrateur.")
    evenements = Evenement.objects.select_related('cours').order_by('-date_debut')
    return render(request, 'e_learning/evenements_admin.html', { 'evenements': evenements })

@login_required
def evenement_create(request):
    """Créer un évènement (admin)"""
    if not getattr(request.user.profile, 'is_admin')():
        return HttpResponseForbidden("Accès réservé à l'administrateur.")
    if request.method == 'POST':
        form = EvenementForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Évènement créé avec succès.")
            return redirect('e_learning:evenements_admin')
    else:
        form = EvenementForm()
    return render(request, 'e_learning/evenements_form.html', { 'form': form, 'action': 'Créer' })

@login_required
def evenement_update(request, pk):
    """Modifier un évènement (admin)"""
    if not getattr(request.user.profile, 'is_admin')():
        return HttpResponseForbidden("Accès réservé à l'administrateur.")
    evenement = get_object_or_404(Evenement, pk=pk)
    if request.method == 'POST':
        form = EvenementForm(request.POST, instance=evenement)
        if form.is_valid():
            form.save()
            messages.success(request, "Évènement modifié avec succès.")
            return redirect('e_learning:evenements_admin')
    else:
        form = EvenementForm(instance=evenement)
    return render(request, 'e_learning/evenements_form.html', { 'form': form, 'action': 'Modifier' })

@login_required
def evenement_delete(request, pk):
    """Supprimer un évènement (admin)"""
    if not getattr(request.user.profile, 'is_admin')():
        return HttpResponseForbidden("Accès réservé à l'administrateur.")
    evenement = get_object_or_404(Evenement, pk=pk)
    if request.method == 'POST':
        titre = evenement.titre
        evenement.delete()
        messages.success(request, f"L'évènement '{titre}' a été supprimé.")
        return redirect('e_learning:evenements_admin')
    return render(request, 'e_learning/evenements_confirm_delete.html', { 'evenement': evenement })


@login_required
def inscription_cours(request, pk):
    """
    S'inscrire à un cours (étudiants uniquement)
    """
    if not request.user.profile.is_etudiant():
        messages.error(request, "Seuls les étudiants peuvent s'inscrire aux cours.")
        return redirect('e_learning:cours_detail', pk=pk)
    
    cours = get_object_or_404(Cours, pk=pk, statut='publie')
    
    # Vérifier si déjà inscrit
    inscription_existante = Inscription.objects.filter(
        etudiant=request.user,
        cours=cours
    ).first()
    
    if inscription_existante:
        if inscription_existante.statut == 'active':
            messages.warning(request, "Vous êtes déjà inscrit à ce cours.")
        else:
            inscription_existante.statut = 'active'
            inscription_existante.save()
            messages.success(request, f"Vous vous êtes réinscrit au cours '{cours.titre}'.")
    else:
        Inscription.objects.create(etudiant=request.user, cours=cours)
        messages.success(request, f"Vous êtes maintenant inscrit au cours '{cours.titre}'.")
        
        # Créer une notification pour l'enseignant
        Notification.objects.create(
            utilisateur=cours.enseignant,
            titre="Nouvelle inscription",
            contenu=f"{request.user.get_full_name() or request.user.username} s'est inscrit à votre cours '{cours.titre}'",
            type='inscription',
            lien=f'/cours/{cours.pk}/'
        )
    
    return redirect('e_learning:cours_detail', pk=pk)


@login_required
def desinscription_cours(request, pk):
    """
    Se désinscrire d'un cours
    """
    cours = get_object_or_404(Cours, pk=pk)
    inscription = get_object_or_404(Inscription, etudiant=request.user, cours=cours)
    
    if request.method == 'POST':
        inscription.statut = 'annulee'
        inscription.save()
        messages.success(request, f"Vous vous êtes désinscrit du cours '{cours.titre}'.")
        return redirect('e_learning:mes_cours')
    
    return render(request, 'e_learning/desinscription_confirm.html', {'cours': cours})


@login_required
def mes_cours(request):
    """
    Liste des cours de l'utilisateur connecté
    """
    if request.user.profile.is_etudiant():
        cours = Cours.objects.filter(
            inscriptions__etudiant=request.user,
            inscriptions__statut='active'
        )
        template = 'e_learning/mes_cours_etudiant.html'
    elif request.user.profile.is_enseignant():
        cours = _get_instructor_courses(request.user)
        template = 'e_learning/mes_cours_enseignant.html'
    else:
        messages.error(request, "Accès non autorisé.")
        return redirect('e_learning:index')
    context = {'cours_list': cours}
    return render(request, template, context)


@login_required
def module_create(request, cours_pk):
    """
    Créer un module dans un cours
    """
    cours = get_object_or_404(Cours, pk=cours_pk)
    
    if cours.enseignant != request.user:
        return HttpResponseForbidden()
    
    if request.method == 'POST':
        form = ModuleForm(request.POST)
        if form.is_valid():
            module = form.save(commit=False)
            module.cours = cours
            module.save()
            messages.success(request, f"Le module '{module.titre}' a été créé.")
            return redirect('e_learning:cours_detail', pk=cours.pk)
    else:
        form = ModuleForm()
    
    return render(request, 'e_learning/module_form.html', {'form': form, 'cours': cours})


@login_required
def devoir_create(request, cours_pk):
    """Créer un devoir pour un cours (enseignant propriétaire uniquement)"""
    cours = get_object_or_404(Cours, pk=cours_pk)
    
    # Seul l'enseignant du cours peut créer un devoir
    if cours.enseignant != request.user:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à créer un devoir pour ce cours.")

    if request.method == 'POST':
        form = DevoirForm(request.POST, request.FILES)
        if form.is_valid():
            devoir = form.save(commit=False)
            devoir.cours = cours
            devoir.save()
            messages.success(request, f"Le devoir '{devoir.titre}' a été créé avec succès.")
            return redirect('e_learning:cours_detail', pk=cours.pk)
    else:
        form = DevoirForm()
    
    return render(request, 'e_learning/devoir_form.html', {'form': form, 'cours': cours})


@login_required
def devoir_create_global(request):
    """Créer un devoir en choisissant un cours (enseignant uniquement)."""
    if not request.user.profile.is_enseignant():
        return HttpResponseForbidden("Accès réservé aux enseignants.")

    if request.method == 'POST':
        form = DevoirGlobalForm(request.POST, request.FILES)
        # Restreindre les cours au propriétaire connecté
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)
        if form.is_valid():
            devoir = form.save(commit=False)
            # Sécurité supplémentaire : vérifier que le cours appartient bien à l'enseignant
            if devoir.cours.enseignant != request.user:
                return HttpResponseForbidden("Vous n'êtes pas autorisé à créer un devoir pour ce cours.")
            devoir.save()
            messages.success(request, f"Le devoir '{devoir.titre}' a été créé avec succès.")
            return redirect('e_learning:cours_detail', pk=devoir.cours.pk)
    else:
        form = DevoirGlobalForm()
        form.fields['cours'].queryset = Cours.objects.filter(enseignant=request.user)

    return render(request, 'e_learning/devoir_form_global.html', {'form': form})


@login_required
def devoir_submit(request, devoir_pk):
    """
    Soumettre un devoir
    """
    devoir = get_object_or_404(Devoir, pk=devoir_pk)
    
    # Vérifier que l'étudiant est inscrit
    if not Inscription.objects.filter(etudiant=request.user, cours=devoir.cours, statut='active').exists():
        return HttpResponseForbidden()
    
    # Vérifier si déjà soumis
    soumission_existante = Soumission.objects.filter(devoir=devoir, etudiant=request.user).first()
    
    if request.method == 'POST':
        form = SoumissionForm(request.POST, request.FILES, instance=soumission_existante)
        if form.is_valid():
            soumission = form.save(commit=False)
            soumission.devoir = devoir
            soumission.etudiant = request.user
            soumission.save()
            messages.success(request, "Votre devoir a été soumis avec succès.")
            return redirect('e_learning:cours_detail', pk=devoir.cours.pk)
    else:
        form = SoumissionForm(instance=soumission_existante)
    
    context = {
        'form': form,
        'devoir': devoir,
        'soumission_existante': soumission_existante
    }
    return render(request, 'e_learning/devoir_submit.html', context)


@login_required
def notifications(request):
    """
    Liste des notifications de l'utilisateur
    """
    notifications = Notification.objects.filter(utilisateur=request.user)
    
    # Marquer comme lues
    notifications.filter(lu=False).update(lu=True)
    
    return render(request, 'e_learning/notifications.html', {'notifications': notifications})


@login_required
def messagerie(request):
    """
    Messagerie interne
    """
    messages_recus = Message.objects.filter(destinataire=request.user)
    messages_envoyes = Message.objects.filter(expediteur=request.user)

    if request.method == 'POST':
        form = MessageForm(request.POST)
        # ne jamais pouvoir s'envoyer un message à soi-même
        form.fields['destinataire'].queryset = User.objects.exclude(id=request.user.id)
        if form.is_valid():
            message_obj = form.save(commit=False)
            message_obj.expediteur = request.user
            message_obj.save()
            messages.success(request, "Message envoyé avec succès.")
            return redirect('e_learning:messagerie')
    else:
        form = MessageForm()
        form.fields['destinataire'].queryset = User.objects.exclude(id=request.user.id)

    context = {
        'messages_recus': messages_recus,
        'messages_envoyes': messages_envoyes,
        'form': form,
    }
    return render(request, 'e_learning/messagerie.html', context)


def offres(request):
    """
    Page Nos Offres (tarifs / plans)
    """
    plans = [
        {
            'name': 'Découverte',
            'price': 'Gratuit',
            'features': ['Accès aux cours publics', 'Messagerie limitée', 'Support communautaire'],
            'icon': 'fa-rocket',
            'highlight': False,
        },
        {
            'name': 'Pro Étudiant',
            'price': '19 DT/mois',
            'features': ['Tous les cours', 'Devoirs illimités', 'Certificats', 'Support prioritaire'],
            'icon': 'fa-graduation-cap',
            'highlight': True,
        },
        {
            'name': "Enseignant+",
            'price': '29 DT/mois',
            'features': ['Création de cours', 'Analytique étudiants', 'Messagerie avancée', 'Monétisation'],
            'icon': 'fa-chalkboard-teacher',
            'highlight': False,
        },
    ]
    return render(request, 'e_learning/offres.html', { 'plans': plans })


def contact(request):
    """
    Page Contactez-nous (formulaire simple)
    """
    if request.method == 'POST':
        nom = request.POST.get('nom')
        email = request.POST.get('email')
        sujet = request.POST.get('sujet')
        message = request.POST.get('message')
        if nom and email and sujet and message:
            messages.success(request, "Merci pour votre message. Nous vous répondrons prochainement.")
            return redirect('e_learning:contact')
        messages.error(request, "Veuillez remplir tous les champs.")
    return render(request, 'e_learning/contact.html')


@login_required
def mes_devoirs(request):
    """
    Liste des devoirs pertinents pour l'utilisateur connecté
    - Étudiant: devoirs des cours où il est inscrit (actif)
    - Enseignant: devoirs des cours qu'il enseigne
    """
    if request.user.profile.is_etudiant():
        devoirs = Devoir.objects.filter(
            cours__inscriptions__etudiant=request.user,
            cours__inscriptions__statut='active'
        ).select_related('cours', 'module').order_by('date_limite').distinct()
        soumissions_ids = set(
            Soumission.objects.filter(etudiant=request.user, devoir__in=devoirs)
            .values_list('devoir_id', flat=True)
        )
        context = { 'devoirs': devoirs, 'soumissions_ids': soumissions_ids, 'mode': 'etudiant' }
    elif request.user.profile.is_enseignant():
        devoirs = Devoir.objects.filter(cours__enseignant=request.user).select_related('cours','module').order_by('-created_at')
        context = { 'devoirs': devoirs, 'mode': 'enseignant' }
    else:
        devoirs = Devoir.objects.all()[:0]
        context = { 'devoirs': devoirs, 'mode': 'autre' }
    return render(request, 'e_learning/mes_devoirs.html', context)