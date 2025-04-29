from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from store.models import Customer

class Command(BaseCommand):
    help = 'Creates Customer objects for users that don\'t have them'

    def handle(self, *args, **kwargs):
        users_without_customers = User.objects.filter(customer__isnull=True)
        count = 0
        for user in users_without_customers:
            Customer.objects.create(
                user=user,
                name=user.username,
                email=user.email if user.email else ''
            )
            count += 1
        self.stdout.write(self.style.SUCCESS(f'Successfully created {count} customer profiles')) 