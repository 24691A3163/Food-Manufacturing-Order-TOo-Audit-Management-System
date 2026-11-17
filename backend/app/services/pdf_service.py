import io
from decimal import Decimal
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from backend.app.core.config import settings
from backend.app.models.invoice import Invoice

class PDFService:
    @staticmethod
    def generate_invoice_pdf(invoice: Invoice) -> bytes:
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=36,
            leftMargin=36,
            topMargin=36,
            bottomMargin=36
        )

        styles = getSampleStyleSheet()
        normal_style = styles["Normal"]
        
        title_style = ParagraphStyle(
            "InvoiceTitle",
            parent=styles["Heading1"],
            fontSize=16,
            leading=20,
            textColor=colors.HexColor("#1e3a8a"),
            fontName="Helvetica-Bold"
        )
        subtitle_style = ParagraphStyle(
            "InvoiceSubtitle",
            parent=styles["Normal"],
            fontSize=9,
            leading=12,
            textColor=colors.HexColor("#475569")
        )
        bold_cell_style = ParagraphStyle(
            "BoldCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=10,
            fontName="Helvetica-Bold"
        )
        cell_style = ParagraphStyle(
            "RegularCell",
            parent=styles["Normal"],
            fontSize=8,
            leading=10
        )

        elements = []

        # 1. Header with Company Info & Title
        header_data = [
            [
                Paragraph(f"<b>{settings.COMPANY_NAME}</b><br/>{settings.COMPANY_ADDRESS}<br/><b>GSTIN:</b> {settings.COMPANY_GSTIN} | <b>State:</b> {settings.COMPANY_STATE} (Code: {settings.COMPANY_STATE_CODE})<br/><b>Phone:</b> {settings.COMPANY_PHONE} | <b>Email:</b> {settings.COMPANY_EMAIL}", subtitle_style),
                Paragraph("<font size=14><b>TAX INVOICE</b></font><br/>(ORIGINAL FOR RECIPIENT)", ParagraphStyle("TR", parent=normal_style, alignment=2, textColor=colors.HexColor("#1e3a8a")))
            ]
        ]
        header_table = Table(header_data, colWidths=[360, 180])
        header_table.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 0),
        ]))
        elements.append(header_table)
        elements.append(Spacer(1, 10))
        elements.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cbd5e1"), spaceAfter=10))

        # 2. Customer & Invoice Details
        cust = invoice.customer
        bill_to_text = f"""<b>Billed To:</b><br/>
<b>{cust.name}</b><br/>
{cust.billing_address or ''}<br/>
<b>GSTIN:</b> {cust.gstin or 'Unregistered'}<br/>
<b>State:</b> {cust.state} (Code: {cust.state_code})<br/>
<b>Contact:</b> {cust.phone or ''}
"""
        inv_meta_text = f"""<b>Invoice No:</b> {invoice.invoice_number}<br/>
<b>Invoice Date:</b> {invoice.invoice_date.strftime('%d-%b-%Y') if invoice.invoice_date else ''}<br/>
<b>Order No:</b> {invoice.order.order_number if invoice.order else 'Direct'}<br/>
<b>Place of Supply:</b> {invoice.place_of_supply}<br/>
<b>Transaction Type:</b> {'INTERSTATE (IGST)' if invoice.is_interstate else 'INTRASTATE (CGST + SGST)'}
"""
        details_table = Table([
            [Paragraph(bill_to_text, cell_style), Paragraph(inv_meta_text, cell_style)]
        ], colWidths=[300, 240])
        details_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor("#f8fafc")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('LEFTPADDING', (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ]))
        elements.append(details_table)
        elements.append(Spacer(1, 12))

        # 3. Items Table
        if invoice.is_interstate:
            headers = ["S.No", "Description of Goods", "HSN", "Qty", "Rate (₹)", "Taxable (₹)", "IGST %", "IGST (₹)", "Total (₹)"]
            col_widths = [25, 140, 50, 35, 45, 60, 45, 60, 80]
        else:
            headers = ["S.No", "Description of Goods", "HSN", "Qty", "Rate (₹)", "Taxable (₹)", "CGST (₹)", "SGST (₹)", "Total (₹)"]
            col_widths = [25, 135, 50, 35, 45, 60, 55, 55, 80]

        table_rows = [[Paragraph(f"<b>{h}</b>", bold_cell_style) for h in headers]]

        idx = 1
        for item in invoice.items:
            prod_name = item.product.name if item.product else "Food Item"
            if invoice.is_interstate:
                row = [
                    Paragraph(str(idx), cell_style),
                    Paragraph(prod_name, cell_style),
                    Paragraph(str(item.hsn_code), cell_style),
                    Paragraph(f"{float(item.quantity):.0f}", cell_style),
                    Paragraph(f"{float(item.unit_price):.2f}", cell_style),
                    Paragraph(f"{float(item.taxable_value):.2f}", cell_style),
                    Paragraph(f"{float(item.igst_rate):.1f}%", cell_style),
                    Paragraph(f"{float(item.igst_amount):.2f}", cell_style),
                    Paragraph(f"{float(item.total_item_amount):.2f}", cell_style),
                ]
            else:
                row = [
                    Paragraph(str(idx), cell_style),
                    Paragraph(prod_name, cell_style),
                    Paragraph(str(item.hsn_code), cell_style),
                    Paragraph(f"{float(item.quantity):.0f}", cell_style),
                    Paragraph(f"{float(item.unit_price):.2f}", cell_style),
                    Paragraph(f"{float(item.taxable_value):.2f}", cell_style),
                    Paragraph(f"{float(item.cgst_amount):.2f} (2.5%)", cell_style),
                    Paragraph(f"{float(item.sgst_amount):.2f} (2.5%)", cell_style),
                    Paragraph(f"{float(item.total_item_amount):.2f}", cell_style),
                ]
            table_rows.append(row)
            idx += 1

        items_table = Table(table_rows, colWidths=col_widths)
        items_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#e2e8f0")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#94a3b8")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        elements.append(items_table)
        elements.append(Spacer(1, 10))

        # 4. Summary & Payment Status
        summary_rows = [
            ["Taxable Subtotal:", f"₹ {float(invoice.taxable_amount):,.2f}"]
        ]
        if invoice.is_interstate:
            summary_rows.append([f"IGST ({float(invoice.igst_rate):.1f}%):", f"₹ {float(invoice.igst_amount):,.2f}"])
        else:
            summary_rows.append([f"CGST ({float(invoice.cgst_rate):.1f}%):", f"₹ {float(invoice.cgst_amount):,.2f}"])
            summary_rows.append([f"SGST ({float(invoice.sgst_rate):.1f}%):", f"₹ {float(invoice.sgst_amount):,.2f}"])
        summary_rows.append(["Invoice Grand Total:", f"₹ {float(invoice.total_amount):,.2f}"])
        summary_rows.append(["Amount Paid:", f"₹ {float(invoice.amount_paid):,.2f}"])
        summary_rows.append(["Balance Due:", f"₹ {float(invoice.balance_due):,.2f}"])

        sum_table_data = []
        for label, val in summary_rows:
            is_bold = "Total" in label or "Due" in label
            font_fn = bold_cell_style if is_bold else cell_style
            sum_table_data.append([
                Paragraph(f"<b>{label}</b>" if is_bold else label, font_fn),
                Paragraph(f"<b>{val}</b>" if is_bold else val, ParagraphStyle("Val", parent=font_fn, alignment=2))
            ])

        sum_table = Table(sum_table_data, colWidths=[140, 100])
        sum_table.setStyle(TableStyle([
            ('BACKGROUND', (0, -3), (-1, -3), colors.HexColor("#f1f5f9")),
            ('BOX', (0, 0), (-1, -1), 0.5, colors.HexColor("#cbd5e1")),
            ('INNERGRID', (0, 0), (-1, -1), 0.5, colors.HexColor("#e2e8f0")),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ]))

        footer_notes = f"""<b>Declaration:</b> We declare that this invoice shows the actual price of the goods described and that all particulars are true and correct.<br/>
<b>Bank Details:</b> State Bank of India, Thuvakudi Branch | <b>A/c:</b> 38890011223 | <b>IFSC:</b> SBIN0001234<br/><br/>
<b>Dispatch Status:</b> {invoice.dispatch_status.upper()} | <b>Payment Status:</b> {invoice.status.upper()}
"""
        combined_bottom = Table([
            [Paragraph(footer_notes, cell_style), sum_table]
        ], colWidths=[300, 240])
        combined_bottom.setStyle(TableStyle([
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]))
        elements.append(KeepTogether(combined_bottom))

        elements.append(Spacer(1, 25))
        sign_table = Table([
            [
                Paragraph("Customer Seal & Signature", ParagraphStyle("SignL", parent=cell_style, alignment=0)),
                Paragraph(f"For <b>{settings.COMPANY_NAME}</b><br/><br/><br/>Authorized Signatory", ParagraphStyle("SignR", parent=cell_style, alignment=2))
            ]
        ], colWidths=[270, 270])
        elements.append(sign_table)

        doc.build(elements)
        buffer.seek(0)
        return buffer.getvalue()

