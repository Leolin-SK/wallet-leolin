"""
Serializers — Conversion modèles ↔ JSON
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from decimal import Decimal
from .models import UserProfile, Category, Transaction, Budget, Objectif, Recurrente, Transfert


TAUX_FCFA = Decimal('655.957')


# ─── AUTH ─────────────────────────────────────────────────────────────────────

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password', 'password2']

    def validate(self, data):
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password2": "Les mots de passe ne correspondent pas."})
        return data

    def create(self, validated_data):
        validated_data.pop('password2')
        user = User.objects.create_user(**validated_data)
        # Créer le profil + catégories par défaut
        UserProfile.objects.create(user=user)
        _create_default_categories(user)
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class UserProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    solde_actuel_eur = serializers.SerializerMethodField()
    solde_actuel_fcfa = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = '__all__'

    def get_solde_actuel_eur(self, obj):
        total_in = sum(t.montant_eur for t in obj.user.transactions.filter(type_tx='income'))
        total_out = sum(t.montant_eur for t in obj.user.transactions.filter(type_tx='expense'))
        return float(obj.solde_initial + total_in - total_out)

    def get_solde_actuel_fcfa(self, obj):
        return round(self.get_solde_actuel_eur(obj) * float(TAUX_FCFA), 2)


# ─── CATÉGORIES ───────────────────────────────────────────────────────────────

class CategorySerializer(serializers.ModelSerializer):
    depenses_total_eur = serializers.SerializerMethodField()
    depenses_mois_eur = serializers.SerializerMethodField()
    budget_restant_eur = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = '__all__'
        read_only_fields = ['user']

    def get_depenses_total_eur(self, obj):
        return float(sum(t.montant_eur for t in obj.transactions.filter(type_tx='expense')))

    def get_depenses_mois_eur(self, obj):
        from datetime import date
        today = date.today()
        return float(sum(
            t.montant_eur for t in obj.transactions.filter(
                type_tx='expense', date__year=today.year, date__month=today.month
            )
        ))

    def get_budget_restant_eur(self, obj):
        return float(obj.budget_mensuel) - self.get_depenses_mois_eur(obj)


# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────

class TransactionSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    montant_fcfa = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)

    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['user', 'montant_fcfa']

    def validate_montant_eur(self, value):
        if value <= 0:
            raise serializers.ValidationError("Le montant doit être positif.")
        return value


class TransactionCreateSerializer(serializers.ModelSerializer):
    """Serializer simplifié pour la création"""
    class Meta:
        model = Transaction
        fields = ['category', 'type_tx', 'label', 'montant_eur', 'date', 'note', 'is_recurrent']


# ─── BUDGETS ──────────────────────────────────────────────────────────────────

class BudgetSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    depenses_mois = serializers.SerializerMethodField()
    pourcentage_utilise = serializers.SerializerMethodField()

    class Meta:
        model = Budget
        fields = '__all__'
        read_only_fields = ['user']

    def get_depenses_mois(self, obj):
        return float(sum(
            t.montant_eur for t in obj.category.transactions.filter(
                type_tx='expense', date__year=obj.annee, date__month=obj.mois
            )
        ))

    def get_pourcentage_utilise(self, obj):
        if obj.montant_eur == 0:
            return 0
        return min(round(self.get_depenses_mois(obj) / float(obj.montant_eur) * 100, 1), 100)


# ─── OBJECTIFS ────────────────────────────────────────────────────────────────

class ObjectifSerializer(serializers.ModelSerializer):
    pourcentage = serializers.ReadOnlyField()
    mensualite_recommandee = serializers.ReadOnlyField()
    montant_restant = serializers.SerializerMethodField()

    class Meta:
        model = Objectif
        fields = '__all__'
        read_only_fields = ['user']

    def get_montant_restant(self, obj):
        return float(max(obj.montant_cible_eur - obj.montant_atteint_eur, Decimal('0')))


# ─── RÉCURRENTES ──────────────────────────────────────────────────────────────

class RecurrenteSerializer(serializers.ModelSerializer):
    category_detail = CategorySerializer(source='category', read_only=True)
    montant_fcfa = serializers.SerializerMethodField()

    class Meta:
        model = Recurrente
        fields = '__all__'
        read_only_fields = ['user']

    def get_montant_fcfa(self, obj):
        return float(obj.montant_eur * TAUX_FCFA)


# ─── TRANSFERTS ───────────────────────────────────────────────────────────────

class TransfertSerializer(serializers.ModelSerializer):
    montant_net_recu_eur = serializers.SerializerMethodField()

    class Meta:
        model = Transfert
        fields = '__all__'
        read_only_fields = ['user']

    def get_montant_net_recu_eur(self, obj):
        return float(obj.montant_envoye_eur - obj.frais_eur)


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

class DashboardSerializer(serializers.Serializer):
    """Données agrégées pour le dashboard"""
    solde_eur = serializers.FloatField()
    solde_fcfa = serializers.FloatField()
    solde_initial_eur = serializers.FloatField()
    pourcentage_capital = serializers.FloatField()
    total_revenus_eur = serializers.FloatField()
    total_depenses_eur = serializers.FloatField()
    mois_revenus_eur = serializers.FloatField()
    mois_depenses_eur = serializers.FloatField()
    mois_solde_eur = serializers.FloatField()
    total_famille_eur = serializers.FloatField()
    total_epargne_eur = serializers.FloatField()
    health_level = serializers.CharField()
    alertes = serializers.ListField(child=serializers.DictField())
    evolution_mensuelle = serializers.ListField(child=serializers.DictField())


class SimulateurTransfertSerializer(serializers.Serializer):
    """Simulation de transfert famille"""
    montant_eur = serializers.FloatField()

    PROVIDERS = [
        {'id': 'orange',   'name': 'Orange Money',  'frais_pct': 0,    'frais_fixe': 0,  'delai': 'Instantané'},
        {'id': 'sendwave', 'name': 'Sendwave',       'frais_pct': 0.01, 'frais_fixe': 0,  'delai': 'Instantané'},
        {'id': 'lemfi',    'name': 'LemFi',          'frais_pct': 0.015,'frais_fixe': 0,  'delai': 'Instantané'},
        {'id': 'remitly',  'name': 'Remitly',        'frais_pct': 0,    'frais_fixe': 3,  'delai': 'Quelques min'},
        {'id': 'wu',       'name': 'Western Union',  'frais_pct': 0.08, 'frais_fixe': 0,  'delai': 'Variable'},
    ]

    def simulate(self, montant):
        TAUX = 655.957
        results = []
        for p in self.PROVIDERS:
            frais = montant * p['frais_pct'] + p['frais_fixe']
            net = montant - frais
            results.append({
                **p,
                'frais_eur': round(frais, 2),
                'montant_net_eur': round(net, 2),
                'montant_fcfa': round(net * TAUX),
                'is_best': p['id'] == 'orange',
            })
        return sorted(results, key=lambda x: -x['montant_fcfa'])


class RepartitionSerializer(serializers.Serializer):
    """Répartition automatique d'un montant"""
    montant_eur = serializers.FloatField()


# ─── HELPER ───────────────────────────────────────────────────────────────────

def _create_default_categories(user):
    """Crée les catégories par défaut pour un nouvel utilisateur"""
    defaults = [
        {'nom': 'Loyer',         'icone': '🏠', 'couleur': '#4ade80', 'type_cat': 'fixe',    'budget_mensuel': 320,  'ordre': 1, 'description': 'Colocation Lille'},
        {'nom': 'Alimentation',  'icone': '🍽️', 'couleur': '#fb923c', 'type_cat': 'fixe',    'budget_mensuel': 100,  'ordre': 2, 'description': 'CROUS + Lidl + Too Good To Go'},
        {'nom': 'Transport',     'icone': '🚌', 'couleur': '#60a5fa', 'type_cat': 'fixe',    'budget_mensuel': 27,   'ordre': 3, 'description': 'Abonnement Ilévia Lille'},
        {'nom': 'Téléphone',     'icone': '📱', 'couleur': '#a78bfa', 'type_cat': 'fixe',    'budget_mensuel': 5,    'ordre': 4, 'description': 'Lycamobile'},
        {'nom': 'Hygiène',       'icone': '🧴', 'couleur': '#f472b6', 'type_cat': 'fixe',    'budget_mensuel': 15,   'ordre': 5, 'description': 'Produits Lidl/Aldi'},
        {'nom': 'Fournitures',   'icone': '📚', 'couleur': '#34d399', 'type_cat': 'fixe',    'budget_mensuel': 5,    'ordre': 6, 'description': 'PDF + bibliothèque'},
        {'nom': 'Famille 🇨🇲',   'icone': '🌍', 'couleur': '#e879f9', 'type_cat': 'fixe',    'budget_mensuel': 100,  'ordre': 7, 'description': 'Orange Money'},
        {'nom': 'Épargne A2',    'icone': '🏦', 'couleur': '#fbbf24', 'type_cat': 'fixe',    'budget_mensuel': 50,   'ordre': 8, 'description': 'Réserve alternance'},
        {'nom': 'Imprévus',      'icone': '🆘', 'couleur': '#f87171', 'type_cat': 'fixe',    'budget_mensuel': 30,   'ordre': 9, 'description': 'Fonds urgence'},
        {'nom': 'Revenus Job',   'icone': '💼', 'couleur': '#22d3ee', 'type_cat': 'revenu',  'budget_mensuel': 0,    'ordre': 10,'description': 'Uber Eats, cours particuliers'},
        {'nom': 'Autre',         'icone': '💡', 'couleur': '#94a3b8', 'type_cat': 'variable','budget_mensuel': 0,    'ordre': 11,'description': 'Divers'},
    ]
    for d in defaults:
        Category.objects.create(user=user, **d)
