import streamlit as st
import math

# --- Configuración de la Página ---
st.set_page_config(page_title="Calculadora HCC Avanzada + Trasplante", layout="wide")

# --- Títulos y Descripciones ---
st.title("Calculadora Integral, Pronóstica y de Criterios de Trasplante para Hepatocarcinoma")
st.markdown("*Dr. Santiago Ramírez Guerrero // Dr. Simmons David Gough Coto — Instituto Nacional de Cancerología, CDMX*")
st.markdown("**Colaboradores:** Drs: Jorge Guerrero Ixtlahuac, Andrea Paola González Rodríguez, Jessica Sainz Castro, Rodrigo Meléndez Coral")
st.markdown("*Instagram: @radioresidentes_*")
st.markdown("---")

st.warning("🚨 **Disclaimer Médico:** Herramienta de apoyo educativo/clínico. **No sustituye el juicio médico individualizado, la evaluación completa del paciente, ni las decisiones de un comité multidisciplinario.** Las cifras de pronóstico son estimaciones poblacionales. Los criterios de trasplante son una guía inicial; la elegibilidad final depende de una evaluación exhaustiva en un centro de trasplante.")
st.markdown("---")

# --- Entradas de Usuario ---
st.subheader("📝 Ingreso de parámetros clínicos")
col1, col2, col3 = st.columns(3) # Usar 3 columnas para mejor distribución

with col1:
    st.write("**Función Hepática y General:**")
    bilirrubina = st.number_input("Bilirrubina total (mg/dL)", min_value=0.1, value=1.0, step=0.1, format="%.1f")
    albumina = st.number_input("Albúmina sérica (g/dL)", min_value=1.0, value=3.5, step=0.1, format="%.1f")
    INR = st.number_input("INR", min_value=0.5, value=1.1, step=0.1, format="%.1f")
    ascitis = st.selectbox("Ascitis", ["Ausente", "Leve (Controlada con diuréticos)", "Moderada/Severa (Refractaria)"], index=0)
    encefalopatia_grado = st.selectbox("Encefalopatía Hepática (Grado)", ["Ninguna (Grado 0)", "Grado 1-2", "Grado 3-4"], index=0)


with col2:
    st.write("**Parámetros Sistémicos:**")
    creatinina = st.number_input("Creatinina sérica (mg/dL)", min_value=0.1, value=1.0, step=0.1, format="%.1f")
    sodio = st.number_input("Sodio sérico (mEq/L)", min_value=100.0, max_value=160.0, value=137.0, step=1.0)
    estado_performance = st.selectbox("Estado funcional (ECOG PS)", [0, 1, 2, 3, 4], index=0)
    AFP = st.number_input("Alfafetoproteína (AFP) (ng/mL)", min_value=0.0, value=20.0, step=1.0)


with col3:
    st.write("**Características del Tumor:**")
    número_tumores = st.number_input("Número de nódulos tumorales", min_value=1, value=1, step=1)
    tamaño_tumor = st.number_input("Tamaño del nódulo más grande (cm)", min_value=0.1, value=3.0, step=0.1, format="%.1f")
    # Nuevo input para UCSF
    suma_diametros_tumores = st.number_input("Suma de diámetros de TODOS los nódulos (cm)", min_value=tamaño_tumor, value=max(tamaño_tumor, 3.0), step=0.1, format="%.1f", help="Requerido para Criterios UCSF. Si solo hay 1 tumor, es igual al tamaño del nódulo más grande.")
    invasion_vascular = st.checkbox("Invasión vascular macroscópica presente")
    metastasis = st.checkbox("Metástasis extrahepáticas presentes")


st.write("**Parámetros Post-TACE (Opcional - para Score ART):**")
col_tace1, col_tace2 = st.columns(2)
with col_tace1:
    respuesta_tumoral_tace = st.selectbox("Respuesta tumoral radiológica a TACE (ej. mRECIST)", ["No aplica / No evaluado", "Respuesta Completa/Parcial", "Enfermedad Estable", "Progresión de Enfermedad"], index=0)
with col_tace2:
    bilirrubina_post_tace = st.number_input("Bilirrubina total post-TACE (mg/dL)", min_value=0.1, value=bilirrubina, step=0.1, format="%.1f", help="Valor post-TACE para calcular ART score.")

st.markdown("---")

# --- Funciones de Cálculo (Lógica Interna Mayormente Sin Cambios) ---

def calcular_ChildPugh(bilir, alb, inr, asc, encef_grado):
    score = 0
    if bilir <= 2: score += 1
    elif bilir <= 3: score += 2
    else: score += 3
    if alb >= 3.5: score += 1
    elif alb >= 2.8: score += 2
    else: score += 3
    if inr <= 1.7: score += 1
    elif inr <= 2.3: score += 2
    else: score += 3
    if asc == "Ausente": score += 1
    elif asc == "Leve (Controlada con diuréticos)": score += 2
    else: score += 3
    if encef_grado == "Ninguna (Grado 0)": score += 1
    elif encef_grado == "Grado 1-2": score += 2
    else: score += 3
    return score

def get_child_pugh_class(score):
    if score <= 6: return "A"
    elif score <= 9: return "B"
    else: return "C"

def calcular_ALBI(bilir, alb):
    bilir_umol = bilir * 17.1
    alb_gl = alb * 10
    albi_score = (math.log10(bilir_umol) * 0.66) + (alb_gl * -0.085)
    return round(albi_score, 2)

def calcular_MELD(creat, bilir, inr):
    creat = min(max(creat, 1.0), 4.0)
    bilir = max(bilir, 1.0)
    inr = max(inr, 1.0)
    meld_score = (0.957 * math.log(creat) +
                  0.378 * math.log(bilir) +
                  1.120 * math.log(inr) +
                  0.643) * 10
    return round(meld_score)

def calcular_MELD_Na(meld_score, sod):
    sod = min(max(sod, 125.0), 137.0)
    meld_na_score = meld_score + 1.32 * (137 - sod) - (0.033 * meld_score * (137 - sod))
    return round(meld_na_score)

def calcular_BCLC_corregido(cp_class, perf, size, num, inv, met):
    # Estadio D (Terminal)
    if cp_class == 'C' or perf >= 3:
        estadio = "Estadio D (Terminal)"
        tratamiento = ("**Mejor Cuidado de Soporte (BSC):** Enfocado en calidad de vida, manejo de síntomas, cuidados paliativos. "
                       "Considerar criterios de inclusión para ensayos clínicos si aplica.")
        return estadio, tratamiento

    # Estadio C (Avanzado) - Child-Pugh A o B
    if inv or met or perf >= 1:
        estadio = "Estadio C (Avanzado)"
        tratamiento = ("**Terapia Sistémica:**\n"
                       "- **1ª Línea Preferida:** Atezolizumab + Bevacizumab (si no hay contraindicaciones).\n"
                       "- **Otras 1ª Líneas:** Sorafenib, Lenvatinib.\n"
                       "- **Secuenciales/2ª Línea:** Cabozantinib, Regorafenib (post-Sorafenib), Ramucirumab (si AFP > 400 post-Sorafenib), Pembrolizumab.\n"
                       "- Considerar TARE (Y-90) o TACE en casos muy seleccionados (investigacional o fuera de indicación estándar para C)."
                       )
        return estadio, tratamiento

    # A partir de aquí, asumimos ECOG PS 0 y Child-Pugh A o B
    # Estadio 0 (Muy Temprano) - Child-Pugh A, ECOG 0
    if num == 1 and size <= 2 and cp_class == 'A' and perf == 0:
        estadio = "Estadio 0 (Muy Temprano)"
        tratamiento = ("**Opciones Curativas:**\n"
                       "- **Resección Quirúrgica:** Si función hepática preservada y tumor resecable.\n"
                       "- **Ablación Local (RFA/MWA):** Especialmente si no candidato a resección (ubicación, comorbilidades).\n"
                       "- **Trasplante Hepático:** Si cumple criterios específicos (ver sección Criterios de Trasplante) y disponibilidad."
                       )
        return estadio, tratamiento

    # Estadio A (Temprano) - Child-Pugh A/B, ECOG 0
    is_within_milan_approx = (num == 1 and size <= 5) or (num >= 2 and num <= 3 and size <= 3)
    if is_within_milan_approx and perf == 0:
         estadio = "Estadio A (Temprano)"
         tratamiento = ("**Opciones Curativas/Control a Largo Plazo:**\n"
                        "- **Resección Quirúrgica:** Opción preferida si técnicamente factible y Child-Pugh A.\n"
                        "- **Trasplante Hepático:** Si cumple Criterios de Milán (u otros aplicables, ver sección Criterios de Trasplante) y es candidato.\n"
                        "- **Ablación Local (RFA/MWA):** Alternativa curativa si no candidato a resección/trasplante o como puente."
                        )
         return estadio, tratamiento

    # Estadio B (Intermedio) - Child-Pugh A/B, ECOG 0
    if perf == 0:
        estadio = "Estadio B (Intermedio)"
        tratamiento = ("**Terapia Loco-regional:**\n"
                       "- **Quimioembolización Transarterial (TACE):** Tratamiento estándar. Convencional (cTACE) o con esferas cargadas (DEB-TACE).\n"
                       "- **Radioembolización Transarterial (TARE / SIRT con Y-90):** Alternativa en algunos centros/casos (ej. invasión portal segmentaria, tumores grandes no aptos para TACE).\n"
                       "- Considerar Terapia Sistémica si progresión tras TACE o TACE no factible/contraindicado."
                       )
        return estadio, tratamiento

    # Fallback
    return "Estadio Indeterminado", "Revisar datos de entrada o lógica de clasificación."

def calcular_CLIP(cp_class, afp, inv, num, size_cm):
     score = 0
     score += 0 if cp_class == 'A' else 1
     score += 1 if afp > 400 else 0
     score += 1 if inv else 0
     st.warning("Advertencia CLIP: La morfología tumoral se simplifica aquí. El score puede ser impreciso.", icon="⚠️")
     if num == 1 and size_cm <= 5: score += 0
     elif num > 1 and size_cm <= 5: score += 1
     else: score += 2
     return score

def calcular_ART(bili_pre, bili_post, cp_class_pre, resp_radio):
    st.warning("Advertencia ART: Score original usa Aumento AST>25%, Child basal, y mRECIST. Esta es una implementación adaptada.", icon="⚠️")
    puntos = 0
    if bili_post > bili_pre * 1.25: puntos += 1.5
    if cp_class_pre == 'B': puntos += 1
    if resp_radio == "Enfermedad Estable" or resp_radio == "Progresión de Enfermedad": puntos += 1.5
    riesgo = "Bajo riesgo / Considerar Retratamiento TACE" if puntos <= 1.5 else "Alto riesgo / Considerar Terapia Sistémica"
    return round(puntos,1), riesgo

def calcular_HKLC(perf, size, num, inv, met, cp_class):
     st.warning("Advertencia HKLC: Sistema complejo, validado ppal. en Asia. Implementación muy simplificada. Usar con cautela como alternativa a BCLC.", icon="⚠️")
     if met or perf >= 3: return "HKLC Estadio V (o IVb)", "Paliativo / Sistémico"
     elif inv: return "HKLC Estadio IIIb/IVa (Simplificado)", "TACE / Sistémico / Paliativo"
     elif perf <= 1 and ((num == 1 and size <= 5) or (num <= 3 and size <= 3)) and cp_class == 'A': return "HKLC Estadio I", "Curativo (Resección/Trasplante/Ablación)"
     elif num > 3 or size > 5 or cp_class == 'B': return "HKLC Estadio II/IIIa (Simplificado)", "TACE / Resección (seleccionados) / Sistémico"
     else: return "HKLC Estadio II (Simplificado)", "Resección / TACE / Ablación"

# --- Funciones para Criterios de Trasplante ---
def check_milan(num, size_largest):
    """Verifica Criterios de Milán."""
    return (num == 1 and size_largest <= 5) or \
           (num >= 2 and num <= 3 and size_largest <= 3)

def check_ucsf(num, size_largest, size_total):
    """Verifica Criterios UCSF."""
    return (num == 1 and size_largest <= 6.5) or \
           (num >= 2 and num <= 3 and size_largest <= 4.5 and size_total <= 8)

def check_up_to_seven(num, size_largest):
    """Verifica Criterios Up-to-Seven."""
    return (size_largest + num) <= 7

# --- Validación Básica (Sin cambios) ---
errores = []
if albumina < 1.5: errores.append("⚠️ Albúmina (< 1.5 g/dL) extremadamente baja.")
if bilirrubina > 20: errores.append("⚠️ Bilirrubina (> 20 mg/dL) extremadamente alta.")
if creatinina > 10: errores.append("⚠️ Creatinina (> 10 mg/dL) muy alta.")
if sodio < 110 or sodio > 155: errores.append("⚠️ Sodio (110-155 mEq/L) fuera de rango.")
if suma_diametros_tumores < tamaño_tumor: errores.append("⚠️ Suma de diámetros no puede ser menor que el tamaño del tumor más grande.")

if errores:
    for error in errores:
        st.error(error)
    st.stop()

# --- Botón de Cálculo y Resultados ---
if st.button("📊 Calcular Scores, Pronóstico y Criterios de Trasplante"):

    # --- Cálculos Principales ---
    cp_score = calcular_ChildPugh(bilirrubina, albumina, INR, ascitis, encefalopatia_grado)
    cp_class = get_child_pugh_class(cp_score)
    albi_score = calcular_ALBI(bilirrubina, albumina)
    meld_score = calcular_MELD(creatinina, bilirrubina, INR)
    meld_na_score = calcular_MELD_Na(meld_score, sodio)
    bclc_estadio, bclc_trat = calcular_BCLC_corregido(cp_class, estado_performance, tamaño_tumor, número_tumores, invasion_vascular, metastasis)
    clip_score = calcular_CLIP(cp_class, AFP, invasion_vascular, número_tumores, tamaño_tumor)
    hklc_estadio, hklc_trat = calcular_HKLC(estado_performance, tamaño_tumor, número_tumores, invasion_vascular, metastasis, cp_class)
    art_score, art_riesgo = None, "No calculado"
    if respuesta_tumoral_tace != "No aplica / No evaluado":
         art_score, art_riesgo = calcular_ART(bilirrubina, bilirrubina_post_tace, cp_class, respuesta_tumoral_tace)

    # --- Evaluación Criterios de Trasplante ---
    # Solo si el paciente NO tiene invasión vascular NI metástasis (requisito básico para considerar trasplante por HCC)
    puede_trasplante_oncologico = not invasion_vascular and not metastasis
    cumple_milan = check_milan(número_tumores, tamaño_tumor) if puede_trasplante_oncologico else False
    cumple_ucsf = check_ucsf(número_tumores, tamaño_tumor, suma_diametros_tumores) if puede_trasplante_oncologico else False
    cumple_up_to_seven = check_up_to_seven(número_tumores, tamaño_tumor) if puede_trasplante_oncologico else False
    cumple_unos_optn_std = cumple_milan # El criterio estándar UNOS/OPTN para MELD exception se basa en Milán

    # --- Mostrar Resultados ---
    st.subheader("📈 Resultados Calculados y Pronóstico Estimado")
    st.markdown(f"**Paciente con ECOG {estado_performance}, Child-Pugh {cp_class} ({cp_score} pts), {número_tumores} nódulo(s), mayor de {tamaño_tumor} cm, suma diámetros {suma_diametros_tumores} cm, {'CON' if invasion_vascular else 'SIN'} invasión vascular, {'CON' if metastasis else 'SIN'} metástasis.**")
    st.markdown("---")

    res_col1, res_col2 = st.columns(2)

    # --- Columna 1: Función Hepática y Scores Generales ---
    with res_col1:
        st.markdown(f"**Función Hepática y Sistémica:**")
        # Child-Pugh
        st.metric(label="Child-Pugh Score", value=f"{cp_score} (Clase {cp_class})")
        with st.expander("Interpretación y Pronóstico Child-Pugh"):
            st.markdown("- **Clase A (5–6):** Compensada.\n- **Clase B (7–9):** Compromiso funcional.\n- **Clase C (10–15):** Descompensada.")
            st.markdown("**Pronóstico Estimado (Supervivencia general en cirrosis):**")
            st.markdown("- A: 1 año ~95%, 5 años ~50-60%\n- B: 1 año ~80%, 5 años ~30-40%\n- C: 1 año ~45%, 5 años ~10-20%")
            st.caption("Nota: Supervivencia puede ser peor en presencia de HCC activo.")

        # ALBI
        st.metric(label="ALBI Score", value=f"{albi_score}")
        with st.expander("Interpretación y Pronóstico ALBI"):
             st.markdown("- **Grado 1:** ≤ -2.60 (Mejor)\n- **Grado 2:** > -2.60 y ≤ -1.39 (Intermedio)\n- **Grado 3:** > -1.39 (Peor)")
             st.markdown("**Pronóstico Estimado:** Asociado con supervivencia post-tratamientos. Grado 3 implica peor supervivencia.")
             st.caption("[Ref. ALBI](https://pubmed.ncbi.nlm.nih.gov/25512453/)")

        # MELD / MELD-Na
        st.metric(label="MELD Score", value=f"{meld_score}")
        st.metric(label="MELD-Na Score", value=f"{meld_na_score}")
        with st.expander("Interpretación y Pronóstico MELD / MELD-Na"):
            st.markdown("Estiman mortalidad a 3 meses en lista de espera para trasplante hepático.")
            if meld_score < 10: mort = "~2%"
            elif meld_score <= 19: mort = "~6%"
            elif meld_score <= 29: mort = "~20%"
            elif meld_score <= 39: mort = "~50%"
            else: mort = ">70%"
            st.markdown(f"- Mortalidad estimada a 3m (MELD {meld_score}): {mort}")
            st.markdown("- MELD-Na refina la predicción (especialmente con hiponatremia).")
            st.caption("[Refs. MELD/MELD-Na]")

        # CLIP
        st.metric(label="CLIP Score", value=f"{clip_score}")
        with st.expander("Interpretación y Pronóstico CLIP"):
             st.markdown("- **Score 0-1:** Mejor pronóstico relativo.\n- **Score 2-3:** Intermedio.\n- **Score 4-6:** Peor pronóstico.")
             if clip_score <= 1: surv_clip = "~27-31 meses"
             elif clip_score <= 3: surv_clip = "~8-13 meses"
             else: surv_clip = "~1-3 meses"
             st.markdown(f"- Supervivencia Mediana Histórica Estimada: {surv_clip}")
             st.warning("⚠️ Datos de supervivencia CLIP antiguos. Usar con cautela.")
             st.caption("[Ref. CLIP](https://pubmed.ncbi.nlm.nih.gov/10733537/)")

    # --- Columna 2: Estadificación HCC y Trasplante ---
    with res_col2:
        st.markdown(f"**Estadificación y Tratamiento del HCC:**")
        # BCLC
        st.subheader(f"BCLC: {bclc_estadio}")
        st.info(f"**Recomendación Terapéutica Principal (BCLC):**\n{bclc_trat}")
        with st.expander("Pronóstico Estimado BCLC (Mediana de Supervivencia)"):
            if bclc_estadio == "Estadio 0 (Muy Temprano)": surv = "> 60 meses (>70% a 5 años)"
            elif bclc_estadio == "Estadio A (Temprano)": surv = "~ 36-60 meses (~50-70% a 5 años)"
            elif bclc_estadio == "Estadio B (Intermedio)": surv = "~ 20-30 meses"
            elif bclc_estadio == "Estadio C (Avanzado)": surv = "~ 12-18 meses (mejorando)"
            elif bclc_estadio == "Estadio D (Terminal)": surv = "~ 3-4 meses"
            else: surv = "Indeterminado"
            st.markdown(f"- {bclc_estadio}: {surv}")
            st.caption("Estimaciones. [Ref. EASL/BCLC]")

        # HKLC
        st.metric(label="HKLC Estadio (Simplificado)", value=f"{hklc_estadio}", delta=hklc_trat, delta_color="off")
        with st.expander("Interpretación HKLC"):
            st.markdown("Sistema pronóstico alternativo (validado ppal. en Asia).")
            st.markdown("**Advertencia:** Implementación muy simplificada.")
            st.caption("[Ref. HKLC](https://pubmed.ncbi.nlm.nih.gov/24583061/)")

        # ART Score (si aplica)
        if art_score is not None:
             st.metric(label="ART Score (Adaptado)", value=f"{art_score}", delta=art_riesgo, delta_color="inverse")
             with st.expander("Interpretación ART Score"):
                 st.markdown("Evalúa beneficio probable de **repetir TACE**.")
                 st.markdown("- **Bajo Riesgo (≤ 1.5):** Podría beneficiarse de TACE adicional.")
                 st.markdown("- **Alto Riesgo (> 1.5):** Probable bajo beneficio; considerar T. Sistémica.")
                 st.caption("[Ref. ART original](https://pubmed.ncbi.nlm.nih.gov/23316013/)")
        else:
             st.caption("ART Score no calculado (requiere datos post-TACE).")

    # --- Sección Dedicada a Criterios de Trasplante ---
    st.markdown("---")
    st.subheader(" Transplant Criteria Evaluation for HCC")
    st.markdown("Evaluación inicial de criterios oncológicos para trasplante hepático (requiere ausencia de invasión vascular macroscópica y metástasis extrahepáticas). La elegibilidad final depende de evaluación completa en centro de trasplante.")

    if not puede_trasplante_oncologico:
        st.error("❌ **No cumple criterios oncológicos básicos para trasplante** (presencia de invasión vascular y/o metástasis).")
    else:
        st.success("✅ **Cumple criterios oncológicos básicos para trasplante** (Ausencia de MVI y EHS). Evaluación de criterios específicos:")

        crit_col1, crit_col2 = st.columns(2)
        with crit_col1:
            st.markdown("**Criterios de Milán:** (Estándar)")
            st.markdown("`(1 tumor ≤ 5 cm) o (2-3 tumores, ≤ 3 cm cada uno)`")
            if cumple_milan:
                st.success("   **Cumple ✅**")
            else:
                st.warning("   **No Cumple ❌**")

            st.markdown("**Criterios UNOS/OPTN (Estándar):**")
            st.markdown("`(Alineados con Milán para MELD exception)`")
            if cumple_unos_optn_std:
                st.success("   **Cumple ✅**")
            else:
                 st.warning("   **No Cumple ❌**")
                 st.caption("   (Podría ser elegible via downstaging o criterios extendidos según centro)")


        with crit_col2:
            st.markdown("**Criterios UCSF:** (Expandidos)")
            st.markdown("`(1 tumor ≤ 6.5 cm) o (2-3 tumores, ≤ 4.5 cm el mayor Y suma diámetros ≤ 8 cm)`")
            if cumple_ucsf:
                st.success("   **Cumple ✅**")
            else:
                st.warning("   **No Cumple ❌**")

            st.markdown("**Criterios Up-to-Seven:** (Expandidos)")
            st.markdown("`(Suma [tamaño mayor tumor en cm] + [número de tumores] ≤ 7)`")
            if cumple_up_to_seven:
                st.success("   **Cumple ✅**")
            else:
                st.warning("   **No Cumple ❌**")

    st.markdown("---")
    st.success("Cálculos completados. **Interpretar en contexto clínico y discutir en comité multidisciplinario.**")

# --- Pie de página ---
st.markdown("---")
st.caption("Desarrollado con Python y Streamlit. V1.3 - Incluye Criterios de Trasplante. Revisar guías periódicamente.")
