from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import Donation
from datetime import timedelta

class Command(BaseCommand):
    help = 'Cleans up donations that have been expired for more than 24 hours'

    def handle(self, *args, **kwargs):
        now = timezone.now()
        cleanup_threshold = now - timedelta(hours=24)

        # Update status of any past-due available/requested donations to expired
        expired_count = Donation.objects.filter(
            status__in=['available', 'requested'],
            expiry_time__lt=now
        ).update(status='expired')
        
        self.stdout.write(self.style.SUCCESS(f'Marked {expired_count} donations as expired.'))

        # Delete donations that have been expired and are older than 24 hours
        donations_to_delete = Donation.objects.filter(
            status='expired',
            expiry_time__lt=cleanup_threshold
        )
        
        delete_count, _ = donations_to_delete.delete()
        
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {delete_count} expired donations.'))
