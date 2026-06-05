from django.contrib import admin
from .models import UserProfile, Category, Transaction, Budget, Objectif, Recurrente, Transfert

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'solde_initial', 'devise_preference', 'ville_etudes']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['icone', 'nom', 'type_cat', 'budget_mensuel', 'user']
    list_filter = ['type_cat', 'user']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['date', 'type_tx', 'label', 'montant_eur', 'montant_fcfa', 'category', 'user']
    list_filter = ['type_tx', 'date', 'user']
    search_fields = ['label', 'note']
    ordering = ['-date']

@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    list_display = ['category', 'mois', 'annee', 'montant_eur', 'user']

@admin.register(Objectif)
class ObjectifAdmin(admin.ModelAdmin):
    list_display = ['icone', 'label', 'montant_cible_eur', 'montant_atteint_eur', 'pourcentage', 'termine']

@admin.register(Recurrente)
class RecurrenteAdmin(admin.ModelAdmin):
    list_display = ['label', 'montant_eur', 'type_tx', 'jour_du_mois', 'active']

@admin.register(Transfert)
class TransfertAdmin(admin.ModelAdmin):
    list_display = ['date', 'provider', 'montant_envoye_eur', 'frais_eur', 'montant_recu_fcfa']