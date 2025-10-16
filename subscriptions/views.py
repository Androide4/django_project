# subscriptions/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import ListView, DetailView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Subscription, Plan
from .forms import SubscriptionForm
from django.http import HttpResponseNotFound
from django.utils import timezone
from datetime import timedelta

class SubscriptionListView(LoginRequiredMixin, ListView):
    model = Subscription
    template_name = 'subscriptions/subscription_list.html'
    context_object_name = 'subscriptions'
    paginate_by = 20

    def get_queryset(self):
        # Mostrar solo suscripciones del usuario autenticado
        return Subscription.objects.filter(user=self.request.user).order_by('-end_date')

class SubscriptionDetailView(LoginRequiredMixin, DetailView):
    model = Subscription
    template_name = 'subscriptions/subscription_detail.html'
    context_object_name = 'subscription'

    def get_queryset(self):
        # seguridad: sólo el propietario puede ver su detalle
        return Subscription.objects.filter(user=self.request.user)

class SubscriptionCreateView(LoginRequiredMixin, CreateView):
    model = Subscription
    form_class = SubscriptionForm
    template_name = 'subscriptions/subscription_form.html'
    success_url = reverse_lazy('subscriptions:list')

    def form_valid(self, form):
        # Asigna el usuario actual como owner
        obj = form.save(commit=False)
        obj.user = self.request.user

        # Si hay plan y plan.duration_days se puede calcular end_date automáticamente
        if obj.plan and (not obj.end_date or obj.end_date <= obj.start_date):
            try:
                days = obj.plan.duration_days or 0
                obj.end_date = obj.start_date + timedelta(days=days)
            except Exception:
                pass

        obj.save()
        return super().form_valid(form)

# Custom 404 view (puede usarse en handler404)
def custom_404_view(request, exception=None):
    return render(request, '404.html', status=404)
