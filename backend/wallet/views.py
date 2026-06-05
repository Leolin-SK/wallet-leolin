"""
Views API — Wallet Léolin
Tous les endpoints REST
"""

from rest_framework import viewsets, status, generics
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.db.models import Sum, Q
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
import calendar

from .models import UserProfile, Category, Transaction, Budget, Objectif, Recurrente, Transfert
from .serializers import (
    RegisterSerializer, UserProfileSerializer, CategorySerializer,
    TransactionSerializer, TransactionCreateSerializer, BudgetSerializer,
    ObjectifSerializer, RecurrenteSerializer, TransfertSerializer,
    DashboardSerializer, SimulateurTransfertSerializer, RepartitionSerializer
)

TAUX_FCFA = Decimal('655.957')
CHARGES_FIXES_TOTAL = Decimal('622.00')  # Total charges fixes mensuelles


# ─── INSCRIPTION ──────────────────────────────────────────────────────────────

class RegisterView(generics.CreateAPIView):
    """POST /api/auth/register/ — Créer un compte"""
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Compte créé avec succès. Bienvenue Léolin ! 🎉',
            'username': user.username,
        }, status=status.HTTP_201_CREATED)


# ─── PROFIL ───────────────────────────────────────────────────────────────────

class ProfileView(generics.RetrieveUpdateAPIView):
    """GET/PUT /api/profile/ — Lire et modifier son profil"""
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        profile, _ = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


# ─── DASHBOARD ────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard(request):
    """GET /api/dashboard/ — Données agrégées pour le tableau de bord"""
    user = request.user
    today = date.today()

    profile, _ = UserProfile.objects.get_or_create(user=user)
    txs = user.transactions.all()

    # Calculs globaux
    total_in = txs.filter(type_tx='income').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')
    total_out = txs.filter(type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')
    solde = profile.solde_initial + total_in - total_out

    # Mois en cours
    mois_txs = txs.filter(date__year=today.year, date__month=today.month)
    mois_in = mois_txs.filter(type_tx='income').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')
    mois_out = mois_txs.filter(type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')

    # Famille & épargne
    cat_famille = user.categories.filter(nom__icontains='famille').first()
    cat_epargne = user.categories.filter(nom__icontains='pargne').first()
    total_famille = txs.filter(category=cat_famille, type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0') if cat_famille else Decimal('0')
    total_epargne = txs.filter(category=cat_epargne, type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0') if cat_epargne else Decimal('0')

    # Santé financière
    if solde > profile.solde_initial * Decimal('0.7'):
        health = 'excellent'
    elif solde > profile.solde_initial * Decimal('0.4'):
        health = 'bon'
    else:
        health = 'critique'

    # Alertes
    alertes = []
    if solde < Decimal('1000'):
        alertes.append({'level': 'danger', 'icon': '🚨', 'text': 'Solde critique ! Contacte le service social CROUS.'})
    elif solde < profile.seuil_alerte:
        alertes.append({'level': 'warn', 'icon': '⚠️', 'text': f'Solde sous {profile.seuil_alerte}€. Réduis les dépenses.'})
    if mois_in == 0:
        alertes.append({'level': 'warn', 'icon': '💼', 'text': 'Aucun revenu ce mois. Lance Uber Eats ou Superprof.'})
    elif mois_in > mois_out:
        alertes.append({'level': 'good', 'icon': '💰', 'text': f'Excédent de {float(mois_in-mois_out):.2f}€ ce mois. Transfère vers l\'épargne !'})

    # Évolution mensuelle (6 derniers mois)
    evolution = []
    for i in range(5, -1, -1):
        d = today.replace(day=1) - timedelta(days=i*30)
        m_txs = txs.filter(date__year=d.year, date__month=d.month)
        m_in = float(m_txs.filter(type_tx='income').aggregate(s=Sum('montant_eur'))['s'] or 0)
        m_out = float(m_txs.filter(type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or 0)
        evolution.append({
            'mois': d.month, 'annee': d.year,
            'label': ['Jan','Fév','Mar','Avr','Mai','Jun','Jul','Aoû','Sep','Oct','Nov','Déc'][d.month-1],
            'revenus': m_in, 'depenses': m_out, 'net': m_in - m_out
        })

    return Response({
        'solde_eur': float(solde),
        'solde_fcfa': float(solde * TAUX_FCFA),
        'solde_initial_eur': float(profile.solde_initial),
        'pourcentage_capital': float(solde / profile.solde_initial * 100) if profile.solde_initial else 0,
        'total_revenus_eur': float(total_in),
        'total_depenses_eur': float(total_out),
        'mois_revenus_eur': float(mois_in),
        'mois_depenses_eur': float(mois_out),
        'mois_solde_eur': float(mois_in - mois_out),
        'total_famille_eur': float(total_famille),
        'total_epargne_eur': float(total_epargne),
        'health_level': health,
        'alertes': alertes,
        'evolution_mensuelle': evolution,
    })


# ─── TRANSACTIONS ─────────────────────────────────────────────────────────────

class TransactionViewSet(viewsets.ModelViewSet):
    """
    CRUD complet sur les transactions
    GET    /api/transactions/           — liste (avec filtres)
    POST   /api/transactions/           — créer
    GET    /api/transactions/{id}/      — détail
    PUT    /api/transactions/{id}/      — modifier
    DELETE /api/transactions/{id}/      — supprimer
    POST   /api/transactions/repartir/ — répartition automatique
    GET    /api/transactions/stats/     — statistiques
    """
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Transaction.objects.filter(user=self.request.user).select_related('category')
        # Filtres optionnels
        mois = self.request.query_params.get('mois')
        annee = self.request.query_params.get('annee')
        type_tx = self.request.query_params.get('type')
        category = self.request.query_params.get('category')
        if mois: qs = qs.filter(date__month=mois)
        if annee: qs = qs.filter(date__year=annee)
        if type_tx: qs = qs.filter(type_tx=type_tx)
        if category: qs = qs.filter(category__id=category)
        return qs

    def get_serializer_class(self):
        if self.action == 'create':
            return TransactionCreateSerializer
        return TransactionSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['post'])
    def repartir(self, request):
        """POST /api/transactions/repartir/ — Répartition automatique d'un montant"""
        montant_eur = Decimal(str(request.data.get('montant_eur', 0)))
        if montant_eur <= 0:
            return Response({'error': 'Montant invalide'}, status=400)

        # Récupérer les catégories fixes
        cats = request.user.categories.filter(type_cat='fixe', budget_mensuel__gt=0)
        total_budget = sum(c.budget_mensuel for c in cats)

        if total_budget == 0:
            return Response({'error': 'Aucune catégorie fixe configurée'}, status=400)

        repartition = []
        for cat in cats:
            pct = cat.budget_mensuel / total_budget
            allocated = round(montant_eur * pct, 2)
            repartition.append({
                'category_id': cat.id,
                'category_nom': cat.nom,
                'category_icone': cat.icone,
                'category_couleur': cat.couleur,
                'pourcentage': round(float(pct * 100), 1),
                'montant_budget_eur': float(cat.budget_mensuel),
                'montant_alloue_eur': float(allocated),
                'montant_alloue_fcfa': round(float(allocated * TAUX_FCFA)),
            })

        return Response({
            'montant_total_eur': float(montant_eur),
            'montant_total_fcfa': round(float(montant_eur * TAUX_FCFA)),
            'repartition': repartition,
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """GET /api/transactions/stats/ — Statistiques par catégorie"""
        today = date.today()
        mois = int(request.query_params.get('mois', today.month))
        annee = int(request.query_params.get('annee', today.year))

        txs = Transaction.objects.filter(
            user=request.user, date__year=annee, date__month=mois
        )
        cats = request.user.categories.all()
        stats = []
        for cat in cats:
            cat_txs = txs.filter(category=cat)
            spent = cat_txs.filter(type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')
            earned = cat_txs.filter(type_tx='income').aggregate(s=Sum('montant_eur'))['s'] or Decimal('0')
            stats.append({
                'category': CategorySerializer(cat).data,
                'depenses_eur': float(spent),
                'revenus_eur': float(earned),
                'budget_restant_eur': float(cat.budget_mensuel - spent),
                'depassement': spent > cat.budget_mensuel,
            })
        return Response(stats)


# ─── CATÉGORIES ───────────────────────────────────────────────────────────────

class CategoryViewSet(viewsets.ModelViewSet):
    """CRUD catégories"""
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── BUDGETS ──────────────────────────────────────────────────────────────────

class BudgetViewSet(viewsets.ModelViewSet):
    """CRUD budgets mensuels"""
    serializer_class = BudgetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Budget.objects.filter(user=self.request.user)
        mois = self.request.query_params.get('mois')
        annee = self.request.query_params.get('annee')
        if mois: qs = qs.filter(mois=mois)
        if annee: qs = qs.filter(annee=annee)
        return qs

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


# ─── OBJECTIFS ────────────────────────────────────────────────────────────────

class ObjectifViewSet(viewsets.ModelViewSet):
    """CRUD objectifs financiers"""
    serializer_class = ObjectifSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Objectif.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def alimenter(self, request, pk=None):
        """POST /api/objectifs/{id}/alimenter/ — Ajouter un montant à un objectif"""
        objectif = self.get_object()
        montant = Decimal(str(request.data.get('montant_eur', 0)))
        if montant <= 0:
            return Response({'error': 'Montant invalide'}, status=400)
        objectif.montant_atteint_eur += montant
        if objectif.montant_atteint_eur >= objectif.montant_cible_eur:
            objectif.termine = True
        objectif.save()
        return Response(ObjectifSerializer(objectif).data)


# ─── RÉCURRENTES ──────────────────────────────────────────────────────────────

class RecurrenteViewSet(viewsets.ModelViewSet):
    """CRUD dépenses récurrentes"""
    serializer_class = RecurrenteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Recurrente.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'])
    def appliquer(self, request, pk=None):
        """POST /api/recurrentes/{id}/appliquer/ — Enregistrer cette récurrente comme transaction"""
        recurrente = self.get_object()
        tx = Transaction.objects.create(
            user=request.user,
            category=recurrente.category,
            type_tx=recurrente.type_tx,
            label=recurrente.label,
            montant_eur=recurrente.montant_eur,
            date=date.today(),
            note='Dépense récurrente automatique',
            is_recurrent=True,
        )
        return Response({
            'message': f'{recurrente.label} enregistré avec succès.',
            'transaction': TransactionSerializer(tx).data,
        })


# ─── TRANSFERTS ───────────────────────────────────────────────────────────────

class TransfertViewSet(viewsets.ModelViewSet):
    """CRUD transferts famille"""
    serializer_class = TransfertSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Transfert.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def simuler_transfert(request):
    """POST /api/transferts/simuler/ — Simuler un transfert famille"""
    montant = float(request.data.get('montant_eur', 0))
    if montant <= 0:
        return Response({'error': 'Montant invalide'}, status=400)

    sim = SimulateurTransfertSerializer()
    results = sim.simulate(montant)
    return Response({
        'montant_envoye_eur': montant,
        'taux_fcfa': 655.957,
        'resultats': results,
    })


# ─── ANALYSE ──────────────────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def analyse(request):
    """GET /api/analyse/ — Analyse complète + plan de structuration"""
    user = request.user
    today = date.today()
    mois = int(request.query_params.get('mois', today.month))
    annee = int(request.query_params.get('annee', today.year))

    txs_mois = user.transactions.filter(date__year=annee, date__month=mois)
    mois_in = float(txs_mois.filter(type_tx='income').aggregate(s=Sum('montant_eur'))['s'] or 0)
    mois_out = float(txs_mois.filter(type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or 0)

    cats = user.categories.filter(type_cat='fixe', budget_mensuel__gt=0)
    recommandations = []
    reste_a_allouer = []

    for cat in cats:
        spent = float(txs_mois.filter(category=cat, type_tx='expense').aggregate(s=Sum('montant_eur'))['s'] or 0)
        budget = float(cat.budget_mensuel)
        ratio = spent / budget if budget > 0 else 0
        remaining = max(budget - spent, 0)

        if ratio > 1.2:
            recommandations.append({'level': 'danger', 'icon': '🔴', 'text': f'{cat.nom} : dépassement de {spent-budget:.2f}€. Réduis immédiatement.'})
        elif ratio > 0.85:
            recommandations.append({'level': 'warn', 'icon': '🟡', 'text': f'{cat.nom} : tu approches du plafond ({ratio*100:.0f}%). Vigilance.'})
        elif spent > 0 and ratio < 0.4:
            recommandations.append({'level': 'good', 'icon': '🟢', 'text': f'{cat.nom} : excellent contrôle — {budget-spent:.2f}€ d\'économies ce mois.'})

        if remaining > 0:
            reste_a_allouer.append({'category': cat.nom, 'icone': cat.icone, 'couleur': cat.couleur, 'restant_eur': remaining, 'restant_fcfa': round(remaining * 655.957)})

    if mois_in == 0:
        recommandations.append({'level': 'warn', 'icon': '💼', 'text': 'Aucun revenu ce mois. Lance-toi sur Uber Eats ou Superprof dès aujourd\'hui.'})
    elif mois_in > mois_out:
        recommandations.append({'level': 'good', 'icon': '💰', 'text': f'Excédent de {mois_in-mois_out:.2f}€ ce mois. Transfère vers l\'épargne !'})

    actions = [
        {'icon': '💼', 'text': f'Générer {max(float(CHARGES_FIXES_TOTAL)-mois_in, 0):.2f}€ de plus — active Uber Eats ce week-end'} if mois_in < float(CHARGES_FIXES_TOTAL)
        else {'icon': '🏦', 'text': f'Transfère {max((mois_in-mois_out)*0.3, 0):.2f}€ vers l\'épargne Année 2 maintenant'},
        {'icon': '🍽️', 'text': 'Too Good To Go 3× cette semaine → économise ~10€ sur l\'alimentation'},
        {'icon': '📊', 'text': 'Reviens analyser tes dépenses chaque vendredi soir — 5 min suffisent'},
    ]

    return Response({
        'mois': mois, 'annee': annee,
        'revenus_eur': mois_in, 'depenses_eur': mois_out, 'solde_mois_eur': mois_in - mois_out,
        'recommandations': recommandations,
        'reste_a_allouer': reste_a_allouer,
        'actions_prioritaires': actions,
    })
