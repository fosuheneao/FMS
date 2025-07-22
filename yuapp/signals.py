from twilio.rest import Client
from django.conf import settings# yuapp/signals.py
from django.core.mail import send_mail
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction

from .models import Payment, Balance, PaymentMethod, ApprovalStatusChoices

User = get_user_model()

@receiver(post_save, sender=Payment)
def handle_payment_post_save(sender, instance, created, **kwargs):
    # Signal to auto-approve cash payments and update order & balance
    # when payment is approved.
    
    updated_fields = []

    # Auto-approve cash payments
    if created and instance.payment_method == PaymentMethod.CASH:
        if instance.approval_status != ApprovalStatusChoices.APPROVED:
            instance.approval_status = ApprovalStatusChoices.APPROVED
            instance.approved_at = timezone.now()

            # Assign default approver if desired
            system_user = User.objects.filter(username='system').first()
            if system_user:
                instance.approved_by = system_user
                updated_fields.append("approved_by")

            updated_fields += ["approval_status", "approved_at"]
            instance.save(update_fields=updated_fields)

    # Ensure updates happen only for approved payments
    if instance.approval_status == ApprovalStatusChoices.APPROVED:
        order = instance.order
        if order:
            with transaction.atomic():
                # Update order payment status
                order.update_payment_status()

                # Update or create Balance
                Balance.objects.update_or_create(
                    order=order,
                    defaults={
                        'total_due': order.total_amount or 0,
                        'amount_paid': order.total_paid or 0,
                        'created_by': instance.created_by,
                    }
                )


########### SEND EMAIL USING SENDGRID
def send_admin_sms(message):
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)

    for phone in settings.ADMIN_PHONE_NUMBERS:
        try:
            client.messages.create(
                body=message,
                from_=settings.TWILIO_PHONE_NUMBER,
                to=phone
            )
        except Exception as e:
            # Log error or handle it gracefully
            print(f"Failed to send SMS to {phone}: {e}")


######### send emails
@receiver(post_save, sender=Payment)
def notify_admin_on_pending_mobile_or_bank_payment(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.payment_method in [PaymentMethod.MOBILE_MONEY, PaymentMethod.BANK_TRANSFER] and instance.approval_status == ApprovalStatusChoices.PENDING:
        subject = f"Pending Payment Approval - Order #{instance.order.id}"
        payment_type = instance.get_payment_method_display()
        message = (
            f"A new {payment_type} payment has been made for Order #{instance.order.id}.\n\n"
            f"Amount: {instance.amount_paid}\n"
            f"Date: {instance.payment_date}\n"
            f"Paid By: {instance.paid_by or 'Unknown'}\n"
            f"Reference: {instance.reference_number or 'N/A'}\n\n"
            f"Please log in to approve or reject this payment."
        )

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            settings.ADMIN_EMAILS,
            fail_silently=False
        )
        
@receiver(post_save, sender=Payment)
def notify_admin_on_pending_mobile_or_bank_payment(sender, instance, created, **kwargs):
    if not created:
        return

    if instance.payment_method in [PaymentMethod.MOBILE_MONEY, PaymentMethod.BANK_TRANSFER] and instance.approval_status == ApprovalStatusChoices.PENDING:
        subject = f"Pending Payment Approval - Order #{instance.order.id}"
        from_email = settings.DEFAULT_FROM_EMAIL
        to_emails = settings.ADMIN_EMAILS

        context = {
            'payment_type': instance.get_payment_method_display(),
            'order_id': instance.order.id,
            'amount': instance.amount_paid,
            'date': instance.payment_date.strftime('%Y-%m-%d %H:%M'),
            'paid_by': instance.paid_by or 'Unknown',
            'reference': instance.reference_number or 'N/A',
        }

        text_content = (
            f"A new {context['payment_type']} payment has been made for Order #{context['order_id']}.\n\n"
            f"Amount: {context['amount']}\n"
            f"Date: {context['date']}\n"
            f"Paid By: {context['paid_by']}\n"
            f"Reference: {context['reference']}\n\n"
            f"Please log in to approve or reject this payment."
        )
        html_content = render_to_string('emails/payment_pending_notification.html', context)

        msg = EmailMultiAlternatives(subject, text_content, from_email, to_emails)
        msg.attach_alternative(html_content, "text/html")
        msg.send()