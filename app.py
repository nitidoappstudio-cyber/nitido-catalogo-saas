import streamlit as st
from supabase import create_client, Client
import urllib.parse

st.set_page_config(page_title="Catálogo", page_icon="🛍️", layout="centered")

# --- 1. CSS GLOBAL: OCULTAR MENÚ Y ARREGLAR MODO OSCURO ---
st.markdown("""
    <style>
    [data-testid="collapsedControl"] { display: none !important; }
    [data-testid="stSidebar"] { display: none !important; }
    
    /* Fuerza el texto de todos los botones de filtro a color blanco brillante */
    div[data-testid="stButton"] button p {
        color: #FFFFFF !important;
        font-weight: 600 !important;
    }
    
    /* Estilo del botón verde de WhatsApp individual */
    .btn-wa-individual {
        background-color: #25D366;
        color: white !important;
        text-align: center;
        padding: 8px;
        border-radius: 8px;
        text-decoration: none;
        display: block;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)
# ----------------------------------------------------------

# --- 2. INICIAR LA MEMORIA DEL CARRITO DE COMPRAS ---
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# --- 3. CREDENCIALES SEGURAS ---
SUPABASE_URL = st.secrets["SUPABASE_URL"]
SUPABASE_KEY = st.secrets["SUPABASE_KEY"]
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- 4. IDENTIFICAR COMERCIO POR LA URL ---
if "tienda" in st.query_params:
    slug_comercio = st.query_params["tienda"]
else:
    st.error("💻 Bienvenida a Nítido App Studio. Por favor, asegúrate de ingresar al enlace completo de la tienda.")
    st.stop()

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

# --- 5. INTERFAZ DEL CARRITO FLOTANTE (Se muestra solo si hay productos) ---
if st.session_state.carrito:
    with st.expander(f"🛒 Ver mi carrito ({len(st.session_state.carrito)} artículos)"):
        total = 0
        texto_pedido = f"Hola {comercio.get('nombre', 'tienda')}, quiero hacer el siguiente pedido:\n\n"
        
        for item in st.session_state.carrito:
            st.write(f"- {item['nombre']} (${item['precio']})")
            total += item['precio']
            texto_pedido += f"- {item['nombre']} (${item['precio']})\n"
            
        st.write(f"**Total a pagar: ${total}**")
        texto_pedido += f"\n*Total: ${total}*"
        
        # Enviar carrito completo
        numero_wa = comercio.get('whatsapp', '') # Asegúrate de que tu tabla comercios tenga esta columna
        url_wa_carrito = f"https://wa.me/{numero_wa}?text={urllib.parse.quote(texto_pedido)}"
        
        st.markdown(f'<a href="{url_wa_carrito}" target="_blank" class="btn-wa-individual">🟢 Enviar pedido completo</a>', unsafe_allow_html=True)
        
        if st.button("🗑️ Vaciar carrito"):
            st.session_state.carrito = []
            st.rerun()

st.divider()

# --- 6. MOSTRAR PRODUCTOS CON BOTONES HÍBRIDOS (Ejemplo de lógica) ---
try:
    # Asegúrate de que el nombre de tu tabla de productos y la columna de relación coincidan
    res_productos = supabase.table('productos').select('*').eq('comercio_id', comercio['id']).execute()
    productos = res_productos.data
except Exception as e:
    st.error("Aún no hay productos cargados.")
    productos = []

# Crear grilla de productos
columnas = st.columns(2)
for i, prod in enumerate(productos):
    with columnas[i % 2]:
        with st.container(border=True):
            if prod.get('imagen_url'):
                st.image(prod['imagen_url'], use_container_width=True)
            
            st.markdown(f"**{prod.get('nombre', 'Producto')}**")
            st.write(f"${prod.get('precio', 0)}")
            
            # BOTÓN 1: Carrito (Boutique de golosinas)
            if st.button("➕ Al carrito", key=f"add_{prod.get('id', i)}"):
                st.session_state.carrito.append({'nombre': prod.get('nombre'), 'precio': prod.get('precio')})
                st.toast(f"{prod.get('nombre')} agregado al carrito")
                st.rerun()
                
            # BOTÓN 2: Directo (Tienda de ropa)
            texto_directo = f"Hola, quiero comprar: {prod.get('nombre')} (${prod.get('precio')})"
            url_wa_directo = f"https://wa.me/{comercio.get('whatsapp', '')}?text={urllib.parse.quote(texto_directo)}"
            st.markdown(f'<a href="{url_wa_directo}" target="_blank" class="btn-wa-individual">Comprar ahora</a>', unsafe_allow_html=True)
   


