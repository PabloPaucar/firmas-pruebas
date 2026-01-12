import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

def generar_firma_banco_final(datos):
    canvas_w, canvas_h = 1200, 600 
    celeste_banco = "#23b5d6"
    im = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    try:
        font_nombre = ImageFont.truetype("Gotham-Medium.ttf", 36)
        font_cargo = ImageFont.truetype("Gotham-Medium.ttf", 20)
        font_aptos = ImageFont.truetype("Aptos.ttf", 18)
        font_book = ImageFont.truetype("Gotham-Book.ttf", 18)
    except:
        st.error("Error: No se encontraron las fuentes .ttf.")
        return None

    x_base, x_sangria = 220, 235 
    y_start = 30
    y_current = y_start
    max_x = 0

    def dibujar_y_medir(texto, x, y, fuente, color="black"):
        nonlocal max_x
        draw.text((x, y), texto, font=fuente, fill=color)
        bbox = draw.textbbox((x, y), texto, font=fuente)
        if bbox[2] > max_x: max_x = bbox[2]

    # Renderizado con espaciado amplio y uniforme
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
        logo = Image.open("logofban.png")
        altura_bloque = y_end - y_start
        aspect_ratio = logo.width / logo.height
        logo_res = logo.resize((int(altura_bloque * aspect_ratio), int(altura_bloque)), Image.Resampling.LANCZOS)
        im.paste(logo_res, (15, y_start), logo_res if logo_res.mode == 'RGBA' else None)
    except: pass

    return im.crop((0, 0, max_x + 35, y_end + 25))

# --- INTERFAZ WEB (ORDEN DE ARRIBA HACIA ABAJO) ---
st.set_page_config(page_title="Generador Firmas Solidario", layout="centered")
st.title("🏦 Generador de Firmas Solidario")

with st.form("form_final"):
    st.subheader("📝 Datos de Identidad")
    nombres_in = st.text_input("1. Nombres (se usará solo el primero):")
    
    col_a1, col_a2 = st.columns(2)
    with col_a1:
        primer_apellido = st.text_input("2. Primer Apellido:")
    with col_a2:
        segundo_apellido = st.text_input("3. Segundo Apellido (Obligatorio):")
        
    cargo = st.text_input("4. Cargo:")

    st.markdown("---")
    st.subheader("📞 Configuración de Contacto")
    
    email = st.text_input("5. Correo electrónico corporativo:")
    
    col_c, col_e = st.columns(2)
    with col_c:
        cel_raw = st.text_input("6. Celular (Opcional):", placeholder="Ej: 0992926771")
    with col_e:
        ext = st.text_input("7. Extensión (Opcional):", placeholder="Ej: 3432")

    submit = st.form_submit_button("🚀 GENERAR FIRMA")

if submit:
    patron_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Validaciones de obligatoriedad
    if not (nombres_in and primer_apellido and segundo_apellido and cargo and email):
        st.error("⚠️ Error: Todos los campos de Identidad (Nombre, Apellidos y Cargo) y el Email son obligatorios.")
    elif not re.match(patron_email, email):
        st.error("❌ El formato del correo electrónico es incorrecto.")
    else:
        # Lógica: Solo primer nombre
        nombre_solo = nombres_in.strip().split(" ")[0].capitalize()
        # Lógica: Inicial obligatoria del segundo apellido
        inicial_s = f"{segundo_apellido.strip()[0].upper()}."
        nombre_final = f"{nombre_solo} {primer_apellido.strip().capitalize()} {inicial_s}"

        # Lógica: Celular formato +593 XX XXX XXXX
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
        
        resultado = generar_firma_banco_final(info)
        if resultado:
            st.image(resultado, caption="Vista previa de tu firma")
            buf = io.BytesIO()
            resultado.save(buf, format="PNG")
            st.download_button("📥 Descargar Firma", buf.getvalue(), f"Firma_{primer_apellido}.png", "image/png")