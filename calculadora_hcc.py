import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Calculadora HCC - Blanco", layout="wide")

# Encabezado
st.markdown("# Calculadora Integral de Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero*  ")
st.markdown("*Médico Radiólogo*  ")
st.markdown("*Fellowship de Radiología Intervencionista*  ")
st.markdown("*Instituto Nacional de Cancerología, Ciudad de México*  ")
st.markdown("*RESIDENTES DE RADIOLOGÍA INTERVENCIONISTA INCAN*  ")
st.markdown("**Con la colaboración de:**  ")
st.markdown("- González Rodríguez Andrea Paola  ")
st.markdown("- Sainz Castro Jessica  ")
st.markdown("- Meléndez Coral Rodrigo  ")
st.markdown("- Gough Coto Simmons David  ")
st.markdown("- Jorge Guerrero Ixtlahuac  ")
st.markdown("*@radioresidentes_*  ")
st.markdown("---")

st.warning("⚠️ Esta herramienta es de apoyo educativo y clínico. No reemplaza la valoración médica integral ni la toma de decisiones clínicas individualizadas.")

st.sidebar.header("📋 Parámetros Clínicos del Paciente")
bilirrubina = st.sidebar.number_input("Bilirrubina (mg/dL)", min_value=0.1, step=0.1)
albumina = st.sidebar.number_input("Albúmina (g/dL)", min_value=0.1, step=0.1)
INR = st.sidebar.number_input("INR", min_value=0.1, step=0.1)
ascitis = st.sidebar.selectbox("Ascitis", ["ausente", "leve", "severa"])
encefalopatia = st.sidebar.selectbox("Encefalopatía", [0, 1, 2])
creatinina = st.sidebar.number_input("Creatinina (mg/dL)", min_value=0.1, step=0.1)
sodio = st.sidebar.number_input("Sodio (mEq/L)", min_value=100.0, step=0.5)
tamaño_tumor = st.sidebar.number_input("Tamaño del tumor mayor (cm)", min_value=0.1, step=0.1)
número_tumores = st.sidebar.number_input("Número de tumores", min_value=1, step=1)
estado_performance = st.sidebar.selectbox("Estado funcional (ECOG)", ["bueno", "malo"])
AFP = st.sidebar.number_input("AFP (ng/mL)", min_value=0.0, step=1.0)
bilirrubina_post = st.sidebar.number_input("Bilirrubina post-TACE (mg/dL)", min_value=0.1, step=0.1)
respuesta_tumoral = st.sidebar.selectbox("Respuesta tumoral a TACE", ["respuesta", "estable", "progresion"])
invasion = st.sidebar.checkbox("Invasión vascular")
metastasis = st.sidebar.checkbox("Metástasis a distancia")

# Funciones

def calcular_ALBI(bilir, alb):
    bil_umol = bilir * 17.1
    return round(math.log10(bil_umol) - 0.085 * alb, 2)

def calcular_ChildPugh(bilir, alb, inr, asc, encef):
    score = 0
    score += 1 if bilir <= 2 else 2 if bilir <= 3 else 3
    score += 1 if alb >= 3.5 else 2 if alb >= 2.8 else 3
    score += 1 if inr <= 1.7 else 2 if inr <= 2.3 else 3
    score += {"ausente":1, "leve":2, "severa":3}[asc]
    score += {0:1, 1:2, 2:3}[encef]
    return score

def calcular_MELD(creat, bilir, inr):
    creat = min(max(creat, 1), 4)
    bilir = max(bilir, 1)
    inr = max(inr, 1)
    meld = 3.78 * math.log(bilir) + 11.2 * math.log(inr) + 9.57 * math.log(creat) + 6.43
    return round(meld)

def calcular_MELD_Na(meld, sod):
    sod = min(max(sod, 125), 137)
    meld_na = meld + 1.32 * (137 - sod) - 0.033 * meld * (137 - sod)
    return round(meld_na)

def calcular_BCLC(size, num, perf, inv, met):
    if perf == "malo" or inv or met:
        return "Estadio C", "Terapia sistémica / dirigida"
    if num == 1 and size <= 2:
        return "Estadio 0", "Resección, RFA o Trasplante"
    if (num == 1 and size <= 5) or (num <= 3 and size <= 3):
        return "Estadio A", "Resección, RFA o Trasplante"
    return "Estadio B", "TACE"

# Cálculo
if st.button("Calcular"):
    ALBI = calcular_ALBI(bilirrubina, albumina)
    CP = calcular_ChildPugh(bilirrubina, albumina, INR, ascitis, encefalopatia)
    MELD = calcular_MELD(creatinina, bilirrubina, INR)
    MELD_Na = calcular_MELD_Na(MELD, sodio)
    BCLC, trat = calcular_BCLC(tamaño_tumor, número_tumores, estado_performance, invasion, metastasis)

    st.header("Resultados")
    st.write(f"- ALBI Score: {ALBI}")
    with st.expander("Interpretación del ALBI"):
        st.markdown("""
        - **Grado 1**: ALBI ≤ -2.60  
        - **Grado 2**: -2.60 < ALBI ≤ -1.39  
        - **Grado 3**: ALBI > -1.39  
        """)

    st.write(f"- Child-Pugh: {CP} (Clase {'A' if CP <= 6 else 'B' if CP <= 9 else 'C'})")
    with st.expander("Interpretación del Child-Pugh"):
        st.markdown("""
        - **Clase A (5-6 puntos):** Buena función hepática, riesgo quirúrgico bajo.  
        - **Clase B (7-9 puntos):** Función intermedia, riesgo moderado.  
        - **Clase C (10-15 puntos):** Disfunción grave, contraindicación para cirugía o trasplante.  
        """)

    st.write(f"- MELD Score: {MELD}")
    with st.expander("Interpretación del MELD"):
        st.markdown("""
        - **Supervivencia a 1 año**: 90% en lista de espera vs 83% trasplantado.  
        - **En sepsis o PBE**: supervivencia a 3 meses ~90%.  
        - **En TIPS**: mortalidad 1 mes entre 5–25%.  
        - **MELD 10–19**: bajo riesgo (~90% 3 meses).  
        - **MELD >20**: riesgo significativo, considerar trasplante urgente.  
        """)

    st.write(f"- MELD-Na Score: {MELD_Na}")
    with st.expander("Interpretación del MELD-Na"):
        st.markdown("""
        - Ajusta el MELD incorporando el sodio, mejorando predicción de mortalidad.  
        - **Sodio bajo** se asocia a mayor riesgo de muerte en lista de espera.  
        - Se usa para priorización en trasplante.  
        """)

    st.write(f"- BCLC: {BCLC} → {trat}")
    with st.expander("Tabla de Clasificación BCLC actualizada"):
        st.markdown("""
        | Estadio | Características principales | Tratamiento recomendado |
        |---------|------------------------------|--------------------------|
        | **0** | Nódulo único ≤2 cm, ECOG 0, función hepática conservada | Resección, RFA o Trasplante |
        | **A** | Nódulo único ≤5 cm o ≤3 nódulos ≤3 cm, ECOG 0 | Resección, RFA o Trasplante |
        | **B** | Multinodular, sin invasión ni metástasis, ECOG 0 | TACE |
        | **C** | Invasión vascular o metástasis o ECOG 1–2 | Terapia sistémica |
        | **D** | ECOG >2 o Child-Pugh C sin opción a trasplante | Cuidados paliativos |
        """)

