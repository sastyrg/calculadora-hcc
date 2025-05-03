import streamlit as st
import math

# --- Configuración de la Página ---
st.set_page_config(page_title="Calculadora HCC", layout="wide")

# --- Títulos y Descripciones ---
st.title("Calculadora Integral de Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero // Dr. Simmons David Gough Coto — Instituto Nacional de Cancerología, CDMX*")
st.markdown("**Colaboradores:** Drs: Jorge Guerrero Ixtlahuac, Andrea Paola González Rodríguez, Jessica Sainz Castro, Rodrigo Meléndez Coral")
st.markdown("*Instagram: @radioresidentes_*")
st.markdown("---")

st.markdown("🧭 **Propósito:** Esta herramienta es de apoyo educativo y clínico. **No sustituye el juicio médico individualizado ni las decisiones de un comité multidisciplinario.** Está diseñada para estimar la función hepática y orientar la clasificación del Hepatocarcinoma (HCC) según guías internacionales. La precisión depende de la exactitud de los datos ingresados.")
st.markdown("---")

# --- Entradas de Usuario ---
st.subheader("📝 Ingreso de parámetros clínicos")
col1, col2 = st.columns(2)

with col1:
    st.write("**Función Hepática y General:**")
    bilirrubina = st.number_input("Bilirrubina total (mg/dL)", min_value=0.1, value=1.0, step=0.1, format="%.1f")
    albumina = st.number_input("Albúmina sérica (g/dL)", min_value=1.0, value=3.5, step=0.1, format="%.1f")
    INR = st.number_input("INR", min_value=0.5, value=1.1, step=0.1, format="%.1f")
    ascitis = st.selectbox("Ascitis", ["Ausente", "Leve (Controlada con diuréticos)", "Moderada/Severa (Refractaria)"], index=0)
    # Asegúrate que la clasificación de encefalopatía coincida con los grados usados en Child-Pugh
    encefalopatia_grado = st.selectbox("Encefalopatía Hepática (Grado)", ["Ninguna (Grado 0)", "Grado 1-2", "Grado 3-4"], index=0)
    creatinina = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, value=1.0, step=0.1, format="%.1f")
    sodio = st.number_input("Sodio sérico (mEq/L)", min_value=100.0, max_value=160.0, value=137.0, step=1.0)
    estado_performance = st.selectbox("Estado funcional (ECOG Performance Status)", [0, 1, 2, 3, 4], index=0)

with col2:
    st.write("**Características del Tumor:**")
    tamaño_tumor = st.number_input("Tamaño del nódulo tumoral más grande (cm)", min_value=0.1, value=3.0, step=0.1, format="%.1f")
    número_tumores = st.number_input("Número de nódulos tumorales", min_value=1, value=1, step=1)
    invasion_vascular = st.checkbox("Invasión vascular macroscópica presente")
    metastasis = st.checkbox("Metástasis extrahepáticas presentes")
    AFP = st.number_input("Alfafetoproteína (AFP) (ng/mL)", min_value=0.0, value=20.0, step=1.0)

st.write("**Parámetros Post-TACE (Opcional - para Score ART):**")
respuesta_tumoral_tace = st.selectbox("Respuesta tumoral radiológica a TACE (ej. mRECIST)", ["No aplica / No evaluado", "Respuesta Completa/Parcial", "Enfermedad Estable", "Progresión de Enfermedad"], index=0)
bilirrubina_post_tace = st.number_input("Bilirrubina total post-TACE (mg/dL)", min_value=0.1, value=bilirrubina, step=0.1, format="%.1f", help="Valor de bilirrubina después del procedimiento TACE para calcular ART score.")

st.markdown("---")

# --- Funciones de Cálculo ---

def calcular_ChildPugh(bilir, alb, inr, asc, encef_grado):
    """Calcula el score numérico de Child-Pugh."""
    score = 0
    # Bilirrubina
    if bilir <= 2: score += 1
    elif bilir <= 3: score += 2
    else: score += 3
    # Albúmina
    if alb >= 3.5: score += 1
    elif alb >= 2.8: score += 2
    else: score += 3
    # INR
    if inr <= 1.7: score += 1
    elif inr <= 2.3: score += 2
    else: score += 3
    # Ascitis
    if asc == "Ausente": score += 1
    elif asc == "Leve (Controlada con diuréticos)": score += 2
    else: score += 3 # Moderada/Severa
    # Encefalopatía
    if encef_grado == "Ninguna (Grado 0)": score += 1
    elif encef_grado == "Grado 1-2": score += 2
    else: score += 3 # Grado 3-4
    return score

def get_child_pugh_class(score):
    """Determina la Clase Child-Pugh a partir del score."""
    if score <= 6: return "A"
    elif score <= 9: return "B"
    else: return "C" # score 10-15

def calcular_ALBI(bilir, alb):
    """Calcula el score ALBI."""
    # Convertir bilirrubina mg/dL a umol/L (factor ~17.1)
    bilir_umol = bilir * 17.1
    # Convertir albumina g/dL a g/L (factor 10)
    alb_gl = alb * 10
    albi_score = (math.log10(bilir_umol) * 0.66) + (alb_gl * -0.085)
    # Asegúrate de usar la fórmula correcta (hay variantes), esta es común: 0.66*log10(Bilirubin [μmol/L]) − 0.085*(Albumin [g/L])
    return round(albi_score, 2)

def calcular_MELD(creat, bilir, inr):
    """Calcula el MELD score original."""
    # Aplicar límites según la fórmula estándar
    creat = min(max(creat, 1.0), 4.0)
    bilir = max(bilir, 1.0)
    inr = max(inr, 1.0)
    # Fórmula MELD
    meld_score = (0.957 * math.log(creat) +
                  0.378 * math.log(bilir) +
                  1.120 * math.log(inr) +
                  0.643) * 10
    return round(meld_score)

def calcular_MELD_Na(meld_score, sod):
    """Calcula el MELD-Na score."""
    # Aplicar límites al sodio para la fórmula MELD-Na
    sod = min(max(sod, 125.0), 137.0)
    meld_na_score = meld_score + 1.32 * (137 - sod) - (0.033 * meld_score * (137 - sod))
    # Algunas versiones limitan el MELD original a 40 antes de calcular MELD-Na
    # meld_original_capped = min(meld_score, 40)
    # meld_na_score = meld_original_capped + 1.32*(137 - sod) - (0.033 * meld_original_capped * (137 - sod))
    # Usaremos la versión sin el cap de 40 por simplicidad inicial, revisar fuente preferida.
    return round(meld_na_score)


def calcular_BCLC_corregido(cp_class, perf, size, num, inv, met):
    """Calcula el Estadio BCLC siguiendo el árbol de decisión."""
    # Fuente principal recomendada: EASL Clinical Practice Guidelines on HCC (versión más reciente)
    # https://easl.eu/publications/clinical-practice-guidelines/

    # Estadio D (Terminal)
    if cp_class == 'C' or perf >= 3:
        return "Estadio D (Terminal)", "Mejor Cuidado de Soporte (BSC)"

    # Estadio C (Avanzado) - Requiere Child-Pugh A o B
    if inv or met or perf >= 1: # Presencia de inv/met O síntomas (ECOG 1-2)
        # Si ECOG es 1 o 2, es C (asumiendo Child A/B, ya que C es D)
        if perf == 1 or perf == 2:
             return "Estadio C (Avanzado)", "Terapia Sistémica (Ej. Atezolizumab + Bevacizumab, Sorafenib, Lenvatinib)"
        # Si hay invasión o metástasis (y ECOG=0, Child A/B), también es C
        if inv or met:
             return "Estadio C (Avanzado)", "Terapia Sistémica (Ej. Atezolizumab + Bevacizumab, Sorafenib, Lenvatinib)"
        # Nota: Teóricamente, un paciente podría tener ECOG 0 y cumplir criterios de B pero tener Child B alto (ej B9),
        # algunas guías pueden moverlo a C o requerir evaluación individualizada. Esta lógica sigue el flujo estándar.

    # A partir de aquí, asumimos ECOG PS 0 y Child-Pugh A o B

    # Estadio 0 (Muy Temprano)
    if num == 1 and size <= 2 and cp_class == 'A' and perf == 0: # Requiere Child A y ECOG 0
        return "Estadio 0 (Muy Temprano)", "Resección / Ablación (RFA/MWA) / Trasplante (si cumple criterios específicos)"

    # Estadio A (Temprano)
    # Criterios comunes: Nódulo único <= 5cm O hasta 3 nódulos <= 3cm. Requiere ECOG 0 y Child A/B.
    is_within_milan_approx = (num == 1 and size <= 5) or (num >= 2 and num <= 3 and size <= 3)
    if is_within_milan_approx and perf == 0: # Child A o B ya filtrado, ECOG 0 requerido
         return "Estadio A (Temprano)", "Resección / Ablación (RFA/MWA) / Trasplante Hepático"

    # Estadio B (Intermedio)
    # Si no es 0, A, C, D -> Es B. Definido como: Multinodular más allá de A, Child A/B, ECOG 0.
    # Esta condición captura los casos restantes con ECOG 0 y Child A/B.
    if perf == 0: # Ya sabemos que no cumple 0 ni A (por tamaño/número) y no es C/D
        return "Estadio B (Intermedio)", "Quimioembolización Transarterial (TACE)"

    # Fallback / Caso inesperado
    return "Estadio Indeterminado", "Revisar datos de entrada o lógica de clasificación"


def calcular_Okuda(size_cm, asc, alb, bilir):
    """Calcula el score Okuda. ADVERTENCIA: Usa tamaño en cm, Okuda original usa % volumen hepático."""
    score = 0
    # Okuda original: Tumor >50% del hígado (1 punto) vs <=50% (0 puntos)
    # Esta implementación usa un umbral simple de tamaño > 5cm como proxy (¡Inexacto!)
    # score += 1 if size_cm > 5 else 0 # --> COMENTADO POR INEXACTITUD. Considerar eliminar o pedir % volumen.
    st.warning("Advertencia Okuda: El cálculo original usa % de volumen hepático, no tamaño en cm. El score aquí puede ser impreciso respecto a ese punto.", icon="⚠️")
    score += 1 if asc != "Ausente" else 0
    score += 1 if alb < 3.0 else 0
    score += 1 if bilir > 3.0 else 0
    return score

def calcular_CLIP(cp_class, afp, inv, num, size_cm):
     """Calcula el score CLIP. ADVERTENCIA: Usa tamaño/número como proxy para morfología."""
     score = 0
     # Child-Pugh Stage (A=0, B/C=1)
     score += 0 if cp_class == 'A' else 1
     # AFP (≤400=0, >400=1)
     score += 1 if afp > 400 else 0
     # Invasión Vascular Portal (No=0, Sí=1) - Usamos la invasión vascular general como proxy
     score += 1 if inv else 0
     # Morfología Tumoral (Uninodular y extensión <50% = 0; Multinodular = 1; Masivo o extensión >50% = 2)
     # Esto es difícil de mapear directamente desde num/size. Simplificación GROSERA:
     st.warning("Advertencia CLIP: La morfología tumoral se simplifica aquí. El score puede ser impreciso.", icon="⚠️")
     if num == 1 and size_cm <= 5: # Proxy muy simple para uninodular <50%
         score += 0
     elif num > 1 and size_cm <= 5: # Proxy muy simple para multinodular
         score += 1
     else: # Proxy muy simple para masivo / >50%
         score += 2
     return score

def calcular_ART(bili_pre, bili_post, cp_class_pre, resp_radio):
    """Calcula el ART score (Assessment for Retreatment with TACE).
       ADVERTENCIA: Versión original usa AST >25% aumento, Child-Pugh basal, y respuesta mRECIST."""
    st.warning("Advertencia ART: El score original usa Aumento de AST >25%, Clase Child-Pugh basal y respuesta mRECIST. Esta es una implementación adaptada/simplificada.", icon="⚠️")
    puntos = 0
    # 1. Aumento Bilirrubina (Adaptación, original es AST)
    if bili_post > bili_pre * 1.25: # Umbral arbitrario de aumento >25% para bili, ajustar si se tiene fuente específica
        puntos += 1.5 # Ejemplo de puntuación, ajustar a fuente
    # 2. Child-Pugh Basal (Original: A=0, B=1)
    if cp_class_pre == 'B': # Asumiendo que C no recibiría TACE o retratamiento
        puntos += 1 # Ejemplo de puntuación, ajustar a fuente
    # 3. Respuesta Radiológica (Original: Sin respuesta [SD/PD]=1.5)
    if resp_radio == "Enfermedad Estable" or resp_radio == "Progresión de Enfermedad":
        puntos += 1.5 # Ejemplo de puntuación, ajustar a fuente

    # Interpretación simple basada en puntos (ajustar umbrales según fuente)
    if puntos <= 1.5:
        riesgo = "Bajo riesgo de no beneficio / Considerar Retratamiento TACE"
    else: # Puntos > 1.5 (o >=2.5 según la fuente original)
        riesgo = "Alto riesgo de no beneficio / Considerar cambio a Terapia Sistémica"
    return round(puntos,1), riesgo

def calcular_HKLC(perf, size, num, inv, met, cp_class):
     """Calcula el estadio HKLC (Hong Kong Liver Cancer staging).
     ADVERTENCIA: Sistema complejo, esta es una simplificación EXTREMA."""
     st.warning("Advertencia HKLC: El sistema HKLC es complejo con 5 estadios y subestadios. Esta es una implementación muy simplificada y puede no ser precisa.", icon="⚠️")

     # Simplificación basada en algunos criterios clave (no exhaustiva)
     if met or perf >= 3:
         return "HKLC Estadio V (o IVb)", "Paliativo / Sistémico" # Metástasis o muy mal estado
     elif inv: # Invasión vascular portal mayor
          # Podría ser IIb, IIIa/b, IVa dependiendo de otros factores (Child, tamaño, etc.)
          return "HKLC Estadio IIIb/IVa (Simplificado)", "TACE / Sistémico / Paliativo"
     elif perf <= 1 and ((num == 1 and size <= 5) or (num <= 3 and size <= 3)) and cp_class == 'A':
         # Dentro de criterios Milán y buena función/estado
         return "HKLC Estadio I", "Curativo (Resección/Trasplante/Ablación)"
     elif num > 3 or size > 5 or cp_class == 'B':
         # Más allá de Milán o peor función hepática
         # Podría ser IIa/b, IIIa dependiendo de detalles
         return "HKLC Estadio II/IIIa (Simplificado)", "TACE / Resección (seleccionados) / Sistémico"
     else:
         # Casos intermedios
         return "HKLC Estadio II (Simplificado)", "Resección / TACE / Ablación"

# --- Validación Básica ---
errores = []
if albumina < 1.5:
    errores.append("⚠️ Albúmina (< 1.5 g/dL) es extremadamente baja. Verifica el dato.")
if bilirrubina > 20:
    errores.append("⚠️ Bilirrubina (> 20 mg/dL) es extremadamente alta. Verifica el dato.")
if creatinina > 10:
    errores.append("⚠️ Creatinina (> 10 mg/dL) es muy alta. Verifica el dato.")
if sodio < 110 or sodio > 155:
     errores.append("⚠️ Sodio fuera del rango fisiológico común (110-155 mEq/L). Verifica el dato.")

# Mostrar errores si existen
if errores:
    for error in errores:
        st.error(error)
    st.stop() # Detener ejecución si hay errores graves de entrada

# --- Botón de Cálculo y Resultados ---
if st.button("📊 Calcular Todos los Scores"):

    # Cálculos primarios
    cp_score = calcular_ChildPugh(bilirrubina, albumina, INR, ascitis, encefalopatia_grado)
    cp_class = get_child_pugh_class(cp_score)
    albi_score = calcular_ALBI(bilirrubina, albumina)
    meld_score = calcular_MELD(creatinina, bilirrubina, INR)
    meld_na_score = calcular_MELD_Na(meld_score, sodio)

    # Cálculos de estadificación HCC
    bclc_estadio, bclc_trat = calcular_BCLC_corregido(cp_class, estado_performance, tamaño_tumor, número_tumores, invasion_vascular, metastasis)
    okuda_score = calcular_Okuda(tamaño_tumor, ascitis, albumina, bilirrubina)
    clip_score = calcular_CLIP(cp_class, AFP, invasion_vascular, número_tumores, tamaño_tumor)
    hklc_estadio, hklc_trat = calcular_HKLC(estado_performance, tamaño_tumor, número_tumores, invasion_vascular, metastasis, cp_class)

    # Cálculo ART (solo si aplica)
    art_score, art_riesgo = None, "No calculado (Requiere datos pre/post TACE y selección de respuesta)"
    if respuesta_tumoral_tace != "No aplica / No evaluado":
         art_score, art_riesgo = calcular_ART(bilirrubina, bilirrubina_post_tace, cp_class, respuesta_tumoral_tace)


    st.subheader("📈 Resultados Calculados")
    res_col1, res_col2 = st.columns(2)

    with res_col1:
        st.markdown(f"**Función Hepática:**")
        st.metric(label="Child-Pugh Score", value=f"{cp_score} (Clase {cp_class})")
        with st.expander("Interpretación Child-Pugh"):
            st.markdown("- **Clase A (5–6 puntos):** Enfermedad hepática bien compensada.\n- **Clase B (7–9 puntos):** Compromiso funcional significativo.\n- **Clase C (10–15 puntos):** Enfermedad descompensada.")
            st.caption("[Referencia Child-Pugh](https://www.ncbi.nlm.nih.gov/books/NBK542308/)")

        st.metric(label="ALBI Score", value=f"{albi_score}")
        with st.expander("Interpretación ALBI"):
             st.markdown("- **Grado 1:** ALBI ≤ -2.60 (Mejor pronóstico)\n- **Grado 2:** -2.60 < ALBI ≤ -1.39 (Pronóstico intermedio)\n- **Grado 3:** ALBI > -1.39 (Peor pronóstico)")
             st.caption("[Referencia ALBI](https://pubmed.ncbi.nlm.nih.gov/25512453/)")

        st.metric(label="MELD Score", value=f"{meld_score}")
        with st.expander("Interpretación MELD"):
            st.markdown("Estima mortalidad a 3 meses en lista de espera para trasplante. Mayor score = Mayor mortalidad.")
            st.caption("[Referencia MELD](https://pubmed.ncbi.nlm.nih.gov/11172350/)")

        st.metric(label="MELD-Na Score", value=f"{meld_na_score}")
        with st.expander("Interpretación MELD-Na"):
            st.markdown("Variante del MELD que incorpora el sodio sérico, mejora la predicción de mortalidad.")
            st.caption("[Referencia MELD-Na](https://pubmed.ncbi.nlm.nih.gov/18768945/)")

    with res_col2:
        st.markdown(f"**Estadificación del Hepatocarcinoma (HCC):**")
        st.metric(label="BCLC Estadio", value=f"{bclc_estadio}", delta=f"Recomendación: {bclc_trat}", delta_color="off")
        with st.expander("Detalles BCLC"):
            st.markdown("""
            - **0 (Muy Temprano):** Nódulo único ≤2cm, Child-Pugh A, ECOG 0. Tto: Curativo (Resección/Ablación/Trasplante).
            - **A (Temprano):** Nódulo único ≤5cm o ≤3 nódulos ≤3cm, Child-Pugh A/B, ECOG 0. Tto: Curativo (Resección/Ablación/Trasplante).
            - **B (Intermedio):** Multinodular (>A), Child-Pugh A/B, ECOG 0. Tto: TACE.
            - **C (Avanzado):** Invasión vascular, Metástasis extrahepáticas o ECOG 1-2, Child-Pugh A/B. Tto: Terapia Sistémica.
            - **D (Terminal):** Child-Pugh C o ECOG ≥3. Tto: Mejor Cuidado de Soporte (BSC).
            """)
            st.caption("[Referencia Principal BCLC - EASL 2024](https://www.journal-of-hepatology.eu/article/S0168-8278(24)02508-X/abstract)") # Actualizar si hay nueva versión

        st.metric(label="Okuda Estadio", value=f"{okuda_score}")
        with st.expander("Interpretación Okuda"):
            st.markdown("- **Estadio I:** 0 puntos\n- **Estadio II:** 1-2 puntos\n- **Estadio III:** 3-4 puntos\n(Basado en Bilirrubina, Albúmina, Ascitis. *Advertencia: Factor tamaño tumoral omitido por usar cm en vez de % volumen.*)")
            st.caption("[Referencia Okuda](https://pubmed.ncbi.nlm.nih.gov/2990661/)")

        st.metric(label="CLIP Score", value=f"{clip_score}")
        with st.expander("Interpretación CLIP"):
             st.markdown("- **Score 0-1:** Mejor pronóstico\n- **Score 2-3:** Pronóstico intermedio\n- **Score 4-6:** Peor pronóstico\n(Basado en Child-Pugh, AFP, Morfología tumoral, Invasión portal. *Advertencia: Morfología tumoral simplificada.*)")
             st.caption("[Referencia CLIP](https://pubmed.ncbi.nlm.nih.gov/10733537/)")

        st.metric(label="HKLC Estadio (Simplificado)", value=f"{hklc_estadio}", delta=hklc_trat, delta_color="off")
        with st.expander("Interpretación HKLC"):
            st.markdown("Sistema pronóstico alternativo, útil en Asia. *Advertencia: Implementación muy simplificada.*")
            st.caption("[Referencia HKLC](https://pubmed.ncbi.nlm.nih.gov/24583061/)")

        # Mostrar ART solo si se calculó
        if art_score is not None:
             st.metric(label="ART Score (Adaptado)", value=f"{art_score}", delta=art_riesgo, delta_color="inverse") # inverse para resaltar riesgo alto
             with st.expander("Interpretación ART"):
                 st.markdown("Evalúa beneficio de retratamiento con TACE. *Advertencia: Implementación adaptada/simplificada.*")
                 st.caption("[Referencia ART original](https://pubmed.ncbi.nlm.nih.gov/23316013/)")
        else:
             st.info("ART Score no calculado. Requiere seleccionar respuesta a TACE e ingresar bilirrubina post-TACE.")


    st.markdown("---")
    st.success("Cálculos completados. Recuerda interpretar los resultados en el contexto clínico completo del paciente.")

# --- Pie de página ---
st.markdown("---")
st.caption("Desarrollado con ❤️ usando Python y Streamlit. Versión 1.1 - Revisar periódicamente actualizaciones de guías.")
