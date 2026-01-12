from PIL import Image, ImageDraw, ImageFont

def generar_firma_banco_final(datos):
    # --- 1. CONFIGURACIÓN DEL LIENZO ---
    canvas_w, canvas_h = 1200, 500 
    celeste_banco = "#23b5d6" #
    im = Image.new('RGB', (canvas_w, canvas_h), (255, 255, 255))
    draw = ImageDraw.Draw(im)

    # --- 2. CARGA DE FUENTES ---
    font_nombre = ImageFont.truetype("Gotham-Medium.ttf", 36)
    font_cargo = ImageFont.truetype("Gotham-Medium.ttf", 20)
    font_aptos = ImageFont.truetype("Aptos.ttf", 18)
    font_book = ImageFont.truetype("Gotham-Book.ttf", 18)

    # --- 3. COORDENADAS CON ESPACIADO AMPLIADO ---
    x_base = 240 
    x_sangria = 265 # Ajuste leve para compensar el aire extra
    y_start = 25
    y_current = y_start
    max_x = 0

    def dibujar_y_medir(texto, x, y, fuente, color="black"):
        nonlocal max_x
        draw.text((x, y), texto, font=fuente, fill=color)
        bbox = draw.textbbox((x, y), texto, font=fuente)
        if bbox[2] > max_x: max_x = bbox[2]

    # ESPACIADO UNIFORME INCREMENTADO:
    # Usaremos saltos de 26px para evitar que se vea amontonado
    
    # Nombre
    dibujar_y_medir(datos["nombre"], x_base, y_current, font_nombre, celeste_banco)
    y_current += 48 # Salto tras el nombre

    # Cargo
    dibujar_y_medir(datos["cargo"], x_base, y_current, font_cargo)
    y_current += 24 # Salto estándar ampliado

    # Bloque Contacto (Fijo, Celular, Email)
    for item in [datos["fijo"], datos["celular"], datos["email"]]:
        dibujar_y_medir(item, x_sangria, y_current, font_aptos)
        y_current += 24 # Antes era 22, ahora tiene más aire
    
    # Bloque Inferior (Dirección, Web)
    dibujar_y_medir(datos["direccion"], x_base, y_current, font_book)
    y_current += 24 # Salto idéntico ampliado
    dibujar_y_medir(datos["web"], x_base, y_current, font_book)
    
    y_end = y_current + 20

    # --- 4. LOGO SINCRONIZADO CON EL NUEVO TAMAÑO ---
    try:
        logo = Image.open("logofban.png")
        altura_bloque = y_end - y_start
        aspect_ratio = logo.width / logo.height
        nuevo_ancho = int(altura_bloque * aspect_ratio)
        logo_res = logo.resize((nuevo_ancho, int(altura_bloque)), Image.Resampling.LANCZOS)
        
        # Posicionamiento con margen izquierdo limpio
        im.paste(logo_res, (15, y_start), logo_res if logo_res.mode == 'RGBA' else None)
    except: pass

    # --- 5. RECORTE FINAL ---
    final_w = max_x + 30 # Más margen a la derecha
    final_h = y_end + 20 # Más margen abajo
    im_final = im.crop((0, 0, final_w, final_h))

    # --- 6. GUARDAR ---
    im_final.save("Firma_Final_Espaciada.png")
    print(f"✅ Firma generada con espaciado ampliado: {final_w}x{final_h} px")
    return im_final

# Datos de prueba
info = {

}

generar_firma_banco_final(info)