from django.db import models

# Create your models here.

from django.db.models import Sum

from accounts.models import Donor
from centers.models import CareCenter

CATEGORIES = [
    ('food', 'Food'),
    ('clothes', 'Clothes'),
    ('medicine', 'Medicine'),
    ('books', 'Books'),
    ('other', 'Other'),
]


class PickupInfo(models.Model):
    """Hand-over details shared by pledges and claims (abstract: no table of its own)."""
    METHODS = [
        ('center_pickup', 'Care centre sends a person to collect'),
        ('donor_delivers', 'Donor delivers to the care centre'),
    ]
    method = models.CharField(max_length=20, choices=METHODS, blank=True)
    pickup_address = models.TextField(blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    pickup_time = models.CharField(max_length=40, blank=True)
    person_name = models.CharField(max_length=100, blank=True)
    person_phone = models.CharField(max_length=15, blank=True)

    class Meta:
        abstract = True


# ---------- A) Needs market: care centre -> donors ----------

class NeedPost(models.Model):
    center = models.ForeignKey(CareCenter, on_delete=models.CASCADE, related_name='need_posts')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    quantity = models.PositiveIntegerField()
    unit = models.CharField(max_length=30, blank=True)
    description = models.TextField()
    needed_by = models.DateField(null=True, blank=True)
    is_closed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.center.name})'

    @property
    def taken(self):
        if hasattr(self, 'taken_qty'):          # filled by helpers.with_taken() for lists
            return self.taken_qty
        total = self.pledges.filter(status__in=['taken', 'completed']).aggregate(t=Sum('quantity'))['t']
        return total or 0

    @property
    def remaining(self):
        return max(self.quantity - self.taken, 0)

    @property
    def is_open(self):
        return (not self.is_closed) and self.remaining > 0

    @property
    def percent(self):
        return min(round(self.taken * 100 / self.quantity), 100) if self.quantity else 0

    @property
    def cover(self):
        photos = list(self.photos.all())
        return photos[0] if photos else None


class NeedPhoto(models.Model):
    post = models.ForeignKey(NeedPost, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='needs/%Y/%m/')


class NeedPledge(PickupInfo):
    """A donor takes (a part of) a centre's need."""
    class Status(models.TextChoices):
        TAKEN = 'taken', 'Taken'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    post = models.ForeignKey(NeedPost, on_delete=models.CASCADE, related_name='pledges')
    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='pledges')
    quantity = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.TAKEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.donor} took {self.quantity} of {self.post.title}'

    @property
    def bucket(self):
        return {'taken': 'pending', 'completed': 'completed'}.get(self.status, 'closed')


# ---------- B) Donor items: donor -> care centres ----------

class Offer(models.Model):
    class Status(models.TextChoices):
        OPEN = 'open', 'Open'
        RESERVED = 'reserved', 'Reserved'
        COMPLETED = 'completed', 'Completed'
        CLOSED = 'closed', 'Closed'

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='offers')
    title = models.CharField(max_length=150)
    category = models.CharField(max_length=20, choices=CATEGORIES)
    quantity = models.PositiveIntegerField()
    description = models.TextField()
    city = models.CharField(max_length=60)
    address = models.TextField()
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.OPEN, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.donor})'

    @property
    def cover(self):
        photos = list(self.photos.all())
        return photos[0] if photos else None


class OfferPhoto(models.Model):
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='offers/%Y/%m/')


class OfferClaim(PickupInfo):
    """A care centre asks for a donor's item. Claims form a line ordered by created_at."""
    class Status(models.TextChoices):
        WAITING = 'waiting', 'Waiting'
        ACCEPTED = 'accepted', 'Accepted'
        DECLINED = 'declined', 'Declined'
        COMPLETED = 'completed', 'Completed'
        CANCELLED = 'cancelled', 'Cancelled'

    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name='claims')
    center = models.ForeignKey(CareCenter, on_delete=models.CASCADE, related_name='claims')
    message = models.TextField(blank=True)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.WAITING, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created_at']
        unique_together = ('offer', 'center')

    def __str__(self):
        return f'{self.center.name} wants {self.offer.title}'

    @property
    def bucket(self):
        if self.status in ('waiting', 'accepted'):
            return 'pending'
        return 'completed' if self.status == 'completed' else 'closed'


# ---------- C) Contact form on the landing page ----------

class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name}: {self.message[:40]}'