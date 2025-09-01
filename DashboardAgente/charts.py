"""
charts.py - Funciones para crear visualizaciones con Plotly
"""
import plotly.express as px
import plotly.graph_objects as go
from utils import ALXEDO_COLORS

def get_alxedo_layout(title, x_title="", y_title=""):
    """
    Layout base optimizado para gráficas Plotly con mejor visibilidad.
    
    Args:
        title: Título del gráfico
        x_title: Título del eje X
        y_title: Título del eje Y
        
    Returns:
        Layout de Plotly configurado
    """
    return go.Layout(
        title={
            'text': f'<b>{title}</b>', 
            'x': 0.5, 
            'font': {'size': 18, 'color': ALXEDO_COLORS['dark_blue']}
        },
        xaxis={
            'title': {'text': x_title, 'font': {'size': 14, 'color': ALXEDO_COLORS['dark_blue']}},
            'gridcolor': '#e0e0e0',
            'tickfont': {'size': 12, 'color': ALXEDO_COLORS['dark_blue']}
        },
        yaxis={
            'title': {'text': y_title, 'font': {'size': 14, 'color': ALXEDO_COLORS['dark_blue']}},
            'gridcolor': '#e0e0e0',
            'tickfont': {'size': 12, 'color': ALXEDO_COLORS['dark_blue']}
        },
        plot_bgcolor='white',
        paper_bgcolor='white',
        font={'family': "Arial, sans-serif", 'color': ALXEDO_COLORS['dark_blue'], 'size': 12},
        margin=dict(t=80, l=80, r=60, b=80),
        hoverlabel=dict(
            bgcolor="white",
            font_size=14,
            font_family="Arial"
        )
    )

def crear_histograma_duracion(conversaciones_df, turnos_promedio):
    """
    Crea histograma de duración de conversaciones.
    
    Args:
        conversaciones_df: DataFrame con datos de conversaciones
        turnos_promedio: Promedio de turnos
        
    Returns:
        Figura de Plotly
    """
    fig = px.histogram(
        conversaciones_df, 
        x='max_turnos', 
        nbins=15,
        labels={'max_turnos': 'Número de Turnos', 'count': 'Frecuencia'},
        color_discrete_sequence=[ALXEDO_COLORS['primary_blue']]
    )
    
    fig.add_vline(
        x=turnos_promedio, 
        line_dash="dash", 
        line_color=ALXEDO_COLORS['secondary_orange'],
        annotation_text=f"Promedio: {turnos_promedio:.1f}",
        annotation_position="top"
    )
    
    fig.update_layout(get_alxedo_layout("Duración de Conversaciones", "Número de Turnos", "Frecuencia"))
    fig.update_traces(hovertemplate='Turnos: %{x}<br>Frecuencia: %{y}<extra></extra>')
    
    return fig

def crear_pie_distribucion_longitud(conversaciones_df):
    """
    Crea gráfico de pie para distribución por longitud de conversaciones.
    
    Args:
        conversaciones_df: DataFrame con datos de conversaciones
        
    Returns:
        Figura de Plotly
    """
    bins = ['1-2 turnos', '3-5 turnos', '6-10 turnos', '11+ turnos']
    
    counts = [
        (conversaciones_df['max_turnos'] <= 2).sum(),
        ((conversaciones_df['max_turnos'] >= 3) & (conversaciones_df['max_turnos'] <= 5)).sum(),
        ((conversaciones_df['max_turnos'] >= 6) & (conversaciones_df['max_turnos'] <= 10)).sum(),
        (conversaciones_df['max_turnos'] > 10).sum()
    ]
    
    fig = px.pie(
        values=counts, 
        names=bins, 
        hole=0.4,
        color_discrete_sequence=[
            ALXEDO_COLORS['primary_blue'], 
            ALXEDO_COLORS['secondary_orange'], 
            ALXEDO_COLORS['success_green'], 
            ALXEDO_COLORS['warning_yellow']
        ]
    )
    
    fig.update_layout(get_alxedo_layout("Distribución por Longitud"))
    fig.update_traces(
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='%{label}<br>Cantidad: %{value}<br>Porcentaje: %{percent}<extra></extra>'
    )
    
    return fig

def crear_barras_categorias(df):
    """
    Crea gráfico de barras horizontales para categorías.
    
    Args:
        df: DataFrame con datos categorizados
        
    Returns:
        Figura de Plotly
    """
    categoria_counts = df['categoria'].value_counts()
    
    fig = px.bar(
        y=categoria_counts.index, 
        x=categoria_counts.values, 
        orientation='h',
        labels={'x': 'Número de Consultas', 'y': 'Categoría'},
        text=categoria_counts.values,
        color=categoria_counts.values,
        color_continuous_scale='Viridis'
    )
    
    fig.update_traces(
        texttemplate='%{text}',
        textposition='outside',
        hovertemplate='Categoría: %{y}<br>Consultas: %{x}<extra></extra>'
    )
    
    fig.update_layout(
        get_alxedo_layout("Consultas por Categoría", "Número de Consultas", "Categorías"),
        yaxis={'categoryorder': 'total ascending'},
        showlegend=False,
        coloraxis_showscale=False
    )
    
    return fig

def crear_treemap_subcategorias(df):
    """
    Crea treemap de subcategorías.
    
    Args:
        df: DataFrame con datos categorizados
        
    Returns:
        Figura de Plotly
    """
    df_subcat = df.groupby(['categoria', 'subcategoria']).size().reset_index(name='count')
    
    fig = px.treemap(
        df_subcat, 
        path=[px.Constant("Todas las Categorías"), 'categoria', 'subcategoria'], 
        values='count',
        color='count', 
        color_continuous_scale='Blues',
        hover_data={'count': ':,'}
    )
    
    fig.update_traces(
        textinfo="label+value",
        hovertemplate='<b>%{label}</b><br>Cantidad: %{value}<extra></extra>'
    )
    
    fig.update_layout(
        get_alxedo_layout("Distribución Detallada"), 
        margin=dict(t=50, l=10, r=10, b=10)
    )
    
    return fig