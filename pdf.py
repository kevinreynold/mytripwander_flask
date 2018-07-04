from reportlab.pdfgen import canvas

from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm, cm
from reportlab.lib.enums import TA_JUSTIFY,TA_LEFT,TA_CENTER,TA_RIGHT

class TripPDF():
    def __init__(self, filename="test_report_lab.pdf", print_data=None, total_days_trip=None, dest_title=None, total_budget=None, first_city=None, start_date=None, offline=False):
        pdfmetrics.registerFont(TTFont('Arial', 'font/arial.ttf'))
        pdfmetrics.registerFont(TTFont('Cyberbit', 'font/cyberbit.ttf'))

        self.print_data = print_data
        self.total_days_trip = total_days_trip
        self.dest_title = dest_title
        self.total_budget = total_budget
        self.first_city = first_city
        self.start_date = start_date

        if offline:
            self.filename = "C:\\xampp\\htdocs\\pdf_result\\" + filename
        else:
            self.filename = r"/var/www/html/pdf/" + filename

        self.doc = SimpleDocTemplate(self.filename, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.25*cm, topMargin=2*cm, bottomMargin=2*cm)
        self.style = getSampleStyleSheet()
        self.style.wordWrap = 'CJK'

        # doc.pagesize = landscape(A4)

        self.elements = []

        self.data = [
            ["Name", "Category", "Time"],
            ["Hong Kong International Airport (HKG)", "Airport", "11:05 - 12:05"],
            ["Imperial Hotel Hong Kong", "Hotel", "12:45 - 13:45"],
            ["Julio 훌리오 강남역본점", "Food", "14:05 - 14:50"],
            ["Soho, Hong Kong", "Attraction", "15:25 - 16:30"],
            ["Huashan 1914 Creative Park 華山1914文化創意產業園區", "Attraction", "17:15 - 18:30"]
        ]

    def addPageNumber(self, canvas, doc):
        page_num = canvas.getPageNumber()
        text = "%s" % page_num

        canvas.saveState()
        canvas.setFont('Arial',11)
        canvas.drawCentredString(doc.pagesize[0]/2.0, 1.25*cm, text)
        canvas.restoreState()

    def setHeader(self, canvas, doc):
        canvas.saveState()

        canvas.setFont('Arial',16)
        canvas.drawString(1.5*cm, 28*cm, 'Trip Wander - Itinerary')

        canvas.setFont('Arial',14.5)
        canvas.drawCentredString((doc.pagesize[0]/2.0)-(0.25*cm), 26.4*cm, str(self.total_days_trip) + ' Days Trip')
        canvas.drawCentredString((doc.pagesize[0]/2.0)-(0.25*cm), 25.6*cm, self.dest_title)
        canvas.drawCentredString((doc.pagesize[0]/2.0)-(0.25*cm), 24.8*cm, self.start_date)

        canvas.setFont('Arial',10)
        canvas.drawString(1.5*cm, 24.65*cm, 'From:')
        canvas.drawString(1.5*cm, 24.2*cm, self.first_city)
        canvas.drawRightString(doc.pagesize[0]-(1.5*cm), 24.65*cm, 'Total Budget:')
        canvas.drawRightString(doc.pagesize[0]-(1.5*cm), 24.2*cm, self.total_budget)

        canvas.setFillColor(colors.black)
        canvas.rect(1.5*cm, 27.69*cm, 18*cm, 0.01*cm, fill=1)
        canvas.rect(1.5*cm, 27.6*cm, 18*cm, 0.01*cm, fill=1)
        canvas.rect(1.5*cm, 23.89*cm, 18*cm, 0.01*cm, fill=1)
        canvas.rect(1.5*cm, 23.8*cm, 18*cm, 0.01*cm, fill=1)
        canvas.restoreState()

        self.addPageNumber(canvas, doc)

    def setBody(self):
        self.elements.append(Spacer(1,3*cm))
        for country_data in self.print_data:
            self.setCountrySchedule(country_data)

    def makeRouteData(self, route_data):
        result = []
        result.append(["Name", "Category", "Time"])
        for place_data in route_data:
            name = place_data['place']['name']
            type = ''
            if place_data['place']['category_id'] == 1:
                type = 'Airport'
            elif place_data['place']['category_id'] == 2:
                type = 'Attraction'
            elif place_data['place']['category_id'] == 3:
                type = 'Food'
            elif place_data['place']['category_id'] == 4:
                type = 'Hotel'
            time = place_data['string_format'].split(' | ')[1]
            result.append([name, type, time])

        return result

    def setCountrySchedule(self, country_data):
        PS_Country = ParagraphStyle(name='custom1', fontName='Arial', fontSize=18, alignment=TA_CENTER)
        PS_City = ParagraphStyle(name='custom2', fontName='Arial', fontSize=16)
        PS_Day = ParagraphStyle(name='custom3', fontName='Arial', fontSize=12)
        PS_Name = ParagraphStyle(name='custom4', fontName='Cyberbit', fontSize=11.5, leading=15)
        PS_Other = ParagraphStyle(name='custom5', fontName='Cyberbit', fontSize=11.5, leading=15, alignment=TA_CENTER)

        self.elements.append(Spacer(0,1.25*cm))
        self.elements.append(Paragraph(country_data['country_name'], PS_Country))

        for city_data in country_data['cities']:
            self.elements.append(Spacer(0,0.65*cm))
            self.elements.append(Paragraph(city_data['city'], PS_City))
            self.elements.append(Spacer(0,0.5*cm))
            for per_day_data in city_data['list_dest']:
                day_title = 'Day %s - %s' % (str(per_day_data['day']), per_day_data['date'])
                self.elements.append(Paragraph(day_title, PS_Day))
                self.elements.append(Spacer(0,0.3*cm))

                # TABEL
                data = self.makeRouteData(per_day_data['route_data'])
                data_len = len(data)

                table_style = TableStyle()
                table_style.add('BOX', (0,0), (-1,-1), 1, colors.Color(68/255, 114/255, 196/255))

                for each in range(data_len):
                    if each % 2 == 0:
                        bg_color = colors.Color(217/255, 226/255, 243/255)
                    else:
                        bg_color = colors.white
                    table_style.add('BACKGROUND', (0,each), (-1,each), bg_color)

                table_style.add('BACKGROUND', (0,0), (-1,0), colors.Color(68/255, 114/255, 196/255))

                table_data = [[Paragraph(cell, PS_Name) if cell_index == 0 else Paragraph(cell, PS_Other) for cell_index, cell in enumerate(row)] for row_index, row in enumerate(data)]
                t = Table(table_data, colWidths=[12.5 * cm, 2.5 * cm, 3 * cm])
                t.setStyle(table_style)
                self.elements.append(t)
                self.elements.append(Spacer(0,0.3*cm))

    def run(self):
        self.setBody()
        self.doc.build(self.elements, onFirstPage=self.setHeader, onLaterPages=self.addPageNumber)

# trip_pdf = TripPDF()
# trip_pdf.run()
