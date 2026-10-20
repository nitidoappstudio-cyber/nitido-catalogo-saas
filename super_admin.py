import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Directorio - Nítido App Studio", page_icon="👑", layout="wide")

SUPABASE_URL = "https://imomygeeknnaojbicrez.supabase.co"
# ATENCIÓN: AQUÍ VA LA CLAVE "SERVICE_ROLE", NO LA ANON PUBLIC
SUPABASE_SERVICE_KEY = "sb_secret_muNwMrJXIo0qvbNsg0Fc4Q_pouzx4In" 

supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# --- ESTILOS OSCUROS PARA TODA LA APP SÚPER-ADMIN ---
st.markdown("""
    <style>
    .stApp { background-color: #0f172a !important; color: #f8fafc; }
    h1, h2, h3, h4, h5, h6, p, span, div, label { color: #e2e8f0 !important; }
    div[data-testid="stExpander"] { background-color: #1e293b !important; border-color: #334155 !important; }
    div[data-testid="stForm"] { background-color: #1e293b !important; border-color: #334155 !important; }
    input { background-color: #334155 !important; color: white !important; border-color: #475569 !important; }
    hr { border-color: #334155 !important; }
    </style>
""", unsafe_allow_html=True)

# --- LOGIN DE SEGURIDAD PARA TI ---
if "super_admin_ok" not in st.session_state:
    st.session_state.super_admin_ok = False

if not st.session_state.super_admin_ok:
    st.markdown("<h1 style='text-align: center; margin-top:50px;'>👑 Nítido App Studio<br><span style='font-size: 20px; color: #94a3b8 !important;'>Portal Exclusivo de Dirección</span></h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        clave_maestra = st.text_input("Clave de Acceso Gerencial", type="password")
        if st.button("Verificar Identidad", use_container_width=True):
            if clave_maestra == "nitido2026": 
                st.session_state.super_admin_ok = True
                st.rerun()
            else:
                st.error("Acceso Denegado.")
    st.stop()

# --- ENCABEZADO Y CERRAR SESIÓN ---
col_titulo, col_logout = st.columns([4, 1])
with col_titulo:
    st.title("👑 Central de Operaciones")
    st.write("Bienvenida. Desde aquí das de alta a los locales y administras sus enlaces.")
with col_logout:
    st.write("")
    # Usamos type="primary" para que el botón resalte más (por defecto en el tema oscuro será llamativo)
    if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary"):
        st.session_state.super_admin_ok = False
        st.rerun()

# --- PANEL DE CONTROL DE CLIENTES ---
tab1, tab2 = st.tabs(["👥 Locales Activos", "➕ Alta de Nuevo Cliente"])

with tab2:
    st.subheader("Crear un nuevo local y usuario de acceso")
    st.info("Al completar este formulario, el cliente ya podrá iniciar sesión en admin.nitido.app con el correo y contraseña que le asignes aquí.")
    
    with st.form("nuevo_cliente", clear_on_submit=True):
        email = st.text_input("Correo electrónico del cliente (Login)")
        password = st.text_input("Contraseña temporal (Ej: clave1234)")
        st.divider()
        nombre_marca = st.text_input("Nombre comercial de la marca (Ej: Ropa de Juan)")
        slug = st.text_input("Enlace único web (Ej: ropa-juan) - Usa solo minúsculas y guiones, sin espacios")
        
        if st.form_submit_button("Dar de alta cliente", type="primary"):
            if email and password and nombre_marca and slug:
                try:
                    nuevo_user = supabase.auth.admin.create_user({
                        "email": email, "password": password, "email_confirm": True
                    })
                    nuevo_comercio = {
                        "email_dueno": email, "nombre_marca": nombre_marca, "slug": slug,
                        "numero_whatsapp": "", "color_principal": "#333333", "categorias": ["General"]
                    }
                    supabase.table('comercios').insert(nuevo_comercio).execute()
                    st.success(f"¡Éxito! El local '{nombre_marca}' fue creado. Su link será: /?tienda={slug}")
                except Exception as e:
                    st.error(f"Ocurrió un error (verifica que el correo o slug no existan ya): {e}")
            else:
                st.warning("Completa todos los campos para continuar.")

with tab1:
    st.subheader("Directorio de Comercios")
    comercios = supabase.table('comercios').select('*').order('id', desc=False).execute()
    
    if comercios.data:
        for c in comercios.data:
            with st.expander(f"🏪 {c['nombre_marca']} (Link: /?tienda={c['slug']})"):
                st.write(f"**Email de acceso (Dueño):** {c.get('email_dueno', 'No asignado')}")
                st.write(f"**Color de la marca:** {c.get('color_principal', 'No asignado')}")
                st.write(f"**WhatsApp:** {c.get('numero_whatsapp', 'No configurado')}")
                
                st.divider()
                st.write("🔑 **Gestión de Contraseñas:**")
                st.caption("Por seguridad informática internacional, las contraseñas están encriptadas de forma irreversible.")
                st.info(f"Si el cliente olvida su clave, ve a tu panel de **Supabase > Authentication > Users**, busca el correo '{c.get('email_dueno', '...')} ' y presiona los tres puntitos para seleccionar **'Reset Password'**.")
    else:
        st.write("Aún no tienes clientes registrados.")