from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookRequest, Notification, Transaction

@receiver(post_save, sender=BookRequest)
def create_transaction_after_approval(sender, instance, created, **kwargs):
    if instance.status != "approved":
        return

    # Avoid duplicate
    exists = Transaction.objects.filter(
        book=instance.book,
        borrower=instance.requester,
        owner=instance.book.owner,
        transaction_type=instance.request_type,
        status="received"
    ).first()

    if exists:
        return

    # Create Transaction
    txn = Transaction.objects.create(
        book=instance.book,
        owner=instance.book.owner,
        borrower=instance.requester,
        transaction_type=instance.request_type,
        status="received"
    )

    # Mark book unavailable only for RENT
    if instance.request_type == "rent":
        instance.book.available_for = "none"
        instance.book.save()

@receiver(post_save, sender=Transaction)
def notify_on_book_return(sender, instance, **kwargs):
    # Only on status change to returned
    if instance.status != "returned":
        return

    book = instance.book

    # Mark book available again (only for rent)
    if instance.transaction_type == "rent":
        book.available_for = "rent"
        book.save()

    # Notify wishlist users
    wishlist_users = book.wishlist_users.all()

    for user in wishlist_users:
        Notification.objects.create(
            user=user,
            message=f"The book '{book.title}' is now available again!"
        )
