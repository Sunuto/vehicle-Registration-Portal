from django.core.mail import EmailMultiAlternatives
from django.conf import settings

def send_vehicle_status_email(vehicle, status):
    """Send email notification when vehicle status changes"""
    user = vehicle.owner
    if not user.email:
        return

    full_name = user.get_full_name() or user.username

    if status == 'approved':
        subject = 'Vehicle Registration Approved – Department of Transport Management, Nepal'
        plain_message = f"""
Government of Nepal
Department of Transport Management

Dear {full_name},

This is to inform you that your vehicle registration application has been APPROVED.

Vehicle Details:
- Make: {vehicle.make}
- Model: {vehicle.model}
- Year: {vehicle.year}
- Color: {vehicle.color}
- Engine Number: {vehicle.engine_number}
- Chassis Number: {vehicle.chassis_number}

Reference No: VEH-{vehicle.id:06d}
Status: Approved
Date: {vehicle.reviewed_at.strftime('%B %d, %Y')}

You may now download your official registration slip from the Vehicle Registration Portal.

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
        <p>This is to inform you that your vehicle registration application has been:</p>
        <p style="text-align:center;margin:20px 0;">
            <span style="background:#16a34a;color:#fff;padding:8px 20px;border-radius:4px;font-weight:bold;letter-spacing:1px;">APPROVED</span>
        </p>
        <table style="width:100%;margin:20px 0;border-collapse:collapse;font-size:14px;">
            <tr><td style="padding:6px 0;color:#555;">Make:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.make}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Model:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.model}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Year:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.year}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Color:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.color}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Engine No:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.engine_number}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Chassis No:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.chassis_number}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Reference No:</td><td style="padding:6px 0;font-weight:bold;">VEH-{vehicle.id:06d}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Date:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.reviewed_at.strftime('%B %d, %Y')}</td></tr>
        </table>
        <p>You may now download your official registration slip from the Vehicle Registration Portal.</p>
        <hr style="border:none;border-top:1px solid #eee;margin:20px 0;">
        <p style="font-size:12px;color:#888;">This is a system-generated email. Please do not reply to this email.</p>
        <p style="font-size:12px;color:#888;margin:0;">Department of Transport Management, Government of Nepal</p>
    </div>
</div>
"""
    elif status == 'rejected':
        subject = 'Vehicle Registration Rejected – Department of Transport Management, Nepal'
        plain_message = f"""
Government of Nepal
Department of Transport Management

Dear {full_name},

This is to inform you that your vehicle registration application has been REJECTED.

Vehicle: {vehicle.make} {vehicle.model} ({vehicle.year})
Reason: {vehicle.remarks or 'No remarks provided'}

Reference No: VEH-{vehicle.id:06d}
Status: Rejected
Date: {vehicle.reviewed_at.strftime('%B %d, %Y')}

Please review the remarks and resubmit your application through the Vehicle Registration Portal.

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
        <p>This is to inform you that your vehicle registration application has been:</p>
        <p style="text-align:center;margin:20px 0;">
            <span style="background:#dc2626;color:#fff;padding:8px 20px;border-radius:4px;font-weight:bold;letter-spacing:1px;">REJECTED</span>
        </p>
        <p><strong>Vehicle:</strong> {vehicle.make} {vehicle.model} ({vehicle.year})</p>
        <p><strong>Reason:</strong> {vehicle.remarks or 'No remarks provided'}</p>
        <table style="width:100%;margin:20px 0;border-collapse:collapse;font-size:14px;">
            <tr><td style="padding:6px 0;color:#555;">Reference No:</td><td style="padding:6px 0;font-weight:bold;">VEH-{vehicle.id:06d}</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Status:</td><td style="padding:6px 0;font-weight:bold;color:#dc2626;">Rejected</td></tr>
            <tr><td style="padding:6px 0;color:#555;">Date:</td><td style="padding:6px 0;font-weight:bold;">{vehicle.reviewed_at.strftime('%B %d, %Y')}</td></tr>
        </table>
        <p>Please review the remarks and resubmit your application through the Vehicle Registration Portal.</p>
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