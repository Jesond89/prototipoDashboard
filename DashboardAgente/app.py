"""
app.py - Punto de entrada principal de la aplicación Streamlit
"""
import streamlit as st
import pandas as pd

# Importar módulos personalizados
from utils import (
    ALXEDO_COLORS,
    get_custom_css,
    calcular_metricas_conversacion
)
from data_loader import (
    cargar_y_procesar_datos,
    aplicar_filtros,
    preparar_datos_descarga,
    obtener_top_preguntas
)
from charts import (
    crear_histograma_duracion,
    crear_pie_distribucion_longitud,
    crear_barras_categorias,
    crear_treemap_subcategorias
)

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Alxedo - Centro de Análisis Conversacional",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💧"
)

# --- APLICAR CSS PERSONALIZADO ---
st.markdown(get_custom_css(), unsafe_allow_html=True)

# CSS adicional para mejorar el file uploader en el sidebar
st.markdown("""
<style>
    /* Solución específica para el file uploader en el sidebar */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 8px !important;
    }
    
    /* Todos los elementos dentro del dropzone */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] * {
        color: #003F5C !important;
    }
    
    /* El pequeño texto de instrucciones */
    [data-testid="stSidebar"] [data-testid="stFileUploaderDropzone"] small {
        color: #6C757D !important;
        opacity: 1 !important;
    }
    
    /* Botón Browse files mejorado */
    [data-testid="stSidebar"] button[kind="secondary"] {
        background-color: #00A9E0 !important;
        color: white !important;
        border: none !important;
    }
    
    [data-testid="stSidebar"] button[kind="secondary"]:hover {
        background-color: #FF8C42 !important;
    }
    
    /* Para el texto "Drag and drop file here" */
    [data-testid="stSidebar"] .uploadedFileName {
        color: #003F5C !important;
    }
</style>
""", unsafe_allow_html=True)

# --- FUNCIONES DE RENDERIZADO ---

def render_header():
    """Renderiza el header de la aplicación."""
    col1, col2 = st.columns([1, 5])
    with col2:
        st.title("Centro de Análisis Conversacional")
        st.markdown("**Alxedo** - _Purificadores de Agua Inteligentes_")
    st.markdown("---")

def render_metricas_principales(df, metricas):
    """
    Muestra métricas principales del agente.
    
    Args:
        df: DataFrame con los datos originales
        metricas: Diccionario con métricas calculadas
    """
    st.header("📊 Métricas Principales")
    
    if not metricas:
        st.warning("No se pudieron calcular las métricas.")
        return
    
    # KPIs principales
    cols = st.columns(4)
    cols[0].metric("Conversaciones", f"{metricas['total_conversaciones']:,}")
    cols[1].metric("Interacciones", f"{metricas['total_interacciones']:,}")
    cols[2].metric("Turnos Promedio", f"{metricas['turnos_promedio']:.1f}")
    cols[3].metric("Conversaciones Largas (>10)", metricas['conversaciones_largas'])
    
    # Visualizaciones
    st.subheader("📊 Visualizaciones")
    cols = st.columns(2)
    
    with cols[0]:
        fig = crear_histograma_duracion(
            metricas['conversaciones_df'], 
            metricas['turnos_promedio']
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        fig = crear_pie_distribucion_longitud(metricas['conversaciones_df'])
        st.plotly_chart(fig, use_container_width=True)

def render_analisis_categorias(df):
    """
    Análisis de categorías y temas.
    
    Args:
        df: DataFrame con datos clasificados
    """
    st.header("📝 Análisis de Categorías")
    
    if 'categoria' not in df.columns:
        st.warning("No se encontraron datos de clasificación.")
        return
    
    cols = st.columns([3, 2])
    
    with cols[0]:
        fig = crear_barras_categorias(df)
        st.plotly_chart(fig, use_container_width=True)
    
    with cols[1]:
        fig = crear_treemap_subcategorias(df)
        st.plotly_chart(fig, use_container_width=True)
    
    # Top preguntas frecuentes
    st.subheader("🔍 Top 15 Preguntas Frecuentes (FAQs)")
    
    df_faqs = obtener_top_preguntas(df, n=15, filtrar_saludos=True)
    
    if not df_faqs.empty:
        st.dataframe(
            df_faqs,
            use_container_width=True,
            hide_index=False,
            column_config={
                "Pregunta": st.column_config.TextColumn(
                    "Pregunta",
                    width="large",
                ),
                "Frecuencia": st.column_config.NumberColumn(
                    "Frecuencia",
                    format="%d",
                    width="small",
                )
            }
        )
    else:
        st.info("No se encontraron preguntas frecuentes después de filtrar saludos.")

def render_exploracion_datos(df):
    """
    Exploración interactiva de datos.
    
    Args:
        df: DataFrame con los datos
    """
    st.header("🔍 Exploración de Datos")
    
    # Filtros
    cols = st.columns(3)
    
    # Filtro por categoría
    categorias_disponibles = ['Todas'] + sorted(df['categoria'].unique().tolist())
    categoria_seleccionada = cols[0].selectbox('Filtrar por Categoría', categorias_disponibles)
    
    # Filtro por subcategoría (dependiente de categoría)
    if categoria_seleccionada != 'Todas':
        subcategorias_disponibles = ['Todas'] + sorted(
            df[df['categoria'] == categoria_seleccionada]['subcategoria'].unique().tolist()
        )
        subcategoria_seleccionada = cols[1].selectbox('Filtrar por Subcategoría', subcategorias_disponibles)
    else:
        subcategoria_seleccionada = 'Todas'
    
    # Filtro por longitud de conversación
    turnos_min = cols[2].slider(
        'Turnos mínimos en conversación', 
        1, 
        int(df['turn_position'].max()), 
        1
    )
    
    # Aplicar filtros
    df_filtrado = aplicar_filtros(df, categoria_seleccionada, subcategoria_seleccionada, turnos_min)
    
    # Mostrar resultados
    st.write(f"**Mostrando {len(df_filtrado):,} de {len(df):,} interacciones**")
    
    # Tabla de datos con configuración mejorada
    columnas_mostrar = ['conversation_name', 'turn_position', 'user_utterances', 'categoria', 'subcategoria']
    df_display = df_filtrado[columnas_mostrar].copy()
    df_display.columns = ['Conversación', 'Turno', 'Mensaje del Usuario', 'Categoría', 'Subcategoría']
    
    # Mostrar dataframe
    st.dataframe(
        df_display,
        use_container_width=True,
        height=400,
        hide_index=True,
        column_config={
            "Conversación": st.column_config.TextColumn(
                "Conversación",
                width="small",
            ),
            "Turno": st.column_config.NumberColumn(
                "Turno",
                format="%d",
                width="small",
            ),
            "Mensaje del Usuario": st.column_config.TextColumn(
                "Mensaje del Usuario",
                width="large",
            ),
            "Categoría": st.column_config.TextColumn(
                "Categoría",
                width="medium",
            ),
            "Subcategoría": st.column_config.TextColumn(
                "Subcategoría",
                width="medium",
            )
        }
    )
    
    # Botón de descarga
    if not df_filtrado.empty:
        csv_data = preparar_datos_descarga(df_filtrado)
        st.download_button(
            "📥 Descargar datos filtrados (CSV)",
            csv_data,
            'analisis_alxedo_filtrado.csv',
            'text/csv'
        )

def render_info_inicial():
    """Información inicial cuando no hay archivo cargado."""
    st.info("⬆️ Por favor, carga un archivo CSV en la barra lateral para comenzar.")
    
    st.markdown("""
    <div class='info-box'>
        <h3>¿Qué hace este panel?</h3>
        <p>Este dashboard te permite analizar las conversaciones de tu agente conversacional de Alxedo.</p>
        <ul>
            <li><strong>Métricas Principales:</strong> Estadísticas clave sobre conversaciones e interacciones</li>
            <li><strong>Análisis de Categorías:</strong> Clasificación automática de consultas por temas</li>
            <li><strong>Exploración de Datos:</strong> Filtros interactivos para análisis detallado</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Renderiza la barra lateral."""
    st.sidebar.title("⚙️ Configuración")
    st.sidebar.markdown("Sube tu archivo CSV para empezar el análisis.")
    
    uploaded_file = st.sidebar.file_uploader(
        "**Selecciona un archivo CSV**", 
        type="csv",
        help="Columnas requeridas: user_utterances, conversation_name, turn_position"
    )
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📋 Requisitos del archivo
    
    El archivo CSV debe contener las siguientes columnas:
    - `user_utterances`: Mensajes del usuario
    - `conversation_name`: ID de la conversación
    - `turn_position`: Posición del turno
    
    ### 🔧 Columnas opcionales
    - `intent_name`: Intent detectado
    - `live_agent_handoff`: Escalamientos
    - `end_session_exit`: Finalizaciones
    """)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    ### 📊 Sobre Alxedo
    
    Dashboard de análisis conversacional para optimizar 
    la experiencia del cliente con nuestros purificadores 
    de agua inteligentes.
    
    **Versión:** 1.0.0  
    **Actualizado:** 2024
    """)
    
    return uploaded_file

# --- FUNCIÓN PRINCIPAL ---
def main():
    """Función principal de la aplicación."""
    
    # Renderizar header
    render_header()
    
    # Renderizar sidebar y obtener archivo
    uploaded_file = render_sidebar()
    
    if uploaded_file:
        try:
            # Cargar y procesar datos
            with st.spinner('Procesando archivo...'):
                df_original, df_limpio = cargar_y_procesar_datos(uploaded_file)
            
            if df_limpio.empty:
                st.error("El archivo no contiene datos válidos para analizar.")
                return
            
            st.success(f"✅ Archivo procesado: **{len(df_original):,}** interacciones analizadas")
            
            # Calcular métricas
            metricas = calcular_metricas_conversacion(df_original)
            
            # Crear pestañas
            tab1, tab2, tab3 = st.tabs([
                "📊 Métricas Principales", 
                "📝 Análisis de Categorías", 
                "🔍 Exploración"
            ])
            
            with tab1:
                render_metricas_principales(df_original, metricas)
            
            with tab2:
                render_analisis_categorias(df_limpio)
            
            with tab3:
                render_exploracion_datos(df_limpio)
        
        except Exception as e:
            st.error(f"Error al procesar el archivo: {str(e)}")
            st.info("Por favor, verifica que el archivo tenga el formato correcto.")
    
    else:
        render_info_inicial()

# --- PUNTO DE ENTRADA ---
if __name__ == "__main__":
    main()