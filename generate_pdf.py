import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, KeepTogether
)

def create_jarvis_notes_pdf(filename="Jarvis_AI_Assistant_Notes.pdf"):
    pdf_path = os.path.abspath(filename)
    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        rightMargin=36,
        leftMargin=36,
        topMargin=36,
        bottomMargin=36
    )

    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor('#004D5E'),
        alignment=0,
        spaceAfter=6
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=13,
        leading=16,
        textColor=colors.HexColor('#7B61FF'),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=18,
        textColor=colors.HexColor('#0B0F17'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2_Custom',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=15,
        textColor=colors.HexColor('#006070'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body_Custom',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=10,
        leading=14,
        textColor=colors.HexColor('#1E293B'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet_Custom',
        parent=body_style,
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=4
    )

    code_style = ParagraphStyle(
        'Code_Custom',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#0F172A'),
        backColor=colors.HexColor('#F1F5F9'),
        borderColor=colors.HexColor('#CBD5E1'),
        borderWidth=0.5,
        borderPadding=6,
        spaceBefore=4,
        spaceAfter=6
    )

    story = []

    # Title & Header Banner
    story.append(Paragraph("JARVIS AI ASSISTANT — COMPLETE PROJECT NOTES", title_style))
    story.append(Paragraph("Project Architecture, Features, Code Workflow & Bug Fix Explanations", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=2, color=colors.HexColor('#00D4FF'), spaceAfter=15))

    # 1. Introduction
    story.append(Paragraph("1. System Overview (Kya Hai Yeh Project?)", h1_style))
    intro_p = (
        "<b>Jarvis AI Assistant</b> ek advanced voice and text controlled AI system hai jo user ke PC par commands execute "
        "karta hai. Isme <b>Dual Interface</b> milta hai: Ek desktop CustomTkinter Cyberpunk window aur ek modern HTML5 Holographic Web HUD server. "
        "Yeh Groq Llama 3.3 70B Model, Whisper Speech Recognition, aur Edge-TTS engine ka upayog karke real-time Hinglish conversation karta hai."
    )
    story.append(Paragraph(intro_p, body_style))
    story.append(Spacer(1, 8))

    # Key Features Table
    features_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Technology Used</b>", body_style), Paragraph("<b>Function / Use Case</b>", body_style)],
        [Paragraph("<b>LLM Brain</b>", body_style), Paragraph("Groq (Llama-3.3-70b)", body_style), Paragraph("Natural language understanding, Hinglish replies, JSON action generation.", body_style)],
        [Paragraph("<b>Speech-To-Text (STT)</b>", body_style), Paragraph("Groq Whisper v3 / Google STT", body_style), Paragraph("Voice audio ko text me convert karta hai dynamic energy VAD ke sath.", body_style)],
        [Paragraph("<b>Text-To-Speech (TTS)</b>", body_style), Paragraph("Edge-TTS / pyttsx3", body_style), Paragraph("Natural human-like voice synthesis (GuyNeural voice) offline fallback k sath.", body_style)],
        [Paragraph("<b>Desktop GUI</b>", body_style), Paragraph("CustomTkinter & Tkinter", body_style), Paragraph("Cyberpunk HUD dashboard, real-time waveform visualizer, system metrics.", body_style)],
        [Paragraph("<b>Web HUD Server</b>", body_style), Paragraph("Python http.server + Web Speech", body_style), Paragraph("Browser command center (http://localhost:8000) with 3D canvas orb animation.", body_style)],
        [Paragraph("<b>System Control</b>", body_style), Paragraph("PyAutoGUI, OS, Subprocess, Pycaw", body_style), Paragraph("Volume control, app opening, screenshots, system lock/shutdown.", body_style)]
    ]

    t_feat = Table(features_data, colWidths=[120, 160, 260])
    t_feat.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#E2E8F0')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_feat)
    story.append(Spacer(1, 14))

    # 2. Architecture & File Structure
    story.append(Paragraph("2. Codebase Structure (Files and Modules)", h1_style))
    structure_text = (
        "Project ki directory structure aur har main file ka role niche diya gaya hai:<br/>"
        "• <b>main.py</b> — Main entry point. Desktop GUI aur Web Server ko start karta hai, continuous mic listening loop hold karta hai.<br/>"
        "• <b>web_server.py</b> — Lightweight HTTP server jo <code>/api/status</code>, <code>/api/metrics</code>, aur <code>/api/command</code> endpoints provide karta hai.<br/>"
        "• <b>config.py</b> — Environment variables (.env file loading), API Keys, Model configurations, Contacts dictionary aur Default Prompts handle karta hai.<br/>"
        "• <b>core/llm_brain.py</b> — Groq Llama 3.3 integration, conversation memory (history), aur Hinglish System Prompt ke sath JSON <code>&lt;ACTION&gt;</code> parser.<br/>"
        "• <b>core/stt_engine.py</b> — Microphone calibration, background noise cancellation, Whisper Large v3 aur Google STT speech recognition.<br/>"
        "• <b>core/tts_engine.py</b> — Thread-safe Microsoft Edge-TTS voice generation + Pygame audio playback + pyttsx3 offline fallback.<br/>"
        "• <b>core/wake_word.py</b> — Hands-free wake word detector ('Hey Jarvis', 'Aura') jo continuous background monitoring karta hai.<br/>"
        "• <b>automation/system_control.py</b> — Windows automation routines (App launcher, volume control via Pycaw, screenshot capture, PC lock/shutdown).<br/>"
        "• <b>gui/app_window.py</b> — CustomTkinter dark cyberpunk GUI containing sidebar metrics, audio spectrum canvas, and quick action buttons.<br/>"
        "• <b>web/index.html</b> — Interactive web interface with 60 FPS HTML5 canvas quantum orb visualizer."
    )
    story.append(Paragraph(structure_text, body_style))
    story.append(Spacer(1, 14))

    # 3. How Workflow Works
    story.append(Paragraph("3. Executive Workflow (Kaise Kaam Karta Hai?)", h1_style))
    flow_steps = [
        "<b>Step 1: Input Trigger</b> — User voice microhpone se bolta hai ya GUI / Web HUD me text entry dwara command bhejta hai.",
        "<b>Step 2: Speech Recognition</b> — <code>SpeechToTextEngine</code> audio input record karke Groq Whisper Large v3 model ko bhejta hai jo high accuracy text me convert karta hai.",
        "<b>Step 3: Intent & Action Analysis</b> — Text <code>llm_brain.py</code> ko pass hota hai. LLM user query ke aadhar par response frame karta hai. Agar system action required hai (jaise 'open youtube' ya 'mute volume'), toh LLM JSON tag append karta hai:<br/><code>Mummy ko message bhej raha hu. &lt;ACTION&gt;{\"type\": \"whatsapp\", \"contact\": \"mummy\", \"message\": \"aa raha hu\"}&lt;/ACTION&gt;</code>",
        "<b>Step 4: Execution & Feedback</b> — System automation module JSON payload read karke task run karta hai aur <code>tts_engine.py</code> natural voice se bolkar user ko confirmation deta hai."
    ]
    for step in flow_steps:
        story.append(Paragraph(f"• {step}", bullet_style))
    story.append(Spacer(1, 14))

    # 4. Recent Errors & Debugging Summary
    story.append(Paragraph("4. Key Errors Identified and Fixed (Bug Fixes Summary)", h1_style))
    
    fixes_data = [
        [Paragraph("<b>Bug / Error Issue</b>", body_style), Paragraph("<b>Root Cause</b>", body_style), Paragraph("<b>Applied Fix Solution</b>", body_style)],
        [
            Paragraph("<b>Wake Word Context Error</b><br/><i>AssertionError: Audio source inside context manager</i>", body_style),
            Paragraph("Microphone context outer loop me lock hone ki wajah se double-entry exception aa rahi thi.", body_style),
            Paragraph("<code>wake_word.py</code> me microphone context lifecycle ko retry loop ke andar safely isolate kiya.", body_style)
        ],
        [
            Paragraph("<b>Corrupt MP3 Playback</b><br/><i>music_drmp3: corrupt mp3 file (bad tags)</i>", body_style),
            Paragraph("Edge-TTS connection lag ki wajah se incomplete/0-byte MP3 save kar raha tha.", body_style),
            Paragraph("<code>tts_engine.py</code> me <code>os.path.getsize(tmp_path) &gt; 100</code> check add karke automatic offline fallback lagaya.", body_style)
        ],
        [
            Paragraph("<b>Missing Contact Dictionary</b><br/><i>Contact dictionary mein nahi mila</i>", body_style),
            Paragraph("<code>config.py</code> me <code>CONTACTS</code> mapping dict missing tha.", body_style),
            Paragraph("<code>config.py</code> me default <code>CONTACTS</code> map insert karke contact lookup error solve kiya.", body_style)
        ],
        [
            Paragraph("<b>Web HUD Action Handling</b><br/><i>Commands not executing from Web UI</i>", body_style),
            Paragraph("<code>web_server.py</code> LLM se aaye JSON <code>&lt;ACTION&gt;</code> tag ko extract karke execute nahi kar raha tha.", body_style),
            Paragraph("<code>web_server.py</code> ke <code>/api/command</code> handler me action parser & executor introduce kiya.", body_style)
        ]
    ]

    t_fixes = Table(fixes_data, colWidths=[150, 195, 195])
    t_fixes.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#F8FAFC')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(t_fixes)
    story.append(Spacer(1, 14))

    # 5. Quick Command Reference & Setup
    story.append(Paragraph("5. User Setup & Execution Guide", h1_style))
    setup_code = (
        "# 1. Environment file (.env) setup:<br/>"
        "GROQ_API_KEY=gsk_your_groq_api_key_here<br/><br/>"
        "# 2. Install Dependencies:<br/>"
        "pip install -r requirements.txt<br/><br/>"
        "# 3. Run Jarvis Desktop Assistant & Web HUD:<br/>"
        "python main.py<br/><br/>"
        "# 4. Access Web Interface:<br/>"
        "Open browser at http://localhost:8000"
    )
    story.append(Paragraph(setup_code, code_style))

    doc.build(story)
    print(f"PDF Notes generated successfully: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_jarvis_notes_pdf()
