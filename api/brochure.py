import os
import urllib.request
import json
import io
from http.server import BaseHTTPRequestHandler
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

def load_env():
    env = dict(os.environ) # Start with Vercel's environment variables
    # Check parent directory for a local .env file (useful for local development/testing)
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(parent_dir, '.env')
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    k, v = line.split('=', 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
    return env

def fetch_db_metrics():
    env = load_env()
    supabase_url = env.get('SUPABASE_URL')
    supabase_key = env.get('SUPABASE_ANON_KEY')
    
    metrics = {
        'stats_projects': '50+',
        'stats_clients': '30+',
        'stats_members': '15+',
        'stats_satisfaction': '99%'
    }
    
    if not supabase_url or not supabase_key:
        return metrics
        
    try:
        url = f"{supabase_url.rstrip('/')}/rest/v1/website_settings?select=*"
        req = urllib.request.Request(url)
        req.add_header('apikey', supabase_key)
        req.add_header('Authorization', f"Bearer {supabase_key}")
        
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            for item in data:
                key = item.get('key')
                val = item.get('value')
                if key in metrics:
                    metrics[key] = str(val)
    except Exception:
        pass
        
    return metrics

def draw_cover_background(canvas, doc):
    canvas.saveState()
    # Deep midnight solid background
    canvas.setFillColor(colors.HexColor('#090D16'))
    canvas.rect(0, 0, 8.5*inch, 11*inch, fill=1, stroke=0)
    
    # Elegant Left Accent Vertical Bar
    canvas.setFillColor(colors.HexColor('#411BFF'))
    canvas.rect(36, 0, 6, 11*inch, fill=1, stroke=0)
    
    # Modern glowing brand accent (Top Left)
    canvas.setFillColor(colors.HexColor('#00F0FF1A')) # Very subtle cyan glow
    canvas.circle(0, 11*inch, 3.5*inch, fill=1, stroke=0)
    
    canvas.restoreState()

def draw_later_background(canvas, doc):
    canvas.saveState()
    # Clean minimalist white background
    canvas.setFillColor(colors.white)
    canvas.rect(0, 0, 8.5*inch, 11*inch, fill=1, stroke=0)
    
    # Left Margin Accent line (extends down the page vertically, very modern)
    canvas.setFillColor(colors.HexColor('#F1F5F9'))
    canvas.rect(36, 0, 1.5, 11*inch, fill=1, stroke=0)
    
    # Running Header (No line divider, just elegant text)
    canvas.setFont("Helvetica-Bold", 7.5)
    canvas.setFillColor(colors.HexColor('#94A3B8'))
    canvas.drawString(54, 11*inch - 40, "LIXTEN TECHNOLOGIES")
    canvas.drawRightString(8.5*inch - 54, 11*inch - 40, "CAPABILITIES & PROFILE")
    
    # Running Footer (Clean page number)
    canvas.setFont("Helvetica-Bold", 9)
    canvas.setFillColor(colors.HexColor('#475569'))
    canvas.drawString(54, 40, "www.lixten.in")
    canvas.drawRightString(8.5*inch - 54, 40, str(doc.page))
    
    canvas.restoreState()

def build_pdf_buffer(buffer):
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=54,
        leftMargin=54,
        topMargin=75,
        bottomMargin=75
    )
    
    styles = getSampleStyleSheet()
    
    # Modern Editorial Colors
    primary_color = colors.HexColor('#411BFF')
    secondary_color = colors.HexColor('#5C3AFF')
    dark_slate = colors.HexColor('#0F172A')
    white = colors.white
    
    # Custom Typography Styles
    cover_title_style = ParagraphStyle(
        'CoverTitle',
        fontName='Helvetica-Bold',
        fontSize=52,
        leading=58,
        textColor=white,
        spaceAfter=4
    )
    cover_subtitle_style = ParagraphStyle(
        'CoverSubtitle',
        fontName='Helvetica',
        fontSize=18,
        leading=24,
        textColor=colors.HexColor('#00F0FF'),
        spaceAfter=40
    )
    cover_desc_style = ParagraphStyle(
        'CoverDesc',
        fontName='Helvetica',
        fontSize=10.5,
        leading=17,
        textColor=colors.HexColor('#94A3B8'),
        spaceAfter=60
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=26,
        textColor=dark_slate,
        spaceBefore=10,
        spaceAfter=15,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyText',
        fontName='Helvetica',
        fontSize=10,
        leading=16,
        textColor=colors.HexColor('#475569'),
        spaceAfter=12
    )
    
    bullet_style = ParagraphStyle(
        'BulletText',
        parent=body_style,
        leftIndent=12,
        firstLineIndent=-8,
        spaceAfter=6
    )
    
    card_title_style = ParagraphStyle(
        'CardTitle',
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=dark_slate,
        spaceAfter=6,
        keepWithNext=True
    )
    
    card_desc_style = ParagraphStyle(
        'CardDesc',
        fontName='Helvetica',
        fontSize=9,
        leading=14,
        textColor=colors.HexColor('#475569')
    )
    
    metric_num_style = ParagraphStyle(
        'MetricNum',
        fontName='Helvetica-Bold',
        fontSize=36,
        leading=42,
        textColor=primary_color,
        alignment=1
    )
    
    metric_label_style = ParagraphStyle(
        'MetricLabel',
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11,
        textColor=colors.HexColor('#94A3B8'),
        alignment=1
    )

    story = []
    
    # ------------------ PAGE 1: COVER PAGE ------------------
    story.append(Spacer(1, 160))
    story.append(Paragraph("LIXTEN", cover_title_style))
    story.append(Paragraph("TECHNOLOGIES", cover_subtitle_style))
    
    # Accent indicator bar in cover flow
    story.append(Table([['']], colWidths=[60], rowHeights=[3], style=[('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#00F0FF'))]))
    story.append(Spacer(1, 20))
    
    story.append(Paragraph(
        "A premium enterprise software engineering firm specializing in high-performance digital ecosystems. We architect security-hardened applications, scalable cloud infrastructure, and intelligent automation systems designed to accelerate business operations and define industry leaders.",
        cover_desc_style
    ))
    
    story.append(Spacer(1, 40))
    
    # Cover bottom contacts
    info_data = [
        [
            Paragraph("<b>E-Mail</b><br/>lixtentechnologies@gmail.com", ParagraphStyle('C1', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#64748B'))),
            Paragraph("<b>Web Portal</b><br/>www.lixten.in", ParagraphStyle('C2', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#64748B'))),
            Paragraph("<b>Location</b><br/>Chennai, TN, India", ParagraphStyle('C3', fontName='Helvetica', fontSize=8.5, leading=12, textColor=colors.HexColor('#64748B'))),
        ]
    ]
    info_table = Table(info_data, colWidths=[200, 150, 150])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(info_table)
    
    story.append(PageBreak())
    
    # ------------------ PAGE 2: CORPORATE PROFILE & PHILOSOPHY ------------------
    story.append(Paragraph("01 / Corporate Profile & Core Philosophy", section_heading))
    story.append(Paragraph(
        "<b>Lixten Technologies</b> is a premier technology partner specializing in custom enterprise engineering. We operate at the intersection of business strategy and cutting-edge software architecture, helping global brands, scaleups, and visionary founders eliminate technical debt, secure critical data assets, and achieve structural efficiency.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Vision & Mission Cards
    mv_data = [
        [
            Paragraph("THE VISION", ParagraphStyle('VTitle', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=primary_color)),
            Paragraph("THE MISSION", ParagraphStyle('MTitle', fontName='Helvetica-Bold', fontSize=10, leading=14, textColor=secondary_color))
        ],
        [
            Paragraph("To architect the foundational digital systems for the world's most innovative enterprises, ensuring seamless reliability, bulletproof security, and unmatched operational scale.", ParagraphStyle('VBody', fontName='Helvetica', fontSize=9.5, leading=14.5, textColor=colors.HexColor('#475569'))),
            Paragraph("To engineer custom, high-performance software platforms that protect corporate interests, automate complex workflows, and deliver clear, measurable customer ROI.", ParagraphStyle('MBody', fontName='Helvetica', fontSize=9.5, leading=14.5, textColor=colors.HexColor('#475569')))
        ]
    ]
    mv_table = Table(mv_data, colWidths=[240, 240])
    mv_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 12),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#F1F5F9')),
        ('LINELEFT', (0,0), (0,-1), 3, primary_color),
        ('LINELEFT', (1,0), (1,-1), 3, secondary_color),
    ]))
    story.append(mv_table)
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("Core Engineering Values", ParagraphStyle('SubH', fontName='Helvetica-Bold', fontSize=12, textColor=dark_slate, spaceBefore=8, spaceAfter=8)))
    story.append(Paragraph("&bull; <b>Zero-Trust Cybersecurity:</b> Implementing PostgreSQL Row-Level Security (RLS), advanced encryption standards (AES-256), secure CSP headers, and rigid API authentication to isolate data and defend against exploits.", bullet_style))
    story.append(Paragraph("&bull; <b>Blazing Fast UI/UX Performance:</b> Leveraging modern web paradigms (SSR, static optimization, asset virtualization) to deliver lightning-fast response times (LCP &lt; 1.2s, INP &lt; 50ms) with zero layout shifts.", bullet_style))
    story.append(Paragraph("&bull; <b>Scalable Data Architectures:</b> Designing distributed, redundant database systems with optimized indexing, sharding, and connection pooling to support millions of concurrent read/write queries.", bullet_style))
    story.append(Paragraph("&bull; <b>Automated CI/CD DevOps:</b> Deploying containerized architectures using Docker and Kubernetes with automated integration pipelines on AWS, Azure, and Vercel for zero-downtime launches.", bullet_style))
    
    story.append(Spacer(1, 10))
    story.append(Paragraph(
        "By focusing on native code execution, API security, and reduced package dependencies, we safeguard your digital assets against modern cyber threats while maintaining absolute design flexibility.",
        body_style
    ))
    
    story.append(PageBreak())
    
    # ------------------ PAGE 3: SERVICES GRID ------------------
    story.append(Paragraph("02 / Engineering Services & Core Capabilities", section_heading))
    story.append(Paragraph(
        "Our engineers specialize in developing systems from initial database schema design to containerized production deployment, verifying every module against security and performance checklists.",
        body_style
    ))
    story.append(Spacer(1, 10))
    
    # Minimalist Card with top-accent border
    def make_service_card(title, desc, stack):
        card_data = [
            [Paragraph(title, card_title_style)],
            [Paragraph(desc, card_desc_style)],
            [Spacer(1, 8)],
            [Paragraph(f"<b>Stack:</b> {stack}", ParagraphStyle('StackText', fontName='Helvetica-Bold', fontSize=7.5, leading=10, textColor=colors.HexColor('#94A3B8')))]
        ]
        t = Table(card_data, colWidths=[226])
        t.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
            ('PADDING', (0,0), (-1,-1), 16),
            ('TOPPADDING', (0,0), (-1,-1), 14),
            ('BOTTOMPADDING', (0,0), (-1,-1), 14),
            ('LINEABOVE', (0,0), (-1,0), 3, primary_color), # Modern top line accent
            ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ]))
        return t

    grid_data = [
        [
            make_service_card("Enterprise Web Development", "Highly optimized, fully responsive web systems. We focus on server-side rendering, bundle size reduction, and asset lazy-loading to ensure maximum page speeds and search rankings.", "React, Next.js, TypeScript, TailwindCSS, Node.js"),
            make_service_card("Custom Software & Core APIs", "Scalable server architectures and microservices. We build secure RESTful/GraphQL schemas, custom automation tools, background workers, and seamless external systems integration.", "Go, Python, FastAPI, Express.js, PostgreSQL, Redis")
        ],
        [
            make_service_card("Cybersecurity & Compliance Auditing", "Penetration testing, vulnerability scanning, and security audits. We implement PostgreSQL Row-Level Security policies, API rate-limiting, and strict identity access management.", "OWASP Top 10, Kali Linux, IAM, Postgres RLS, OAuth2"),
            make_service_card("DevOps, Cloud Scaling & Serverless", "Deployment of resilient cloud infrastructures. We migrate monolithic applications to AWS or Azure with auto-scaling groups, database replication, and blue-green deploy pipelines.", "Docker, Kubernetes, AWS, Terraform, GitHub Actions")
        ]
    ]
    
    grid_table = Table(grid_data, colWidths=[246, 246])
    grid_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 16),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('PADDING', (0,0), (-1,-1), 0),
    ]))
    story.append(grid_table)
    
    story.append(PageBreak())
    
    # ------------------ PAGE 4: ENGINEERING LIFECYCLE & METRICS ------------------
    story.append(Paragraph("03 / Engineering Lifecycle & Operational Metrics", section_heading))
    story.append(Paragraph(
        "Every project follows our structured delivery lifecycle to guarantee secure, high-performance, and reliable deployments.",
        body_style
    ))
    story.append(Spacer(1, 5))
    
    lifecycle_data = [
        [
            Paragraph("<b>1 / Scoping & Architecture</b><br/>Wireframing, database schema mapping, system architecture planning, and milestone agreements.", card_desc_style),
            Paragraph("<b>2 / Agile Dev Sprints</b><br/>Iterative development cycles with continuous delivery, automated linting, and weekly client reviews.", card_desc_style),
            Paragraph("<b>3 / Security & QA Audits</b><br/>Comprehensive penetration testing, load testing, static analysis, and row-level data access rules verification.", card_desc_style),
            Paragraph("<b>4 / Launch & Telemetry</b><br/>Zero-downtime production deployment, analytics integration, and active performance logging.", card_desc_style)
        ]
    ]
    lifecycle_table = Table(lifecycle_data, colWidths=[117, 117, 117, 117])
    lifecycle_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#F8FAFC')),
        ('PADDING', (0,0), (-1,-1), 10),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOX', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINEBELOW', (0,0), (-1,-1), 2.5, secondary_color),
    ]))
    story.append(lifecycle_table)
    story.append(Spacer(1, 20))
    
    # Live stats fetch
    metrics = fetch_db_metrics()
    
    metrics_data = [
        [
            Paragraph(metrics.get('stats_projects', '50+'), metric_num_style),
            Paragraph(metrics.get('stats_clients', '30+'), metric_num_style),
            Paragraph(metrics.get('stats_members', '15+'), metric_num_style),
            Paragraph(metrics.get('stats_satisfaction', '99%'), metric_num_style)
        ],
        [
            Paragraph("Projects Completed", metric_label_style),
            Paragraph("Active Clients", metric_label_style),
            Paragraph("Core Engineers", metric_label_style),
            Paragraph("Client Satisfaction", metric_label_style)
        ]
    ]
    metrics_table = Table(metrics_data, colWidths=[126, 126, 126, 126])
    metrics_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('PADDING', (0,0), (-1,-1), 8),
        ('LINELEFT', (1,0), (1,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINELEFT', (2,0), (2,-1), 0.5, colors.HexColor('#E2E8F0')),
        ('LINELEFT', (3,0), (3,-1), 0.5, colors.HexColor('#E2E8F0')),
    ]))
    story.append(metrics_table)
    
    story.append(Spacer(1, 20))
    
    # Modern Contact Card
    contact_title_style = ParagraphStyle(
        'ContactTitle',
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=white
    )
    contact_desc_style = ParagraphStyle(
        'ContactDesc',
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        textColor=colors.HexColor('#CBD5E1')
    )
    
    contact_data = [
        [Paragraph("Start Your Engineering Project", contact_title_style)],
        [Spacer(1, 4)],
        [Paragraph("Partner with Lixten Technologies to transform your business operations. Our Chennai-based engineering hub is ready to conduct a technical evaluation, perform a security audit, or architect a custom software solution tailored to your scale.", contact_desc_style)],
        [Spacer(1, 10)],
        [
            Table([
                [
                    Paragraph("<b>Email Support</b><br/>lixtentechnologies@gmail.com", ParagraphStyle('CD1', fontName='Helvetica', fontSize=8.5, leading=12, textColor=white)),
                    Paragraph("<b>Web Portal</b><br/>www.lixten.in", ParagraphStyle('CD2', fontName='Helvetica', fontSize=8.5, leading=12, textColor=white)),
                    Paragraph("<b>Office</b><br/>Chennai, TN, India", ParagraphStyle('CD3', fontName='Helvetica', fontSize=8.5, leading=12, textColor=white))
                ]
            ], colWidths=[180, 140, 120], style=[
                ('PADDING', (0,0), (-1,-1), 0),
                ('VALIGN', (0,0), (-1,-1), 'TOP'),
            ])
        ]
    ]
    
    contact_box = Table(contact_data, colWidths=[468])
    contact_box.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#090D16')),
        ('PADDING', (0,0), (-1,-1), 20),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('LINELEFT', (0,0), (0,-1), 4, colors.HexColor('#411BFF')),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#1E293B')),
    ]))
    
    story.append(contact_box)
    
    doc.build(story, onFirstPage=draw_cover_background, onLaterPages=draw_later_background)

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        pdf_buffer = io.BytesIO()
        try:
            build_pdf_buffer(pdf_buffer)
            pdf_data = pdf_buffer.getvalue()
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="brochure.pdf"')
            self.send_header('Content-Length', len(pdf_data))
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            self.wfile.write(pdf_data)
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(f"Server Error generating PDF: {str(e)}".encode('utf-8'))
        finally:
            pdf_buffer.close()
        return
