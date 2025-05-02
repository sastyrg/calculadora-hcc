# Código completo actualizado con interpretaciones y enlaces

import streamlit as st
import math

st.set_page_config(page_title="Calculadora HCC", layout="wide")

st.markdown("# Calculadora Integral de Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero*  ")
st.markdown("*Dr. Simmons David Gough Coto ")
st.markdown("*Médicos Radiólogos - Fellowships en Radiología Intervencionista*  ")
st.markdown("*Instituto Nacional de Cancerología, Ciudad de México*  ")
st.markdown("**RESIDENTES DE RADIOLOGÍA INTERVENCIONISTA INCAN**")
st.markdown("- González Rodríguez Andrea Paola")
st.markdown("- Sainz Castro Jessica")
st.markdown("- Meléndez Coral Rodrigo")
st.markdown("- Guerrero Ixtlahuac Jorge")
st.markdown("*@radioresidentes_*")

st.markdown("---")

# Variables simuladas para demostración
bilirubina = 3.5
albumina = 2.9
inr = 2.1
ascitis = "leve"
encefalopatia = 1
creatinina = 1.2
sodio = 130
tamano_tumor = 60
respuesta_tumoral = "estable"
bilirrubina_post = 4.2
bilirrubina_pre = 3.5
invasion = True
metastasis = False
estado_performance = "bueno"
número_tumores = 4

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

# Cálculos
ALBI = calcular_ALBI(bilirubina, albumina)
CP = calcular_ChildPugh(bilirubina, albumina, inr, ascitis, encefalopatia)
MELD = calcular_MELD(creatinina, bilirubina, inr)
MELD_Na = calcular_MELD_Na(MELD, sodio)
BCLC, trat = calcular_BCLC(tamano_tumor, número_tumores, estado_performance, invasion, metastasis)

st.header("Resultados")
st.write(f"- ALBI Score: {ALBI}")
with st.expander("Interpretación del ALBI"):
    st.markdown("""
    - **Grado 1**: ALBI ≤ -2.60  
    - **Grado 2**: -2.60 < ALBI ≤ -1.39  
    - **Grado 3**: ALBI > -1.39  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/25723794/)
    """)

st.write(f"- Child-Pugh: {CP} (Clase {'A' if CP <= 6 else 'B' if CP <= 9 else 'C'})")
with st.expander("Interpretación del Child-Pugh"):
    st.markdown("""
    - **Clase A (5-6 puntos):** Buena función hepática.  
    - **Clase B (7-9):** Disfunción moderada.  
    - **Clase C (10-15):** Disfunción severa.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/4751248/)
    """)

st.write(f"- MELD Score: {MELD}")
with st.expander("Interpretación del MELD"):
    st.markdown("""
    - Predice mortalidad en enfermedad hepática avanzada.  
    - MELD > 15: indica necesidad de trasplante.  
    - Usado en asignación de órganos.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/11231926/)
    """)

st.write(f"- MELD-Na Score: {MELD_Na}")
with st.expander("Interpretación del MELD-Na"):
    st.markdown("""
    - Añade el sodio al MELD tradicional.  
    - Mejor predicción de mortalidad.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/18825644/)
    """)

st.write(f"- BCLC: {BCLC} → {trat}")
with st.expander("Interpretación del BCLC"):
    st.markdown("""
    - **0**: Tumor único ≤2 cm, ECOG 0.  
    - **A**: ≤3 tumores ≤3 cm o uno ≤5 cm.  
    - **B**: Multinodular.  
    - **C**: Invasión, metástasis o ECOG 1-2.  
    - **D**: Terminal.  
    [Ver fuente](https://www.journal-of-hepatology.eu/article/S0168-8278(22)00330-9/fulltext)
    """)

# OKUDA
okuda = 0
if tamano_tumor > 50: okuda += 1
if ascitis != "ausente": okuda += 1
if albumina < 3: okuda += 1
if bilirubina > 3: okuda += 1
st.write(f"- Okuda Score: {okuda}")
with st.expander("Interpretación del Okuda"):
    st.markdown("""
    - Estadio I: 0–1 puntos  
    - Estadio II: 2 puntos  
    - Estadio III: 3–4 puntos  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/2989237/)
    """)

# ART
art_score = 0
if bilirrubina_post - bilirrubina_pre > 0: art_score += 1
if respuesta_tumoral == "progresion": art_score += 2
elif respuesta_tumoral == "estable": art_score += 1
st.write(f"- ART Score: {art_score}")
with st.expander("Interpretación del ART"):
    st.markdown("""
    - 0–1 puntos: repetir TACE.  
    - ≥2 puntos: considerar sistémica.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/23355517/)
    """)

# HKLC
hklc = "III"
if estado_performance == "bueno" and número_tumores <= 3 and tamano_tumor <= 5 and not invasion and not metastasis:
    hklc = "I"
elif estado_performance == "bueno" and not metastasis:
    hklc = "II"
elif estado_performance == "malo" and metastasis:
    hklc = "IV"
st.write(f"- HKLC: {hklc}")
with st.expander("Interpretación del HKLC"):
    st.markdown("""
    - I–II: tratamientos curativos.  
    - III–IV: enfermedad avanzada.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/24613803/)
    """)

# CLIP
clip = 0
if bilirubina > 3: clip += 1
if albumina < 3.5: clip += 1
if ascitis != "ausente": clip += 1
if tamano_tumor > 50: clip += 1
st.write(f"- CLIP Score: {clip}")
with st.expander("Interpretación del CLIP"):
    st.markdown("""
    - 0–1: buen pronóstico.  
    - 2–3: intermedio.  
    - ≥4: mal pronóstico.  
    [Ver fuente](https://pubmed.ncbi.nlm.nih.gov/11090031/)
    """)
