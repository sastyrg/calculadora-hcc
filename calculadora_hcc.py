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

# Resultado de ejemplo
if st.button("Calcular"):
    st.subheader("📊 Resultados")

    # Aquí se llamarán las funciones de cálculo previamente definidas (omitidas por claridad en este bloque)
    # Variables de ejemplo para mostrar las interpretaciones
    albi = -2.1
    cp = 7
    meld = 15
    meld_na = 19
    bclc = "Estadio B"
    trat = "TACE"
    okuda = 1
    art = 1
    hklc = "HKLC II/III"
    clip = 2

    # ALBI
    st.write(f"**ALBI Score:** {albi}")
    with st.expander("Interpretación pronóstica del ALBI"):
        st.markdown("""
- Grado 1 (ALBI ≤ -2.60): **Buena función hepática**  
  - Supervivencia global media: **~24 meses**  
- Grado 2 (-2.60 < ALBI ≤ -1.39): **Función intermedia**  
  - Supervivencia: **~14 meses**  
- Grado 3 (ALBI > -1.39): **Disfunción hepática severa**  
  - Supervivencia: **<6 meses**  
[Fuente: Johnson PJ et al. JCO 2015](https://pubmed.ncbi.nlm.nih.gov/25512453/)
        """)

    # Child-Pugh
    st.write(f"**Child-Pugh:** {cp}")
    with st.expander("Interpretación pronóstica del Child-Pugh"):
        st.markdown(f"""
- Clase A (5–6): **Buena función hepática**  
  - Supervivencia a 1 año: **100%**  
- Clase B (7–9): **Disfunción hepática moderada**  
  - Supervivencia a 1 año: **~80%**  
- Clase C (10–15): **Disfunción hepática grave**  
  - Supervivencia a 1 año: **~45%**  
[Fuente: Pugh RN et al. Br J Surg. 1973](https://www.ncbi.nlm.nih.gov/books/NBK542308/)
        """)

    # MELD
    st.write(f"**MELD Score:** {meld} puntos")
    with st.expander("Interpretación pronóstica del MELD"):
        if meld < 10:
            st.markdown("""
- Mortalidad a 3 meses: **<5%**  
- Riesgo bajo. Seguimiento ambulatorio.  
            """)
        elif 10 <= meld < 20:
            st.markdown("""
- Mortalidad a 3 meses: **6–20%**  
- Riesgo moderado. Evaluación para trasplante.  
            """)
        elif 20 <= meld < 30:
            st.markdown("""
- Mortalidad a 3 meses: **20–55%**  
- Alta prioridad para trasplante.  
            """)
        else:
            st.markdown("""
- Mortalidad a 3 meses: **>70%**  
- Evaluación urgente o cuidados paliativos.  
            """)
        st.markdown("[Fuente: Kamath PS et al. Mayo Clin Proc 2001](https://pubmed.ncbi.nlm.nih.gov/11172350/)")

    # MELD-Na
    st.write(f"**MELD-Na Score:** {meld_na} puntos")
    with st.expander("Interpretación clínica del MELD-Na"):
        st.markdown(f"""
- **Lista de espera para trasplante:**  
  Supervivencia a 1 año ≈ **{round(100 - 0.3 * meld_na)}%**  
- **En PBE o sepsis:**  
  MELD-Na ≥25 → Supervivencia 3 meses: **<50%**  
- **En colocación de TIPS:**  
  MELD-Na ≥18 → Mortalidad a 1 mes: **5–25%**  
[Fuente: Kim WR et al. Liver Transpl 2008](https://pubmed.ncbi.nlm.nih.gov/18768945/)
        """)

    # BCLC
    st.write(f"**BCLC:** {bclc} → **{trat}**")
    with st.expander("Interpretación pronóstica y terapéutica del BCLC"):
        st.markdown("""
- Estadio 0: Tumor único ≤2 cm, ECOG 0 → Resección, RFA, Trasplante  
  - Supervivencia 5 años: >70%  
- Estadio A: ≤3 nódulos ≤3 cm o 1 tumor ≤5 cm, ECOG 0 → Resección, RFA, Trasplante  
  - Supervivencia 5 años: 50–70%  
- Estadio B: Tumores multinodulares, ECOG 0 → TACE  
  - Supervivencia media: 20–30 meses  
- Estadio C: Invasión vascular o metástasis, ECOG 1–2 → Terapia sistémica  
  - Supervivencia media: 8–16 meses  
- Estadio D: ECOG >2 o Child C → Cuidados paliativos  
  - Supervivencia: <6 meses  
[Guía EASL 2022 – J Hepatol](https://www.journal-of-hepatology.eu/article/S0168-8278(24)02508-X/abstract)
        """)

    # Okuda
    st.write(f"**Okuda Score:** {okuda}")
    with st.expander("Interpretación pronóstica del Okuda"):
        st.markdown("""
- Estadio I (0–1 puntos): Supervivencia media: >12 meses  
- Estadio II (2 puntos): Supervivencia media: ~6 meses  
- Estadio III (3–4 puntos): Supervivencia media: ~3 meses  
[Fuente: Okuda K et al. Cancer. 1985](https://pubmed.ncbi.nlm.nih.gov/2990661/)
        """)

    # ART
    st.write(f"**ART Score:** {art} puntos")
    with st.expander("Interpretación del ART Score (post-TACE)"):
        st.markdown("""
- 0–1 puntos: Riesgo bajo → Repetir TACE posible  
- ≥2 puntos: Riesgo alto → Suspender TACE, considerar terapia sistémica  
[Fuente: Sieghart W et al. Hepatology 2013](https://pubmed.ncbi.nlm.nih.gov/23316013/)
        """)

    # HKLC
    st.write(f"**HKLC:** {hklc}")
    with st.expander("Interpretación pronóstica del HKLC"):
        st.markdown("""
- HKLC I–II: Tratamiento curativo → Supervivencia 5 años: >60%  
- HKLC III: Tratamiento paliativo/combinado → Supervivencia media: ~12 meses  
- HKLC IV–V: Enfermedad avanzada → Supervivencia media: <6 meses  
[Fuente: Yau T et al. J Clin Oncol. 2014](https://pubmed.ncbi.nlm.nih.gov/24583061/)
        """)

    # CLIP
    st.write(f"**CLIP Score:** {clip}")
    with st.expander("Interpretación pronóstica del CLIP"):
        st.markdown("""
- 0–1 puntos: Buen pronóstico → Supervivencia media: ~30 meses  
- 2–3 puntos: Pronóstico intermedio → Supervivencia media: 12–20 meses  
- ≥4 puntos: Mal pronóstico → Supervivencia media: <6 meses  
[Fuente: Cillo A et al. Hepatology 2006](https://pubmed.ncbi.nlm.nih.gov/10733537/)
        """)
