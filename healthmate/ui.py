"""HealthMate Streamlit interface."""
import json
import os
import importlib

import csv
from datetime import datetime

def save_user_log_to_csv():
    file_path = "data/user_health_logs.csv"
    os.makedirs("data", exist_ok=True)
    file_exists = os.path.isfile(file_path)
    
    profile = st.session_state.get("user_profile", {})
    conditions = st.session_state.get("diagnosed_conditions", [])
    latest_condition = conditions[-1] if conditions else {}
    symptoms = ", ".join(latest_condition.get("symptoms", []))
    disease = latest_condition.get("disease", "None")
    
    row = {
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Name": profile.get("name", "Unknown"),
        "Age": profile.get("age", ""),
        "Gender": profile.get("gender", ""),
        "Weight": profile.get("weight", ""),
        "Height": profile.get("height", ""),
        "Blood Group": profile.get("blood_group", ""),
        "Existing Conditions": ", ".join(profile.get("existing_conditions", [])),
        "Allergies": profile.get("allergies", ""),
        "Detected Symptoms": symptoms,
        "Diagnosis": disease
    }
    fieldnames = ["Timestamp", "Name", "Age", "Gender", "Weight", "Height", "Blood Group", "Existing Conditions", "Allergies", "Detected Symptoms", "Diagnosis"]
    try:
        with open(file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            if not file_exists:
                writer.writeheader()
            writer.writerow(row)
    except Exception:
        pass

import streamlit as st

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import pathlib
import json as _json

from .ai import get_ai_response, get_ai_diet_plan, extract_condition_from_chat
from .data import DISEASE_INFO, get_diet_plan, normalize_disease_name
from .nlp import extract_symptoms, match_disease
from .config import load_env

load_env()

st.set_page_config(
    page_title="HealthMate AI – Your Personal Health Assistant",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ────────────────────────────────────────────────────────────────────

def extract_text_from_pdf(dest):
    text = ''
    # First try pure Python PDF libraries
    for module_name in ['PyPDF2', 'pypdf']:
        try:
            pdfmod = importlib.import_module(module_name)
            reader_cls = None
            if hasattr(pdfmod, 'PdfReader'):
                reader_cls = pdfmod.PdfReader
            elif hasattr(pdfmod, 'PdfFileReader'):
                reader_cls = pdfmod.PdfFileReader
            if reader_cls:
                with open(dest, 'rb') as fh:
                    reader = reader_cls(fh)
                    pages = getattr(reader, 'pages', []) or []
                    for p in pages:
                        try:
                            extracted = p.extract_text()
                            if extracted:
                                text += extracted
                        except Exception:
                            pass
                if text.strip():
                    return text
        except ImportError:
            continue
        except Exception:
            pass

    # Try pdfplumber as a fallback
    try:
        pdfplumber = importlib.import_module('pdfplumber')
        with pdfplumber.open(dest) as pdf:
            for page in pdf.pages:
                try:
                    extracted = page.extract_text()
                    if extracted:
                        text += extracted
                except Exception:
                    pass
        if text.strip():
            return text
    except ImportError:
        pass
    except Exception:
        pass

    # Try pdfminer.high_level
    try:
        pdfminer = importlib.import_module('pdfminer.high_level')
        extracted = pdfminer.extract_text(str(dest))
        if extracted:
            return extracted
    except ImportError:
        pass
    except Exception:
        pass

    # Try OCR for scanned PDFs when possible
    try:
        pdf2image = importlib.import_module('pdf2image')
        PIL = importlib.import_module('PIL')
        pytesseract = importlib.import_module('pytesseract')
        images = pdf2image.convert_from_path(dest, dpi=200)
        for img in images:
            try:
                text += pytesseract.image_to_string(img)
            except Exception:
                pass
        if text.strip():
            return text
    except ImportError:
        pass
    except Exception:
        pass

    return text


def extract_text_from_image(dest):
    try:
        PIL = importlib.import_module('PIL')
        pytesseract = importlib.import_module('pytesseract')
        img = PIL.Image.open(dest)
        return pytesseract.image_to_string(img) or ''
    except Exception:
        return ''


def inject_global_styles():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/4.7.0/css/font-awesome.min.css');

    * { font-family: 'Inter', sans-serif; }

    /* ── THEME: Cool Slate Blue & Mint-Fresh Sea Breeze ── */
    :root {
        --blue:         #7AB2D3; /* Medium Sky Blue Primary */
        --blue-d:       #4A628A; /* Slate Blue Darker Action */
        --cyan:         #B9E5E8; /* Duck Egg Blue Secondary */
        --cyan-d:       #96C5C8; /* Darker Cyan */
        --sky:          #DFF2EB; /* Mint White Highlights */
        --sky-d:        #B5D6CA; /* Dark Mint Accent */
        --cream:        #DFF2EB; /* Soft Mint Cream Replacement */
        --bg-dark:      #0B111E; /* Midnight Slate Obsidian */
        --bg-mid:       #121A2A; /* Deep Navy-Slate Midground */
        --bg-card:      rgba(18, 26, 42, 0.85); /* Glassmorphic Sea Card */
        --border:       rgba(122, 178, 211, 0.22); /* Sky Blue Border */
        --border-glow:  rgba(122, 178, 211, 0.45);
        --text-muted:   #7E8F9F; /* Slate Cozy Muted Blue-Gray */
        --text-light:   #D1DCE5; /* Crisp Light Blue-Gray */
        --text-bright:  #F0F4F8; /* Icy Soft White */
    }

    /* Main Background */
    .stApp {
        background: radial-gradient(circle at 50% 50%, #121A2A 0%, #0B111E 100%);
        background-attachment: fixed;
    }

    /* Animated background glow */
    .stApp::before {
        content: '';
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background:
            radial-gradient(ellipse at 20% 20%, rgba(122, 178, 211, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 80%, rgba(185, 229, 232, 0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 50%, rgba(223, 242, 235, 0.04) 0%, transparent 60%);
        pointer-events: none; z-index: 0;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0B111E 0%, #121A2A 50%, #090D18 100%) !important;
        border-right: 1.5px solid rgba(122, 178, 211, 0.2) !important;
    }
    section[data-testid="stSidebar"] * { color: #D1DCE5 !important; }
    
    /* General Sidebar button fallback styling */
    section[data-testid="stSidebar"] .stButton button,
    section[data-testid="stSidebar"] button {
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8) !important;
        border: 1px solid rgba(122, 178, 211, 0.55) !important;
        border-radius: 12px !important;
        padding: 10px 14px !important;
        font-weight: 700 !important;
        box-shadow: 0 8px 24px rgba(122, 178, 211, 0.18) !important;
        transition: all 0.3s ease !important;
    }
    section[data-testid="stSidebar"] .stButton button:hover,
    section[data-testid="stSidebar"] button:hover {
        background: linear-gradient(135deg, #B9E5E8, #DFF2EB) !important;
        box-shadow: 0 10px 30px rgba(122, 178, 211, 0.3) !important;
    }
    
    /* Ensure solid black text color for all buttons in the sidebar and all their inner elements */
    .stSidebar [data-testid="stButton"] button,
    .stSidebar [data-testid="stButton"] button *,
    .stSidebar button,
    .stSidebar button *,
    [data-testid="stSidebar"] [data-testid="stButton"] button,
    [data-testid="stSidebar"] [data-testid="stButton"] button *,
    [data-testid="stSidebar"] button,
    [data-testid="stSidebar"] button *,
    .stSidebar [data-testid="stButton"] [data-testid="stMarkdownContainer"] p,
    .stSidebar [data-testid="stButton"] [data-testid="stMarkdownContainer"] span,
    [data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stMarkdownContainer"] p,
    [data-testid="stSidebar"] [data-testid="stButton"] [data-testid="stMarkdownContainer"] span {
        color: #000000 !important;
    }
    
    section[data-testid="stSidebar"] h3,
    section[data-testid="stSidebar"] h2 {
        color: #F0F4F8 !important;
    }

    /* Active & Inactive Navigation Item Styling */
    .active-nav-item div[data-testid="stButton"] button {
        background: linear-gradient(90deg, rgba(122, 178, 211, 0.15) 0%, rgba(185, 229, 232, 0.05) 100%) !important;
        color: #7AB2D3 !important;
        border: 1.5px solid rgba(122, 178, 211, 0.45) !important;
        border-left: 5px solid #7AB2D3 !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 15px rgba(122, 178, 211, 0.15), inset 0 1px 0 rgba(255,255,255,0.05) !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 16px !important;
    }
    
    .inactive-nav-item div[data-testid="stButton"] button {
        background: transparent !important;
        color: #7E8F9F !important;
        border: 1.5px solid transparent !important;
        border-left: 5px solid transparent !important;
        border-radius: 12px !important;
        font-weight: 500 !important;
        box-shadow: none !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding-left: 16px !important;
        transition: all 0.25s ease !important;
    }
    
    .inactive-nav-item div[data-testid="stButton"] button:hover {
        background: rgba(18, 26, 42, 0.45) !important;
        color: #F0F4F8 !important;
        border: 1.5px solid rgba(122, 178, 211, 0.15) !important;
        border-left: 5px solid rgba(122, 178, 211, 0.4) !important;
    }

    /* Profile Card */
    .profile-card {
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.1) 0%, rgba(185, 229, 232, 0.08) 50%, rgba(223, 242, 235, 0.05) 100%);
        border: 2px solid rgba(122, 178, 211, 0.35);
        border-radius: 22px;
        padding: 24px 20px;
        margin-bottom: 18px;
        box-shadow: 0 12px 48px rgba(122, 178, 211, 0.15), inset 0 1px 0 rgba(255,255,255,0.05), 0 0 30px rgba(122, 178, 211, 0.08);
        backdrop-filter: blur(10px);
        transition: all 0.3s ease;
    }
    .profile-card:hover {
        box-shadow: 0 16px 60px rgba(122, 178, 211, 0.25), inset 0 1px 0 rgba(255,255,255,0.05), 0 0 40px rgba(122, 178, 211, 0.18);
        transform: translateY(-2px);
    }
    .profile-avatar {
        width: 80px; height: 80px;
        background: linear-gradient(135deg, #7AB2D3 0%, #B9E5E8 50%, #DFF2EB 100%);
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 36px; margin: 0 auto 14px auto;
        box-shadow: 0 0 32px rgba(122, 178, 211, 0.4), 0 8px 24px rgba(185, 229, 232, 0.3), inset 0 1px 0 rgba(255,255,255,0.2);
        border: 3px solid rgba(122, 178, 211, 0.6);
    }
    .profile-name { 
        color: #F0F4F8 !important; 
        font-size: 20px; 
        font-weight: 800; 
        text-align: center; 
        background: linear-gradient(135deg, #DFF2EB, #7AB2D3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .profile-detail { 
        color: #D1DCE5 !important; 
        font-size: 14px; 
        text-align: center; 
        margin-top: 6px;
        font-weight: 500;
    }
    .stat-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-top: 14px; }
    .stat-item {
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.08), rgba(185, 229, 232, 0.05));
        border-radius: 12px; 
        padding: 10px;
        text-align: center; 
        border: 1.5px solid rgba(122, 178, 211, 0.25);
        box-shadow: 0 4px 12px rgba(122, 178, 211, 0.1);
        transition: all 0.2s ease;
    }
    .stat-item:hover {
        border-color: rgba(122, 178, 211, 0.55);
        box-shadow: 0 6px 16px rgba(122, 178, 211, 0.18);
        transform: translateY(-1px);
    }
    .stat-label { 
        font-size: 10px; 
        color: #7E8F9F !important; 
        text-transform: uppercase; 
        letter-spacing: 0.6px;
        font-weight: 700;
    }
    .stat-value { 
        font-size: 16px; 
        font-weight: 700; 
        color: #DFF2EB !important; 
        margin-top: 3px;
        background: linear-gradient(135deg, #DFF2EB, #7AB2D3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }

    /* Chat Messages */
    .chat-container {
        max-height: 540px;
        overflow-y: auto;
        padding: 8px 4px;
        scrollbar-width: thin;
        scrollbar-color: rgba(122, 178, 211, 0.4) transparent;
    }
    .msg-user {
        display: flex; justify-content: flex-end; margin: 10px 0;
    }
    .msg-user .bubble {
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8);
        color: #0B111E; padding: 13px 18px; border-radius: 20px 20px 4px 20px;
        max-width: 72%; font-size: 14px; line-height: 1.55;
        box-shadow: 0 4px 16px rgba(122, 178, 211, 0.35), 0 2px 6px rgba(185, 229, 232, 0.25);
    }
    .msg-bot {
        display: flex; justify-content: flex-start; margin: 10px 0; align-items: flex-start; gap: 10px;
    }
    .bot-avatar {
        width: 38px; height: 38px; min-width: 38px;
        background: linear-gradient(135deg, #B9E5E8, #7AB2D3);
        border-radius: 50%; display: flex; align-items: center;
        justify-content: center; font-size: 17px;
        box-shadow: 0 3px 12px rgba(122, 178, 211, 0.4);
    }
    .msg-bot .bubble {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.95));
        border: 1.5px solid rgba(122, 178, 211, 0.25);
        color: #D1DCE5; padding: 13px 18px; border-radius: 4px 20px 20px 20px;
        max-width: 78%; font-size: 14px; line-height: 1.65;
        box-shadow: 0 4px 16px rgba(0,0,0,0.4);
    }

    /* Alert Boxes */
    .alert-severe {
        background: linear-gradient(135deg, rgba(239,68,68,0.12), rgba(185,28,28,0.08));
        border: 1px solid rgba(239,68,68,0.45);
        border-left: 4px solid #ef4444;
        border-radius: 14px; padding: 16px; margin: 10px 0;
        color: #fca5a5;
        box-shadow: 0 4px 20px rgba(239,68,68,0.1);
    }
    .alert-moderate {
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.12), rgba(185, 229, 232, 0.08));
        border: 1px solid rgba(122, 178, 211, 0.45);
        border-left: 4px solid #7AB2D3;
        border-radius: 14px; padding: 16px; margin: 10px 0;
        color: #DFF2EB;
    }
    .alert-mild {
        background: linear-gradient(135deg, rgba(185, 229, 232, 0.12), rgba(223, 242, 235, 0.08));
        border: 1px solid rgba(185, 229, 232, 0.4);
        border-left: 4px solid #B9E5E8;
        border-radius: 14px; padding: 16px; margin: 10px 0;
        color: #DFF2EB;
    }
    .info-box {
        background: rgba(18, 26, 42, 0.85);
        border: 1.5px solid rgba(122, 178, 211, 0.25);
        border-radius: 14px; padding: 16px; margin: 10px 0;
        color: #D1DCE5;
    }

    /* Prominent Labels for Inputs */
    .stTextInput label, .stNumberInput label, .stSelectbox label, .stMultiSelect label, .stTextArea label {
        font-size: 16px !important;
        font-weight: 700 !important;
        color: #B9E5E8 !important;
        margin-bottom: 10px !important;
        display: inline-block !important;
        letter-spacing: 0.3px !important;
    }

    /* Input Area - Text inputs & Textareas */
    .stTextInput input, .stTextArea textarea {
        background: rgba(11, 17, 30, 0.95) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.35) !important;
        border-radius: 16px !important; color: #D1DCE5 !important;
        font-size: 17px !important; padding: 16px 20px !important;
        min-height: 54px !important;
        transition: all 0.2s ease !important;
        box-sizing: border-box !important;
    }
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #7AB2D3 !important;
        box-shadow: 0 0 0 3px rgba(122, 178, 211, 0.2), 0 0 20px rgba(122, 178, 211, 0.1) !important;
    }
    .stTextInput input::placeholder, .stTextArea textarea::placeholder { color: #7E8F9F !important; }

    /* Buttons */
    .stButton button {
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8) !important;
        color: #0B111E !important;
        border: 2px solid rgba(122, 178, 211, 0.45) !important;
        border-radius: 14px !important;
        font-weight: 700 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 6px 20px rgba(122, 178, 211, 0.25), inset 0 1px 0 rgba(255,255,255,0.15) !important;
        letter-spacing: 0.4px;
        text-shadow: 0 1px 1px rgba(255,255,255,0.2);
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #4A628A, #96C5C8) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 30px rgba(122, 178, 211, 0.4), inset 0 1px 0 rgba(255,255,255,0.2) !important;
        border-color: rgba(122, 178, 211, 0.7) !important;
    }
    .stButton button:active { 
        transform: translateY(0) !important;
        box-shadow: 0 4px 12px rgba(122, 178, 211, 0.3) !important;
    }

    /* Section Headers */
    .section-header {
        font-size: 23px; font-weight: 800;
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8, #DFF2EB);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 18px; letter-spacing: -0.3px;
    }
    .card {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.9), rgba(11, 17, 30, 0.85));
        border: 1.5px solid rgba(122, 178, 211, 0.22);
        border-radius: 18px; padding: 22px; margin-bottom: 18px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
    }

    /* Metric Cards */
    .metric-card {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9));
        border: 1.5px solid rgba(122, 178, 211, 0.22);
        border-radius: 16px; padding: 18px; text-align: center;
        box-shadow: 0 4px 20px rgba(0,0,0,0.25);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover { transform: translateY(-2px); box-shadow: 0 8px 30px rgba(122, 178, 211, 0.22); }
    .metric-value { font-size: 30px; font-weight: 800; background: linear-gradient(135deg, #7AB2D3, #B9E5E8); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .metric-label { font-size: 12px; color: #7E8F9F; text-transform: uppercase; margin-top: 5px; letter-spacing: 0.5px; }

    /* Nav Pills */
    .nav-pill {
        display: inline-block;
        padding: 6px 16px; border-radius: 20px;
        background: rgba(122, 178, 211, 0.12);
        border: 1px solid rgba(122, 178, 211, 0.3);
        color: #DFF2EB; font-size: 13px; font-weight: 500;
        cursor: pointer; margin: 4px;
    }
    .nav-pill.active {
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8);
        border-color: #7AB2D3; color: #0B111E;
    }

    /* Quick Symptom Buttons */
    .symptom-chip {
        display: inline-block; margin: 6px;
        padding: 8px 16px; border-radius: 20px;
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.15), rgba(185, 229, 232, 0.12));
        border: 1.5px solid rgba(122, 178, 211, 0.45);
        color: #F0F4F8; 
        font-size: 13px; 
        cursor: pointer;
        font-weight: 600;
        transition: all 0.25s ease;
        box-shadow: 0 4px 12px rgba(122, 178, 211, 0.15);
    }
    .symptom-chip:hover {
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.25), rgba(185, 229, 232, 0.2));
        border-color: rgba(122, 178, 211, 0.75);
        box-shadow: 0 6px 18px rgba(122, 178, 211, 0.25);
        transform: translateY(-1px);
    }

    /* Voice Button */
    .voice-btn {
        background: linear-gradient(135deg, #ef4444, #7AB2D3) !important;
        border-radius: 50% !important;
        width: 46px !important; height: 46px !important;
        font-size: 20px !important;
        box-shadow: 0 4px 15px rgba(122, 178, 211, 0.4) !important;
    }
    .voice-btn:hover {
        background: linear-gradient(135deg, #dc2626, #4A628A) !important;
        box-shadow: 0 6px 22px rgba(122, 178, 211, 0.55) !important;
    }
    .voice-btn.recording {
        background: linear-gradient(135deg, #ef4444, #dc2626) !important;
        animation: pulse-red 1.2s infinite;
    }
    @keyframes pulse-red {
        0%, 100% { box-shadow: 0 0 0 0 rgba(239,68,68,0.5); }
        50% { box-shadow: 0 0 0 10px rgba(239,68,68,0); }
    }

    /* Send Button specific (matching Speak button exactly) */
    div[data-testid="stFormSubmitButton"] button {
        background: rgba(11, 17, 30, 0.95) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.4) !important;
        color: #7AB2D3 !important;
        height: 46px !important;
        min-height: 46px !important;
        border-radius: 12px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        box-shadow: 0 0 10px rgba(122, 178, 211, 0.15) !important;
        text-shadow: none !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        letter-spacing: normal !important;
        margin-top: 0 !important;
        padding: 0 18px !important;
    }
    div[data-testid="stFormSubmitButton"] button:hover {
        background: rgba(11, 17, 30, 0.95) !important;
        border-color: #7AB2D3 !important;
        box-shadow: 0 0 15px rgba(122, 178, 211, 0.4) !important;
        color: #B9E5E8 !important;
        transform: scale(1.02) !important;
    }
    div[data-testid="stFormSubmitButton"] button:active {
        transform: scale(0.98) !important;
    }

    /* Scrollbar */
    ::-webkit-scrollbar { width: 5px !important; height: 5px !important; display: block !important; }
    html::-webkit-scrollbar, body::-webkit-scrollbar { display: block !important; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(122, 178, 211, 0.4); border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: rgba(122, 178, 211, 0.6); }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(11, 17, 30, 0.8) !important;
        border-radius: 14px; padding: 5px; gap: 4px;
        border: 1px solid rgba(122, 178, 211, 0.22);
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent !important; border-radius: 10px !important;
        color: #7E8F9F !important; font-weight: 500; transition: all 0.2s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8) !important;
        color: #0B111E !important;
        box-shadow: 0 4px 12px rgba(122, 178, 211, 0.35) !important;
    }

    /* Diagnosis badge */
    .diagnosis-card {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.98), rgba(11, 17, 30, 0.95));
        border: 1.5px solid rgba(122, 178, 211, 0.45);
        border-radius: 18px; padding: 20px; margin: 12px 0;
        box-shadow: 0 8px 32px rgba(122, 178, 211, 0.15);
    }

    /* Onboarding step */
    .step-active { border-color: #7AB2D3 !important; }
    .step-done   { border-color: #B9E5E8 !important; }

    /* Hide Streamlit Branding */
    footer { visibility: hidden; }
    #MainMenu { visibility: hidden; }
    .stDeployButton { display: none; }

    /* Number input styling */
    .stNumberInput input {
        background: rgba(11, 17, 30, 0.95) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.3) !important;
        border-radius: 16px !important; color: #D1DCE5 !important;
        font-size: 17px !important; padding: 16px 20px !important;
        min-height: 54px !important;
        box-sizing: border-box !important;
    }
    .stNumberInput input:focus {
        border-color: #7AB2D3 !important;
        box-shadow: 0 0 0 3px rgba(122, 178, 211, 0.2), 0 0 20px rgba(122, 178, 211, 0.1) !important;
    }

    /* Select box */
    .stSelectbox > div > div {
        background: rgba(11, 17, 30, 0.95) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.3) !important;
        border-radius: 16px !important; color: #D1DCE5 !important;
        min-height: 54px !important;
        font-size: 17px !important;
        padding: 6px 12px !important;
        box-sizing: border-box !important;
        display: flex !important;
        align-items: center !important;
    }
    .stSelectbox > div > div:focus-within {
        border-color: #7AB2D3 !important;
        box-shadow: 0 0 0 3px rgba(122, 178, 211, 0.2), 0 0 20px rgba(122, 178, 211, 0.1) !important;
    }
    .stSelectbox div[data-baseweb="select"] {
        font-size: 17px !important;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(11, 17, 30, 0.95) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.3) !important;
        border-radius: 16px !important;
        min-height: 54px !important;
        font-size: 17px !important;
        padding: 6px 12px !important;
        box-sizing: border-box !important;
    }
    .stMultiSelect > div > div:focus-within {
        border-color: #7AB2D3 !important;
        box-shadow: 0 0 0 3px rgba(122, 178, 211, 0.2), 0 0 20px rgba(122, 178, 211, 0.1) !important;
    }
    .stMultiSelect span[data-baseweb="tag"] {
        font-size: 14px !important;
        padding: 4px 10px !important;
        background: linear-gradient(135deg, rgba(122, 178, 211, 0.25), rgba(185, 229, 232, 0.2)) !important;
        border: 1px solid rgba(122, 178, 211, 0.45) !important;
        color: #F0F4F8 !important;
        border-radius: 8px !important;
    }

    /* Success / warning / error messages */
    .stSuccess { background: rgba(122, 178, 211, 0.1) !important; border-color: rgba(122, 178, 211, 0.4) !important; color: #DFF2EB !important; border-radius: 12px !important; }
    .stWarning { background: rgba(185, 229, 232, 0.1) !important; border-color: rgba(185, 229, 232, 0.4) !important; color: #DFF2EB !important; border-radius: 12px !important; }
    .stError { background: rgba(239, 68, 68, 0.1) !important; border-color: rgba(239, 68, 68, 0.4) !important; color: #fca5a5 !important; border-radius: 12px !important; }

    /* ONBOARDING CARD - PERSISTENT STYLING */
    .onboarding-card {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9)) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.3) !important;
        border-radius: 18px !important;
        padding: 30px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.35) !important;
        max-width: 650px !important;
        width: 100% !important;
        margin: 0 auto !important;
    }

    /* Chat wrapper - PERSISTENT STYLING */
    .chat-wrapper {
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.9), rgba(11, 17, 30, 0.85)) !important;
        border: 1.5px solid rgba(122, 178, 211, 0.25) !important;
        border-radius: 16px !important;
        padding: 16px !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.4) !important;
        margin-bottom: 20px !important;
        min-height: 400px !important;
    }
    /* Ensure main content stretches to viewport and utilizes full available screen */
    .main .block-container,
    div[data-testid="stAppViewBlockContainer"],
    .block-container { 
        min-height: calc(100vh - 160px) !important; 
        max-width: 98% !important; 
        width: 98% !important;
        padding-left: 2rem !important; 
        padding-right: 2rem !important;
    }

    /* Mobile responsive adjustments */
    @media (max-width: 980px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"],
        .block-container {
            padding-left: 1rem !important;
            padding-right: 1rem !important;
            width: 100% !important;
            max-width: 100% !important;
            min-width: 0 !important;
        }
        .chat-wrapper,
        .card,
        .metric-card,
        .diagnosis-card,
        .onboarding-card {
            padding: 14px !important;
            border-radius: 18px !important;
        }
        .chat-container {
            max-height: 60vh !important;
        }
        .stTextInput input,
        .stTextArea textarea,
        .stNumberInput input,
        .stSelectbox > div > div,
        .stMultiSelect > div > div {
            min-height: 44px !important;
            font-size: 15px !important;
            padding: 12px 14px !important;
        }
        div[data-testid="stFormSubmitButton"] button,
        .mic-btn,
        .voice-btn {
            height: 44px !important;
            min-height: 44px !important;
        }
        .stButton button {
            width: 100% !important;
        }
        form[data-testid="stForm"] > div > div {
            flex-wrap: wrap !important;
            gap: 0.8rem !important;
        }
        div[data-testid="stTextInput"] input {
            width: 100% !important;
        }
    }
    @media (max-width: 680px) {
        .main .block-container,
        div[data-testid="stAppViewBlockContainer"],
        .block-container {
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
        }
        .section-header { font-size: 20px !important; }
        .metric-value { font-size: 26px !important; }
        .stButton button { font-size: 13px !important; }
    }
    div[data-testid="stTextInput"] input,
    .stTextArea textarea {
        -webkit-appearance: none !important;
        appearance: none !important;
        outline: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stTextInput"] input:-webkit-autofill {
        box-shadow: 0 0 0px 1000px rgba(11,17,30,.95) inset !important;
        -webkit-text-fill-color: #D1DCE5 !important;
    }
    </style>
    """, unsafe_allow_html=True)

inject_global_styles()




# ─── SESSION STATE INIT ──────────────────────────────────────────────────────────
if "page" not in st.session_state:
    st.session_state.page = "login"
if "user_profile" not in st.session_state:
    st.session_state.user_profile = {}
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user_email" not in st.session_state:
    st.session_state.user_email = ""

def _get_user_prefix():
    email = st.session_state.get("user_email", "default")
    if not email:
        return "default"
    safe = ''.join([c for c in email if c.isalnum() or c in ('_', '-', '@', '.')]).lower() or 'default'
    safe = safe.replace('@', '_at_').replace('.', '_dot_')
    return safe

def _get_user_data_path():
    prefix = _get_user_prefix()
    return pathlib.Path("user_data") / f"user_{prefix}.json"

def load_chat_history_from_file():
    # Redundant: chat history is loaded directly inside load_user_data
    pass

def save_chat_history_to_file():
    # Save the consolidated user data file containing profile, logs, and chat history
    save_user_data()

def delete_chat_history_file():
    st.session_state.chat_history = []
    save_user_data()

def save_user_data():
    prefix = _get_user_prefix()
    if prefix == "default":
        return
    path = _get_user_data_path()
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sync reactive states into the user profile dictionary before saving
        st.session_state.user_profile["water_intake"] = st.session_state.get("water_intake", 0)
        st.session_state.user_profile["meal_tracker"] = st.session_state.get("meal_tracker", {"Breakfast": False, "Lunch": False, "Dinner": False, "Snacks": False})
        st.session_state.user_profile["ai_diet_enabled"] = st.session_state.get("ai_diet_enabled", False)
        
        merged_data = {
            "profile": st.session_state.user_profile,
            "health_logs": st.session_state.get("health_logs", []),
            "chat_history": st.session_state.get("chat_history", []),
            "diagnosed_conditions": st.session_state.get("diagnosed_conditions", [])
        }
        with path.open('w', encoding='utf-8') as f:
            _json.dump(merged_data, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def load_user_data(email):
    st.session_state.user_email = email
    prefix = _get_user_prefix()
    path = _get_user_data_path()
    
    # ─── SEAMLESS AUTO-MIGRATION FROM LEGACY SEPARATE FILES ───
    legacy_profile = pathlib.Path(f"profile_{prefix}.json")
    legacy_logs = pathlib.Path(f"logs_{prefix}.json")
    legacy_chat = pathlib.Path(f"chat_history_{prefix}.json")
    
    if legacy_profile.exists() and not path.exists():
        try:
            profile_data = {}
            with legacy_profile.open('r', encoding='utf-8') as f:
                profile_data = _json.load(f)
            
            logs_data = []
            if legacy_logs.exists():
                with legacy_logs.open('r', encoding='utf-8') as f:
                    logs_data = _json.load(f)
                    
            chat_data = []
            if legacy_chat.exists():
                with legacy_chat.open('r', encoding='utf-8') as f:
                    chat_data = _json.load(f)
            
            path.parent.mkdir(parents=True, exist_ok=True)
            merged = {
                "profile": profile_data,
                "health_logs": logs_data,
                "chat_history": chat_data,
                "diagnosed_conditions": []
            }
            with path.open('w', encoding='utf-8') as f:
                _json.dump(merged, f, ensure_ascii=False, indent=2)
                
            # Delete migrated legacy files
            try: legacy_profile.unlink()
            except: pass
            try: legacy_logs.unlink()
            except: pass
            try: legacy_chat.unlink()
            except: pass
        except Exception:
            pass

    if path.exists():
        try:
            with path.open('r', encoding='utf-8') as f:
                merged_data = _json.load(f)
            
            st.session_state.user_profile = merged_data.get("profile", {"email": email})
            st.session_state.health_logs = merged_data.get("health_logs", [])
            st.session_state.chat_history = merged_data.get("chat_history", [])
            st.session_state.diagnosed_conditions = merged_data.get("diagnosed_conditions", [])
            
            # Load active states
            st.session_state.water_intake = st.session_state.user_profile.get("water_intake", 0)
            st.session_state.meal_tracker = st.session_state.user_profile.get("meal_tracker", {"Breakfast": False, "Lunch": False, "Dinner": False, "Snacks": False})
            st.session_state.ai_diet_enabled = st.session_state.user_profile.get("ai_diet_enabled", False)
            return True
        except Exception:
            st.session_state.user_profile = {"email": email}
            
    # Default fallback for new/empty profile
    st.session_state.user_profile = {"email": email}
    st.session_state.health_logs = []
    st.session_state.chat_history = []
    st.session_state.diagnosed_conditions = []
    st.session_state.water_intake = 0
    st.session_state.meal_tracker = {"Breakfast": False, "Lunch": False, "Dinner": False, "Snacks": False}
    st.session_state.ai_diet_enabled = False
    return False

if "health_logs" not in st.session_state:
    st.session_state.health_logs = []
if "diagnosed_conditions" not in st.session_state:
    st.session_state.diagnosed_conditions = []
if "onboarding_step" not in st.session_state:
    st.session_state.onboarding_step = 0
if "chat_input_key" not in st.session_state:
    st.session_state.chat_input_key = 0
if "_profile_loaded" not in st.session_state:
    st.session_state._profile_loaded = False

def show_login():
    import base64
    inject_global_styles()
    
    # ── Load Healthcare AI Projector Image directly inside Python ──
    img_base64 = ""
    try:
        with open("assets/login_hero.png", "rb") as f:
            img_base64 = base64.b64encode(f.read()).decode("utf-8")
    except Exception:
        pass
        
    # ── Custom Screen Overrides & Particle Styles ──
    st.markdown(f"""
    <style>
    /* Full Screen Breathing Mesh Backdrop */
    .stApp {{
        background: radial-gradient(circle at 10% 20%, #121A2A 0%, #0B111E 100%) !important;
        background-attachment: fixed !important;
    }}
    
    /* CSS Drifting Ambient Particles */
    .floating-particle {{
        position: fixed;
        width: 16px;
        height: 16px;
        background: radial-gradient(circle, rgba(122, 178, 211, 0.4) 0%, rgba(122, 178, 211, 0) 70%);
        border-radius: 50%;
        pointer-events: none;
        z-index: 1;
        animation: floatParticle 12s ease-in-out infinite;
    }}
    .p1 {{ top: 15%; left: 8%; animation-duration: 14s; }}
    .p2 {{ top: 72%; left: 18%; animation-duration: 20s; animation-delay: -2s; }}
    .p3 {{ top: 28%; right: 12%; animation-duration: 16s; animation-delay: -5s; }}
    .p4 {{ top: 82%; right: 22%; animation-duration: 22s; animation-delay: -8s; }}

    @keyframes floatParticle {{
        0%, 100% {{ transform: translateY(0) translateX(0) scale(1); opacity: 0.3; }}
        50% {{ transform: translateY(-45px) translateX(25px) scale(1.3); opacity: 0.8; }}
    }}

    /* Luxury Asymmetric Glassmorphic Login Card */
    .login-card-left {{
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9)) !important;
        border: 2px solid rgba(122, 178, 211, 0.35) !important;
        border-radius: 28px !important;
        padding: 42px !important;
        box-shadow: 0 25px 80px rgba(122, 178, 211, 0.15), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.05),
                    0 0 35px rgba(122, 178, 211, 0.08) !important;
        backdrop-filter: blur(25px) !important;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1) !important;
        margin-top: 15px;
    }}
    .login-card-left:hover {{
        border-color: rgba(122, 178, 211, 0.6) !important;
        box-shadow: 0 35px 100px rgba(122, 178, 211, 0.28), 
                    inset 0 1px 0 rgba(255, 255, 255, 0.08),
                    0 0 50px rgba(122, 178, 211, 0.18) !important;
        transform: translateY(-4px);
    }}
    
    .login-logo {{
        font-size: 72px;
        margin-bottom: 8px;
        filter: drop-shadow(0 0 16px rgba(122, 178, 211, 0.5));
        animation: logoPulse 3s ease-in-out infinite;
        text-align: center;
    }}
    @keyframes logoPulse {{
        0%, 100% {{ transform: scale(1); filter: drop-shadow(0 0 16px rgba(122, 178, 211, 0.5)); }}
        50% {{ transform: scale(1.04); filter: drop-shadow(0 0 26px rgba(122, 178, 211, 0.75)); }}
    }}
    
    .login-title {{
        font-size: 38px !important;
        font-weight: 800 !important;
        background: linear-gradient(135deg, #7AB2D3, #B9E5E8, #DFF2EB);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin: 0 !important;
        letter-spacing: -0.8px !important;
        text-align: center;
    }}
    .login-subtitle {{
        color: #7E8F9F !important;
        font-size: 15px !important;
        margin-top: 8px !important;
        margin-bottom: 25px !important;
        font-weight: 500 !important;
        text-align: center;
    }}

    /* Futuristic Projector Case & Floating HUD Tags */
    .showcase-card {{
        position: relative;
        background: linear-gradient(135deg, rgba(18, 26, 42, 0.75), rgba(11, 17, 30, 0.65));
        border: 2px solid rgba(122, 178, 211, 0.28);
        border-radius: 28px;
        overflow: hidden;
        padding: 12px;
        box-shadow: 0 25px 70px rgba(0,0,0,0.6), 0 0 40px rgba(122, 178, 211, 0.05);
        animation: floatyShowcase 6s ease-in-out infinite;
        transition: all 0.5s ease;
        margin-top: 15px;
    }}
    .showcase-card:hover {{
        border-color: rgba(122, 178, 211, 0.5);
        box-shadow: 0 35px 90px rgba(0,0,0,0.8), 0 0 50px rgba(122, 178, 211, 0.12);
    }}
    
    @keyframes floatyShowcase {{
        0%, 100% {{ transform: translateY(0) rotate(0deg); }}
        50% {{ transform: translateY(-10px) rotate(0.4deg); }}
    }}
    
    .showcase-img {{
        width: 100%;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
        filter: brightness(0.92) contrast(1.03);
        transition: all 0.6s cubic-bezier(0.4, 0, 0.2, 1);
        display: block;
    }}
    .showcase-card:hover .showcase-img {{
        transform: scale(1.02);
        filter: brightness(1.02) contrast(1.08);
    }}
    
    /* Live HUD Stats Badges Over Image */
    .hud-badge {{
        position: absolute;
        background: rgba(11, 17, 30, 0.9);
        border: 1.5px solid rgba(122, 178, 211, 0.45);
        border-radius: 20px;
        padding: 8px 16px;
        font-size: 13px;
        font-weight: 700;
        color: #F0F4F8;
        box-shadow: 0 8px 24px rgba(0,0,0,0.5), 0 0 15px rgba(122, 178, 211, 0.15);
        backdrop-filter: blur(12px);
        display: flex;
        align-items: center;
        gap: 6px;
        animation: hudPulse 3s ease-in-out infinite alternate;
        z-index: 10;
    }}
    .hud-badge.b-top {{
        top: 25px;
        left: 25px;
        border-color: #7AB2D3;
        animation-delay: 0s;
    }}
    .hud-badge.b-mid {{
        bottom: 95px;
        right: 25px;
        border-color: #B9E5E8;
        animation-delay: -0.7s;
    }}
    .hud-badge.b-bot {{
        bottom: 35px;
        left: 25px;
        border-color: #DFF2EB;
        animation-delay: -1.4s;
    }}
    
    @keyframes hudPulse {{
        0% {{ transform: translateY(0) scale(1); box-shadow: 0 8px 24px rgba(0,0,0,0.5); }}
        100% {{ transform: translateY(-4px) scale(1.03); box-shadow: 0 12px 30px rgba(122, 178, 211, 0.25); }}
    }}
    
    .showcase-caption {{
        margin-top: 14px;
        text-align: center;
        color: #D1DCE5;
        font-size: 14px;
        font-weight: 600;
        letter-spacing: 0.5px;
        opacity: 0.85;
    }}
    </style>
    
    <!-- Drift Particle Node Layer -->
    <div class="floating-particle p1"></div>
    <div class="floating-particle p2"></div>
    <div class="floating-particle p3"></div>
    <div class="floating-particle p4"></div>
    """, unsafe_allow_html=True)
    
    # ── Split-Screen Responsive Layout ──
    col1, col2 = st.columns([1, 1.15], gap="large")
    
    with col1:
        st.markdown("""
        <div class="login-card-left">
            <div class="login-logo">🏥</div>
            <div class="login-title">HealthMate AI</div>
            <div class="login-subtitle">Your Premium Personal Clinical Health Companion 🩺</div>
        """, unsafe_allow_html=True)
        
        email = st.text_input("📧 Gmail / Email Address", placeholder="e.g. ankit@gmail.com", key="login_email")
        password = st.text_input("🔑 Password (any password accepted)", type="password", placeholder="••••••••", key="login_password")
        
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        if st.button("🚀 Access Health Portal", width='stretch', key="login_btn"):
            if not email:
                st.error("⚠️ Please enter a valid Email ID to log in!")
            elif "@" not in email or "." not in email:
                st.error("⚠️ Please enter a valid email format (e.g. name@gmail.com)!")
            elif not password:
                st.error("⚠️ Please enter a password to secure your local environment session!")
            else:
                has_profile = load_user_data(email)
                st.session_state.logged_in = True
                
                if has_profile:
                    st.success(f"🔑 Welcome back! Profile for {st.session_state.user_profile.get('name', 'User')} loaded successfully.")
                    st.session_state.page = "chat"
                else:
                    st.success("✨ New account detected! Bypassing to onboarding.")
                    st.session_state.page = "onboarding"
                    st.session_state.onboarding_step = 0
                
                st.query_params["email"] = email
                _save_profile_to_url(st.session_state.user_profile, st.session_state.page)
                st.rerun()
                
        st.markdown("</div>", unsafe_allow_html=True)
        
    with col2:
        if img_base64:
            st.markdown(f"""
<div class="showcase-card">
    <div class="hud-badge b-top">🩺 BP: 118/74</div>
    <div class="hud-badge b-mid">💓 HR: 72 bpm</div>
    <div class="hud-badge b-bot">🎯 SpO2: 99%</div>
    <img class="showcase-img" src="data:image/png;base64,{img_base64}" alt="Advanced Healthcare AI Platform Graphic" />
</div>
<div class="showcase-caption">🧬 REAL-TIME BIO-INSIGHTS CLINICAL SYSTEM ENGINE</div>
""", unsafe_allow_html=True)
        else:
            # Fallback if image failed to load, keeping the container clean
            st.markdown("""
            <div class="showcase-card" style="min-height: 480px; display: flex; align-items: center; justify-content: center;">
                <div style="text-align: center; color: #7E8F9F;">
                    <div style="font-size: 50px; margin-bottom: 15px;">🧬</div>
                    <div style="font-weight: 700; font-size: 16px; color: #7AB2D3;">Advanced Healthcare AI Platform</div>
                    <div style="font-size: 13px; margin-top: 5px;">Real-Time Bio-Insights Engine</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

def show_onboarding():
    st.markdown("""
    <div style='text-align:center; padding: 40px 0 20px 0;'>
        <div style='font-size:70px; margin-bottom:16px;'>🏥</div>
        <h1 style='font-size:38px; font-weight:800; background: linear-gradient(135deg, #7AB2D3, #B9E5E8, #DFF2EB);
            -webkit-background-clip:text; -webkit-text-fill-color:transparent; margin:0;'>
            Welcome to HealthMate AI
        </h1>
        <p style='color:#7E8F9F; font-size:16px; margin-top:10px;'>
            Your intelligent personal health companion 🩺
        </p>
    </div>
    """, unsafe_allow_html=True)

    step = st.session_state.onboarding_step
    steps = ["👤 Basic Info", "📊 Physical Stats", "🩸 Medical Details"]
    
    cols = st.columns(3)
    for i, (col, s) in enumerate(zip(cols, steps)):
        with col:
            color = "#7AB2D3" if i == step else ("#B9E5E8" if i < step else "#1B2A4A")
            st.markdown(f"""
            <div style='text-align:center; padding:10px; background:rgba(18, 26, 42, 0.6);
                border-radius:10px; border:2px solid {color}; color:{"#7AB2D3" if i==step else ("#B9E5E8" if i < step else "#7E8F9F")};
                font-size:14px; font-weight:{"600" if i==step else "400"}'>
                {s}
            </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    container = st.container(border=False)
    
    if step == 0:
        with container:
            st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
            st.markdown("### 👤 Tell us about yourself")
            name = st.text_input("Your Full Name", placeholder="e.g. Rahul Sharma", key="inp_name")
            age = st.number_input("Your Age", min_value=1, max_value=120, value=25, key="inp_age")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="inp_gender")
            
            if st.button("Next →", key="ob_next1", width='stretch'):
                if name:
                    st.session_state.user_profile.update({"name": name, "age": age, "gender": gender})
                    st.session_state.onboarding_step = 1
                    st.rerun()
                else:
                    st.error("Please enter your name to continue!")
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif step == 1:
        with container:
            st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
            st.markdown("### 📊 Physical Information")
            weight = st.number_input("Weight (kg)", min_value=10.0, max_value=300.0, value=65.0, step=0.5)
            height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=165.0, step=0.5)
            
            if weight > 0 and height > 0:
                bmi = weight / ((height/100)**2)
                bmi_color = "#10b981" if 18.5 <= bmi < 25 else "#f59e0b" if 25 <= bmi < 30 else "#ef4444" if bmi >= 30 else "#f59e0b"
                bmi_label = "Normal ✅" if 18.5 <= bmi < 25 else "Overweight ⚠️" if 25 <= bmi < 30 else "Obese 🔴" if bmi >= 30 else "Underweight ⚠️"
                st.markdown(f"""
                <div style='background:rgba(28,20,18,0.8); border:1px solid {bmi_color}; border-radius:10px;
                    padding:12px; text-align:center; margin:8px 0;'>
                    <div style='font-size:28px; font-weight:700; color:{bmi_color};'>{bmi:.1f}</div>
                    <div style='color:#96847f; font-size:13px;'>BMI – {bmi_label}</div>
                </div>""", unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back", key="ob_back1", width='stretch'):
                    st.session_state.onboarding_step = 0
                    st.rerun()
            with col2:
                if st.button("Next →", key="ob_next2", width='stretch'):
                    st.session_state.user_profile.update({"weight": weight, "height": height})
                    st.session_state.onboarding_step = 2
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)
    
    elif step == 2:
        with container:
            st.markdown('<div class="onboarding-card">', unsafe_allow_html=True)
            st.markdown("### 🩸 Medical Details")
            blood_group = st.selectbox("Blood Group", ["A+", "A-", "B+", "B-", "O+", "O-", "AB+", "AB-", "Don't Know"])
            existing = st.multiselect("Existing Conditions (if any)", 
                ["Diabetes", "Hypertension", "Heart Disease", "Asthma", "Thyroid", 
                 "Kidney Disease", "None"], default=["None"])
            allergies = st.text_input("Known Allergies", placeholder="e.g. Penicillin, Dust (optional)")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("← Back", key="ob_back2", width='stretch'):
                    st.session_state.onboarding_step = 1
                    st.rerun()
            with col2:
                if st.button("🚀 Start HealthMate!", key="ob_finish", width='stretch'):
                    st.session_state.user_profile.update({
                        "blood_group": blood_group,
                        "existing_conditions": existing,
                        "allergies": allergies,
                        "joined": datetime.now().strftime("%d %b %Y")
                    })
                    _save_profile_to_url(st.session_state.user_profile, "main")
                    name = st.session_state.user_profile.get("name", "")
                    st.session_state.chat_history = [{
                        "role": "assistant",
                        "content": f"Hi {name}! 👋 I'm HealthMate, your personal AI health assistant! I've noted your profile and I'm ready to help you.\n\nYou can **tell me about any symptoms you're feeling**, ask health questions, or type **'diet plan'** to see your personalized nutrition plan.\n\nHow are you feeling today? 😊",
                        "timestamp": datetime.now().strftime("%H:%M")
                    }]
                    save_user_log_to_csv()
                    save_user_data()
                    st.session_state.page = "main"
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────


def show_sidebar():
    profile = st.session_state.user_profile
    name = profile.get("name", "User")
    age = profile.get("age", "—")
    gender = profile.get("gender", "—")
    weight = profile.get("weight", "—")
    height = profile.get("height", "—")
    blood = profile.get("blood_group", "—")
    
    bmi_text = "—"
    if isinstance(weight, (int, float)) and isinstance(height, (int, float)) and height > 0:
        bmi = weight / ((height/100)**2)
        bmi_text = f"{bmi:.1f}"
    
    gender_emoji = "👨" if gender == "Male" else "👩" if gender == "Female" else "🧑"
    
    st.sidebar.markdown(f"""
    <div class="profile-card">
        <div style='text-align: center;'>
            <div class="profile-avatar">{gender_emoji}</div>
            <div class="profile-name">{name}</div>
            <div class="profile-detail">🩸 {blood} | {age} yrs</div>
        </div>
        <div class="stat-grid">
            <div class="stat-item">
                <div class="stat-label">⚖️ Weight</div>
                <div class="stat-value">{weight}</div>
                <div style='font-size:10px; color:#96847f;'>kg</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">📏 Height</div>
                <div class="stat-value">{height}</div>
                <div style='font-size:10px; color:#96847f;'>cm</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">📊 BMI</div>
                <div class="stat-value">{bmi_text}</div>
                <div style='font-size:10px; color:#96847f;'>score</div>
            </div>
            <div class="stat-item">
                <div class="stat-label">📅 Since</div>
                <div class="stat-value" style="font-size:13px">{profile.get('joined', '15M26')}</div>
                <div style='font-size:10px; color:#96847f;'>2026</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    if profile.get("existing_conditions") and "None" not in profile.get("existing_conditions", ["None"]):
        conditions = ", ".join([c for c in profile["existing_conditions"] if c != "None"])
        st.sidebar.markdown(f"""
        <div style='background:rgba(122,178,211,0.1); border:1px solid rgba(122,178,211,0.3);
            border-radius:10px; padding:10px; margin-bottom:12px;'>
            <div style='color:#7AB2D3; font-size:12px; font-weight:600;'>⚠️ Medical History</div>
            <div style='color:#DFF2EB; font-size:13px; margin-top:4px;'>{conditions}</div>
        </div>""", unsafe_allow_html=True)
    
    st.sidebar.markdown("### 🧭 Navigation")
    pages = [
        ("💬 Chat", "chat"),
        ("📊 Health Dashboard", "dashboard"),
        ("🥗 Diet Plan", "diet"),
        ("📋 Health Tracker", "tracker"),
        ("🧾 Medical Report Analyzer", "report"),
    ]
    for label, page_id in pages:
        if st.sidebar.button(label, key=f"nav_{page_id}", width='stretch'):
            st.session_state.page = page_id
            st.rerun()
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 🚨 Emergency")
    st.sidebar.markdown("""
    <div style='background:linear-gradient(135deg,rgba(122,178,211,0.15),rgba(223,242,235,0.1));
        border:1px solid rgba(122,178,211,0.5); border-radius:12px; padding:14px;
        box-shadow: 0 4px 16px rgba(122,178,211,0.1);'>
        <div style='color:#7AB2D3; font-weight:800; font-size:15px; margin-bottom:6px;'>📞 108 – Free Ambulance</div>
        <div style='color:#B9E5E8; font-size:13px; margin-bottom:3px;'>📞 112 – National Emergency</div>
        <div style='color:#B9E5E8; font-size:13px; margin-bottom:3px;'>📞 102 – Women & Child Ambulance</div>
        <div style='color:#DFF2EB; font-size:12px; margin-top:6px;'>🏥 1800-180-1104 – Health Helpline</div>
    </div>""", unsafe_allow_html=True)
    
    col_edit, col_logout = st.sidebar.columns(2)
    with col_edit:
        if st.button("✏️ Edit Profile", width='stretch', key="edit_profile"):
            st.session_state.page = "onboarding"
            st.session_state.onboarding_step = 0
            st.rerun()
    with col_logout:
        if st.button("🚪 Logout", width='stretch', key="logout_btn"):
            st.session_state.logged_in = False
            st.session_state.user_email = ""
            st.session_state.user_profile = {}
            st.session_state.chat_history = []
            st.session_state.health_logs = []
            st.session_state.page = "login"
            st.session_state.onboarding_step = 0
            st.session_state._profile_loaded = False
            st.query_params.clear()
            st.rerun()

# ─── CHAT PAGE ───────────────────────────────────────────────────────────────────


def show_chat():
    import re as _re, json
    name = st.session_state.user_profile.get("name", "there")

    # Initialize dynamic premium welcome greeting if chat is empty
    if not st.session_state.chat_history:
        first_name = name.split()[0] if name else "there"
        condition_str = ""
        if st.session_state.diagnosed_conditions:
            latest = st.session_state.diagnosed_conditions[-1]
            disease = latest.get("disease", "")
            if disease:
                condition_str = f" I hope your symptoms related to **{disease}** are getting better."
        st.session_state.chat_history = [{
            "role": "assistant",
            "content": f"Hi {first_name}! 👋 Welcome to HealthMate, your premium personal AI health companion!{condition_str}\n\nHow can I assist you today? You can **describe your symptoms** in detail, ask medical questions, or request a personalized **diet plan**! 🥦✨",
            "timestamp": datetime.now().strftime("%H:%M")
        }]
        try:
            save_chat_history_to_file()
        except Exception:
            pass

    # ── Global CSS ──────────────────────────────────────────────────────────
    st.markdown("""
    <style>
    @keyframes stpulse{0%,100%{opacity:1}50%{opacity:.4}}
    div[data-testid="stTextInput"] {
        margin-bottom: 0 !important;
        display: flex !important;
        align-items: center !important;
    }
    div[data-testid="stTextInput"] label {
        display: none !important;
    }
    div[data-testid="stTextInput"] input {
        background:rgba(11,17,30,.95)!important;
        border:1.5px solid rgba(122,178,211,.4)!important;
        border-radius:12px!important; color:#D1DCE5!important;
        font-size:14px!important; height:46px!important;
        padding:0 16px!important; box-sizing:border-box!important;
        outline: none !important;
        margin: 0 !important;
        width: 100% !important;
        line-height: 46px !important;
    }
    div[data-testid="stTextInput"] input:focus{
        border-color:#7AB2D3!important;
        box-shadow:0 0 0 3px rgba(122,178,211,.2)!important;
    }
    div[data-testid="stTextInput"] input::placeholder{color:#7E8F9F!important;}
    div[data-testid="stFormSubmitButton"],
    div[data-testid="stForm"] div[data-testid="stTextInput"] {
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
        min-height: 46px !important;
        margin-top: 0 !important;
        padding: 0 !important;
    }
    div[data-testid="stFormSubmitButton"] button {
        margin-top: 0 !important;
        min-height: 46px !important;
        height: 46px !important;
        line-height: 46px !important;
    }
    form[data-testid="stForm"] > div > div {
        display: flex !important;
        align-items: center !important;
    }
    </style>""", unsafe_allow_html=True)

    # ── Chat header ─────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style='display:flex;align-items:center;gap:14px;margin-bottom:16px;
        background:linear-gradient(135deg,rgba(18,26,42,.95),rgba(11,17,30,.9));
        border:1px solid rgba(122,178,211,.35);border-radius:18px;padding:14px 20px;
        box-shadow:0 8px 32px rgba(122,178,211,.15);'>
      <div style='width:46px;height:46px;background:linear-gradient(135deg,#7AB2D3,#B9E5E8,#DFF2EB);
          border-radius:50%;display:flex;align-items:center;justify-content:center;
          font-size:21px;box-shadow:0 0 18px rgba(122,178,211,.5);'>🏥</div>
      <div>
        <div style='font-size:19px;font-weight:800;background:linear-gradient(135deg,#7AB2D3,#B9E5E8);
            -webkit-background-clip:text;-webkit-text-fill-color:transparent;'>HealthMate AI</div>
        <div style='font-size:12px;color:#B9E5E8;display:flex;align-items:center;gap:5px;'>
          <span style='width:7px;height:7px;background:#7AB2D3;border-radius:50%;
              box-shadow:0 0 5px #7AB2D3;animation:stpulse 2s infinite;display:inline-block;'></span>
          Online — Ready to help, {name}!
        </div>
      </div>
      <div style='margin-left:auto;background:rgba(122,178,211,.15);border:1px solid rgba(122,178,211,.3);
          border-radius:10px;padding:5px 12px;font-size:12px;color:#DFF2EB;'>🤖 AI Powered</div>
    </div>
    """, unsafe_allow_html=True)

    # ── Quick symptom chips ─────────────────────────────────────────────────
    st.markdown("""
    <div style='background: linear-gradient(135deg, rgba(122,178,211,0.12), rgba(185,229,232,0.12));
        border: 1.5px solid rgba(122,178,211,0.3);
        border-radius: 14px; padding: 14px 16px; margin-bottom: 16px;
        box-shadow: 0 4px 16px rgba(122,178,211,0.15);'>
        <div style='font-size: 16px; font-weight: 800; background: linear-gradient(135deg, #7AB2D3, #B9E5E8);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 10px;'>
            ⚡ Quick Symptoms:
        </div>
    </div>
    """, unsafe_allow_html=True)
    quick_symptoms = ["😤 Fever","🤧 Cold & Cough","🤢 Nausea","😵 Headache",
                      "💔 Chest Pain","😴 Fatigue","🤮 Vomiting","💊 Body Ache"]
    sc = st.columns(4)
    for i, sym in enumerate(quick_symptoms):
        with sc[i % 4]:
            if st.button(sym, key=f"qs_{i}", width='stretch'):
                stxt = sym.split(" ",1)[1]
                msg_content = f"I have {stxt}"
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": msg_content,
                    "timestamp": datetime.now().strftime("%H:%M")
                })
                try:
                    save_chat_history_to_file()
                except Exception:
                    pass
                st.session_state["_pending_user_message"] = msg_content
                st.rerun()

    # ── Build chat messages HTML ────────────────────────────────────────────
    msgs = st.session_state.chat_history

    rows_html = ""
    for idx, msg in enumerate(msgs):
        ts = msg.get("timestamp","")
        if msg["role"] == "user":
            safe = (msg["content"]
                    .replace("&","&amp;").replace("<","&lt;").replace(">","&gt;")
                    .replace("\n","<br>"))
            rows_html += f"""
<div style='display:flex;justify-content:flex-end;margin:8px 0;width:100%;'>
  <div style='display:flex;flex-direction:column;align-items:flex-end;max-width:72%;'>
    <div style='background:linear-gradient(135deg,#7AB2D3,#B9E5E8);color:#0B111E;
        padding:11px 16px;border-radius:18px 18px 4px 18px;width:fit-content;
        font-size:14px;line-height:1.55;box-shadow:0 4px 14px rgba(122,178,211,.35);
        word-break:break-word;overflow-wrap:break-word;white-space:pre-wrap;
        text-align:left;'>{safe}</div>
    <div style='text-align:right;font-size:11px;color:#7E8F9F;margin-top:3px;'>{ts}</div>
  </div>
</div>"""
        else:
            raw = msg["content"]
            # Escape HTML to prevent mismatched tags from breaking the container or leaking `</div>`
            safe_content = (raw
                            .replace("&","&amp;")
                            .replace("<","&lt;")
                            .replace(">","&gt;"))
            fmt = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content).replace("\n","<br>")
            rows_html += f"""
<div style='display:flex;align-items:flex-start;gap:10px;margin:8px 0;width:100%;'>
  <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#B9E5E8,#7AB2D3);
      border-radius:50%;display:flex;align-items:center;justify-content:center;
      font-size:16px;box-shadow:0 3px 10px rgba(122,178,211,.4);flex-shrink:0;'>🤖</div>
  <div style='display:flex;flex-direction:column;align-items:flex-start;max-width:78%;flex:1;min-width:0;'>
    <div style='background:linear-gradient(135deg,rgba(18,26,42,.98),rgba(11,17,30,.95));
        border:1px solid rgba(122,178,211,.25);color:#D1DCE5;
        padding:12px 16px;border-radius:4px 18px 18px 18px;width:fit-content;
        font-size:14px;line-height:1.65;box-shadow:0 4px 14px rgba(0,0,0,.35);
        word-break:break-word;'>{fmt}</div>
    <div style='font-size:11px;color:#96847f;margin-top:3px;'>{ts}</div>
  </div>
</div>"""

    # Diagnosis badge
    diag_html = ""
    if st.session_state.diagnosed_conditions:
        latest = st.session_state.diagnosed_conditions[-1]
        disease = latest.get("disease","")
        conf = latest.get("confidence",0)
        if disease and disease in DISEASE_INFO:
            info = DISEASE_INFO[disease]
            sev = info["severity"]
            sc_map = {"mild":"#DFF2EB","moderate":"#B9E5E8","severe":"#7AB2D3","emergency":"#4A628A"}
            sev_color = sc_map.get(sev,"#7E8F9F")
            diag_html = f"""
<div style='background:linear-gradient(135deg,rgba(18,26,42,.9),rgba(11,17,30,.85));
    border:1px solid rgba(122,178,211,.3);border-radius:14px;padding:16px;margin-top:14px;margin-bottom:14px;'>
  <div style='background:linear-gradient(135deg,#7AB2D3,#B9E5E8,#DFF2EB);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;font-weight:800;font-size:17px;margin-bottom:10px;'>
    ✨ AI Diagnosis: {info['simple_name']}
  </div>
  <div style='display:flex;gap:10px;margin-bottom:10px;flex-wrap:wrap;'>
    <span style='background:rgba(185,229,232,.15);border:1px solid rgba(185,229,232,.3);
        padding:3px 10px;border-radius:20px;font-size:12px;color:#B9E5E8;font-weight:600;'>
      🎯 Confidence: {conf}%</span>
    <span style='background:rgba(0,0,0,.3);border:1px solid {sev_color};
        padding:3px 10px;border-radius:20px;font-size:12px;color:{sev_color};font-weight:600;'>
      ⚕️ Severity: {sev.upper()}</span>
  </div>
  <div style='color:#D1DCE5;font-size:14px;line-height:1.6;padding-left:10px;border-left:3px solid #7AB2D3;'>
    {info['description']}</div>
</div>"""

    # Render entire chat area in native Streamlit flow using st.markdown
    chat_box_placeholder = st.empty()
    html_content = f"<div style='background:linear-gradient(135deg,rgba(18,26,42,0.9),rgba(11,17,30,0.85)); border:1px solid rgba(122,178,211,0.25); border-radius:16px; padding:16px; margin-bottom:16px; display:flex; flex-direction:column;'>{rows_html}{diag_html}</div>"
    chat_box_placeholder.markdown(html_content.replace("\n", " "), unsafe_allow_html=True)

    # ── Severe alert (st.markdown is fine — no scripts needed) ─────────────
    if st.session_state.diagnosed_conditions:
        latest = st.session_state.diagnosed_conditions[-1]
        disease = latest.get("disease","")
        if disease and disease in DISEASE_INFO:
            info = DISEASE_INFO[disease]
            if info.get("when_to_visit") or info.get("severity") in ["severe","emergency"]:
                st.markdown(f"""
                <div style='background:linear-gradient(135deg,rgba(239,68,68,.12),rgba(185,28,28,.08));
                    border:1px solid rgba(239,68,68,.45);border-left:4px solid #ef4444;
                    border-radius:14px;padding:14px 18px;color:#fca5a5;margin-top:6px;'>
                  🚨 <b>{info['simple_name']} — Please See a Doctor Urgently!</b><br>
                  📞 <b>108</b> Free Ambulance &nbsp;|&nbsp; 📞 <b>112</b> National Emergency
                  &nbsp;|&nbsp; 🏥 Visit nearest hospital now.
                </div>""", unsafe_allow_html=True)

    # ── Chat input area form (relocated in normal page flow) ──
    st.markdown("<div class='chat-input-area'></div>", unsafe_allow_html=True)
    with st.form(key="chat_form", clear_on_submit=True):
        input_col, send_col, mic_col = st.columns([4.6, 0.9, 0.9])
        with input_col:
            user_input = st.text_input(
                label="Chat Input",
                label_visibility="collapsed",
                placeholder="Tell me your symptoms... (English or Hindi)",
                key="chat_input_box"
            )
        with send_col:
            send_clicked = st.form_submit_button("Send ➤", width='stretch')
        with mic_col:
            st.iframe(pathlib.Path("assets/mic_recorder.html"), height=46)
            
    # Process message submission
    if send_clicked and user_input.strip():
        message_to_send = user_input.strip()
        st.session_state.chat_history.append({
            "role": "user",
            "content": message_to_send,
            "timestamp": datetime.now().strftime("%H:%M")
        })
        try:
            save_chat_history_to_file()
        except Exception:
            pass
        st.session_state["_pending_user_message"] = message_to_send
        st.rerun()

    # If there is a pending user message, process it and show typewriter animation
    if st.session_state.get("_pending_user_message"):
        pending = st.session_state.pop("_pending_user_message")
        with st.spinner("HealthMate is thinking..."):
            process_message(pending, typing_placeholder=chat_box_placeholder, rows_html=rows_html, diag_html=diag_html)
        st.rerun()

    # ── Clear Conversation Button (Below the input form) ──
    st.markdown("<div style='height:10px;'></div>", unsafe_allow_html=True)
    col_clr, _ = st.columns([1.8, 4.2])
    with col_clr:
        if st.button("🧹 Clear Conversation", width='stretch', key="clear_chat_button"):
            try:
                clear_chat()
            except Exception:
                st.session_state.chat_history = []
            st.rerun()

    # Also push page content up via CSS for comfortable layout margins
    st.markdown("""
    <style>.main .block-container{padding-bottom:100px!important}</style>
    """, unsafe_allow_html=True)


def clear_chat():
    st.session_state.chat_history = []
    st.session_state.diagnosed_conditions = []
    st.session_state._just_replied = False
    # Clear all diet cached plans to force generation of a new, clean baseline diet plan on clear!
    for k in list(st.session_state.keys()):
        if k.startswith("ai_diet_"):
            del st.session_state[k]
    try:
        save_user_log_to_csv()
        save_user_data()
    except Exception:
        pass
    try:
        delete_chat_history_file()
    except Exception:
        pass


def process_message(user_message, typing_placeholder=None, rows_html="", diag_html=""):
    import re as _re
    import time
    
    symptoms = extract_symptoms(user_message)
    disease, confidence = match_disease(symptoms) if symptoms else (None, 0)
    if disease:
        disease = normalize_disease_name(disease)
    
    if disease and confidence >= 20:
        if not st.session_state.diagnosed_conditions or \
           st.session_state.diagnosed_conditions[-1].get("disease") != disease:
            st.session_state.diagnosed_conditions.append({
                "disease": disease,
                "confidence": confidence,
                "timestamp": datetime.now().isoformat(),
                "symptoms": symptoms
            })
            save_user_log_to_csv()
    
    text_lower = user_message.lower()
    if "diet" in text_lower or "diet plan" in text_lower or "food" in text_lower or "kya khana" in text_lower:
        condition = disease if disease else (st.session_state.diagnosed_conditions[-1]["disease"] 
                                             if st.session_state.diagnosed_conditions else None)
        base = get_diet_plan(st.session_state.user_profile, None)
        plan = None
        if condition:
            cache_key = f"ai_diet_{condition}"
            if cache_key in st.session_state:
                plan = st.session_state[cache_key]
            else:
                ai_plan = get_ai_diet_plan(st.session_state.user_profile, condition, base.copy())
                if ai_plan:
                    plan = ai_plan
                    st.session_state[cache_key] = plan
        if not plan:
            plan = get_diet_plan(st.session_state.user_profile, condition)
        response = f"""🥗 **Your Personalized Diet Plan**
 
📊 **BMI: {plan['bmi']} ({plan['bmi_category']}) | Daily Calories: ~{plan['daily_calories']} kcal**
 
🌅 **Breakfast:**
{chr(10).join(['• ' + item for item in plan['breakfast']])}
 
☀️ **Lunch:**
{chr(10).join(['• ' + item for item in plan['lunch']])}
 
🌙 **Dinner:**
{chr(10).join(['• ' + item for item in plan['dinner']])}
 
🍎 **Snacks:**
{chr(10).join(['• ' + item for item in plan['snacks']])}
 
💧 Water: {plan['water']}
🎯 Goal: {plan.get('goal', 'Maintain health')}

❌ **Avoid:** {', '.join(plan['avoid'])}

Type 'diet' anytime to see this plan! You can also check the full Diet Plan section 🥗"""
    else:
        response = get_ai_response(
            user_message,
            st.session_state.user_profile,
            st.session_state.chat_history[:-1],
            symptoms,
            disease
        )
        
        # ── Auto-inject severity warning if a severe/emergency disease matched ──
        if disease and confidence > 40:
            info = DISEASE_INFO.get(disease, {})
            sev = info.get("severity", "")
            if sev in ("severe", "emergency") and "108" not in response:
                response += (
                    f"\n\n🚨 **WARNING — '{info.get('simple_name', disease)}' requires urgent medical attention!**\n"
                    f"• 📞 **108** — Free Ambulance (24/7)\n"
                    f"• 📞 **112** — National Emergency\n"
                    f"• 🏥 Please visit your nearest hospital without delay.\n"
                    f"• ⚠️ Do NOT wait for symptoms to worsen — act now!"
                )
    
    # ── Premium Typewriter Animation Effect ──
    if typing_placeholder and response:
        words = response.split(" ")
        current_text = ""
        ts_now = datetime.now().strftime("%H:%M")
        
        for idx, word in enumerate(words):
            current_text += (word + " ")
            safe_content = (current_text
                            .replace("&","&amp;")
                            .replace("<","&lt;")
                            .replace(">","&gt;"))
            fmt_animated = _re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_content).replace("\n","<br>")
            
            bubble_html = f"""
<div style='display:flex;align-items:flex-start;gap:10px;margin:8px 0;width:100%;'>
  <div style='width:36px;height:36px;min-width:36px;background:linear-gradient(135deg,#B9E5E8,#7AB2D3);
      border-radius:50%;display:flex;align-items:center;justify-content:center;
      font-size:16px;box-shadow:0 3px 10px rgba(122,178,211,.4);flex-shrink:0;'>🤖</div>
  <div style='display:flex;flex-direction:column;align-items:flex-start;max-width:78%;flex:1;min-width:0;'>
    <div style='background:linear-gradient(135deg,rgba(18,26,42,.98),rgba(11,17,30,.95));
        border:1px solid rgba(122,178,211,.25);color:#D1DCE5;
        padding:12px 16px;border-radius:4px 18px 18px 18px;width:fit-content;
        font-size:14px;line-height:1.65;box-shadow:0 4px 14px rgba(0,0,0,.35);
        word-break:break-word;'>{fmt_animated}▒</div>
    <div style='font-size:11px;color:#7E8F9F;margin-top:3px;'>{ts_now}</div>
  </div>
</div>
"""
            # Wrap typewriter bubble inside the main chat container HTML so it types inside the border!
            typing_html = f"<div style='background:linear-gradient(135deg,rgba(18,26,42,0.9),rgba(11,17,30,0.85)); border:1px solid rgba(122,178,211,0.25); border-radius:16px; padding:16px; margin-bottom:16px; display:flex; flex-direction:column;'>{rows_html}{bubble_html}{diag_html}</div>"
            typing_placeholder.markdown(typing_html.replace("\n", " "), unsafe_allow_html=True)
            time.sleep(0.03)
            
    st.session_state.chat_history.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now().strftime("%H:%M")
    })
    try:
        save_chat_history_to_file()
    except Exception:
        pass

# ─── DASHBOARD PAGE ──────────────────────────────────────────────────────────────


def show_dashboard():
    profile = st.session_state.user_profile
    name = profile.get("name", "User")
    
    st.markdown(f'<div class="section-header">📊 Health Dashboard – {name}</div>', unsafe_allow_html=True)
    
    weight = profile.get("weight", 70)
    height = profile.get("height", 165)
    age = profile.get("age", 30)
    gender = profile.get("gender", "Male")
    
    bmi = weight / ((height/100)**2) if height > 0 else 22
    if gender == "Male":
        bmr = 88.36 + (13.4 * weight) + (4.8 * height) - (5.7 * age)
    else:
        bmr = 447.6 + (9.2 * weight) + (3.1 * height) - (4.3 * age)
    daily_cal = int(bmr * 1.4)
    ideal_weight_low = 18.5 * ((height/100)**2)
    ideal_weight_high = 24.9 * ((height/100)**2)
    
    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)
    metrics = [
        ("BMI", f"{bmi:.1f}", "Normal" if 18.5 <= bmi < 25 else "High" if bmi >= 25 else "Low", "⚖️"),
        ("Daily Calories", f"{daily_cal}", "kcal needed", "🔥"),
        ("Ideal Weight", f"{ideal_weight_low:.0f}-{ideal_weight_high:.0f}kg", "for your height", "🎯"),
        ("Conditions Checked", str(len(st.session_state.diagnosed_conditions)), "in this session", "🔍"),
    ]
    for col, (label, value, sub, emoji) in zip([col1,col2,col3,col4], metrics):
        with col:
            st.markdown(f"""
            <div class="metric-card">
                <div style='font-size:24px;'>{emoji}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-label">{label}</div>
                <div style='color:#475569; font-size:11px;'>{sub}</div>
            </div>""", unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)

    # --- Small KPI row: Heart rate sparkline, Water progress, Sleep score, AI recs
    kcol1, kcol2, kcol3, kcol4 = st.columns([1,1,1,1])
    # Prepare 7-day series (prefer real logged data, else session_state, else sample)
    dates = pd.date_range(end=datetime.today(), periods=7)
    # Try to build proxies from user_health_logs.csv
    steps_vals = None
    hr_vals = None
    water_vals = None
    csv_path = pathlib.Path('data/user_health_logs.csv')
    try:
        if csv_path.exists():
            df_logs = pd.read_csv(csv_path, parse_dates=['Timestamp'])
            uname = st.session_state.get('user_profile', {}).get('name')
            if uname and 'Name' in df_logs.columns:
                df_user = df_logs[df_logs['Name'].astype(str).str.contains(str(uname), case=False)]
            else:
                df_user = df_logs
            if not df_user.empty:
                df_user['date'] = df_user['Timestamp'].dt.date
                last7 = [(datetime.today().date() - pd.Timedelta(days=i)) for i in range(6,-1,-1)]
                steps_vals = [(df_user[df_user['date']==d].shape[0] * 1000) for d in last7]
                # water & hr not present — try to read from session_state overrides
    except Exception:
        pass
    if not steps_vals:
        steps_vals = st.session_state.get('steps_7d') or [5400,6800,7200,6900,8000,7600,8200]
    hr_vals = st.session_state.get('hr_7d') or [72,75,70,73,74,71,72]
    water_vals = st.session_state.get('water_7d') or [1400,1500,1200,1600,1700,1500,1800]

    with kcol1:
        df_hr = pd.DataFrame({'date': dates, 'hr': hr_vals})
        fig_hr = px.line(df_hr, x='date', y='hr', markers=True, title='Resting HR (7d)')
        fig_hr.update_traces(line_color='#ef4444', marker=dict(size=6))
        fig_hr.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=180, margin=dict(t=30,b=20,l=10,r=10), font=dict(color='#7E8F9F'))
        st.plotly_chart(fig_hr, width='stretch', config={'displayModeBar': False})
        st.markdown(f"<div style='text-align:center;color:#7E8F9F;'>Avg: <b style='color:#ef4444;'>{int(np.mean(hr_vals))} BPM</b></div>", unsafe_allow_html=True)

    with kcol2:
        today_water = st.session_state.user_profile.get('water_intake_ml', 1200)
        goal_ml = st.session_state.user_profile.get('water_goal_ml', 2000)
        pct = min(100, int((today_water / max(1, goal_ml)) * 100))
        st.markdown("<div style='font-size:14px;color:#D1DCE5;font-weight:600;margin-bottom:6px;'>Water Intake</div>", unsafe_allow_html=True)
        st.progress(pct)
        st.markdown(f"<div style='color:#7E8F9F;margin-top:6px;'>Today: <b style='color:#7AB2D3;'>{today_water} ml</b> / {goal_ml} ml</div>", unsafe_allow_html=True)

    with kcol3:
        sleep_score = st.session_state.user_profile.get('sleep_score', 78)
        fig_sleep = go.Figure(go.Indicator(mode='gauge+number', value=sleep_score, gauge={'axis':{'range':[0,100]}, 'bar':{'color':'#7AB2D3'}, 'steps':[{'range':[0,60],'color':'#ef4444'},{'range':[60,85],'color':'#B9E5E8'},{'range':[85,100],'color':'#10b981'}]}))
        fig_sleep.update_layout(paper_bgcolor='rgba(0,0,0,0)', height=180, margin=dict(t=20,b=10))
        st.plotly_chart(fig_sleep, width='stretch', config={'displayModeBar': False})
        st.markdown("<div style='text-align:center;color:#7E8F9F;'>Sleep Score (last night)</div>", unsafe_allow_html=True)

    with kcol4:
        ai_recs = [
            "Drink a glass of water after waking up.",
            "Walk for 10 minutes after meals to aid digestion.",
            "Keep a consistent sleep schedule for better rest."
        ]
        st.markdown("<div style='font-size:14px;color:#D1DCE5;font-weight:700;margin-bottom:6px;'>AI Recommendations</div>", unsafe_allow_html=True)
        for r in ai_recs:
            st.markdown(f"<div style='color:#7E8F9F;margin-bottom:4px;'>• {r}</div>", unsafe_allow_html=True)

    col_l, col_r = st.columns(2)
    
    with col_l:
        # BMI Gauge
        bmi_val = round(bmi, 1)
        fig_bmi = go.Figure(go.Indicator(
            mode="gauge+number",
            value=bmi_val,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Your BMI", 'font': {'color': '#D1DCE5', 'size': 18}},
            number={'font': {'color': '#7AB2D3', 'size': 32}},
            gauge={
                'axis': {'range': [10, 40], 'tickfont': {'color': '#7E8F9F'}},
                'bar': {'color': '#B9E5E8'},
                'bgcolor': 'rgba(18,26,42,0.8)',
                'steps': [
                    {'range': [10, 18.5], 'color': 'rgba(223,242,235,0.3)'},
                    {'range': [18.5, 25], 'color': 'rgba(185,229,232,0.3)'},
                    {'range': [25, 30], 'color': 'rgba(223,242,235,0.3)'},
                    {'range': [30, 40], 'color': 'rgba(239,68,68,0.3)'},
                ],
                'threshold': {
                    'line': {'color': '#7AB2D3', 'width': 3},
                    'thickness': 0.8,
                    'value': bmi_val
                }
            }
        ))
        fig_bmi.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=260, margin=dict(t=50, b=10, l=20, r=20),
            font={'color': '#7E8F9F'}
        )
        bmi_cat = "Underweight" if bmi < 18.5 else "Normal ✅" if bmi < 25 else "Overweight ⚠️" if bmi < 30 else "Obese 🔴"
        st.plotly_chart(fig_bmi, width='stretch', config={'displayModeBar': False})
        st.markdown(f"<div style='text-align:center; color:#7E8F9F; font-size:14px; margin-top:-10px;'>Category: <b style='color:#B9E5E8;'>{bmi_cat}</b></div>", unsafe_allow_html=True)
    
    with col_r:
        # Caloric breakdown donut
        protein_cal = int(daily_cal * 0.25)
        carb_cal = int(daily_cal * 0.50)
        fat_cal = int(daily_cal * 0.25)
        
        fig_macro = go.Figure(data=[go.Pie(
            labels=["Carbohydrates 🌾", "Protein 💪", "Healthy Fats 🥑"],
            values=[carb_cal, protein_cal, fat_cal],
            hole=0.6,
            marker_colors=['#DFF2EB', '#B9E5E8', '#7AB2D3'],
            textfont={'color': '#D1DCE5', 'size': 12},
        )])
        fig_macro.update_layout(
            paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
            height=260, margin=dict(t=30, b=10, l=10, r=10),
            title={'text': f'Daily Macro Split ({daily_cal} kcal)', 'font': {'color': '#D1DCE5', 'size': 14}, 'x': 0.5},
            legend={'font': {'color': '#7E8F9F'}, 'bgcolor': 'rgba(0,0,0,0)'},
            annotations=[{'text': f'{daily_cal}<br>kcal', 'font': {'color': '#7AB2D3', 'size': 16}, 'showarrow': False}]
        )
        st.plotly_chart(fig_macro, width='stretch', config={'displayModeBar': False})

        # --- Weekly multi-series chart (HR, Steps, Water) ---
        try:
            df_week = pd.DataFrame({
                'date': dates,
                'hr': hr_vals,
                'steps': steps_vals,
                'water_ml': water_vals
            })
            fig_week = go.Figure()
            fig_week.add_trace(go.Scatter(x=df_week['date'], y=df_week['hr'], mode='lines+markers', name='HR (BPM)', line=dict(color='#ef4444')))
            fig_week.add_trace(go.Bar(x=df_week['date'], y=df_week['steps'], name='Steps', marker_color='#DFF2EB', yaxis='y2', opacity=0.6))
            fig_week.add_trace(go.Scatter(x=df_week['date'], y=df_week['water_ml'], mode='lines+markers', name='Water (ml)', line=dict(color='#B9E5E8')))
            fig_week.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', height=320, margin=dict(t=20,b=10,l=20,r=20), legend=dict(font=dict(color='#7E8F9F')),
                xaxis=dict(tickformat='%a'), yaxis=dict(title='HR / Water', color='#7E8F9F'), yaxis2=dict(title='Steps', overlaying='y', side='right', showgrid=False))
            st.markdown("### 📈 Weekly Health Overview")
            st.plotly_chart(fig_week, width='stretch', config={'displayModeBar': False})
        except Exception:
            pass

        # --- Activity heatmap (sample) ---
        try:
            # 7 days x 12 time buckets
            heat = np.array([[(v % 12) * 8 + (i*3) for i, v in enumerate(steps_vals)] for _ in range(7)])
            fig_heat = go.Figure(data=go.Heatmap(z=heat, x=[f"{h}:00" for h in range(6,18,1)], y=[d.strftime('%a') for d in dates], colorscale='Viridis'))
            fig_heat.update_layout(height=260, margin=dict(t=10,b=10,l=60,r=20), paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#7E8F9F'))
            st.markdown("### 🔥 Activity Heatmap")
            st.plotly_chart(fig_heat, width='stretch', config={'displayModeBar': False})
        except Exception:
            pass
    
    # Symptom history if available
    if st.session_state.diagnosed_conditions:
        st.markdown("### 🔍 Conditions Identified This Session")
        for i, cond in enumerate(st.session_state.diagnosed_conditions):
            dis = cond.get("disease", "Unknown")
            conf = cond.get("confidence", 0)
            info = DISEASE_INFO.get(dis, {})
            sev = info.get("severity", "unknown")
            sev_color = {"mild": "#DFF2EB", "moderate": "#B9E5E8", "severe": "#7AB2D3", "emergency": "#4A628A"}.get(sev, "#7E8F9F")
            simple = info.get("simple_name", dis)
            
            st.markdown(f"""
            <div style='background:rgba(18,26,42,0.8); border:1px solid rgba(122,178,211,0.15);
                border-left:4px solid {sev_color}; border-radius:12px; padding:14px; margin-bottom:8px;'>
                <div style='display:flex; justify-content:space-between; align-items:center;'>
                    <div>
                        <div style='color:#D1DCE5; font-weight:600; font-size:15px;'>{simple}</div>
                        <div style='color:#7E8F9F; font-size:12px; margin-top:2px;'>
                            Symptoms detected: {', '.join(cond.get('symptoms', [])) if isinstance(cond.get('symptoms'), list) else cond.get('symptoms', '')}
                        </div>
                    </div>
                    <div style='text-align:center;'>
                        <div style='color:{sev_color}; font-weight:700; font-size:18px;'>{conf}%</div>
                        <div style='color:#7E8F9F; font-size:11px;'>Confidence</div>
                    </div>
                </div>
            </div>""", unsafe_allow_html=True)

def show_diet():
    profile = st.session_state.user_profile
    name = profile.get("name", "User")
    
    st.markdown(f'<div class="section-header">🥗 Personalized Diet Plan for {name}</div>', unsafe_allow_html=True)
    
    condition = None
    if st.session_state.diagnosed_conditions:
        condition = st.session_state.diagnosed_conditions[-1].get("disease")
    elif profile.get("existing_conditions") and profile["existing_conditions"][0] != "None":
        condition = profile["existing_conditions"][0]
        
    if condition:
        condition = normalize_disease_name(condition)
        
    # Dynamically extract and sync active condition from latest chat history via Gemini!
    if st.session_state.get("chat_history"):
        chat_condition = extract_condition_from_chat(st.session_state.chat_history)
        if chat_condition and chat_condition != "None":
            chat_condition = normalize_disease_name(chat_condition)
            condition = chat_condition
            if not st.session_state.diagnosed_conditions or \
               st.session_state.diagnosed_conditions[-1].get("disease") != chat_condition:
                st.session_state.diagnosed_conditions.append({
                    "disease": chat_condition,
                    "confidence": 95,
                    "timestamp": datetime.now().isoformat(),
                    "symptoms": []
                })
                save_user_log_to_csv()
                save_user_data()
        
    cache_key = f"ai_diet_{condition}" if condition else "ai_diet_general"
    
    # Auto-enable AI optimization dynamically if a clinical condition is diagnosed from the chat
    if condition:
        st.session_state.ai_diet_enabled = True
        profile["ai_diet_enabled"] = True
    else:
        st.session_state.ai_diet_enabled = False
        profile["ai_diet_enabled"] = False
        
    plan = None
    
    if st.session_state.get("ai_diet_enabled", False) and condition:
        if cache_key in st.session_state:
            plan = st.session_state[cache_key]
        else:
            base = get_diet_plan(profile, condition)
            ai_plan = get_ai_diet_plan(profile, condition, base.copy())
            if ai_plan:
                st.session_state[cache_key] = ai_plan
                plan = ai_plan
                
    if not plan:
        plan = get_diet_plan(profile, condition)
        
    if not plan:
        st.info('No diet plan could be generated for your profile yet.')
        return

    bmi_val = plan.get('bmi', 22.0)
    bmi_color = "#10b981" if 18.5 <= bmi_val < 25 else "#f59e0b" if 25 <= bmi_val < 30 else "#ef4444" if bmi_val >= 30 else "#f59e0b"
    bmi_label = "Normal ✅" if 18.5 <= bmi_val < 25 else "Overweight ⚠️" if 25 <= bmi_val < 30 else "Obese 🔴" if bmi_val >= 30 else "Underweight ⚠️"
    
    st.markdown(f"""
    <div style='display:grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap:16px; margin-bottom:20px;'>
        <div style='background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9));
             border: 1.5px solid rgba(122, 178, 211, 0.3); border-radius:16px; padding:16px; text-align:center;
             box-shadow: 0 8px 32px rgba(0,0,0,0.3);'>
            <div style='color:#B9E5E8; font-size:12px; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;'>Active BMI</div>
            <div style='font-size:28px; color:{bmi_color}; font-weight:800; margin:6px 0;'>{bmi_val}</div>
            <div style='color:#D1DCE5; font-size:12px; font-weight:500;'>{bmi_label}</div>
        </div>
        <div style='background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9));
             border: 1.5px solid rgba(122, 178, 211, 0.3); border-radius:16px; padding:16px; text-align:center;
             box-shadow: 0 8px 32px rgba(0,0,0,0.3);'>
            <div style='color:#B9E5E8; font-size:12px; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;'>Target Calories</div>
            <div style='font-size:28px; color:#DFF2EB; font-weight:800; margin:6px 0;'>{plan['daily_calories']} <span style='font-size:14px; font-weight:500; color:#7E8F9F;'>kcal</span></div>
            <div style='color:#D1DCE5; font-size:12px; font-weight:500;'>Daily Energy Budget</div>
        </div>
        <div style='background: linear-gradient(135deg, rgba(18, 26, 42, 0.95), rgba(11, 17, 30, 0.9));
             border: 1.5px solid rgba(122, 178, 211, 0.3); border-radius:16px; padding:16px; text-align:center;
             box-shadow: 0 8px 32px rgba(0,0,0,0.3);'>
            <div style='color:#B9E5E8; font-size:12px; text-transform:uppercase; font-weight:700; letter-spacing:0.5px;'>Diet Goal</div>
            <div style='font-size:18px; color:#7AB2D3; font-weight:800; margin:10px 0;'>🎯 {plan.get('goal','Maintain health')}</div>
            <div style='color:#D1DCE5; font-size:12px; font-weight:500;'>Active Target Guidance</div>
        </div>
    </div>
    """, unsafe_allow_html=True)



    st.markdown("### 🍽️ Today's Menu & Logging")
    st.info("Check off the meals you consume to track your daily progress and visual nourishment!")
    
    if "meal_tracker" not in st.session_state:
        st.session_state.meal_tracker = {"Breakfast": False, "Lunch": False, "Dinner": False, "Snacks": False}
    elif not isinstance(st.session_state.meal_tracker, dict):
        st.session_state.meal_tracker = {"Breakfast": False, "Lunch": False, "Dinner": False, "Snacks": False}
        
    cols = st.columns(3)
    meals = [('Breakfast', plan.get('breakfast', [])), ('Lunch', plan.get('lunch', [])), ('Dinner', plan.get('dinner', []))]
    
    for c, (label, items) in zip(cols, meals):
        with c:
            checked = st.checkbox(f"I ate {label} today", value=st.session_state.meal_tracker.get(label, False), key=f"chk_meal_{label}")
            if checked != st.session_state.meal_tracker.get(label, False):
                st.session_state.meal_tracker[label] = checked
                st.session_state.user_profile["meal_tracker"] = st.session_state.meal_tracker
                save_user_data()
                st.rerun()
                
            box_border = "rgba(16, 185, 129, 0.45)" if checked else "rgba(122, 178, 211, 0.22)"
            box_bg = "rgba(16, 185, 129, 0.08)" if checked else "rgba(18, 26, 42, 0.7)"
            
            st.markdown(f"""
            <div style='background:{box_bg}; border: 1.5px solid {box_border}; border-radius:12px; padding:16px; min-height:160px;'>
                <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                    <div style='color:#7AB2D3; font-weight:700; font-size:16px;'>{label}</div>
                    <span style='font-size:12px; font-weight:600; color:{"#10b981" if checked else "#7E8F9F"}'>
                        {"✓ Eaten" if checked else "○ Pending"}
                    </span>
                </div>
            """, unsafe_allow_html=True)
            if items:
                for it in items:
                    st.markdown(f"<div style='font-size:13px; color:#D1DCE5; margin-bottom:4px;'>• {it}</div>", unsafe_allow_html=True)
            else:
                st.markdown("<div style='font-size:13px; color:#7E8F9F;'>• No suggestions</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    
    sn_col, adv_col = st.columns([1,1])
    with sn_col:
        checked_snack = st.checkbox("I ate Snacks today", value=st.session_state.meal_tracker.get("Snacks", False), key="chk_meal_Snacks")
        if checked_snack != st.session_state.meal_tracker.get("Snacks", False):
            st.session_state.meal_tracker["Snacks"] = checked_snack
            st.session_state.user_profile["meal_tracker"] = st.session_state.meal_tracker
            save_user_data()
            st.rerun()
            
        box_border = "rgba(16, 185, 129, 0.45)" if checked_snack else "rgba(122, 178, 211, 0.22)"
        box_bg = "rgba(16, 185, 129, 0.08)" if checked_snack else "rgba(18, 26, 42, 0.7)"
        
        st.markdown(f"""
        <div style='background:{box_bg}; border: 1.5px solid {box_border}; border-radius:12px; padding:16px;'>
            <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:10px;'>
                <div style='color:#7AB2D3; font-weight:700; font-size:16px;'>🍎 Snacks & Extras</div>
                <span style='font-size:12px; font-weight:600; color:{"#10b981" if checked_snack else "#7E8F9F"}'>
                    {"✓ Eaten" if checked_snack else "○ Pending"}
                </span>
            </div>
        """, unsafe_allow_html=True)
        for s in plan.get('snacks', []):
            st.markdown(f"<div style='font-size:13px; color:#D1DCE5; margin-bottom:4px;'>• {s}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
    with adv_col:
        st.markdown("""
        <div style='background:rgba(239, 68, 68, 0.06); border: 1.5px solid rgba(239, 68, 68, 0.35); border-radius:12px; padding:16px; height: 100%;'>
            <div style='color:#ef4444; font-weight:700; font-size:16px; margin-bottom:10px;'>⚠️ Avoid Strictly</div>
        """, unsafe_allow_html=True)
        for a in plan.get('avoid', []):
            st.markdown(f"<div style='font-size:13px; color:#fca5a5; margin-bottom:4px;'>✕ {a}</div>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

    checked_count = sum(1 for v in st.session_state.meal_tracker.values() if v)
    total_meals = len(st.session_state.meal_tracker)
    progress_pct = checked_count / total_meals
    progress_cal = int(progress_pct * plan['daily_calories'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"""
    <div style='background: rgba(18, 26, 42, 0.95); border: 1.5px solid rgba(122, 178, 211, 0.25); border-radius: 14px; padding: 18px;'>
        <div style='display:flex; justify-content:space-between; align-items:center; margin-bottom:8px;'>
            <div style='color:#D1DCE5; font-weight:700; font-size:15px;'>⚡ Daily Nutrient & Calorie Meter</div>
            <div style='color:#7AB2D3; font-weight:700; font-size:15px;'>{progress_cal} / {plan['daily_calories']} kcal consumed</div>
        </div>
    """, unsafe_allow_html=True)
    st.progress(progress_pct)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("### 💧 Interactive Hydration Tracker")
    
    if "water_intake" not in st.session_state:
        st.session_state.water_intake = st.session_state.user_profile.get("water_intake", 0)
        
    water_target = 3000
    water_pct = min(st.session_state.water_intake / water_target, 1.0)
    
    water_col1, water_col2 = st.columns([1, 2])
    with water_col1:
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, rgba(185, 229, 232, 0.15), rgba(122, 178, 211, 0.08));
             border: 2px solid rgba(185, 229, 232, 0.45); border-radius: 16px; padding: 20px; text-align: center;'>
            <div style='font-size: 50px; margin-bottom: 8px;'>🥤</div>
            <div style='font-size: 26px; font-weight: 800; color: #B9E5E8;'>{st.session_state.water_intake} <span style='font-size:14px; font-weight:500; color:#7E8F9F;'>ml</span></div>
            <div style='font-size: 12px; color: #D1DCE5; margin-top: 4px;'>Daily Progress ({int(water_pct * 100)}%)</div>
        </div>
        """, unsafe_allow_html=True)
    with water_col2:
        st.markdown("""
        <div style='padding-top: 10px;'>
            <div style='color:#cbd5e1; font-weight:600; font-size:14px; margin-bottom:8px;'>Add Drink Size:</div>
        </div>
        """, unsafe_allow_html=True)
        
        btn_cols = st.columns(3)
        with btn_cols[0]:
            if st.button("➕ 250 ml (Glass)", key="wat_250", width='stretch'):
                st.session_state.water_intake += 250
                st.session_state.user_profile["water_intake"] = st.session_state.water_intake
                save_user_data()
                st.rerun()
        with btn_cols[1]:
            if st.button("➕ 500 ml (Bottle)", key="wat_500", width='stretch'):
                st.session_state.water_intake += 500
                st.session_state.user_profile["water_intake"] = st.session_state.water_intake
                save_user_data()
                st.rerun()
        with btn_cols[2]:
            if st.button("🔄 Reset", key="wat_reset", width='stretch'):
                st.session_state.water_intake = 0
                st.session_state.user_profile["water_intake"] = 0
                save_user_data()
                st.rerun()
                
        st.markdown(f"""
        <div style='margin-top:16px;'>
            <div style='display:flex; justify-content:space-between; font-size:12px; color:#94a3b8; margin-bottom:4px;'>
                <span>0 ml</span>
                <span>Target: 3000 ml</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        st.progress(water_pct)


# ─── MEDICAL REPORT ANALYZER ───────────────────────────────────────────────────
def analyze_report_text(text):
    """Simple rule-based analyzer to detect common lab issues."""
    findings = []
    t = text.lower()

    # Hemoglobin
    import re
    hb = None
    m = re.search(r'(hemoglobin|hgb)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*(g/dl|gdl)?', t)
    if m:
        try:
            hb = float(m.group(2))
        except Exception:
            hb = None
    if hb is not None:
        findings.append(('Hemoglobin', hb))
        if hb < 12.0:
            findings.append(('Interpretation', f'Low hemoglobin ({hb} g/dL) — may indicate anemia.'))
        else:
            findings.append(('Interpretation', f'Hemoglobin {hb} g/dL — within expected range.'))
    else:
        if 'low hemoglobin' in t or 'anemia' in t:
            findings.append(('Hemoglobin', 'Reported low or anemia'))

    # Glucose / HbA1c
    gly = None
    m = re.search(r'(hba1c|a1c)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*%?', t)
    if m:
        try:
            gly = float(m.group(2))
        except Exception:
            gly = None
        if gly is not None:
            findings.append(('HbA1c', gly))
            if gly >= 6.5:
                findings.append(('Interpretation', f'HbA1c {gly}% — suggests diabetes/high long-term glucose.'))
            elif gly >= 5.7:
                findings.append(('Interpretation', f'HbA1c {gly}% — pre-diabetes range.'))
    else:
        m = re.search(r'(glucose|sugar)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*(mg/dl|mmol/l)?', t)
        if m:
            try:
                gly = float(m.group(2))
            except Exception:
                gly = None
            if gly is not None:
                findings.append(('Glucose', gly))
                if gly >= 200:
                    findings.append(('Interpretation', f'Random glucose {gly} mg/dL — high, possible diabetes.'))
                elif gly >= 126:
                    findings.append(('Interpretation', f'Fasting glucose {gly} mg/dL — high (diabetes range).'))

    # Cholesterol
    m_tot = re.search(r'(total cholesterol|cholesterol)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*(mg/dl)?', t)
    m_ldl = re.search(r'(ldl)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*(mg/dl)?', t)
    m_hdl = re.search(r'(hdl)[^\d\n\r]{0,30}([0-9]+\.?[0-9]*)\s*(mg/dl)?', t)
    if m_tot:
        try:
            tot = float(m_tot.group(2))
            findings.append(('Total Cholesterol', tot))
            if tot >= 240:
                findings.append(('Interpretation', f'Total cholesterol {tot} mg/dL — high risk.'))
            elif tot >= 200:
                findings.append(('Interpretation', f'Total cholesterol {tot} mg/dL — borderline high.'))
        except Exception:
            pass
    if m_ldl:
        try:
            ldl = float(m_ldl.group(2))
            findings.append(('LDL', ldl))
            if ldl >= 160:
                findings.append(('Interpretation', f'LDL {ldl} mg/dL — very high.'))
            elif ldl >= 130:
                findings.append(('Interpretation', f'LDL {ldl} mg/dL — high.'))
        except Exception:
            pass
    if m_hdl:
        try:
            hdl = float(m_hdl.group(2))
            findings.append(('HDL', hdl))
            if hdl < 40:
                findings.append(('Interpretation', f'HDL {hdl} mg/dL — low (higher risk).'))
        except Exception:
            pass

    # Keyword catches
    if 'high sugar' in t or 'high glucose' in t or 'hypergly' in t:
        findings.append(('Sugar', 'Reported high'))
    if 'low hemoglobin' in t or 'low hb' in t:
        findings.append(('Hemoglobin', 'Reported low'))
    if 'high cholesterol' in t or 'ldl high' in t:
        findings.append(('Cholesterol', 'Reported high'))

    return findings


def show_report():
    st.markdown('<div class="section-header">🧾 Medical Report Analyzer</div>', unsafe_allow_html=True)
    st.markdown('Upload blood reports (PDF/CSV/TXT) or X-ray images; AI will summarize key findings.', unsafe_allow_html=True)
    uploaded = st.file_uploader('Upload reports (PDF, TXT, CSV, JPG, PNG). You can upload multiple files.', type=['pdf','txt','csv','jpg','jpeg','png'], accept_multiple_files=True)
    if not uploaded:
        st.info('No files uploaded yet. Upload a blood report PDF or image to begin analysis.')
        return

    uploads_dir = pathlib.Path('uploads')
    uploads_dir.mkdir(exist_ok=True)

    all_text = ''
    for f in uploaded:
        dest = uploads_dir / f.name
        with dest.open('wb') as out:
            out.write(f.getbuffer())
        # Try to extract text depending on type
        text = ''
        if f.name.lower().endswith('.pdf'):
            text = extract_text_from_pdf(dest)
        elif f.name.lower().endswith(('.jpg','.jpeg','.png')):
            text = extract_text_from_image(dest)
        elif f.name.lower().endswith('.csv'):
            try:
                df = pd.read_csv(dest)
                text = df.to_string()
            except Exception:
                pass
        else:
            try:
                text = dest.read_text(encoding='utf-8')
            except Exception:
                pass

        if text:
            all_text += '\n' + text

    if not all_text.strip():
        st.warning('No text could be extracted from the uploaded files. Please upload a readable PDF/image or install the required OCR/PDF libraries.')
        return

    if st.button('Get AI Summary & Advice'):
        prompt = 'Summarize the following medical report and highlight any high sugar, low hemoglobin, or cholesterol issues. Provide friendly advice and next steps.\n\n' + all_text[:4000]
        try:
            summary = get_ai_response(prompt, st.session_state.user_profile, [], [], None)
        except Exception:
            summary = 'AI not available. Please ensure AI backend is configured.'
        st.markdown('### AI Summary')
        st.write(summary)
    # Medical report analyzer completes execution here successfully.

# ─── HEALTH TRACKER PAGE ─────────────────────────────────────────────────────────


def show_tracker():
    name = st.session_state.user_profile.get("name", "User")
    st.markdown(f'<div class="section-header">📋 Health Tracker – {name}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("### ➕ Log Today's Health")
    col1, col2 = st.columns(2)
    with col1:
        temp = st.number_input("🌡️ Temperature (°C)", min_value=35.0, max_value=42.0, value=37.0, step=0.1)
        bp_sys = st.number_input("💉 BP – Systolic (top)", min_value=80, max_value=200, value=120)
        spo2 = st.number_input("💨 Oxygen Level (%)", min_value=85, max_value=100, value=98)
    with col2:
        bp_dia = st.number_input("💉 BP – Diastolic (bottom)", min_value=50, max_value=130, value=80)
        pulse = st.number_input("💓 Pulse (beats/min)", min_value=40, max_value=200, value=72)
        mood = st.select_slider("😊 How are you feeling?", 
                                options=["😟 Bad", "😐 Okay", "🙂 Good", "😄 Great", "🤩 Excellent"])
    
    notes = st.text_area("📝 Any symptoms today?", placeholder="e.g. Mild headache in morning, felt tired after lunch...")
    
    if st.button("💾 Log Health Data", width='stretch'):
        # Initialize flags
        if "_profile_loaded" not in st.session_state: st.session_state._profile_loaded = False
        log_entry = {
            "date": datetime.now().strftime("%d %b %Y %H:%M"),
            "temperature": temp,
            "bp": f"{bp_sys}/{bp_dia}",
            "spo2": spo2,
            "pulse": pulse,
            "mood": mood,
            "notes": notes
        }
        st.session_state.health_logs.append(log_entry)
        save_user_data()
        st.success("✅ Health data logged successfully!")
        
        # Alerts
        alerts = []
        if temp > 37.5: alerts.append(f"⚠️ Fever detected ({temp}°C) — Stay hydrated and rest")
        if temp > 38.5: alerts.append(f"🚨 HIGH Fever ({temp}°C) — Consider seeing a doctor if it persists")
        if bp_sys > 140: alerts.append(f"⚠️ High BP ({bp_sys}/{bp_dia}) — Rest and avoid salt")
        if bp_sys < 90: alerts.append(f"⚠️ Low BP ({bp_sys}/{bp_dia}) — Drink ORS, eat something salty")
        if spo2 < 95: alerts.append(f"🚨 Low Oxygen ({spo2}%) — Take deep breaths; seek medical help if below 92%")
        if pulse > 100: alerts.append(f"⚠️ Elevated Heart Rate ({pulse} bpm) — Rest and stay calm")
        
        for alert in alerts:
            st.warning(alert)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Historical Data
    if st.session_state.health_logs:
        st.markdown("### 📈 Health History")
        
        logs = st.session_state.health_logs
        
        # Temperature Chart
        if len(logs) >= 2:
            dates = [l["date"].split(" ")[0] + " " + l["date"].split(" ")[1] for l in logs]
            temps = [l["temperature"] for l in logs]
            spO2s = [l["spo2"] for l in logs]
            
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=dates, y=temps, mode='lines+markers+text',
                name='Temp (°C)', line={'color': '#7AB2D3', 'width': 2},
                marker={'size': 8, 'color': '#7AB2D3'},
                text=[f"{t}°C" for t in temps], textposition='top center',
                textfont={'color': '#DFF2EB', 'size': 10}
            ))
            fig_temp.add_hline(y=37.5, line_dash="dash", line_color="rgba(239,68,68,0.5)",
                               annotation_text="Fever threshold", annotation_font_color="#f87171")
            fig_temp.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=220, margin=dict(t=30, b=30, l=40, r=20),
                title={'text': 'Temperature Trend', 'font': {'color': '#D1DCE5', 'size': 14}},
                xaxis={'tickfont': {'color': '#7E8F9F'}, 'gridcolor': 'rgba(122,178,211,0.05)'},
                yaxis={'tickfont': {'color': '#7E8F9F'}, 'gridcolor': 'rgba(122,178,211,0.05)', 'range': [36, 40]},
                legend={'font': {'color': '#7E8F9F'}, 'bgcolor': 'rgba(0,0,0,0)'},
            )
            
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.plotly_chart(fig_temp, width='stretch', config={'displayModeBar': False})
            
            fig_spo2 = go.Figure()
            fig_spo2.add_trace(go.Scatter(
                x=dates, y=spO2s, mode='lines+markers',
                name='SpO2 %', line={'color': '#B9E5E8', 'width': 2},
                marker={'size': 8}, fill='tozeroy',
                fillcolor='rgba(185,229,232,0.1)'
            ))
            fig_spo2.add_hline(y=95, line_dash="dash", line_color="rgba(239,68,68,0.5)",
                               annotation_text="Min normal", annotation_font_color="#f87171")
            fig_spo2.update_layout(
                paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                height=220, margin=dict(t=30, b=30, l=40, r=20),
                title={'text': 'Oxygen Level (%)', 'font': {'color': '#D1DCE5', 'size': 14}},
                xaxis={'tickfont': {'color': '#7E8F9F'}, 'gridcolor': 'rgba(122,178,211,0.05)'},
                yaxis={'tickfont': {'color': '#7E8F9F'}, 'gridcolor': 'rgba(122,178,211,0.05)', 'range': [90, 101]},
                legend={'font': {'color': '#7E8F9F'}, 'bgcolor': 'rgba(0,0,0,0)'},
            )
            with col_chart2:
                st.plotly_chart(fig_spo2, width='stretch', config={'displayModeBar': False})
        
        # Log table
        st.markdown("### 📋 All Health Logs")
        for log in reversed(st.session_state.health_logs[-10:]):
            bp_color = "#10b981"
            try:
                sys_val = int(log["bp"].split("/")[0])
                if sys_val > 140: bp_color = "#ef4444"
                elif sys_val > 130: bp_color = "#f59e0b"
            except: pass
            
            temp_color = "#10b981" if log["temperature"] <= 37.5 else "#f59e0b" if log["temperature"] <= 38.5 else "#ef4444"
            spo2_color = "#10b981" if log["spo2"] >= 96 else "#f59e0b" if log["spo2"] >= 92 else "#ef4444"
            
            st.markdown(f"""
            <div style='background:rgba(18,26,42,0.8); border:1px solid rgba(122,178,211,0.1);
                border-radius:12px; padding:14px; margin-bottom:8px;'>
                <div style='display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px;'>
                    <div style='color:#7E8F9F; font-size:12px;'>📅 {log['date']}</div>
                    <div style='color:{temp_color}; font-size:13px;'>🌡️ {log['temperature']}°C</div>
                    <div style='color:{bp_color}; font-size:13px;'>💉 {log['bp']} mmHg</div>
                    <div style='color:{spo2_color}; font-size:13px;'>💨 SpO₂: {log['spo2']}%</div>
                    <div style='color:#7AB2D3; font-size:13px;'>💓 {log['pulse']} bpm</div>
                    <div style='color:#DFF2EB; font-size:13px;'>{log['mood']}</div>
                </div>
                {f"<div style='color:#7E8F9F; font-size:12px; margin-top:6px;'>📝 {log['notes']}</div>" if log['notes'] else ""}
            </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style='text-align:center; padding:40px; color:#64748b;'>
            <div style='font-size:48px; margin-bottom:12px;'>📊</div>
            <div style='font-size:16px;'>No health data logged yet!</div>
            <div style='font-size:14px; margin-top:8px;'>Use the form above to start tracking your health daily</div>
        </div>""", unsafe_allow_html=True)

# ─── PERSISTENCE + HAMBURGER HELPERS ────────────────────────────────────────────
_HMP_PARAM = "hmp"




def _save_profile_to_url(profile: dict, page: str = None):
    """Encode profile as base64 JSON into URL query param — survives page refresh."""
    import base64
    encoded = base64.b64encode(json.dumps(profile).encode()).decode()
    st.query_params[_HMP_PARAM] = encoded
    if st.session_state.get("user_email"):
        st.query_params["email"] = st.session_state.user_email
    if page:
        st.query_params["p"] = page




def _load_profile_from_url():
    """On first load restore user profile from URL query param or email parameter."""
    if st.session_state.get("_profile_loaded", False):
        return
    st.session_state._profile_loaded = True
    
    # Check for direct email query parameter (refresh persistence)
    email_param = st.query_params.get("email", None)
    if email_param:
        has_profile = load_user_data(email_param)
        st.session_state.logged_in = True
        st.session_state.page = st.query_params.get("p", "main")
        return

    import base64
    raw = st.query_params.get(_HMP_PARAM, None)
    if not raw:
        return
    try:
        profile = json.loads(base64.b64decode(raw.encode()).decode())
        if profile.get("name"):
            st.session_state.user_profile = profile
            st.session_state.page = st.query_params.get("p", "main")
            
            # Load email
            email = profile.get("email") or (profile.get("name").lower().replace(" ", "") + "@gmail.com")
            st.session_state.user_email = email
            st.session_state.logged_in = True
            load_user_data(email)
    except Exception:
        pass




def _inject_hamburger():
    """Inject the ☰ button directly into the parent page DOM via a 0-height component."""
    st.components.v1.html("""
    <!DOCTYPE html><html><head><meta charset="utf-8"></head>
    <body style="margin:0;padding:0;overflow:hidden;">
    <script>
    (function(){
      var pd = window.parent.document;
      if (pd.getElementById('hm-stoggle')) return;
      var btn = pd.createElement('button');
      btn.id = 'hm-stoggle';
      btn.title = 'Toggle sidebar';
      btn.textContent = '\u2630';
      btn.onclick = function () {
        var selectors = [
          'button[data-testid="collapsedControl"]',
          'button[data-testid="baseButton-headerNoPadding"]',
          '[data-testid="stSidebarCollapsedControl"] button',
          'button[aria-label="Close sidebar"]',
          'button[aria-label="Open sidebar"]',
          'section[data-testid="stSidebar"] > div > div > button'
        ];
        for (var i = 0; i < selectors.length; i++) {
          var b = pd.querySelector(selectors[i]);
          if (b) { b.click(); return; }
        }
        var s = pd.querySelector('section[data-testid="stSidebar"]');
        if (s) {
          var cur = s.style.transform || window.parent.getComputedStyle(s).transform;
          s.style.transform = (cur && cur.indexOf('translateX') !== -1 && cur.indexOf('-1') !== -1)
            ? 'translateX(0)' : 'translateX(-110%)';
        }
      };
      pd.body.appendChild(btn);
    })();
    </script>
    </body></html>
    """, height=0, scrolling=False)


# ─── MAIN APP ────────────────────────────────────────────────────────────────────


def main():
    # Initialize session state on first load
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_email" not in st.session_state:
        st.session_state.user_email = ""
    if "page" not in st.session_state:
        st.session_state.page = "login"
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = {}
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "health_logs" not in st.session_state:
        st.session_state.health_logs = []
    if "diagnosed_conditions" not in st.session_state:
        st.session_state.diagnosed_conditions = []
    if "onboarding_step" not in st.session_state:
        st.session_state.onboarding_step = 0
    if "chat_input_key" not in st.session_state:
        st.session_state.chat_input_key = 0
    if "_profile_loaded" not in st.session_state:
        st.session_state._profile_loaded = False
    if "_just_replied" not in st.session_state:
        st.session_state["_just_replied"] = False

    # Ensure global styles are (re-)injected on every rerun
    try:
        inject_global_styles()
    except Exception:
        # fail silently if Streamlit isn't available during static checks
        pass

    # Restore profile from URL query param before anything renders
    _load_profile_from_url()
    
    # Sync current page to URL
    if st.session_state.page != "login" and st.session_state.page != "onboarding":
        st.query_params["p"] = st.session_state.page

    if not st.session_state.logged_in:
        st.session_state.page = "login"
        show_login()
    elif st.session_state.page == "onboarding":
        show_onboarding()
    else:
        show_sidebar()

        page = st.session_state.page
        if page == "chat" or page == "main":
            show_chat()
        elif page == "dashboard":
            show_dashboard()
        elif page == "diet":
            show_diet()
        elif page == "report":
            show_report()
        elif page == "tracker":
            show_tracker()


if __name__ == "__main__":
    main()

