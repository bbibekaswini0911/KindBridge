from django.db import models

# Create your models here.


class CareCenter(models.Model):
    class CenterType(models.TextChoices):
        ORPHANAGE = 'orphanage', 'Orphanage'
        OLD_AGE_HOME = 'old_age_home', 'Old age home'
        CARE_CENTER = 'care_center', 'Care center'

    name = models.CharField(max_length=150)
    center_type = models.CharField(max_length=20, choices=CenterType.choices)
    state = models.CharField(max_length=60)
    district = models.CharField(max_length=60)
    address = models.TextField()
    description = models.TextField()
    phone = models.CharField(max_length=15, blank=True)
    image = models.ImageField(upload_to='centers/', blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Requirement(models.Model):
    class Category(models.TextChoices):
        FOOD = 'food', 'Food'
        CLOTHES = 'clothes', 'Clothes'
        MEDICINE = 'medicine', 'Medicine'
        BOOKS = 'books', 'Books'
        OTHER = 'other', 'Other'

    center = models.ForeignKey(CareCenter, on_delete=models.CASCADE, related_name='requirements')
    category = models.CharField(max_length=20, choices=Category.choices)
    item_name = models.CharField(max_length=100)
    quantity_needed = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.item_name} for {self.center.name}'