import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

# --- 1. CONFIGURACIÓN DE PÁGINA ---
# Cargamos la imagen para usarla como ícono de la pestaña
try:
    logo_icon = Image.open("logofban.png")
except:
    logo_icon = "🏦" # Backup por si no encuentra el archivo

st.set_page_config(
    page_title="Generador de Firmas - Banco Solidario", 
    page_icon=logo_icon, # AQUÍ SE PONE EL LOGO DEL BANCO
    layout="centered"
)

# CSS para Header Ultra-Compacto y eliminación de espacios en blanco
st.markdown("""
    <style>
    /* ELIMINAR ESPACIO SUPERIOR VACÍO DE STREAMLIT */
    .block-container {
        padding-top: 0.5rem !important; 
        padding-bottom: 0rem !important;
    }
    
    /* HEADER COMPACTO */
    .header-box {
        display: flex;
        align-items: center;
        border-bottom: 2px solid #23b5d6;
        padding-bottom: 10px;
        margin-bottom: 20px;
    }

    .section-header {
        color: #23b5d6;
        font-family: 'Arial', sans-serif;
        font-size: 16px;
        font-weight: bold;
        margin-top: 10px;
        margin-bottom: 10px;
    }

    /* BOTONES */
    div.stButton > button:first-child {
        background-color: #23b5d6;
        color: white !important;
        border-radius: 6px;
        height: 3em;
        font-weight: bold;
        width: 100%;
        border: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- HEADER COMPACTO ---
col_logo, col_titulo = st.columns([1, 5])

with col_logo:
    try:
        st.image("logofban.png", width=80)
    except:
        st.write("🏦")

with col_titulo:
    st.markdown(f"""
        <div style="padding-top: 0px;">
            <span style="color: #23b5d6; font-size: 26px; font-weight: bold;">Generador de Firmas</span><br>
            <span style="color: #666; font-size: 13px;">Banco Solidario - Herramienta de Autogestión</span>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div style="border-bottom: 2px solid #23b5d6; margin-bottom: 20px; margin-top: -10px;"></div>', unsafe_allow_html=True)

# --- FUNCIÓN DE IMAGEN ---
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

# --- FORMULARIO ---
with st.container():
    with st.form("main_form"):
        st.markdown('<div class="section-header">Datos del Colaborador</div>', unsafe_allow_html=True)
        nombres = st.text_input("Nombres")
        c1, c2 = st.columns(2)
        p_ape = c1.text_input("Primer Apellido")
        s_ape = c2.text_input("Segundo Apellido (Obligatorio)")
        
        cargo = st.text_input("Cargo")
        email = st.text_input("Correo Corporativo")
        
        c3, c4 = st.columns(2)
        cel = c3.text_input("Celular (Opcional)")
        ext = c4.text_input("Extensión (Opcional)")
        
        st.markdown("<br>", unsafe_allow_html=True)
        submit = st.form_submit_button("GENERAR FIRMA")

if submit:
    if not (nombres and p_ape and s_ape and cargo and email):
        st.error("Campos obligatorios incompletos.")
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

        st.markdown('<div class="section-header">Resultado</div>', unsafe_allow_html=True)
        img = generar_imagen_firma(info)
        if img:
            st.image(img)
            buf = io.BytesIO()
            img.save(buf, format="PNG")
            st.download_button("📥 DESCARGAR PNG", buf.getvalue(), f"Firma_{p_ape_f}.png", "image/png")
