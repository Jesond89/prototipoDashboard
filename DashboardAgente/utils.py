"""
utils.py - Funciones auxiliares, configuración y constantes
"""
import re
import pandas as pd

# --- PALETA DE COLORES CORPORATIVOS ---
ALXEDO_COLORS = {
    'primary_blue': '#00A9E0',
    'secondary_orange': '#FF8C42',
    'dark_blue': '#003F5C',
    'light_blue': "#225E72",
    'success_green': "#4FBB7E",
    'warning_yellow': '#FFA500',
    'danger_red': '#FF6B6B',
    'neutral_gray': '#6C757D'
}

# --- CLASIFICACIÓN DE PRODUCTOS ALXEDO ---
CATEGORIAS_SUBCATEGORIAS = {
    "Gestión de Pedidos": {
        "Rastreo y Estatus": ["pedido", "rastrear", "estatus", "guia", "donde viene", "llegado", "seguimiento", "envio", "paquete"],
        "Modificación y Cancelación": ["cambiar", "modificar", "cancelar", "dirección", "devolver", "reembolso"],
        "Problemas con Pedido": ["incompleto", "dañado", "equivocado", "problema", "falta", "error", "mal estado"],
    },
    "Purificadores - Info General": {
        "Comparativa de Modelos": ["diferencia", "comparar", "cual elegir", "modelos", "tipos", "mejor", "versus", "vs"],
        "Beneficios y Características": ["beneficios", "ventajas", "por que comprar", "para que sirve", "ahorro", "salud", "caracteristicas", "especificaciones"],
    },
    "Purificador ALX1": {
        "Funcionalidad ALX1": ["alx1", "alta demanda", "conecta", "directo", "presion", "flujo continuo"],
        "App y Monitoreo": ["app", "aplicacion", "monitorear", "calidad", "consumo", "cartuchos", "notificaciones"],
        "Instalación ALX1": ["instalar alx1", "conexion", "toma de agua", "bajo tarja", "llave de paso"],
    },
    "Purificador ALX2": {
        "Funcionalidad ALX2": ["alx2", "portatil", "contenedor", "llenar", "6 litros", "tanque", "deposito"],
        "Agua Alcalina": ["alcalina", "ph", "alcalinidad", "minerales", "ionizada"],
        "Control de Temperatura": ["temperatura", "frio", "caliente", "4 grados", "100 grados"],
    },
    "Tecnología y Filtración": {
        "Osmosis Inversa": ["osmosis", "inversa", "ro", "membrana", "sales", "minerales disueltos"],
        "Cartuchos y Filtros": ["cartucho", "filtro", "sedimentos", "carbon", "vida util", "cambio", "repuesto"],
        "Calidad del Agua": ["purificada", "segura", "impurezas", "bacterias", "cloro", "sabor", "olor"],
    },
    "Mantenimiento y Soporte": {
        "Cambio de Filtros": ["cambiar filtro", "reemplazar cartucho", "mantenimiento", "cuando cambiar", "frecuencia"],
        "Instalación General": ["instalar", "instalacion", "bajo fregadero", "conexion", "plomero", "tutorial"],
        "Garantías y Soporte": ["garantia", "devolucion", "reparacion", "soporte", "servicio tecnico", "falla"],
    },
    "Interacciones Generales": {
        "Saludos y Cortesía": ["hola", "buenos dias", "buenas tardes", "gracias", "adios", "buenas noches"],
        "Consultas de Cuenta": ["mi cuenta", "contraseña", "datos personales", "perfil", "usuario", "registro"],
    },
    "Sin Clasificar": {
        "Otros": ["otros", "miscelaneos", "sin categoria"]
    }
}

# Palabras que se consideran saludos o interacciones básicas
SALUDOS_BASICOS = {
    "hola", "buenos dias", "buenas tardes", "buenas noches", "gracias", 
    "adios", "si", "no", "ok", "aja", "bien", "perfecto", "excelente",
    "de acuerdo", "entendido", "claro", "por favor", "disculpa"
}

# Palabras que se consideran ruido
PALABRAS_RUIDO = {
    "", "si", "no", "ok", "a", "e", "o", "de", "la", "el", 
    "mi", "que", "es", "un", "una", "los", "las", "y", "en", 
    "con", "para", "por"
}

def limpiar_texto(texto):
    """
    Limpia y normaliza texto.
    
    Args:
        texto: String a limpiar
        
    Returns:
        String limpio y normalizado
    """
    if not isinstance(texto, str):
        return ""
    texto = texto.lower().strip()
    texto = re.sub(r'[^\w\sáéíóúñü]', ' ', texto)
    texto = re.sub(r'\s+', ' ', texto).strip()
    return texto

def es_saludo_basico(texto):
    """
    Determina si un texto es un saludo básico.
    
    Args:
        texto: String a evaluar
        
    Returns:
        Boolean indicando si es saludo básico
    """
    texto_limpio = limpiar_texto(texto)
    palabras = set(texto_limpio.split())
    return len(palabras.intersection(SALUDOS_BASICOS)) > 0 and len(palabras) <= 3

def clasificar_consulta(row):
    """
    Clasificación simplificada por palabras clave.
    
    Args:
        row: Fila del dataframe con la consulta
        
    Returns:
        Tupla (categoria, subcategoria, confidence)
    """
    # Priorizar intent nativo si existe
    if 'intent_name' in row and pd.notna(row['intent_name']) and row['intent_name'] not in ['UNSPECIFIED', '', 'Default Welcome Intent']:
        intent = row['intent_name'].replace('_', ' ').title()
        return intent, "Por Intent", 0.9
    
    pregunta = row.get('pregunta_limpia', limpiar_texto(row['user_utterances']))
    mejor_match = None
    mejor_score = 0
    
    for categoria, subcategorias in CATEGORIAS_SUBCATEGORIAS.items():
        for subcategoria, keywords in subcategorias.items():
            matches = sum(1 for keyword in keywords if keyword in pregunta)
            if matches > 0:
                score = matches / len(keywords)
                if score > mejor_score:
                    mejor_score = score
                    mejor_match = (categoria, subcategoria, score)
    
    if mejor_match:
        return mejor_match[0], mejor_match[1], mejor_match[2]
    
    return "Sin Clasificar", "Otros", 0.0

def calcular_metricas_conversacion(df):
    """
    Calcula métricas básicas de conversación.
    
    Args:
        df: DataFrame con los datos de conversación
        
    Returns:
        Diccionario con métricas calculadas
    """
    if df.empty:
        return {}
    
    # Agrupar por conversación
    conversaciones = df.groupby('conversation_name').agg({
        'turn_position': 'max',
        'user_utterances': 'count'
    }).reset_index()
    conversaciones.columns = ['conversation_name', 'max_turnos', 'total_interacciones']
    
    # Detectar escalamientos si existe la columna
    escalamientos = 0
    if 'live_agent_handoff' in df.columns:
        escalamientos = df.groupby('conversation_name')['live_agent_handoff'].max().sum()
    
    # Detectar finalizaciones exitosas si existe la columna
    finalizaciones = 0
    if 'end_session_exit' in df.columns:
        finalizaciones = df.groupby('conversation_name')['end_session_exit'].max().sum()
    
    total_conversaciones = len(conversaciones)
    
    return {
        'total_conversaciones': total_conversaciones,
        'total_interacciones': len(df),
        'turnos_promedio': conversaciones['max_turnos'].mean(),
        'turnos_mediana': conversaciones['max_turnos'].median(),
        'escalamientos': escalamientos,
        'finalizaciones': finalizaciones,
        'conversaciones_largas': (conversaciones['max_turnos'] > 10).sum(),
        'conversaciones_df': conversaciones
    }

def get_custom_css():
    """
    Retorna el CSS personalizado para la aplicación.
    
    Returns:
        String con el CSS
    """
    return f"""
    <style>
        .stApp {{
            background: linear-gradient(180deg, {ALXEDO_COLORS['light_blue']} 0%, white 100%);
        }}
        
        /* Estilos para mejorar visibilidad del texto */
        div[data-testid="stDataFrameResizable"] {{
            background-color: white;
        }}
        
        /* Mejorar contraste en tablas */
        .dataframe {{
            background-color: white !important;
        }}
        
        .dataframe td, .dataframe th {{
            color: {ALXEDO_COLORS['dark_blue']} !important;
            background-color: white !important;
        }}
        
        /* Estilos generales */
        h1, h2, h3 {{ font-weight: 700; }}
        h1 {{ color: {ALXEDO_COLORS['dark_blue']}; border-bottom: 3px solid {ALXEDO_COLORS['primary_blue']}; padding-bottom: 10px; }}
        h2 {{ color: {ALXEDO_COLORS['dark_blue']}; }}
        h3 {{ color: {ALXEDO_COLORS['primary_blue']}; }}

        [data-testid="metric-container"] {{
            background-color: white; 
            border-left: 5px solid {ALXEDO_COLORS['primary_blue']};
            padding: 1rem; 
            border-radius: 8px; 
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        }}
        
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, {ALXEDO_COLORS['primary_blue']} 0%, {ALXEDO_COLORS['dark_blue']} 100%);
        }}
        
        [data-testid="stSidebar"] * {{
            color: white !important;
        }}

        .info-box {{
            background-color: white; 
            border-radius: 10px; 
            padding: 20px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05); 
            margin: 10px 0;
            color: {ALXEDO_COLORS['dark_blue']};
        }}
        
        /* Asegurar que el texto en plotly sea visible */
        .plotly text {{
            fill: {ALXEDO_COLORS['dark_blue']} !important;
        }}
    </style>
    """