from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import InscriptionForm, ConnexionForm, ProfileUpdateForm
from .models import Profile

def inscription(request):
    """
    Vue d'inscription
    """
    if request.user.is_authenticated:
        return redirect('e_learning:index')
    
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Bienvenue {user.first_name} ! Votre compte a été créé avec succès.")
            return redirect('e_learning:index')
    else:
        form = InscriptionForm()
    
    return render(request, 'comptes/register.html', {'form': form})

def connexion(request):
    """
    Vue de connexion
    """
    if request.user.is_authenticated:
        return redirect('e_learning:index')
    
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Content de vous revoir {user.first_name} !")
                next_url = request.GET.get('next', 'e_learning:index')
                return redirect(next_url)
    else:
        form = ConnexionForm()
    
    return render(request, 'comptes/login.html', {'form': form})

@login_required
def deconnexion(request):
    """
    Vue de déconnexion
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('e_learning:index')

@login_required
def profil(request):
    """
    Vue de modification du profil
    """
    if request.method == 'POST':
        form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Votre profil a été mis à jour avec succès.")
            return redirect('comptes:profil')
    else:
        form = ProfileUpdateForm(instance=request.user.profile)
    
    return render(request, 'comptes/profil.html', {'form': form, 'profile': request.user.profile})

@login_required
def profil_public(request, username):
    """
    Vue du profil public d'un utilisateur
    """
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    
    context = {
        'profile_user': user,
        'profile': profile
    }
    
    return render(request, 'comptes/profil_public.html', context)