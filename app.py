import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

# --- 1. CONFIGURACIÓN DE PÁGINA Y ESTILO VISUAL DEL BANCO ---
st.set_page_config(page_title="Generador de Firmas - Banco Solidario", page_icon="🏦")

# CSS personalizado para la identidad del banco
st.markdown("""
    <style>
    /* Estilo para los títulos y subheaders */
    h1, h2, h3 {
        color: #23b5d6 !important;
        font-family: 'Gotham', sans-serif;
    }
    /* Personalización del botón de generar */
    div.stButton > button:first-child {
        background-color: #23b5d6;
        color: white;
        border: None;
        border-radius: 8px;
        width: 100%;
        height: 3em;
        font-weight: bold;
    }
    /* Personalización del botón de descarga */
    div.stDownloadButton > button:first-child {
        background-color: #28a745;
        color: white;
        border-radius: 8px;
        width: 100%;
    }
    /* Estilo de las cajas de texto */
    .stTextInput > div > div > input {
        border-color: #23b5d6;
    }
    </style>
    """, unsafe_allow_html=True)

def generar_firma_banco_final(datos):
    canvas_w, canvas_h = 1200, 600 
    celeste_banco = "#23b5d6" #
    im = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    try:
        font_nombre = ImageFont.truetype("Gotham-Medium.ttf", 36)
        font_cargo = ImageFont.truetype("Gotham-Medium.ttf", 20)
        font_aptos = ImageFont.truetype("Aptos.ttf", 18)
        font_book = ImageFont.truetype("Gotham-Book.ttf", 18)
    except:
        st.error("Error: No se encontraron las fuentes .ttf en el servidor.")
        return None

    x_base, x_sangria = 240, 265 
    y_start = 30
    y_current = y_start
    max_x = 0

    def dibujar_y_medir(texto, x, y, fuente, color="black"):
        nonlocal max_x
        draw.text((x, y), texto, font=fuente, fill=color)
        bbox = draw.textbbox((x, y), texto, font=fuente)
        if bbox[2] > max_x: max_x = bbox[2]

    # Renderizado con espaciado amplio
    dibujar_y_medir(datos["nombre_completo"], x_base, y_current, font_nombre, celeste_banco)
    y_current += 48 
    dibujar_y_medir(datos["cargo"], x_base, y_current, font_cargo)
    y_current += 26 

    if datos["fijo"]:
        dibujar_y_medir(datos["fijo"], x_sangria, y_current, font_aptos)
        y_current += 26
    
    if datos["celular"]:
        dibujar_y_medir(datos["celular"], x_sangria, y_current, font_aptos)
        y_current += 26

    dibujar_y_medir(datos["email"], x_sangria, y_current, font_aptos)
    y_current += 26 
    
    dibujar_y_medir(datos["direccion"], x_base, y_current, font_book)
    y_current += 26 
    dibujar_y_medir(datos["web"], x_base, y_current, font_book)
    
    y_end = y_current + 20

    try:
        logo = Image.open("logofban.png") #
        altura_bloque = y_end - y_start
        aspect_ratio = logo.width / logo.height
        logo_res = logo.resize((int(altura_bloque * aspect_ratio), int(altura_bloque)), Image.Resampling.LANCZOS)
        im.paste(logo_res, (15, y_start), logo_res if logo_res.mode == 'RGBA' else None)
    except: pass

    return im.crop((0, 0, max_x + 35, y_end + 25))

# --- 2. INTERFAZ DE USUARIO ---
st.title("🏦 Generador de Firmas Institucionales")
st.write("Complete sus datos para generar su firma oficial automáticamente.")

with st.form("form_visual"):
    st.subheader("📝 Datos del Colaborador")
    nombres_in = st.text_input("Nombres (se usará el primero):")
    
    col1, col2 = st.columns(2)
    with col1:
        primer_apellido = st.text_input("Primer Apellido:")
    with col2:
        segundo_apellido = st.text_input("Segundo Apellido (Obligatorio):")
        
    cargo = st.text_input("Cargo:")

    st.markdown("---")
    st.subheader("📞 Información de Contacto")
    email = st.text_input("Email corporativo:")
    
    col3, col4 = st.columns(2)
    with col3:
        cel_raw = st.text_input("Celular (Opcional):", placeholder="Ej: 0992926771")
    with col4:
        ext = st.text_input("Extensión (Opcional):", placeholder="Ej: 3432")

    submit = st.form_submit_button("🚀 GENERAR FIRMA")

if submit:
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    if not (nombres_in and primer_apellido and segundo_apellido and cargo and email):
        st.error("⚠️ Error: Todos los campos de identidad y el email son obligatorios.")
    elif not re.match(patron_email, email):
        st.error("❌ El formato del correo electrónico es inválido.")
    else:
        # 1. Solo primer nombre con inicial mayúscula
        nombre_solo = nombres_in.strip().split(" ")[0].capitalize()

        # 2. Lógica Inteligente para el Primer Apellido
        p_apellido_raw = primer_apellido.strip()
        
        # Si el apellido NO tiene espacios (es un solo apellido), aplicamos Capitalize
        if " " not in p_apellido_raw:
            p_apellido_final = p_apellido_raw.capitalize()
        else:
            # Si tiene espacios (apellido compuesto), lo dejamos tal cual el usuario lo escribió
            p_apellido_final = p_apellido_raw
        
        # 3. Inicial del segundo apellido siempre en Mayúscula
        inicial_s = f"{segundo_apellido.strip()[0].upper()}."
        
        nombre_final = f"{nombre_solo} {p_apellido_final} {inicial_s}"

        # 4. Formato de celular con espacios: +593 XX XXX XXXX
        cel_final = ""
        if cel_raw.strip():
            c = cel_raw.strip().lstrip('0') 
            cel_final = f"+593 {c[:2]} {c[2:5]} {c[5:]}"

        fijo_final = f"(02) 3-950-600 Ext. {ext.strip()}" if ext.strip() else ""

        info = {
            "nombre_completo": nombre_final,
            "cargo": cargo.strip(),
            "fijo": fijo_final,
            "celular": cel_final,
            "email": email.strip().lower(),
            "direccion": "Amazonas y Corea N36-69. Quito/ Matriz",
            "web": "www.banco-solidario.com"
        }
        
        # Generar imagen con el espaciado equilibrado
        resultado = generar_firma_banco_final(info)
        
        if resultado:
            st.success("✅ Firma generada correctamente")
            st.image(resultado, caption="Vista previa")
            
            buf = io.BytesIO()
            resultado.save(buf, format="PNG")
            st.download_button("📥 Descargar Firma", buf.getvalue(), f"Firma_{p_apellido_final}.png", "image/png")
