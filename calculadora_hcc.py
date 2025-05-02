import streamlit as st
import math
import matplotlib.pyplot as plt
import pandas as pd

st.set_page_config(page_title="Calculadora HCC - Blanco", layout="wide")

# Encabezado
st.markdown("# Calculadora Integral de Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero*  ")
st.markdown("*Dr. Simmons David Gough Coto*  ")
st.markdown("*Médicos Radiólogos*  ")
st.markdown("*Fellowships de Radiología Intervencionista*  ")
st.markdown("*Instituto Nacional de Cancerología, Ciudad de México*  ")
st.markdown("*@radioresidentes_*  ")
st.markdown("**Con la colaboración de:**  ")
st.markdown("- González Rodríguez Andrea Paola  ")
st.markdown("- Sainz Castro Jessica  ")
st.markdown("- Meléndez Coral Rodrigo  ")
st.markdown("- Jorge Guerrero Ixtlahuac  ")
# Advertencia
st.warning("⚠️ Esta herramienta es de apoyo educativo y clínico. No reemplaza la valoración médica integral ni la toma de decisiones clínicas individualizadas.")

# Sidebar para parámetros
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

# Funciones de cálculo
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

def calcular_BCLC(size, num, perf):
    if (num == 1 and size <= 5) or (num <= 3 and size <= 3):
        return "Estadio A", "RFA o TACE"
    if size > 3 and perf == "bueno":
        return "Estadio B", "TACE"
    if perf == "malo":
        return "Estadio C", "Terapia dirigida"
    return "Estadio C", "Quimioterapia"

def calcular_Criterios_Milan(size, num):
    return (num == 1 and size <= 5) or (num <= 3 and size <= 3)

def calcular_Criterios_Toronto(size, num, afp):
    return size <= 6.5 and num <= 3 and afp <= 400 and not invasion

def calcular_Up7(size, num):
    return size + num <= 7

def calcular_UNOS(meld):
    return meld >= 15

def calcular_ART(b0, b1, resp):
    diff = b1 - b0
    pts = 1 if diff > 0 else 0
    pts += 2 if resp == "progresion" else 1 if resp == "estable" else 0
    return pts

def calcular_Okuda(size, asc, alb, bilir):
    pts = 1 if size > 50 else 0
    pts += 1 if asc != "ausente" else 0
    pts += 1 if alb < 3 else 0
    pts += 1 if bilir > 3 else 0
    return pts

def calcular_HKLC(perf, size, num, inv, met):
    if perf == "bueno" and num <= 3 and size <= 5 and not inv and not met:
        return "HKLC I"
    if perf == "bueno" and not met:
        return "HKLC II/III"
    if perf == "malo" and met:
        return "HKLC IV"
    return "HKLC III/IV"

# Cálculos y visualización
if st.button("Calcular"):
    ALBI = calcular_ALBI(bilirrubina, albumina)
    CP = calcular_ChildPugh(bilirrubina, albumina, INR, ascitis, encefalopatia)
    MELD = calcular_MELD(creatinina, bilirrubina, INR)
    MELD_Na = calcular_MELD_Na(MELD, sodio)
    BCLC, trat = calcular_BCLC(tamaño_tumor, número_tumores, estado_performance)
    milan = calcular_Criterios_Milan(tamaño_tumor, número_tumores)
    toronto = calcular_Criterios_Toronto(tamaño_tumor, número_tumores, AFP)
    up7 = calcular_Up7(tamaño_tumor, número_tumores)
    unos = calcular_UNOS(MELD)
    ART = calcular_ART(bilirrubina, bilirrubina_post, respuesta_tumoral)
    Ok = calcular_Okuda(tamaño_tumor, ascitis, albumina, bilirrubina)
    HKLC = calcular_HKLC(estado_performance, tamaño_tumor, número_tumores, invasion, metastasis)

    st.header("Resultados de las Escalas")
    st.write(f"- ALBI Score: {ALBI}")
    st.write(f"- Child-Pugh Score: {CP} (Clase {'A' if CP <= 6 else 'B' if CP <= 9 else 'C'})")
    st.write(f"- MELD Score: {MELD}")
    st.write(f"- MELD-Na Score: {MELD_Na}")
    st.write(f"- BCLC: {BCLC} → {trat}")
    st.write(f"- Criterios de Milán: {'✔️' if milan else '❌'}")
    st.write(f"- Criterios de Toronto: {'✔️' if toronto else '❌'}")
    st.write(f"- Up-to-7: {'✔️' if up7 else '❌'}")
    st.write(f"- Elegible UNOS: {'✔️' if unos else '❌'}")
    st.write(f"- ART Score: {ART}")
    st.write(f"- Okuda Score: {Ok}")
    st.write(f"- HKLC: {HKLC}")

    st.subheader("Comparación de Puntajes")
    df = pd.DataFrame({
        'Escala': ['ALBI', 'Child-Pugh', 'MELD', 'MELD-Na', 'ART', 'Okuda'],
        'Valor': [ALBI, CP, MELD, MELD_Na, ART, Ok]
    })
    fig, ax = plt.subplots()
    ax.barh(df['Escala'], df['Valor'], color='teal')
    ax.set_xlabel('Puntaje')
    ax.set_title('Comparación de Escalas')
    st.pyplot(fig)

# Footer
st.markdown("---")
