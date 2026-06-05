"""
URLs — App Wallet
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'transactions', views.TransactionViewSet, basename='transaction')
router.register(r'categories', views.CategoryViewSet, basename='category')
router.register(r'budgets', views.BudgetViewSet, basename='budget')
router.register(r'objectifs', views.ObjectifViewSet, basename='objectif')
router.register(r'recurrentes', views.RecurrenteViewSet, basename='recurrente')
router.register(r'transferts', views.TransfertViewSet, basename='transfert')

urlpatterns = [
    # Router automatique (CRUD complet)
    path('', include(router.urls)),

    # Endpoints spéciaux
    path('auth/register/', views.RegisterView.as_view(), name='register'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analyse/', views.analyse, name='analyse'),
    path('transferts/simuler/', views.simuler_transfert, name='simuler-transfert'),
]
