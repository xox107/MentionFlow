import json
import os
from fpdf import FPDF
from datetime import datetime

class PDFReport(FPDF):
    def header(self):
        self.set_font('Arial', 'B', 15)
        self.cell(0, 10, 'MentionFlow - Social Intelligence Report', 0, 1, 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font('Arial', 'I', 8)
        self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

def clean_text(text):
    """Removes characters that the standard PDF fonts cannot handle (Emojis, etc.)"""
    if not text: return "N/A"
    return text.encode('ascii', 'ignore').decode('ascii')

def generate_report():
    pdf = PDFReport()
    pdf.add_page()
    pdf.set_font("Arial", size=11)

    # Find all result files
    files = [f for f in os.listdir('.') if f.startswith('results_') and f.endswith('.json')]
    
    if not files:
        print("No result files found to generate report.")
        return

    for file in files:
        with open(file, 'r', encoding='utf-8') as f:
            try:
                posts = json.load(f)
                pdf.set_font("Arial", 'B', 12)
                pdf.cell(0, 10, f"Source File: {file}", 0, 1)
                pdf.set_font("Arial", size=10)

                for post in posts:
                    title = clean_text(post.get('title', 'No Title'))
                    link = post.get('link', 'No Link')
                    snippet = clean_text(post.get('snippet', 'No Snippet'))

                    pdf.multi_cell(0, 8, f"TITLE: {title}")
                    pdf.set_text_color(0, 0, 255)
                    pdf.cell(0, 0, f"LINK: {link}", ln=1, link=link)
                    pdf.set_text_color(0, 0, 0)
                    pdf.multi_cell(0, 8, f"SNIPPET: {snippet}")
                    pdf.ln(5)
                    pdf.cell(0, 0, '', 'T', 1) # Horizontal line
                    pdf.ln(5)

            except Exception as e:
                print(f"Error processing {file}: {e}")

    output_path = "MentionFlow_Full_Report.pdf"
    pdf.output(output_path)
    print(f"PDF Generated: {output_path}")

if __name__ == "__main__":
    generate_report()