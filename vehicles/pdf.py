from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import io

def generate_vehicle_registration_slip(vehicle):
    """Generate a government-style PDF registration slip"""
    buffer = io.BytesIO()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm,
        leftMargin=2*cm,
        topMargin=2*cm,
        bottomMargin=2*cm,
    )

    elements = []
    styles = getSampleStyleSheet()

    # ── Colors ──
    green_dark = colors.HexColor('#0b3d2e')
    green_light = colors.HexColor('#cde9d8')
    red = colors.HexColor('#dc2626')
    gray = colors.HexColor('#6b7280')
    black = colors.HexColor('#111827')

    # ── Header style ──
    header_style = ParagraphStyle(
        'Header',
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=colors.white,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    sub_header_style = ParagraphStyle(
        'SubHeader',
        fontName='Helvetica',
        fontSize=10,
        textColor=green_light,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    title_style = ParagraphStyle(
        'Title',
        fontName='Helvetica-Bold',
        fontSize=13,
        textColor=black,
        alignment=TA_CENTER,
        spaceAfter=6,
    )
    label_style = ParagraphStyle(
        'Label',
        fontName='Helvetica',
        fontSize=9,
        textColor=gray,
    )
    value_style = ParagraphStyle(
        'Value',
        fontName='Helvetica-Bold',
        fontSize=10,
        textColor=black,
    )
    footer_style = ParagraphStyle(
        'Footer',
        fontName='Helvetica',
        fontSize=8,
        textColor=gray,
        alignment=TA_CENTER,
    )

    # ── Government Header ──
    header_data = [
        [Paragraph('सरकार | Government of Nepal', header_style)],
        [Paragraph('Department of Transport Management', sub_header_style)],
        [Paragraph('Bagmati Province, Kathmandu', sub_header_style)],
    ]
    header_table = Table(header_data, colWidths=[17*cm])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), green_dark),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('TOPPADDING', (0, 0), (-1, -1), 12),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [green_dark]),
    ]))
    elements.append(header_table)
    elements.append(Spacer(1, 0.4*cm))

    # ── Title ──
    elements.append(Paragraph('VEHICLE REGISTRATION CERTIFICATE', title_style))
    elements.append(HRFlowable(width='100%', thickness=2, color=red))
    elements.append(Spacer(1, 0.4*cm))

    # ── Reference + Status ──
    ref_data = [
        [
            Paragraph('<b>Reference No:</b>', label_style),
            Paragraph(f'VEH-{vehicle.id:06d}', value_style),
            Paragraph('<b>Status:</b>', label_style),
            Paragraph('APPROVED', ParagraphStyle('Approved', fontName='Helvetica-Bold', fontSize=10, textColor=colors.HexColor('#16a34a'))),
        ],
        [
            Paragraph('<b>Issue Date:</b>', label_style),
            Paragraph(vehicle.reviewed_at.strftime('%B %d, %Y') if vehicle.reviewed_at else 'N/A', value_style),
            Paragraph('<b>Reviewed By:</b>', label_style),
            Paragraph(str(vehicle.reviewed_by.get_full_name() or vehicle.reviewed_by.username) if vehicle.reviewed_by else 'Staff', value_style),
        ],
    ]
    ref_table = Table(ref_data, colWidths=[3.5*cm, 5*cm, 3*cm, 5.5*cm])
    ref_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f9fafb')),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(ref_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Owner Details ──
    elements.append(Paragraph('OWNER INFORMATION', ParagraphStyle('SectionTitle', fontName='Helvetica-Bold', fontSize=10, textColor=green_dark, spaceAfter=4)))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=green_dark))
    elements.append(Spacer(1, 0.2*cm))

    owner = vehicle.owner
    profile = owner.profile
    owner_data = [
        [Paragraph('Full Name', label_style), Paragraph(owner.get_full_name() or owner.username, value_style),
         Paragraph('Username', label_style), Paragraph(owner.username, value_style)],
        [Paragraph('Email', label_style), Paragraph(owner.email or 'N/A', value_style),
         Paragraph('Phone', label_style), Paragraph(profile.phone or 'N/A', value_style)],
        [Paragraph('Address', label_style), Paragraph(profile.address or 'N/A', value_style),
         Paragraph('Date of Birth', label_style), Paragraph(str(profile.date_of_birth) if profile.date_of_birth else 'N/A', value_style)],
    ]
    owner_table = Table(owner_data, colWidths=[3.5*cm, 5*cm, 3*cm, 5.5*cm])
    owner_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(owner_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Vehicle Details ──
    elements.append(Paragraph('VEHICLE INFORMATION', ParagraphStyle('SectionTitle2', fontName='Helvetica-Bold', fontSize=10, textColor=green_dark, spaceAfter=4)))
    elements.append(HRFlowable(width='100%', thickness=0.5, color=green_dark))
    elements.append(Spacer(1, 0.2*cm))

    vehicle_data = [
        [Paragraph('Vehicle Type', label_style), Paragraph(vehicle.get_vehicle_type_display(), value_style),
         Paragraph('Make', label_style), Paragraph(vehicle.make, value_style)],
        [Paragraph('Model', label_style), Paragraph(vehicle.model, value_style),
         Paragraph('Year', label_style), Paragraph(str(vehicle.year), value_style)],
        [Paragraph('Color', label_style), Paragraph(vehicle.color, value_style),
         Paragraph('Status', label_style), Paragraph(vehicle.status.upper(), value_style)],
        [Paragraph('Engine Number', label_style), Paragraph(vehicle.engine_number, value_style),
         Paragraph('Chassis Number', label_style), Paragraph(vehicle.chassis_number, value_style)],
    ]
    vehicle_table = Table(vehicle_data, colWidths=[3.5*cm, 5*cm, 3*cm, 5.5*cm])
    vehicle_table.setStyle(TableStyle([
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(vehicle_table)
    elements.append(Spacer(1, 0.8*cm))

    # ── Signature Section ──
    sig_data = [
        [
            Paragraph('_______________________', ParagraphStyle('Sig', fontName='Helvetica', fontSize=10, alignment=TA_CENTER)),
            Paragraph('_______________________', ParagraphStyle('Sig', fontName='Helvetica', fontSize=10, alignment=TA_CENTER)),
        ],
        [
            Paragraph('Authorized Officer', ParagraphStyle('SigLabel', fontName='Helvetica-Bold', fontSize=9, textColor=gray, alignment=TA_CENTER)),
            Paragraph('Department Stamp', ParagraphStyle('SigLabel', fontName='Helvetica-Bold', fontSize=9, textColor=gray, alignment=TA_CENTER)),
        ],
    ]
    sig_table = Table(sig_data, colWidths=[8.5*cm, 8.5*cm])
    sig_table.setStyle(TableStyle([
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sig_table)
    elements.append(Spacer(1, 0.5*cm))

    # ── Footer ──
    elements.append(HRFlowable(width='100%', thickness=0.5, color=colors.HexColor('#e5e7eb')))
    elements.append(Spacer(1, 0.2*cm))
    elements.append(Paragraph('This is a system-generated certificate. Department of Transport Management, Government of Nepal.', footer_style))
    elements.append(Paragraph(f'Generated on: {vehicle.reviewed_at.strftime("%B %d, %Y") if vehicle.reviewed_at else "N/A"} | Ref: VEH-{vehicle.id:06d}', footer_style))

    doc.build(elements)
    buffer.seek(0)
    return buffer