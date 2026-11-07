from django.db import models

# Create your models here.

from accounts.models import Donor
from centers.models import CareCenter, Requirement


class DonationRequest(models.Model):
    class Status(models.TextChoices):
        PENDING = 'pending', 'Pending'
        APPROVED = 'approved', 'Approved'
        REJECTED = 'rejected', 'Rejected'

    donor = models.ForeignKey(Donor, on_delete=models.CASCADE, related_name='requests')
    center = models.ForeignKey(CareCenter, on_delete=models.CASCADE, related_name='requests')
    requirement = models.ForeignKey(Requirement, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    message = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.donor} to {self.center} ({self.get_status_display()})'