"""
Modèles de base de données — Wallet Léolin

Tables :
- UserProfile   : Profil étendu de l'utilisateur
- Category      : Catégories de dépenses/revenus
- Transaction   : Toutes les transactions
- Budget        : Budgets mensuels par catégorie
- Objectif      : Objectifs financiers personnels
- Recurrente    : Dépenses récurrentes automatiques
- Transfert     : Historique des transferts famille
"""

from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class UserProfile(models.Model):
    """Profil étendu de l'utilisateur"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    solde_initial = models.DecimalField(
        max_digits=15, decimal_places=2, default=Decimal('6107.00'),
        help_text="Capital de départ en euros"
    )
    devise_preference = models.CharField(
        max_length=4, default='FCFA',
        choices=[('EUR', 'Euro'), ('FCFA', 'Franc CFA')]
    )
    pays_origine = models.CharField(max_length=50, default='Cameroun')
    ville_etudes = models.CharField(max_length=50, default='Lille')
    objectif_famille_annuel = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('1000.00'),
        help_text="Objectif annuel d'envoi à la famille en euros"
    )
    objectif_epargne_annuel = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('3000.00'),
        help_text="Objectif épargne Année 2 en euros"
    )
    seuil_alerte = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('2000.00'),
        help_text="Solde en dessous duquel une alerte est envoyée"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Profil de {self.user.username}"

    class Meta:
        verbose_name = "Profil utilisateur"


class Category(models.Model):
    """Catégories de transactions"""
    TYPE_CHOICES = [
        ('fixe', 'Charge fixe'),
        ('variable', 'Charge variable'),
        ('revenu', 'Revenu'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='categories')
    nom = models.CharField(max_length=50)
    icone = models.CharField(max_length=10, default='💡')
    couleur = models.CharField(max_length=7, default='#94a3b8')
    type_cat = models.CharField(max_length=10, choices=TYPE_CHOICES, default='variable')
    budget_mensuel = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    description = models.CharField(max_length=200, blank=True)
    ordre = models.IntegerField(default=0, help_text="Ordre d'affichage")
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['ordre', 'nom']
        verbose_name = "Catégorie"
        unique_together = ['user', 'nom']

    def __str__(self):
        return f"{self.icone} {self.nom}"


class Transaction(models.Model):
    """Transaction financière (dépense ou revenu)"""
    TYPE_CHOICES = [
        ('expense', 'Dépense'),
        ('income', 'Revenu'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='transactions')
    type_tx = models.CharField(max_length=10, choices=TYPE_CHOICES)
    label = models.CharField(max_length=200, verbose_name="Libellé")
    montant_eur = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Montant en euros"
    )
    montant_fcfa = models.DecimalField(
        max_digits=15, decimal_places=2,
        verbose_name="Montant en FCFA",
        help_text="Calculé automatiquement : montant_eur × 655.957"
    )
    date = models.DateField(verbose_name="Date de la transaction")
    note = models.TextField(blank=True, verbose_name="Note")
    is_recurrent = models.BooleanField(default=False, verbose_name="Dépense récurrente")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    TAUX_FCFA = Decimal('655.957')

    def save(self, *args, **kwargs):
        # Calcul automatique du montant FCFA
        self.montant_fcfa = self.montant_eur * self.TAUX_FCFA
        super().save(*args, **kwargs)

    class Meta:
        ordering = ['-date', '-created_at']
        verbose_name = "Transaction"

    def __str__(self):
        signe = "+" if self.type_tx == 'income' else "-"
        return f"{signe}{self.montant_eur}€ — {self.label} ({self.date})"


class Budget(models.Model):
    """Budget mensuel par catégorie"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='budgets')
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='budgets')
    mois = models.IntegerField(help_text="Mois (1-12)")
    annee = models.IntegerField(help_text="Année (ex: 2026)")
    montant_eur = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'category', 'mois', 'annee']
        verbose_name = "Budget"

    def __str__(self):
        return f"Budget {self.category.nom} — {self.mois}/{self.annee}"


class Objectif(models.Model):
    """Objectif financier personnel"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='objectifs')
    label = models.CharField(max_length=100, verbose_name="Nom de l'objectif")
    icone = models.CharField(max_length=10, default='🎯')
    couleur = models.CharField(max_length=7, default='#818cf8')
    montant_cible_eur = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('1.00'))],
        verbose_name="Montant cible en euros"
    )
    montant_atteint_eur = models.DecimalField(
        max_digits=10, decimal_places=2, default=Decimal('0.00'),
        verbose_name="Montant atteint en euros"
    )
    date_limite = models.DateField(null=True, blank=True, verbose_name="Date limite")
    category_liee = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Catégorie dont les transactions alimentent cet objectif"
    )
    termine = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def pourcentage(self):
        if self.montant_cible_eur == 0:
            return 0
        return min(float(self.montant_atteint_eur / self.montant_cible_eur * 100), 100)

    @property
    def mensualite_recommandee(self):
        """Calcule le montant mensuel nécessaire pour atteindre l'objectif en 12 mois"""
        restant = self.montant_cible_eur - self.montant_atteint_eur
        return max(restant / 12, Decimal('0'))

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Objectif"

    def __str__(self):
        return f"{self.icone} {self.label} — {self.pourcentage:.0f}%"


class Recurrente(models.Model):
    """Dépense ou revenu récurrent mensuel"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurrentes')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    label = models.CharField(max_length=200)
    montant_eur = models.DecimalField(
        max_digits=10, decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    type_tx = models.CharField(
        max_length=10, choices=[('expense', 'Dépense'), ('income', 'Revenu')],
        default='expense'
    )
    jour_du_mois = models.IntegerField(
        default=1,
        help_text="Jour du mois de la dépense (1-28)"
    )
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Dépense récurrente"

    def __str__(self):
        return f"🔄 {self.label} — {self.montant_eur}€/mois"


class Transfert(models.Model):
    """Historique des transferts vers la famille"""
    PROVIDER_CHOICES = [
        ('orange', 'Orange Money'),
        ('sendwave', 'Sendwave'),
        ('lemfi', 'LemFi'),
        ('remitly', 'Remitly'),
        ('wu', 'Western Union'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transferts')
    provider = models.CharField(max_length=20, choices=PROVIDER_CHOICES)
    montant_envoye_eur = models.DecimalField(max_digits=10, decimal_places=2)
    frais_eur = models.DecimalField(max_digits=8, decimal_places=2, default=Decimal('0'))
    montant_recu_fcfa = models.DecimalField(max_digits=15, decimal_places=2)
    destinataire = models.CharField(max_length=100, default='Famille')
    date = models.DateField()
    note = models.TextField(blank=True)
    transaction = models.OneToOneField(
        Transaction, on_delete=models.SET_NULL, null=True, blank=True,
        help_text="Transaction associée dans le wallet"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Transfert famille"

    def __str__(self):
        return f"{self.provider} — {self.montant_envoye_eur}€ → {self.montant_recu_fcfa} FCFA ({self.date})"
