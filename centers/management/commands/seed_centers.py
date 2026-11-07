from django.core.management.base import BaseCommand

from centers.models import CareCenter, Requirement

DATA = [
    {
        'name': 'Asha Kiran Balashram', 'type': 'orphanage',
        'state': 'Odisha', 'district': 'Khordha',
        'address': 'Near Old Town, Bhubaneswar',
        'description': 'A home for children without parents, giving them food, schooling and care.',
        'needs': [('food', 'Rice (kg)', 80), ('books', 'School notebooks', 150), ('clothes', 'Children clothes', 60)],
    },
    {
        'name': 'Shanti Nivas Elder Home', 'type': 'old_age_home',
        'state': 'Odisha', 'district': 'Cuttack',
        'address': 'Buxi Bazar, Cuttack',
        'description': 'A peaceful home where elders live with dignity, regular meals and medical care.',
        'needs': [('medicine', 'Basic medicine kits', 40), ('food', 'Wheat flour (kg)', 100), ('clothes', 'Blankets', 50)],
    },
    {
        'name': 'Jeevan Jyoti Care Centre', 'type': 'care_center',
        'state': 'Odisha', 'district': 'Puri',
        'address': 'Grand Road, Puri',
        'description': 'A care centre supporting people who need shelter and day-to-day help.',
        'needs': [('medicine', 'First aid boxes', 30), ('clothes', 'Bed sheets', 70)],
    },
    {
        'name': 'Snehalaya Children Home', 'type': 'orphanage',
        'state': 'Odisha', 'district': 'Ganjam',
        'address': 'Berhampur, Ganjam',
        'description': 'Shelter and education for orphaned and abandoned children.',
        'needs': [('books', 'Story books', 120), ('food', 'Pulses (kg)', 60), ('other', 'School bags', 45)],
    },
    {
        'name': 'Vriddha Seva Sadan', 'type': 'old_age_home',
        'state': 'Odisha', 'district': 'Sambalpur',
        'address': 'Ainthapali, Sambalpur',
        'description': 'Service home for senior citizens with no one to look after them.',
        'needs': [('clothes', 'Warm shawls', 55), ('medicine', 'Diabetes care kits', 25), ('food', 'Cooking oil (litre)', 40)],
    },
    {
        'name': 'Ananda Care Home', 'type': 'care_center',
        'state': 'Odisha', 'district': 'Khordha',
        'address': 'Patia, Bhubaneswar',
        'description': 'A home that supports differently abled and needy people with food and care.',
        'needs': [('food', 'Rice (kg)', 70), ('medicine', 'Wheelchair repair kits', 10), ('clothes', 'Daily wear clothes', 80)],
    },
    {
        'name': 'Bal Vikas Ashram', 'type': 'orphanage',
        'state': 'Odisha', 'district': 'Balasore',
        'address': 'Sahadevkhunta, Balasore',
        'description': 'Children get a safe home, meals and help with their studies.',
        'needs': [('books', 'Exercise books', 200), ('food', 'Milk powder (kg)', 35)],
    },
    {
        'name': 'Sandhya Elder Care', 'type': 'old_age_home',
        'state': 'Odisha', 'district': 'Khordha',
        'address': 'Chandrasekharpur, Bhubaneswar',
        'description': 'A comfortable home for elders with nursing support and daily activities.',
        'needs': [('medicine', 'BP monitors', 8), ('clothes', 'Blankets', 45), ('other', 'Walking sticks', 20)],
    },
]


class Command(BaseCommand):
    help = 'Add sample care centers and their requirements'

    def handle(self, *args, **options):
        created = 0
        for d in DATA:
            center, was_created = CareCenter.objects.get_or_create(
                name=d['name'],
                defaults={
                    'center_type': d['type'],
                    'state': d['state'],
                    'district': d['district'],
                    'address': d['address'],
                    'description': d['description'],
                },
            )
            if was_created:
                created += 1
                for category, item, qty in d['needs']:
                    Requirement.objects.create(
                        center=center, category=category,
                        item_name=item, quantity_needed=qty,
                    )
        self.stdout.write(self.style.SUCCESS(f'Done. {created} new care center(s) added.'))