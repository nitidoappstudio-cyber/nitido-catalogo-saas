import streamlit as st
from supabase import create_client, Client
import uuid
from io import BytesIO
from PIL import Image

st.set_page_config(page_title="Nítido App Studio", page_icon="💻", layout="wide")

# --- CONEXIÓN A SUPABASE ---
SUPABASE_URL = "https://imomygeeknnaojbicrez.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Imltb215Z2Vla25uYW9qYmljcmV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTE3NjA4MjYsImV4cCI6MjEwNzMzNjgyNn0.25m7iNvfk3op6fJdtvl13N4HRvjB3zHHxoTC5LVRVKs"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# ==========================================
# SISTEMA DE LOGIN (PANTALLA DE ACCESO OSCURA)
# ==========================================
if "usuario" not in st.session_state:
    st.session_state.usuario = None

if st.session_state.usuario is None:
    # --- CSS OSCURO EXCLUSIVO PARA EL LOGIN ---
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] { display: none !important; }
        .stApp { background-color: #0f172a !important; color: #f8fafc !important; }
        div[data-testid="stForm"] { background-color: #1e293b !important; border: 1px solid #334155 !important; border-radius: 15px; padding: 2rem; }
        .marca-agencia { text-align: center; color: white !important; font-weight: 900; font-size: 2.5rem; margin-top: 30px; }
        .subtitulo-agencia { text-align: center; color: #94a3b8 !important; font-size: 1.1rem; margin-bottom: 40px; }
        input { background-color: #334155 !important; color: white !important; border-color: #475569 !important; }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("<h1 class='marca-agencia'>💻 Nítido App Studio</h1>", unsafe_allow_html=True)
    st.markdown("<p class='subtitulo-agencia'>Portal de Gestión para Comercios</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        with st.form("login_form"):
            st.markdown("<h4 style='text-align: center; color: white !important;'>Iniciar Sesión</h4>", unsafe_allow_html=True)
            email_input = st.text_input("Correo electrónico")
            password_input = st.text_input("Contraseña", type="password")
            submit_login = st.form_submit_button("Entrar a mi Tienda", use_container_width=True, type="primary")
            
            if submit_login:
                try:
                    res = supabase.auth.sign_in_with_password({"email": email_input, "password": password_input})
                    st.session_state.usuario = res.user
                    st.rerun() 
                except Exception as e:
                    st.error("Credenciales incorrectas. Revisa tu email y contraseña.")
    st.stop()
else:
    # --- FORZAR FONDO BLANCO EN EL PANEL PRIVADO ---
    # Una vez que el cliente entra, forzamos que su panel sea blanco y limpio
    st.markdown("""
        <style>
        [data-testid="collapsedControl"] { display: none !important; }
        .stApp { background-color: #ffffff !important; color: #31333F !important; }
        h1, h2, h3, h4, h5, h6, p, span, div, label { color: #31333F !important; }
        div[data-testid="stExpander"] { background-color: #ffffff !important; border-color: #e6e6e6 !important; }
        div[data-testid="stForm"] { background-color: #ffffff !important; border-color: #e6e6e6 !important; }
        input, textarea { background-color: #ffffff !important; color: #31333F !important; border-color: #cccccc !important; }
        </style>
    """, unsafe_allow_html=True)

# ==========================================
# PANEL PRIVADO (Todo tu código anterior sigue exactamente igual a partir de aquí)
# ==========================================
# try:
#     email_actual = st.session_state.usuario.email
# ... (asegúrate de que el resto de tu archivo admin.py siga intacto hacia abajo)
# ==========================================
# PANEL PRIVADO (Solo entra si pasó el Login)
# ==========================================

# 1. Buscamos el local que le pertenece a este usuario
try:
    email_actual = st.session_state.usuario.email
    respuesta_comercio = supabase.table('comercios').select('*').eq('email_dueno', email_actual).execute()
    
    if not respuesta_comercio.data:
        st.error(f"El usuario {email_actual} no tiene ningún local asociado en la base de datos.")
        if st.button("Cerrar Sesión"):
            supabase.auth.sign_out()
            st.session_state.usuario = None
            st.rerun()
        st.stop()
        
    comercio_data = respuesta_comercio.data[0]
    comercio_id = comercio_data['id']
    lista_categorias = comercio_data.get('categorias') or ["General"]
except Exception as e:
    st.error("Error al cargar los datos de tu comercio.")
    st.stop()

# --- FUNCIONES DE IMÁGENES ---
def subir_imagen_cuadrada_a_supabase(archivo, nombre_carpeta):
    if archivo is not None:
        img = Image.open(archivo)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        img.thumbnail((800, 800), Image.Resampling.LANCZOS)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='WEBP', quality=85)
        nombre_unico = f"{nombre_carpeta}/{uuid.uuid4()}.webp"
        supabase.storage.from_("imagenes-catalogo").upload(
            path=nombre_unico, file=img_byte_arr.getvalue(), file_options={"content-type": "image/webp"}
        )
        return supabase.storage.from_("imagenes-catalogo").get_public_url(nombre_unico)
    return None

def subir_portada_a_supabase(archivo, nombre_carpeta):
    if archivo is not None:
        img = Image.open(archivo)
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")
        ancho, alto = img.size
        proporcion_deseada = 2.5 
        proporcion_actual = ancho / alto
        if proporcion_actual > proporcion_deseada:
            nuevo_ancho = alto * proporcion_deseada
            img = img.crop(((ancho - nuevo_ancho) / 2, 0, (ancho + nuevo_ancho) / 2, alto))
        elif proporcion_actual < proporcion_deseada:
            nuevo_alto = ancho / proporcion_deseada
            img = img.crop((0, (alto - nuevo_alto) / 2, ancho, (alto + nuevo_alto) / 2))
        img.thumbnail((1200, 480), Image.Resampling.LANCZOS)
        img_byte_arr = BytesIO()
        img.save(img_byte_arr, format='WEBP', quality=85)
        nombre_unico = f"{nombre_carpeta}/{uuid.uuid4()}.webp"
        supabase.storage.from_("imagenes-catalogo").upload(
            path=nombre_unico, file=img_byte_arr.getvalue(), file_options={"content-type": "image/webp"}
        )
        return supabase.storage.from_("imagenes-catalogo").get_public_url(nombre_unico)
    return None

# --- ENCABEZADO Y BOTÓN DE CERRAR SESIÓN ---
col_titulo, col_logout = st.columns([4, 1])
with col_titulo:
    st.title(f"🛍️ Gestión: {comercio_data['nombre_marca']}")
with col_logout:
    st.write("") 
    if st.button("🚪 Cerrar Sesión"):
        supabase.auth.sign_out()
        st.session_state.usuario = None
        st.rerun()

tab1, tab2, tab3 = st.tabs(["Mis Productos", "➕ Agregar Nuevo", "🎨 Mi Tienda / Categorías"])

# --- PESTAÑA 2: AGREGAR PRODUCTO ---
with tab2:
    st.subheader("Cargar un nuevo producto")
    with st.form("nuevo_producto_form", clear_on_submit=True):
        nombre = st.text_input("Nombre del producto")
        col_precio, col_cat = st.columns(2)
        with col_precio:
            precio = st.number_input("Precio ($)", min_value=0.0, step=100.0)
        with col_cat:
            categoria = st.selectbox("Categoría", lista_categorias)
            
        descripcion = st.text_area("Descripción (opcional)")
        archivo_foto = st.file_uploader("Sube una foto del producto", type=['jpg', 'jpeg', 'png', 'webp'])
        submit = st.form_submit_button("Guardar Producto", type="primary")
        
        if submit:
            if nombre and precio > 0 and archivo_foto:
                st.info("Optimizando foto y guardando...")
                url_imagen = subir_imagen_cuadrada_a_supabase(archivo_foto, "productos")
                nuevo_item = {
                    "comercio_id": comercio_id, "nombre": nombre, "precio": precio,
                    "descripcion": descripcion, "imagen_url": url_imagen, "categoria": categoria
                }
                supabase.table('productos').insert(nuevo_item).execute()
                st.success("¡Producto guardado correctamente!")
                st.rerun() 
            else:
                st.warning("El nombre, el precio y la foto son obligatorios.")

# --- PESTAÑA 1: MIS PRODUCTOS ---
with tab1:
    st.subheader("Tus productos actuales")
    productos = supabase.table('productos').select('*').eq('comercio_id', comercio_id).order('fecha_creacion', desc=True).execute()
    
    if productos.data:
        for p in productos.data:
            with st.container(border=True):
                col1, col2, col3 = st.columns([1, 3, 1])
                with col1:
                    if p['imagen_url']:
                        st.image(p['imagen_url'], use_container_width=True)
                with col2:
                    st.subheader(p['nombre'])
                    st.caption(f"🏷️ Categoría: {p.get('categoria', 'General')}")
                    st.write(f"**Precio:** ${p['precio']}")
                with col3:
                    if st.button("🗑️ Borrar", key=f"del_{p['id']}"):
                        supabase.table('productos').delete().eq('id', p['id']).execute()
                        st.success("Producto eliminado.")
                        st.rerun()
    else:
        st.info("Aún no tienes productos cargados.")

# --- PESTAÑA 3: CONFIGURACIÓN Y CATEGORÍAS ---
with tab3:
    st.subheader("Gestión de Categorías")
    col_crear, col_borrar = st.columns(2)
    with col_crear:
        with st.form("nueva_categoria_form", clear_on_submit=True):
            nueva_cat = st.text_input("Añadir nueva categoría")
            if st.form_submit_button("➕ Crear Categoría"):
                if nueva_cat and nueva_cat not in lista_categorias:
                    lista_categorias.append(nueva_cat)
                    supabase.table('comercios').update({"categorias": lista_categorias}).eq('id', comercio_id).execute()
                    st.success(f"'{nueva_cat}' añadida.")
                    st.rerun()
    with col_borrar:
        with st.form("borrar_categoria_form"):
            cat_a_borrar = st.selectbox("Selecciona para eliminar", lista_categorias)
            if st.form_submit_button("🗑️ Borrar Categoría"):
                if cat_a_borrar in lista_categorias:
                    lista_categorias.remove(cat_a_borrar)
                    supabase.table('comercios').update({"categorias": lista_categorias}).eq('id', comercio_id).execute()
                    st.success(f"'{cat_a_borrar}' eliminada.")
                    st.rerun()
                
    st.divider()
    st.subheader("Personaliza tu vidriera")
    with st.form("configuracion_form"):
        nuevo_nombre = st.text_input("Nombre de la marca", value=comercio_data['nombre_marca'])
        nuevo_whatsapp = st.text_input("Número de WhatsApp", value=comercio_data['numero_whatsapp'])
        nuevo_color = st.color_picker("Color principal", value=comercio_data['color_principal'])
        
        st.divider()
        st.write("**Imágenes de la Tienda**")
        col_img1, col_img2 = st.columns(2)
        with col_img1:
            st.write("Logo actual:")
            if comercio_data.get('logo_url'):
                st.image(comercio_data['logo_url'], width=100)
            archivo_logo = st.file_uploader("Subir nuevo logo", type=['png', 'jpg', 'webp'])
            
        with col_img2:
            st.write("Portada actual:")
            if comercio_data.get('portada_url'):
                st.image(comercio_data['portada_url'], width=200)
            archivo_portada = st.file_uploader("Subir nueva Portada", type=['png', 'jpg', 'webp'])
        
        if st.form_submit_button("Guardar Cambios de Diseño"):
            datos_actualizados = {
                "nombre_marca": nuevo_nombre, "numero_whatsapp": nuevo_whatsapp, "color_principal": nuevo_color
            }
            if archivo_logo:
                st.info("Subiendo logo...")
                datos_actualizados["logo_url"] = subir_imagen_cuadrada_a_supabase(archivo_logo, "logos")
            if archivo_portada:
                st.info("Subiendo portada...")
                datos_actualizados["portada_url"] = subir_portada_a_supabase(archivo_portada, "logos")
                
            supabase.table('comercios').update(datos_actualizados).eq('id', comercio_id).execute()
            st.success("Configuración actualizada.")
            st.rerun()