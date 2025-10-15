from decimal import Decimal
from django.conf import settings
from django.db import models
from django.utils import timezone

# Proveedor (Falabella, HBO, etc.)
class Provider(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)
    website = models.URLField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True)  # p.ej. 'retail', 'streaming'
    logo = models.ImageField(upload_to='provider_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"

    def __str__(self):
        return self.name


# Moneda (USD, COP, EUR, GBP, etc.)
class Currency(models.Model):
    code = models.CharField(max_length=3, unique=True)  # ISO code
    symbol = models.CharField(max_length=5, blank=True)
    decimals = models.PositiveSmallIntegerField(default=2)
    last_updated = models.DateTimeField(null=True, blank=True)  # cuando se actualizó tasa si aplica

    class Meta:
        verbose_name = "Moneda"
        verbose_name_plural = "Monedas"

    def __str__(self):
        return self.code


# Planes predefinidos de un proveedor (opcional)
class Plan(models.Model):
    provider = models.ForeignKey(Provider, on_delete=models.CASCADE, related_name="plans")
    name = models.CharField(max_length=120)
    duration_days = models.PositiveIntegerField(help_text="Duración en días")  # p.ej. 30 para mensual
    price = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Plan"
        verbose_name_plural = "Planes"
        unique_together = (('provider','name'),)

    def __str__(self):
        return f"{self.provider.name} - {self.name}"


# Métodos de pago (tokenizados)
class PaymentMethod(models.Model):
    KIND_CHOICES = [
        ('card', 'Card'),
        ('wallet', 'Wallet'),
        ('bank', 'Bank Account'),
        ('other', 'Other'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payment_methods")
    kind = models.CharField(max_length=30, choices=KIND_CHOICES)
    token = models.CharField(max_length=255)  # id/token del gateway (no guardar PAN)
    last4 = models.CharField(max_length=4, blank=True, null=True)
    brand = models.CharField(max_length=50, blank=True, null=True)  # Visa, Mastercard
    is_default = models.BooleanField(default=False)
    metadata = models.JSONField(blank=True, null=True)  # almacenar info extra si se necesita
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Método de pago"
        verbose_name_plural = "Métodos de pago"

    def __str__(self):
        return f"{self.user} - {self.kind} {'(default)' if self.is_default else ''}"


# Suscripción principal
class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('paused', 'Paused'),
        ('cancelled', 'Cancelled'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    provider = models.ForeignKey(Provider, on_delete=models.PROTECT, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, blank=True, related_name="subscriptions")
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    auto_renew = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    description = models.TextField(blank=True, null=True, help_text="Motivo o detalles de la suscripción")  # <-- campo solicitado
    external_id = models.CharField(max_length=255, blank=True, null=True)  # ID en gateway externo si aplica
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Suscripción"
        verbose_name_plural = "Suscripciones"
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"{self.user} - {self.provider} ({self.status})"


# Pagos realizados / intentos de pago
class Payment(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

    # Un pago puede estar ligado a una suscripción o solo al usuario (si es recarga, por ejemplo)
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="payments")
    payment_method = models.ForeignKey(PaymentMethod, on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.ForeignKey(Currency, on_delete=models.PROTECT)
    exchange_rate = models.DecimalField(max_digits=18, decimal_places=8, null=True, blank=True, help_text="Tasa usada para convertir si aplica")
    fee = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reference = models.CharField(max_length=255, blank=True, null=True, help_text="Referencia del gateway o id de transacción")
    gateway_response = models.JSONField(blank=True, null=True)
    paid_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Pago"
        verbose_name_plural = "Pagos"
        indexes = [
            models.Index(fields=['reference']),
            models.Index(fields=['status']),
        ]

    def __str__(self):
        return f"{self.user} - {self.amount} {self.currency} ({self.status})"


# Notificaciones programadas / enviadas (recordatorio de expiración, cobro fallido, etc.)
class Notification(models.Model):
    KIND_CHOICES = [
        ('expiry_reminder', 'Expiry reminder'),
        ('payment_failed', 'Payment failed'),
        ('payment_succeeded', 'Payment succeeded'),
        ('manual', 'Manual'),
    ]
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, null=True, blank=True, related_name="notifications")
    kind = models.CharField(max_length=50, choices=KIND_CHOICES)
    send_at = models.DateTimeField()  # cuándo debe enviarse
    sent_at = models.DateTimeField(null=True, blank=True)  # cuándo se envió realmente
    payload = models.JSONField(blank=True, null=True)  # datos útiles para renderizar notificación
    read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        indexes = [
            models.Index(fields=['user', 'send_at']),
            models.Index(fields=['sent_at']),
        ]

    def __str__(self):
        return f"{self.user} - {self.kind} - send_at={self.send_at}"


# Comentarios / notas múltiples por suscripción
class Comment(models.Model):
    subscription = models.ForeignKey(Subscription, on_delete=models.CASCADE, related_name="comments")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    text = models.TextField()
    metadata = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ['-created_at']

    def __str__(self):
        return f"Comentario de {self.user} en {self.subscription}"


# Registro de auditoría (opcional pero recomendado)
class AuditLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('update', 'Update'),
        ('delete', 'Delete'),
        ('system', 'System'),
    ]
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    model_name = models.CharField(max_length=200)
    object_pk = models.CharField(max_length=200, blank=True, null=True)
    changes = models.JSONField(blank=True, null=True)  # estructura con los cambios
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AuditLog"
        verbose_name_plural = "AuditLogs"
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} {self.model_name} ({self.object_pk}) by {self.user}"
