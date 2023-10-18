from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse

def generate_certificate_pdf(request, user_name, course_name, issued_date):
    # Create a BytesIO buffer to receive the PDF data.
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO buffer as its "file."
    p = canvas.Canvas(buffer)

    # PDF generation code here.
    # You can use p.drawString, p.drawImage, and other methods to customize the certificate.

    # For example:
    p.setFont("Helvetica", 12)
    p.drawString(100, 700, f"Certificate of Completion")
    p.drawString(100, 670, f"This is to certify that")
    p.drawString(100, 650, f"{user_name}")
    p.drawString(100, 630, f"has successfully completed the course")
    p.drawString(100, 610, f"{course_name}")
    p.drawString(100, 590, f"Issued on: {issued_date}")

    # Save the PDF to the BytesIO buffer.
    p.showPage()
    p.save()

    # Rewind the buffer and create a response with the PDF data.
    buffer.seek(0)
    response = HttpResponse(buffer, content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{user_name}_{course_name}_certificate.pdf"'

    return response

