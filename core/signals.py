from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookRequest, Transaction

@receiver(post_save, sender=BookRequest)
def create_transaction_on_approval(sender, instance, created, **kwargs):
    # Only act when an existing request is updated
    if created:
        return  

    # If approved, create a transaction (only if one doesn't already exist)
    if instance.status == "approved":
        Transaction.objects.get_or_create(
            book=instance.book,
            owner=instance.book.owner,
            borrower=instance.requester,
            transaction_type=instance.request_type,
            status="received"
        )
