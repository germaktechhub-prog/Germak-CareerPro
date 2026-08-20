import io
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

class PDFGenerator:
    @staticmethod
    def generate_pdf(doc_title, doc_type, content, template_style="modern"):
        """Generates a binary PDF buffer for CVs, Cover Letters, Application Letters, and LinkedIn summaries."""
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=letter,
            rightMargin=40,
            leftMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        
        # Color palettes based on template
        palette = {
            'modern': colors.HexColor('#1e40af'),      # Deep Blue
            'classic': colors.HexColor('#1f2937'),     # Charcoal
            'executive': colors.HexColor('#4c1d95'),   # Imperial Purple
            'minimal': colors.HexColor('#0f766e')      # Teal
        }
        primary_color = palette.get(template_style, palette['modern'])

        title_style = ParagraphStyle(
            'DocTitle',
            parent=styles['Heading1'],
            fontSize=22,
            leading=26,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            spaceAfter=6
        )
        
        subtitle_style = ParagraphStyle(
            'DocSubtitle',
            parent=styles['Normal'],
            fontSize=10,
            leading=14,
            textColor=colors.HexColor('#4b5563'),
            spaceAfter=12
        )

        heading_style = ParagraphStyle(
            'SectionHeading',
            parent=styles['Heading2'],
            fontSize=12,
            leading=16,
            textColor=primary_color,
            fontName='Helvetica-Bold',
            spaceBefore=10,
            spaceAfter=4
        )

        body_style = ParagraphStyle(
            'BodyText',
            parent=styles['Normal'],
            fontSize=9.5,
            leading=13.5,
            textColor=colors.HexColor('#1f2937'),
            spaceAfter=6
        )

        story = []

        # --- CV Formatting Engine ---
        if doc_type == 'cv':
            personal = content.get('personal', {})
            story.append(Paragraph(personal.get('fullName', doc_title).upper(), title_style))
            
            contact_line = f"{personal.get('email', '')} | {personal.get('phone', '')} | {personal.get('location', '')}"
            if personal.get('linkedin'):
                contact_line += f" | {personal.get('linkedin')}"
            story.append(Paragraph(contact_line, subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=primary_color, spaceAfter=10))

            # Summary
            if content.get('summary'):
                story.append(Paragraph("PROFESSIONAL SUMMARY", heading_style))
                story.append(Paragraph(content['summary'], body_style))

            # Experience
            if content.get('experience'):
                story.append(Paragraph("WORK EXPERIENCE", heading_style))
                for exp in content['experience']:
                    job_header = f"<b>{exp.get('jobTitle', '')}</b> — {exp.get('company', '')} ({exp.get('startDate', '')} - {exp.get('endDate', 'Present')})"
                    story.append(Paragraph(job_header, body_style))
                    if exp.get('responsibilities'):
                        story.append(Paragraph(exp['responsibilities'].replace('\n', '<br/>'), body_style))
                    story.append(Spacer(1, 4))

            # Education
            if content.get('education'):
                story.append(Paragraph("EDUCATION", heading_style))
                for edu in content['education']:
                    edu_line = f"<b>{edu.get('degree', '')}</b>, {edu.get('institution', '')} ({edu.get('endDate', '')})"
                    story.append(Paragraph(edu_line, body_style))

            # Skills
            if content.get('skills'):
                story.append(Paragraph("CORE SKILLS", heading_style))
                skills_str = ", ".join(content['skills']) if isinstance(content['skills'], list) else content['skills']
                story.append(Paragraph(skills_str, body_style))

        # --- Cover / Application Letter Formatting Engine ---
        else:
            story.append(Paragraph(content.get('fullName', doc_title), title_style))
            story.append(Paragraph(f"{content.get('email', '')} | {content.get('phone', '')}", subtitle_style))
            story.append(HRFlowable(width="100%", thickness=1, color=primary_color, spaceAfter=12))

            if content.get('company'):
                story.append(Paragraph(f"<b>To:</b> {content.get('hiringManager', 'Hiring Manager')}", body_style))
                story.append(Paragraph(f"<b>Company:</b> {content.get('company', '')}", body_style))
                story.append(Spacer(1, 8))

            letter_body = content.get('body', content.get('letterText', ''))
            for paragraph in letter_body.split('\n\n'):
                if paragraph.strip():
                    story.append(Paragraph(paragraph.strip().replace('\n', '<br/>'), body_style))
                    story.append(Spacer(1, 6))

        doc.build(story)
        buffer.seek(0)
        return buffer