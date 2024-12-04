import os
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template

from xhtml2pdf import pisa
import pdfkit
pdfkit.configuration(wkhtmltopdf='wkhtmltopdf/bin/wkhtmltopdf.exe')
import tempfile


def render_to_pdf(template_src, context_dict=None):
    if context_dict is None:
        context_dict = {}
    template = get_template(template_src)
    html = template.render(context_dict)
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        pdfkit.from_string(html, temp_file.name, options={'page-size': 'A4',
                                                          'margin-top': '3cm',
                                                          'margin-bottom': '2cm',
                                                          'margin-left': '3cm',
                                                          'margin-right': '2cm',
                                                          'minimum-font-size': 14})

        with open(temp_file.name, "rb") as pdf_file:
            result = pdf_file.read()

    return HttpResponse(result, content_type='application/pdf')