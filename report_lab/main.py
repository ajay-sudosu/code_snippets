from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, cm


pdf = canvas.Canvas('test_pdf.pdf', pagesize=A4)
pdf.drawString(0, 1, "0, 0")
pdf.drawString(0, 100, "0, 100")
pdf.drawString(0, 200, "0, 200")
pdf.drawString(0, 300, "0, 300")
pdf.drawString(0, 400, "0, 400")
pdf.drawString(0, 500, "0, 500")
pdf.drawString(0, 600, "0, 600")
pdf.drawString(0, 700, "0, 700")
pdf.drawString(0, 800, "0, 800")
pdf.drawString(0, 831, "0, 831")

pdf.drawString(100, 0, "100, 0")
pdf.drawString(200, 0, "200, 0")
pdf.drawString(300, 0, "300, 0")
pdf.drawString(400, 0, "400, 0")
pdf.drawString(500, 0, "500, 0")
pdf.drawString(563, 0, "563, 0")

pdf.showPage()
pdf.save()
