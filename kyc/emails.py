from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_kyc_status_email(document, status):
    """Send email notification when KYC status changes"""
    user = document.user
    if not user.email:
        return

    full_name = user.get_full_name() or user.username
    doc_type = document.get_document_type_display()

    if status == 'approved':
        subject = 'KYC Verification Approved – Department of Transport Management, Nepal'
        plain_message = f"""
Government of Nepal
Department of Transport Management

Dear {full_name},

This is to inform you that your {doc_type} submitted for KYC verification has been APPROVED.

You may now proceed to register your vehicle through the Vehicle Registration Portal.

Reference No: KYC-{document.id:06d}
Status: Approved
Date: {document.reviewed_at.strftime('%B %d, %Y')}

This is a system-generated email. Please do not reply to this email.

Department of Transport Management
Government of Nepal
"""
        html_message = f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #ddd;">
    <div style="background:#0b3d2e;padding:20px;text-align:center;">
        <h2 style="color:#fff;margin:0;font-size:18px;">सरकार | Government of Nepal</h2>
        <p style="color:#cde9d8;margin:5px 0 0;font-size:13px;">Department of Transport Management</p>
    </div>
    <div style="padding:25px;background:#fff;">
        <p>Dear <strong>{full_name}</strong>,</p>
        <p>This is to inform you that your <strong>{doc_type}</strong> submitted for KYC verification has been:</p>
        <p style="text-align:center;margin:20px 0;">
            <span style="background:#16a34a;color:#fff;padding:8px 20px;border-radius:4px;font-weight:bold;letter-spacing:1px;">APPROVED</span>
        </p>
        <p>You may now proceed to register your vehicle through the Vehicle Registration Portal.</p>
        <table style="width:100%;margin:20px 0;border-collapse:collapse;font-size:14px;">
            <tr><td style="padding:6px 0;color:#555;">Reference No:</td><td style="padding:6px 0;font-weight:bold;">KYC-{document.id:06d}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Status:</td><td style="padding:6px 0;font-weight:bold;color:#16a34a;">Approved</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Date:</td><td style="padding:6px 0;font-weight:bold;">{document.reviewed_at.strftime('%B %d, %Y')}</td></tr>
        </table>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="font-size:12px;color:#888;">This is a system-generated email. Please do not reply to this email.</p>
        <p style="font-size:12px;color:#888;margin:0;">Department of Transport Management, Government of Nepal</p>
    </div>
</div>
"""
    elif status == 'rejected':
        subject = 'KYC Verification Rejected – Department of Transport Management, Nepal'
        plain_message = f"""
Government of Nepal
Department of Transport Management

Dear {full_name},

This is to inform you that your {doc_type} submitted for KYC verification has been REJECTED.

Reason: {document.remarks or 'No remarks provided'}

Please log in to the Vehicle Registration Portal to upload a new document.

Reference No: KYC-{document.id:06d}
Status: Rejected
Date: {document.reviewed_at.strftime('%B %d, %Y')}

This is a system-generated email. Please do not reply to this email.

Department of Transport Management
Government of Nepal
"""
        html_message = f"""
<div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;border:1px solid #ddd;">
    <div style="background:#0b3d2e;padding:20px;text-align:center;">
        <h2 style="color:#fff;margin:0;font-size:18px;">सरकार | Government of Nepal</h2>
        <p style="color:#cde9d8;margin:5px 0 0;font-size:13px;">Department of Transport Management</p>
    </div>
    <div style="padding:25px;background:#fff;">
        <p>Dear <strong>{full_name}</strong>,</p>
        <p>This is to inform you that your <strong>{doc_type}</strong> submitted for KYC verification has been:</p>
        <p style="text-align:center;margin:20px 0;">
            <span style="background:#dc2626;color:#fff;padding:8px 20px;border-radius:4px;font-weight:bold;letter-spacing:1px;">REJECTED</span>
        </p>
        <p><strong>Reason:</strong> {document.remarks or 'No remarks provided'}</p>
        <p>Please log in to the Vehicle Registration Portal to upload a new document.</p>
        <table style="width:100%;margin:20px 0;border-collapse:collapse;font-size:14px;">
            <tr><td style="padding:6px 0;color:#555;">Reference No:</td><td style="padding:6px 0;font-weight:bold;">KYC-{document.id:06d}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Status:</td><td style="padding:6px 0;font-weight:bold;color:#dc2626;">Rejected</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Date:</td><td style="padding:6px 0;font-weight:bold;">{document.reviewed_at.strftime('%B %d, %Y')}</td></tr>
        </table>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="font-size:12px;color:#888;">This is a system-generated email. Please do not reply to this email.</p>
        <p style="font-size:12px;color:#888;margin:0;">Department of Transport Management, Government of Nepal</p>
    </div>
</div>
"""
    else:
        return

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )
    email.attach_alternative(html_message, "text/html")
    email.send(fail_silently=True)