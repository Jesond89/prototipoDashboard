"""
data_loader.py - Funciones para carga y procesamiento de datos
"""
import pandas as pd
import streamlit as st
from utils import (
    limpiar_texto, 
    clasificar_consulta, 
    PALABRAS_RUIDO
)

@st.cache_data(ttl=3600)
def cargar_y_procesar_datos(uploaded_file):
    """
    Carga y procesa datos de forma optimizada.
    
    Args:
        uploaded_file: Archivo cargado desde Streamlit
        
    Returns:
        Tupla (df_original, df_limpio) con los datos procesados
    """
    try:
        df = pd.read_csv(uploaded_file, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(uploaded_file, encoding='latin-1')
    
    # Verificar columnas mínimas requeridas
    columnas_requeridas = ['user_utterances', 'conversation_name', 'turn_position']
    columnas_faltantes = [col for col in columnas_requeridas if col not in df.columns]
    
    if columnas_faltantes:
        st.error(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
        st.stop()
    
    # Limpiar datos
    df['pregunta_limpia'] = df['user_utterances'].apply(limpiar_texto)
    
    # Filtrar ruido
    df_limpio = df[
        ~df['pregunta_limpia'].isin(PALABRAS_RUIDO) & 
        (df['pregunta_limpia'].str.len() > 2)
    ].copy()
    
    # Clasificar
    clasificacion = df_limpio.apply(clasificar_consulta, axis=1)
    df_limpio[['categoria', 'subcategoria', 'confidence']] = pd.DataFrame(
        clasificacion.tolist(), index=df_limpio.index
    )
    
    return df, df_limpio

def aplicar_filtros(df, categoria='Todas', subcategoria='Todas', turnos_min=1):
    """
    Aplica filtros al DataFrame.
    
    Args:
        df: DataFrame original
        categoria: Categoría seleccionada
        subcategoria: Subcategoría seleccionada
        turnos_min: Número mínimo de turnos
        
    Returns:
        DataFrame filtrado
    """
    df_filtrado = df.copy()
    
    if categoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['categoria'] == categoria]
    
    if subcategoria != 'Todas':
        df_filtrado = df_filtrado[df_filtrado['subcategoria'] == subcategoria]
    
    # Filtrar por turnos mínimos (a nivel de conversación)
    conversaciones_validas = df.groupby('conversation_name')['turn_position'].max()
    conversaciones_validas = conversaciones_validas[conversaciones_validas >= turnos_min].index
    df_filtrado = df_filtrado[df_filtrado['conversation_name'].isin(conversaciones_validas)]
    
    return df_filtrado

def preparar_datos_descarga(df):
    """
    Prepara los datos para descarga en formato CSV.
    
    Args:
        df: DataFrame a preparar
        
    Returns:
        Bytes del CSV codificado
    """
    return df.to_csv(index=False).encode('utf-8')

def obtener_top_preguntas(df, n=15, filtrar_saludos=True):
    """
    Obtiene las preguntas más frecuentes.
    
    Args:
        df: DataFrame con los datos
        n: Número de preguntas a retornar
        filtrar_saludos: Si se deben filtrar saludos básicos
        
    Returns:
        DataFrame con las top preguntas y sus frecuencias
    """
    from utils import es_saludo_basico
    
    df_faqs = df.copy()
    
    # Filtrar saludos básicos si se requiere
    if filtrar_saludos:
        df_faqs = df_faqs[~df_faqs['pregunta_limpia'].apply(es_saludo_basico)]
        # Filtrar también por categoría para excluir interacciones generales
        df_faqs = df_faqs[df_faqs['categoria'] != 'Interacciones Generales']
    
    top_questions = df_faqs['pregunta_limpia'].value_counts().head(n)
    
    if len(top_questions) > 0:
        df_display = pd.DataFrame({
            'Pregunta': top_questions.index,
            'Frecuencia': top_questions.values
        })
        df_display.index = range(1, len(df_display) + 1)
        return df_display
    
    return pd.DataFrame()