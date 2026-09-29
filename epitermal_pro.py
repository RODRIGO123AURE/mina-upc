import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ==========================================
# 1. CONFIGURACIÓN DEL ENTORNO SCADA MINERO
# ==========================================
st.set_page_config(
    page_title="Centro de Control SCADA - Sur Andino",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .stApp {background-color: #0b0f19;}
    .main-title {color: #00E5FF; font-size: 2.2rem; font-weight: 900; text-align: center; font-family: 'Courier New', monospace; letter-spacing: 2px;}
    .sub-title {color: #90A4AE; font-size: 1rem; text-align: center; margin-bottom: 2rem;}
    .kpi-card {background: linear-gradient(145deg, #131c2d, #1a253a); border: 1px solid #263238; border-radius: 8px; padding: 15px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.5);}
    .kpi-value {color: #00E676; font-size: 1.8rem; font-weight: 800; font-family: 'Courier New', monospace; margin:0;}
    .kpi-label {color: #B0BEC5; font-size: 0.75rem; text-transform: uppercase; font-weight: bold; margin:0;}
    .section-box {background-color: #131c2d; padding: 20px; border-radius: 8px; border: 1px solid #263238; margin-top: 20px;}
    </style>
""", unsafe_allow_html=True)

st.markdown('<p class="main-title">CENTRO DE CONTROL SCADA & GEMELO DIGITAL 3D</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Yacimiento Manto Epitermal "Sur Andino" | UPC - Gestión Minera (Grupo 3)</p>', unsafe_allow_html=True)

# ==========================================
# 2. PANEL DE CONTROL (BARRAS DESLIZANTES)
# ==========================================
with st.sidebar:
    st.markdown("### 🎛️ PANEL SCADA OPERATIVO")
    
    st.markdown("#### 💰 Economía y Costos")
    precio_au = st.slider("Precio del Oro (USD/oz)", 1500.0, 3000.0, 2300.0, 25.0)
    opex_total = st.slider("Costo Operativo OPEX (USD/t)", 40.0, 120.0, 72.0, 1.0)
    
    st.markdown("#### ⛰️ Geología y Geomecánica")
    ley_insitu = st.slider("Ley In Situ (g/t Au)", 1.0, 10.0, 3.8, 0.1)
    potencia = st.slider("Potencia del Manto (m)", 2.0, 8.0, 4.0, 0.5)
    rmr_roca = st.slider("Calidad Macizo Rocoso (RMR)", 20, 85, 60, 5)
    
    st.markdown("#### 💧 Sistema Hídrico (Bombeo)")
    caudal_infiltracion = st.slider("Infiltración de Agua (m³/h)", 10.0, 150.0, 50.0, 5.0)
    capacidad_bomba = st.slider("Capacidad de Bombeo (m³/h)", 10.0, 200.0, 75.0, 5.0)
    
    st.markdown("#### 🌬️ Ventilación y Gases (CO2)")
    horas_ventilacion = st.slider("Tiempo de Ventilación (Horas/día)", 2.0, 24.0, 12.0, 1.0)
    maquinaria_activa = st.slider("Flota LHD / Camiones Operando", 1, 10, 4, 1)

# ==========================================
# 3. MOTOR DE CÁLCULO TÉCNICO E HÍDRICO
# ==========================================
REC_MET = 0.88
DENS_MINERAL = 2.75
DENS_ESTERIL = 2.60

sobre_rotura = max(0.1, 1.2 - (rmr_roca / 100))
precio_efectivo = (precio_au / 31.1034) * REC_MET
cut_off = opex_total / precio_efectivo if precio_efectivo > 0 else 0

masa_mineral = potencia * DENS_MINERAL
masa_esteril = sobre_rotura * DENS_ESTERIL
dilucion = (masa_esteril / masa_mineral) * 100
ley_cabeza = (masa_mineral * ley_insitu) / (masa_mineral + masa_esteril)

area_total = (5.0 + 4.0)**2
rec_minera = (1 - ((4.0**2) / area_total)) * 100
esfuerzo_pilar = (DENS_ESTERIL * 200 * 9.81 / 1000) / (rec_minera/100)

nivel_agua_acumulado = max(0.0, (caudal_infiltracion - capacidad_bomba) * 2.5) if caudal_infiltracion > capacidad_bomba else 0.0
co2_ppm = 800 + (maquinaria_activa * 350) / (horas_ventilacion / 12.0)
alerta_co2 = co2_ppm > 2500

precios_simulados = np.random.normal(precio_au, precio_au*0.15, 1000)
precios_efectivos_sim = (precios_simulados / 31.1034) * REC_MET
cutoffs_simulados = opex_total / precios_efectivos_sim
prob_exito = np.sum(ley_cabeza > cutoffs_simulados) / 1000 * 100

# ==========================================
# 4. RENDERIZADO 3D ESTILO DISEÑO MINERO (BASADO EN IMAGEN)
# ==========================================
def renderizar_modelo_minero_realista():
    fig = go.Figure()

    # 1. Rampas en Espiral Principales (Tonos amarillo/naranja como en la referencia)
    theta = np.linspace(0, 6 * np.pi, 150)
    spiral_x = 25 + 15 * np.cos(theta)
    spiral_y = 25 + 15 * np.sin(theta)
    spiral_z = 5 - (theta * 2.2)
    fig.add_trace(go.Scatter3d(
        x=spiral_x, y=spiral_y, z=spiral_z,
        mode='lines',
        line=dict(color='#FFA726', width=5),
        name='Rampa Principal en Espiral (Acceso LHD)'
    ))

    # 2. Niveles Subterráneos Apilados (Múltiples niveles horizontales en azul)
    niveles_z = [-5, -12, -19, -26, -33, -40]
    for idx, z_lvl in enumerate(niveles_z):
        t_lvl = np.linspace(0, 2 * np.pi, 40)
        lx = 25 + (12 - idx*1.5) * np.cos(t_lvl)
        ly = 25 + (12 - idx*1.5) * np.sin(t_lvl)
        lz = np.full_like(lx, z_lvl)
        fig.add_trace(go.Scatter3d(
            x=lx, y=ly, z=lz,
            mode='lines',
            line=dict(color='#29B6F6', width=4),
            name=f'Nivel de Explotación Subterráneo {idx+1}' if idx == 0 else ''
        ))

    # 3. Chimeneas Verticales de Ventilación y Servicios (Líneas verdes)
    for px, py in [(18, 18), (32, 32), (18, 32)]:
        fig.add_trace(go.Scatter3d(
            x=[px, px], y=[py, py], z=[10, -45],
            mode='lines',
            line=dict(color='#66BB6A', width=6),
            name='Chimenea / Raise de Ventilación' if px == 18 and py == 18 else ''
        ))

    # 4. Botaderos y Planta en Superficie (Bloques superiores)
    # Botadero Norte (Celeste)
    bx = np.array([5, 15, 15, 5, 5])
    by = np.array([35, 35, 45, 45, 35])
    bz = np.array([15, 15, 22, 22, 15])
    fig.add_trace(go.Scatter3d(x=bx, y=by, z=bz, mode='lines', line=dict(color='#26A69A', width=4), name='Botadero Norte (Desmonte)'))

    # Planta de Procesamiento (Verde claro)
    px_planta = np.array([38, 45, 45, 38, 38])
    py_planta = np.array([25, 25, 32, 32, 25])
    pz_planta = np.array([12, 12, 18, 18, 12])
    fig.add_trace(go.Scatter3d(x=px_planta, y=py_planta, z=pz_planta, mode='lines', line=dict(color='#D4E157', width=5), name='Planta de Procesamiento'))

    # 5. Espejo de Agua en el Sumidero (Fondo de mina)
    water_z = -42 + (nivel_agua_acumulado * 0.05)
    wx = np.linspace(15, 35, 10)
    wy = np.linspace(15, 35, 10)
    WX, WY = np.meshgrid(wx, wy)
    WZ = np.full_like(WX, water_z)
    fig.add_trace(go.Surface(
        x=WX, y=WY, z=WZ,
        colorscale='Blues', opacity=0.85,
        name='Acumulación de Agua (Sumidero)', showscale=False
    ))

    # 6. Equipos Activos en el Modelo 3D (Bombas, Ventiladores, Camiones)
    fig.add_trace(go.Scatter3d(
        x=[25, 25, 18, 30], y=[25, 25, 18, 28], z=[-20, -43, 8, -25],
        mode='markers+text',
        marker=dict(size=12, color=['#FFA726', '#29B6F6', '#66BB6A', '#FF3D00' if alerta_co2 else '#66BB6A']),
        text=[f'Flota LHD ({maquinaria_activa} Unid.)', 'Bomba de Extracción', 'Ventilador Principal', f'Sensor CO2 ({co2_ppm:.0f} ppm)'],
        textposition='top center',
        textfont=dict(color='white', size=11),
        hovertemplate="Sistema SCADA: %{text}<extra></extra>"
    ))

    fig.update_layout(
        scene=dict(
            xaxis=dict(title='Este (X - m)', showbackground=True, backgroundcolor='#0b0f19', gridcolor='#1f293d'),
            yaxis=dict(title='Norte (Y - m)', showbackground=True, backgroundcolor='#0b0f19', gridcolor='#1f293d'),
            zaxis=dict(title='Elevación (Z - msnm)', showbackground=True, backgroundcolor='#0b0f19', gridcolor='#1f293d'),
            camera=dict(eye=dict(x=1.7, y=-1.7, z=1.2)),
            bgcolor='#0b0f19'
        ),
        margin=dict(l=0, r=0, b=0, t=0),
        height=620,
        paper_bgcolor='#0b0f19',
        showlegend=True
    )
    return fig

# ==========================================
# 5. KPIS SUPERIORES DE CONTROL SCADA
# ==========================================
c1, c2, c3, c4 = st.columns(4)
color_ley = "#00E676" if ley_cabeza >= cut_off else "#FF3D00"
color_agua = "#00E676" if nivel_agua_acumulado == 0 else "#FF3D00"
color_gas = "#FF3D00" if alerta_co2 else "#00E676"

c1.markdown(f'<div class="kpi-card"><p class="kpi-label">Cut-Off / Ley Cabeza</p><p class="kpi-value">{cut_off:.2f} / {ley_cabeza:.2f}</p></div>', unsafe_allow_html=True)
c2.markdown(f'<div class="kpi-card"><p class="kpi-label">Nivel de Agua (Sumidero)</p><p class="kpi-value" style="color:{color_agua}">{nivel_agua_acumulado:.1f} m</p></div>', unsafe_allow_html=True)
c3.markdown(f'<div class="kpi-card"><p class="kpi-label">Concentración CO2</p><p class="kpi-value" style="color:{color_gas}">{co2_ppm:.0f} ppm</p></div>', unsafe_allow_html=True)
c4.markdown(f'<div class="kpi-card"><p class="kpi-label">Prob. Éxito Financiero</p><p class="kpi-value">{prob_exito:.1f}%</p></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ==========================================
# 6. VISTA PRINCIPAL (3D + ASISTENTE IA)
# ==========================================
col_3d, col_ai = st.columns([7, 3])

with col_3d:
    st.plotly_chart(renderizar_modelo_minero_realista(), use_container_width=True)

with col_ai:
    st.markdown("<h3 style='color: #00E5FF;'>🤖 Diagnóstico SCADA en Línea</h3>", unsafe_allow_html=True)
    
    if alerta_co2:
        st.error(f"⚠️ **¡PELIGRO DE GASES!** Concentración de CO2 en {co2_ppm:.0f} ppm. Riesgo tóxico alto. Aumente las horas de ventilación.")
    else:
        st.success(f"✅ **Ambiente Seguro:** Ventilación óptima ({co2_ppm:.0f} ppm).")
        
    if nivel_agua_acumulado > 0:
        st.warning(f"💧 **Alerta Hídrica:** Acumulación de agua en el sumidero ({nivel_agua_acumulado:.1f}m). Incremente la capacidad de la bomba.")
    else:
        st.success("✅ **Sistema Hídrico Controlado:** Sin riesgo de inundación en niveles inferiores.")

    st.markdown("---")
    pregunta_usuario = st.selectbox(
        "Consulta operativa al sistema IA:",
        [
            "¿Es seguro el ingreso de personal a mina?",
            "¿El sistema de bombeo es suficiente?",
            "¿Se aprueba la viabilidad económica actual?",
            "Recomendación general de optimización"
        ]
    )
    
    if "personal" in pregunta_usuario:
        if alerta_co2:
            st.error("Riesgo crítico: No autorizar ingreso hasta mitigar los niveles de CO2 con los ventiladores.")
        else:
            st.success("Personal autorizado: Condiciones atmosféricas y operativas estables.")
    elif "bombeo" in pregunta_usuario:
        st.info(f"Caudal de infiltración: {caudal_infiltracion} m³/h vs Bombeo: {capacidad_bomba} m³/h.")
    elif "viabilidad" in pregunta_usuario:
        st.success(f"Proyecto viable con un margen financiero positivo y {prob_exito:.1f}% de éxito estocástico.")
    else:
        st.success("Mantener un equilibrio entre las horas de ventilación y el régimen de extracción de mineral.")

    st.markdown("---")
    df_export = pd.DataFrame({
        "Parámetro SCADA": ["Cut-Off", "Ley Cabeza", "Nivel Agua", "Concentración CO2", "Éxito Financiero"],
        "Valor Actual": [f"{cut_off:.2f}", f"{ley_cabeza:.2f}", f"{nivel_agua_acumulado:.1f}m", f"{co2_ppm:.0f} ppm", f"{prob_exito:.1f}%"]
    })
    csv = df_export.to_csv(index=False).encode('utf-8')
    st.download_button(label="📥 Descargar Reporte SCADA (CSV)", data=csv, file_name='Reporte_SCADA_SurAndino.csv', mime='text/csv')

# ==========================================
# 7. ESTADÍSTICAS Y GRÁFICOS INFERIORES
# ==========================================
st.markdown("---")
st.markdown("<h2 style='color: #00E5FF; text-align: center;'>📈 ANÁLISIS ESTADÍSTICO Y MONITOREO AMBIENTAL</h2>", unsafe_allow_html=True)

stat_col1, stat_col2 = st.columns(2)

with stat_col1:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("#### 🌬️ Curva de Acumulación de CO2 vs Ventilación")
    st.caption("Efecto de las horas de operación de ventiladores sobre la calidad del aire interior.")
    
    horas_test = np.linspace(2, 24, 12)
    co2_test = 800 + (maquinaria_activa * 350) / (horas_test / 12.0)
    df_co2 = pd.DataFrame({"Horas Ventilación": horas_test, "CO2 (ppm)": co2_test})
    
    fig_co2 = px.line(df_co2, x="Horas Ventilación", y="CO2 (ppm)", markers=True, color_discrete_sequence=['#00E5FF'])
    fig_co2.add_hline(y=2500, line_dash="dash", line_color="red", annotation_text="Límite Máximo Permisible")
    fig_co2.update_layout(paper_bgcolor='#131c2d', plot_bgcolor='#131c2d', font=dict(color='white'), margin=dict(l=10, r=10, t=10, b=10), height=280)
    st.plotly_chart(fig_co2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with stat_col2:
    st.markdown("<div class='section-box'>", unsafe_allow_html=True)
    st.markdown("#### 💧 Balance Hídrico (Infiltración vs Extracción)")
    st.caption("Comparativa de caudales para prevenir inundación en labores subterráneas.")
    
    df_agua = pd.DataFrame({
        "Sistema Hídrico": ["Infiltración Natural", "Capacidad de Bombeo"],
        "Caudal (m³/h)": [caudal_infiltracion, capacidad_bomba]
    })
    fig_agua = px.bar(df_agua, x="Sistema Hídrico", y="Caudal (m³/h)", color="Sistema Hídrico", color_discrete_map={"Infiltración Natural": "#FF3D00", "Capacidad de Bombeo": "#00E5FF"})
    fig_agua.update_layout(paper_bgcolor='#131c2d', plot_bgcolor='#131c2d', font=dict(color='white'), showlegend=False, margin=dict(l=10, r=10, t=10, b=10), height=280)
    st.plotly_chart(fig_agua, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<hr style='border: 1px solid #263238;'><center style='color: #607D8B;'>Centro de Control SCADA Minero Inteligente | Presentación Final Grupo 3 - UPC</center>", unsafe_allow_html=True)