from django.db import transaction as db_transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import BookRequest, Notification, Transaction, Book


"""
SIGNAL BEHAVIOR SUMMARY:

1️⃣ When a BookRequest is saved with status == "approved":
    - A Transaction is created automatically (unless it already exists)
    - RENT:
        -> book becomes unavailable (available_for = "none")
    - DONATE:
        -> book ownership transfers to requester
        -> book becomes unavailable
    - EXCHANGE:
        -> requester must provide exchange_book
        -> swap ownership between both books
        -> both books become unavailable
        -> if missing or invalid exchange_book -> create admin notification

2️⃣ When a Transaction is saved with status == "returned":
    - ONLY for RENT:
        -> book becomes available again (available_for = "rent")
        -> notify wishlist users
"""


# ------------------------------------------------------------
# When request is approved → create Transaction + apply logic
# ------------------------------------------------------------
@receiver(post_save, sender=BookRequest)
def create_transaction_after_approval(sender, instance, created, **kwargs):
    if instance.status != "approved":
        return

    book = instance.book
    requester = instance.requester
    req_type = instance.request_type

    # Avoid duplicate transactions
    exists = Transaction.objects.filter(
        book=book,
        borrower=requester,
        owner=book.owner,
        transaction_type=req_type,
        status="received"
    ).exists()

    if exists:
        return

    # All operations are atomic (safe)
    with db_transaction.atomic():

        # Create Transaction record
        txn = Transaction.objects.create(
            book=book,
            owner=book.owner,
            borrower=requester,
            transaction_type=req_type,
            status="received"
        )

        # --------------------------------------------------------
        # RENT LOGIC
        # --------------------------------------------------------
        if req_type == "rent":
            book.available_for = "none"
            book.save(update_fields=["available_for"])

        # --------------------------------------------------------
        # DONATE LOGIC
        # (Book permanently belongs to requester)
        # --------------------------------------------------------
        elif req_type == "donate":
            book.owner = requester
            book.available_for = "none"
            book.save(update_fields=["owner_id", "available_for"])

        # --------------------------------------------------------
        # EXCHANGE LOGIC
        # (Swap ownership of two books)
        # --------------------------------------------------------
        elif req_type == "exchange":
            exchange_book = getattr(instance, "exchange_book", None)

            # Must exist AND belong to requester
            if exchange_book and exchange_book.owner == requester:
                original_owner = book.owner

                # Swap owners
                book.owner = requester
                exchange_book.owner = original_owner

                # Both books become unavailable after exchange
                book.available_for = "none"
                exchange_book.available_for = "none"

                # Save
                book.save(update_fields=["owner_id", "available_for"])
                exchange_book.save(update_fields=["owner_id", "available_for"])

            else:
                # Missing or invalid exchange_book → create admin notification
                Notification.objects.create(
                    user=book.owner,
                    message=(
                        f"Exchange request #{instance.id} approved but missing/invalid "
                        f"exchange_book. Please complete the exchange manually."
                    )
                )


# ----------------------------------------------------------------------
# When Transaction is marked returned → book becomes available again
# ----------------------------------------------------------------------
@receiver(post_save, sender=Transaction)
def notify_on_book_return(sender, instance, **kwargs):
    if instance.status != "returned":
        return

    book = instance.book

    # Returned books become available again (ONLY for rent)
    if instance.transaction_type == "rent":
        book.available_for = "rent"
        book.save(update_fields=["available_for"])

    # Notify wishlist users (if related_name is 'wishlist_users')
    try:
        wishlist_entries = book.wishlist_users.all()
    except Exception:
        # fallback if related_name not set
        wishlist_entries = getattr(book, "wishlist_set", []).all()

    for item in wishlist_entries:
        # item may be Wishlist or User depending on model
        user = item.user if hasattr(item, "user") else item
        Notification.objects.create(
            user=user,
            message=f"The book '{book.title}' is now available again!"
        )
