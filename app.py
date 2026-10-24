import streamlit as st
from supabase import create_client, Client

st.set_page_config(page_title="Catálogo", page_icon="🛍️", layout="centered")

# --- OCULTAR MENÚ GLOBALMENTE ANTES DEL FRENO ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    </style>
""", unsafe_allow_html=True)
# ------------------------------------------------

SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# 1. IDENTIFICAR EL COMERCIO POR LA URL
if "tienda" in st.query_params:
    slug_comercio = st.query_params["tienda"]
else:
    st.error("💻 Bienvenida a Nítido App Studio. Por favor, asegúrate de ingresar al enlace completo de la tienda.")
    st.stop()

# 2. BUSCAR EL COMERCIO EN LA BASE DE DATOS
try:
    respuesta = supabase.table('comercios').select('*').eq('slug', slug_comercio).execute()
    if not respuesta.data:
        st.error(f"No encontramos ninguna tienda registrada con el nombre '{slug_comercio}'.")
        st.stop()
    comercio = respuesta.data[0]
except Exception as e:
    st.error("Error de conexión al cargar el catálogo.")
    st.stop()

# --- CONVERSOR DE COLOR A TRANSPARENTE ---
def color_transparente(hex_color, opacidad):
    hex_color = str(hex_color).strip().lstrip('#')
    if len(hex_color) == 6:
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return f"rgba({r}, {g}, {b}, {opacidad})"
    return f"rgba(150, 150, 150, {opacidad})"

# Aumentamos la intensidad del fondo (15%)
fondo_acuarela = color_transparente(comercio['color_principal'], 0.15) 
borde_tarjeta = color_transparente(comercio['color_principal'], 0.5)

# --- CSS MEJORADO ---
st.markdown(f"""
    <style>
    /* --- ELIMINACIÓN TOTAL DEL MENÚ LATERAL --- */
    [data-testid="collapsedControl"] {{ display: none !important; }}
    [data-testid="stSidebar"] {{ display: none !important; }}
    
    /* Fondo con más color */
    .stApp {{
        background-color: {fondo_acuarela} !important;
    }}
    /* Tarjetas de productos: fondo blanco fijo y bordes con color */
    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background-color: white !important;
        border-color: {borde_tarjeta} !important;
    }}
    /* Forzar el texto general a oscuro para que Streamlit no lo cambie */
    .stApp, div[data-testid="stMarkdownContainer"] p {{
        color: #222222 !important;
    }}
    .logo-redondo {{
        border-radius: 50%; width: 120px; height: 120px; object-fit: cover;
        border: 4px solid white; box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-top: -60px; position: relative; z-index: 1; display: block;
        margin-left: auto; margin-right: auto;
    }}
    .titulo-marca {{
        text-align: center; color: {comercio['color_principal']} !important;
        font-weight: 800; margin-top: 10px;
    }}
    .btn-comprar {{
        background-color: #25D366; color: white !important; padding: 10px 15px;
        border-radius: 8px; text-decoration: none; display: block;
        text-align: center; font-weight: bold; margin-top: 10px;
    }}
    div[data-testid="stPills"] label[data-selected="true"] {{
        background-color: {comercio['color_principal']} !important;
        color: white !important; border-color: {comercio['color_principal']} !important;
    }}
    div[data-testid="stPills"] label {{
        color: #222222 !important; background-color: white !important;
    }}
    #MainMenu, footer, header {{visibility: hidden;}}
    
    /* --- ESTILOS PARA EL NUEVO FOOTER DEL SAAS --- */
    .footer-saas {{
        text-align: center; padding: 25px 10px; margin-top: 50px;
        border-top: 1px solid rgba(0,0,0,0.05); color: #666; font-size: 0.85rem;
    }}
    .footer-saas strong {{ color: #333; }}
    </style>
""", unsafe_allow_html=True)

# --- PORTADA FIJA (Sin botón de ampliar) ---
if comercio.get('portada_url'):
    # Usamos HTML para que no aparezca el ícono de pantalla completa
    st.markdown(f"""
        <img src="{comercio['portada_url']}" style="width: 100%; height: 180px; object-fit: cover; border-radius: 0px 0px 15px 15px;">
    """, unsafe_allow_html=True)
else:
    st.markdown(f"<div style='height: 150px; background-color: {comercio['color_principal']}; opacity: 0.3; border-radius: 0px 0px 15px 15px;'></div>", unsafe_allow_html=True)

# --- LOGO Y TÍTULO ---
if comercio.get('logo_url'):
    st.markdown(f"<img src='{comercio['logo_url']}' class='logo-redondo'>", unsafe_allow_html=True)

st.markdown(f"<h1 class='titulo-marca'>{comercio['nombre_marca']}</h1>", unsafe_allow_html=True)
st.divider()

# --- FILTROS DE CATEGORÍAS ---
categorias = comercio.get('categorias', [])
if not categorias:
    categorias = ["General"]

categoria_seleccionada = st.pills("Filtrar por:", ["Todos"] + categorias, default="Todos")

# --- LISTA DE PRODUCTOS ---
if categoria_seleccionada == "Todos":
    productos = supabase.table('productos').select('*').eq('comercio_id', comercio['id']).order('fecha_creacion', desc=True).execute()
else:
    productos = supabase.table('productos').select('*').eq('comercio_id', comercio['id']).eq('categoria', categoria_seleccionada).order('fecha_creacion', desc=True).execute()

if productos.data:
    col1, col2 = st.columns(2)
    
    for i, p in enumerate(productos.data):
        col_actual = col1 if i % 2 == 0 else col2
        
        with col_actual:
            with st.container(border=True):
                # Foto de grilla sin botón de ampliar (fija y cuadrada a nivel visual)
                if p['imagen_url']:
                    st.markdown(f"""
                        <img src="{p['imagen_url']}" style="width: 100%; height: 200px; object-fit: cover; border-radius: 8px; margin-bottom: 10px; pointer-events: none;">
                    """, unsafe_allow_html=True)
                
                st.markdown(f"**{p['nombre']}**")
                st.write(f"${p['precio']}")
                
                # Desplegable para ver la foto gigante
                with st.expander("🔍 Ver foto completa"):
                    if p['imagen_url']:
                        st.image(p['imagen_url']) 
                    if p['descripcion']:
                        st.write(f"*{p['descripcion']}*")
                
                mensaje_wa = f"Hola, quiero comprar: {p['nombre']} (${p['precio']})"
                link_wa = f"https://wa.me/{comercio['numero_whatsapp']}?text={mensaje_wa.replace(' ', '%20')}"
                st.markdown(f"<a href='{link_wa}' target='_blank' class='btn-comprar'>📲 Pedir</a>", unsafe_allow_html=True)
else:
    st.info("No hay productos en esta categoría por ahora.")
# ==========================================
# FOOTER DE MARCA (NÍTIDO APP STUDIO)
# ==========================================
st.markdown("""
    <div class="footer-saas">
        Catálogo digital potenciado por <strong>💻 Nítido App Studio</strong><br>
        Soluciones SaaS para comercios
    </div>
""", unsafe_allow_html=True)
