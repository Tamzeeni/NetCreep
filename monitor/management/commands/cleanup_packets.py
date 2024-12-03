from django.core.management.base import BaseCommand

from monitor.models import Packet


class Command(BaseCommand):
    help = "Cleanup old packets keeping only the latest 1000"

    def handle(self, *args, **kwargs):
        initial_count = Packet.objects.count()
        Packet.cleanup_old_packets()
        final_count = Packet.objects.count()
        deleted_count = initial_count - final_count

        self.stdout.write(
            self.style.SUCCESS(
                f"Successfully cleaned up packets. Deleted {deleted_count} old packets. "
                f"Current packet count: {final_count}"
            )
        )
