import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

# --- 1. CONFIGURACIÓN DE PÁGINA ---
try:
    logo_icon = Image.open("logofban.png")
except:
    logo_icon = "🏦"

st.set_page_config(
    page_title="Generador de Firmas - Banco Solidario", 
    page_icon=logo_icon, 
    layout="centered"
)

# --- 2. CSS PARA DISEÑO CORPORATIVO Y LIMPIO ---
st.markdown("""
    <style>
    /* Ocultar elementos nativos de Streamlit */
    header {visibility: hidden;}
    footer {visibility: hidden;}
    #MainMenu {visibility: hidden;}
    .stDeployButton {display:none;}
    
    html, body, [class*="st-"] {
        font-family: 'Inter', 'Segoe UI', Roboto, sans-serif !important;
    }

    .block-container {
        padding-top: 1.5rem !important; 
        margin-top: -30px; 
    }

    .main-title-container {
        padding-top: 2px;
        line-height: 1.0;
    }

    .main-title-text {
        color: #23b5d6;
        font-size: 38px;
        font-weight: 800;
        font-family: 'Trebuchet MS', 'Segoe UI', sans-serif;
        letter-spacing: -1px;
    }

    .sub-title-text {
        color: #555;
        font-size: 14px;
        font-weight: 400;
        letter-spacing: 0.5px;
        text-transform: uppercase;
    }

    .section-header {
        color: #23b5d6;
        font-family: 'Segoe UI Bold', sans-serif;
        font-size: 15px;
        font-weight: 700;
        margin-top: 15px;
        margin-bottom: 15px;
        border-left: 4px solid #23b5d6;
        padding-left: 10px;
    }

    /* Botones con estilo estándar (Normal) */
    div.stButton > button:first-child, div.stDownloadButton > button:first-child {
        width: 100%;
        height: 3.5em;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. HEADER COMPACTO ---
col_logo, col_titulo = st.columns([1, 4])
with col_logo:
    try:
        st.image("logofban.png", width=100)
    except:
        st.write("🏦")

with col_titulo:
    st.markdown(f"""
        <div class="main-title-container">
            <span class="main-title-text">Generador de Firmas</span><br>
            <span class="sub-title-text">Herramienta de Autogestión — Banco Solidario</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="border-bottom: 2px solid #23b5d6; margin-bottom: 25px; margin-top: 10px;"></div>', unsafe_allow_html=True)

# --- 4. FUNCIÓN GENERADORA DE IMAGEN ---
def generar_imagen_firma(datos):
    canvas_w, canvas_h = 600, 130 
    im = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(im)
    try:
        f_nom = ImageFont.truetype("Gotham-Medium.ttf", 20) 
        f_car = ImageFont.truetype("Gotham-Medium.ttf", 13)
        f_apt = ImageFont.truetype("Aptos.ttf", 11)
        f_boo = ImageFont.truetype("Gotham-Book.ttf", 11)
    except: return None

    x_base, x_sang = 140, 150 
    y_curr = 15
    max_x = 0
    def med(txt, x, y, fnt, col="black"):
        nonlocal max_x
        draw.text((x, y), txt, font=fnt, fill=col)
        b = draw.textbbox((x, y), txt, font=fnt)
        if b[2] > max_x: max_x = b[2]

    med(datos["nombre_completo"], x_base, y_curr, f_nom, "#23b5d6")
    y_curr += 22 
    med(datos["cargo"], x_base, y_curr, f_car)
    y_curr += 18
    if datos["fijo"]: med(datos["fijo"], x_sang, y_curr, f_apt); y_curr += 14
    if datos["celular"]: med(datos["celular"], x_sang, y_curr, f_apt); y_curr += 14
    med(datos["email"], x_sang, y_curr, f_apt); y_curr += 14
    med(datos["direccion"], x_base, y_curr, f_boo); y_curr += 14
    med(datos["web"], x_base, y_curr, f_boo)
    
    try:
        logo_f = Image.open("logofban.png")
        h_logo = y_curr - 5 
        logo_res = logo_f.resize((int(h_logo * (logo_f.width/logo_f.height)), h_logo), Image.Resampling.LANCZOS)
        im.paste(logo_res, (15, 15), logo_res if logo_res.mode == 'RGBA' else None)
    except: pass
    return im.crop((0, 0, max_x + 20, y_curr + 20))

# --- 5. FORMULARIO ---
with st.container():
    with st.form("main_form"):
        st.markdown('<div class="section-header">INFORMACIÓN PERSONAL</div>', unsafe_allow_html=True)
        nombres = st.text_input("Nombres", placeholder="Ej: Juan Carlos")
        
        c1, c2 = st.columns(2)
        p_ape = st.text_input("Primer Apellido", placeholder="Ej: Pérez")
        s_ape = st.text_input("Segundo Apellido", placeholder="Ej: Armijos")
        
        st.markdown('<div class="section-header">PUESTO Y CONTACTO</div>', unsafe_allow_html=True)
        cargo = st.text_input("Cargo", placeholder="Ej: Analista de Crédito Senior")
        email = st.text_input("Correo Corporativo", placeholder="Ej: jperez@banco-solidario.com")
        
        c3, c4 = st.columns(2)
        cel = st.text_input("Celular (Opcional)", placeholder="Ej: 0998765432")
        ext = st.text_input("Extensión (Opcional)", placeholder="Ej: 1234")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("Generar Firma Institucional")

if submit:
    if not (nombres and p_ape and s_ape and cargo and email):
        st.error("Por favor, complete los campos obligatorios.")
    elif not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
        st.error("El formato del correo electrónico es incorrecto.")
    else:
        nom = nombres.strip().split(" ")[0].capitalize()
        p_ape_f = p_ape.strip().capitalize()
        s_ini = f"{s_ape.strip()[0].upper()}."
        full_nom = f"{nom} {p_ape_f} {s_ini}"

        cel_f = f"+593 {cel.strip().lstrip('0')[:2]} {cel.strip().lstrip('0')[2:5]} {cel.strip().lstrip('0')[5:]}" if cel.strip() else ""
        fij_f = f"(02) 3-950-600 Ext. {ext.strip()}" if ext.strip() else ""

        info = {
            "nombre_completo": full_nom, "cargo": cargo.strip(),
            "fijo": fij_f, "celular": cel_f, "email": email.strip().lower(),
            "direccion": "Amazonas y Corea N36-69. Quito/ Matriz", "web": "www.banco-solidario.com"
        }

        st.markdown('<div class="section-header">Resultado de la Generación</div>', unsafe_allow_html=True)
        img = generar_imagen_firma(info)
        if img:
            st.image(img)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("Descargar en Formato PNG", buf.getvalue(), f"Firma_{p_ape_f}.png", "image/png")
