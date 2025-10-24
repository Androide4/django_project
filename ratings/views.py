from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy, reverse
from django.views.generic import ListView, CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseForbidden
from subscriptions.models import Subscription
from .models import Rating
from .forms import RatingForm
from django.db import models


class RatingListView(ListView):
    model = Rating
    template_name = "ratings/rating_list.html"
    context_object_name = "ratings"

    def get_queryset(self):
        self.subscription = Subscription.objects.get(pk=self.kwargs["subscription_pk"])
        return Rating.objects.filter(subscription=self.subscription)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["subscription"] = self.subscription
        context["avg_score"] = Rating.objects.filter(subscription=self.subscription).aggregate(
            models.Avg("score")
        )["score__avg"]
        return context


class RatingCreateView(LoginRequiredMixin, CreateView):
    model = Rating
    form_class = RatingForm
    template_name = 'ratings/rating_form.html'

    def dispatch(self, request, *args, **kwargs):
        # validar subs existe y que el usuario sea el dueño
        self.subscription = get_object_or_404(Subscription, pk=self.kwargs.get('subscription_pk'))
        if self.subscription.user != request.user:
            return HttpResponseForbidden("No tienes permiso para calificar esta suscripción.")
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        obj = form.save(commit=False)
        obj.user = self.request.user
        obj.subscription = self.subscription
        obj.save()
        return redirect('subscriptions:detail', pk=self.subscription.pk)