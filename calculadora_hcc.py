import streamlit as st
import math

st.set_page_config(page_title="Calculadora HCC", layout="wide")

st.title("Calculadora Integral de Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero // Dr. Simmons David Gough Coto — Instituto Nacional de Cancerología, CDMX*")
st.markdown("**Colaboradores:** Drs: Jorge Guerrero Ixtlahuac, Andrea Paola González Rodríguez, Jessica Sainz Castro, Rodrigo Meléndez Coral")
st.markdown("*Instagram: @radioresidentes_*")
st.markdown("---")

st.markdown("🧭 **Propósito:** Esta herramienta es de apoyo educativo y clínico. No sustituye el juicio médico ni al comité multidisciplinario. Está diseñada para estimar función hepática y orientar la clasificación del HCC según guías internacionales.")
st.markdown("---")

st.subheader("📝 Ingreso de parámetros clínicos")
col1, col2 = st.columns(2)

with col1:
    bilirrubina = st.number_input("Bilirrubina (mg/dL)", min_value=0.1, value=1.5)
    INR = st.number_input("INR", min_value=0.5, value=1.2)
    creatinina = st.number_input("Creatinina (mg/dL)", min_value=0.1, value=1.0)
    ascitis = st.selectbox("Ascitis", ["ausente", "leve", "severa"])
    encefalopatia = st.selectbox("Encefalopatía", [0, 1, 2])
    albumina = st.number_input("Albúmina (g/dL)", min_value=0.5, value=3.5)

with col2:
    sodio = st.number_input("Sodio (mEq/L)", min_value=100.0, max_value=150.0, value=135.0)
    tamaño_tumor = st.number_input("Tamaño del tumor más grande (cm)", min_value=0.1, value=3.0)
    número_tumores = st.number_input("Número de tumores", min_value=1, value=1)
    estado_performance = st.selectbox("Estado funcional (ECOG)", [0, 1, 2, 3, 4])
    AFP = st.number_input("AFP (ng/mL)", min_value=0.0, value=20.0)
    invasion = st.checkbox("Invasión vascular")
    metastasis = st.checkbox("Metástasis a distancia")

respuesta_tumoral = st.selectbox("Respuesta tumoral a TACE", ["respuesta", "estable", "progresion"])
bilirrubina_post = st.number_input("Bilirrubina post-TACE (mg/dL)", min_value=0.1, value=1.6)

st.markdown("---")

# Funciones de cálculo
def calcular_ALBI(bilir, alb):
    return round(math.log10(bilir * 17.1) - 0.085 * alb, 2)

def calcular_ChildPugh(bilir, alb, inr, asc, encef):
    score = 0
    score += 1 if bilir <= 2 else 2 if bilir <= 3 else 3
    score += 1 if alb >= 3.5 else 2 if alb >= 2.8 else 3
    score += 1 if inr <= 1.7 else 2 if inr <= 2.3 else 3
    score += {"ausente": 1, "leve": 2, "severa": 3}[asc]
    score += {0: 1, 1: 2, 2: 3}[encef]
    return score

def calcular_MELD(creat, bilir, inr):
    creat = min(max(creat, 1), 4)
    bilir = max(bilir, 1)
    inr = max(inr, 1)
    return round(3.78 * math.log(bilir) + 11.2 * math.log(inr) + 9.57 * math.log(creat) + 6.43)

def calcular_MELD_Na(meld, sod):
    sod = min(max(sod, 125), 137)
    return round(meld + 1.32 * (137 - sod) - 0.033 * meld * (137 - sod))

def calcular_BCLC(size, num, perf, inv, met):
    if perf > 2 or inv or met:
        return "Estadio C", "Terapia sistémica / dirigida"
    if num == 1 and size <= 2:
        return "Estadio 0", "Resección, RFA o Trasplante"
    if (num == 1 and size <= 5) or (num <= 3 and size <= 3):
        return "Estadio A", "Resección, RFA o Trasplante"
    return "Estadio B", "TACE"

def calcular_Okuda(size, asc, alb, bilir):
    return int(size > 50) + int(asc != "ausente") + int(alb < 3) + int(bilir > 3)

def calcular_ART(b0, b1, resp):
    puntos = int(b1 > b0)
    puntos += 2 if resp == "progresion" else 1 if resp == "estable" else 0
    return puntos

def calcular_HKLC(perf, size, num, inv, met):
    if perf <= 1 and num <= 3 and size <= 5 and not inv and not met:
        return "HKLC I"
    elif perf <= 2 and not met:
        return "HKLC II/III"
    elif perf >= 3 and met:
        return "HKLC IV"
    return "HKLC III/IV"

def calcular_CLIP(bilir, alb, asc, size):
    return int(bilir > 3) + int(alb < 3.5) + int(asc != "ausente") + int(size > 50)

# Validación básica
errores = []
if albumina < 1.5:
    errores.append("⚠️ Albúmina muy baja. Verifica que el dato ingresado es correcto.")
if bilirrubina > 20:
    errores.append("⚠️ Bilirrubina extremadamente alta. Posible error de ingreso.")

# Mostrar errores si existen
for error in errores:
    st.warning(error)

# Cálculo real con interpretaciones
if st.button("Calcular") and not errores:
    albi = calcular_ALBI(bilirrubina, albumina)
    cp = calcular_ChildPugh(bilirrubina, albumina, INR, ascitis, encefalopatia)
    meld = calcular_MELD(creatinina, bilirrubina, INR)
    meld_na = calcular_MELD_Na(meld, sodio)
    bclc, trat = calcular_BCLC(tamaño_tumor, número_tumores, estado_performance, invasion, metastasis)
    okuda = calcular_Okuda(tamaño_tumor, ascitis, albumina, bilirrubina)
    art = calcular_ART(bilirrubina, bilirrubina_post, respuesta_tumoral)
    hklc = calcular_HKLC(estado_performance, tamaño_tumor, número_tumores, invasion, metastasis)
    clip = calcular_CLIP(bilirrubina, albumina, ascitis, tamaño_tumor)

    st.subheader("📊 Resultados")

    st.write(f"**ALBI Score:** {albi}")
    with st.expander("Interpretación del ALBI"):
        st.markdown("""
- Grado 1: ALBI ≤ -2.60 → Buena función hepática
- Grado 2: -2.60 < ALBI ≤ -1.39 → Moderada
- Grado 3: ALBI > -1.39 → Mal pronóstico
[Fuente](https://pubmed.ncbi.nlm.nih.gov/25512453/)
""")

    st.write(f"**Child-Pugh Score:** {cp}")
    with st.expander("Interpretación del Child-Pugh"):
        st.markdown("""
- A (5–6): Buena función hepática
- B (7–9): Disfunción moderada
- C (10–15): Disfunción severa
[Fuente](https://www.ncbi.nlm.nih.gov/books/NBK542308/)
""")

    st.write(f"**MELD Score:** {meld}")
    with st.expander("Interpretación del MELD"):
        st.markdown("""
- <10: Riesgo bajo (<5%)
- 10–19: Riesgo intermedio (6–20%)
- 20–29: Riesgo alto (20–55%)
- ≥30: Muy alto (>70%)
[Fuente](https://pubmed.ncbi.nlm.nih.gov/11172350/)
""")

    st.write(f"**MELD-Na Score:** {meld_na}")
    with st.expander("Interpretación del MELD-Na"):
        st.markdown(f"""
- Supervivencia estimada a 1 año ≈ {round(100 - 0.3 * meld_na)}%
[Fuente](https://pubmed.ncbi.nlm.nih.gov/18768945/)
""")

    st.write(f"**BCLC:** {bclc} → {trat}")
    with st.expander("Interpretación del BCLC"):
        st.markdown("""
- 0: Tumor ≤2 cm, ECOG 0 → Curativo
- A: ≤3 tumores ≤3 cm → Curativo
- B: Multinodular → TACE
- C: Invasión/Metástasis/ECOG ≥1 → Sistémico
[Fuente](https://www.journal-of-hepatology.eu/article/S0168-8278(24)02508-X/abstract)
""")

    st.write(f"**Okuda Score:** {okuda}")
    with st.expander("Interpretación del Okuda"):
        st.markdown("""
- I: 0–1 ptos
- II: 2 ptos
- III: 3–4 ptos
[Fuente](https://pubmed.ncbi.nlm.nih.gov/2990661/)
""")

    st.write(f"**ART Score:** {art}")
    with st.expander("Interpretación del ART Score"):
        st.markdown("""
- 0–1: Bajo riesgo, repetir TACE
- ≥2: Alto riesgo, considerar sistémico
[Fuente](https://pubmed.ncbi.nlm.nih.gov/23316013/)
""")

    st.write(f"**HKLC:** {hklc}")
    with st.expander("Interpretación del HKLC"):
        st.markdown("""
- I–II: Curativo
- III–IV: Paliativo o sistémico
[Fuente](https://pubmed.ncbi.nlm.nih.gov/24583061/)
""")

    st.write(f"**CLIP Score:** {clip}")
    with st.expander("Interpretación del CLIP"):
        st.markdown("""
- 0–1: Buen pronóstico
- 2–3: Moderado
- ≥4: Mal pronóstico
[Fuente](https://pubmed.ncbi.nlm.nih.gov/10733537/)
""")

