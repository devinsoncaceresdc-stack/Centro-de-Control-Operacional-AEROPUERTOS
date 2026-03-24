import pandas as pd
import streamlit as st
from groq import Groq

#===CARGAR CSS Y JS=================================
def cargar_estilos():
    with open("styles.css", encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

    with open("script.js", encoding="utf-8") as f:
        st.markdown(f"<script>{f.read()}</script>", unsafe_allow_html=True)

cargar_estilos()

#===CONFIGURAR PAGINA ==============================
st.set_page_config(layout='wide')

st.markdown("""
<div class="dashboard-header">
    <h1>✈️ Centro de Control Operacional</h1>
    <p style="color:#8892b0;">Monitoreo Inteligente de Operaciones Aeroportuarias</p>
</div>
""", unsafe_allow_html=True)

#===CONFIGURAR API KEY==============================
api_key = st.secrets.get("GROQ_API_KEY")

if not api_key:
    st.error("⚠️ Falta configurar GROQ_API_KEY en Secrets")
    st.stop()

cliente = Groq(api_key=api_key)

#===SESSION STATE===================================
if "informe" not in st.session_state:
    st.session_state.informe = ""

#===CARGAR DATA===================================
archivo = st.file_uploader('Cargar archivo Excel (.xlsx)', type=['xlsx'])

if archivo is not None:
    df = pd.read_excel(archivo)

    filas, columnas = df.shape

    # KPI CARDS
    st.markdown(f"""
    <div style="display:flex; gap:20px; margin-bottom:20px;">
        <div class="kpi-card">
            <div class="kpi-title">Filas</div>
            <div class="kpi-value">{filas}</div>
        </div>
        <div class="kpi-card">
            <div class="kpi-title">Columnas</div>
            <div class="kpi-value">{columnas}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    nums = df.select_dtypes(include='number').columns.tolist()
    cats = df.select_dtypes(include='object').columns.tolist()

    resumen = [f'Filas: {filas}', f'Columnas: {columnas}']

    for col in nums:
        s = df[col].dropna()
        q1, q3 = s.quantile([0.25, 0.75])
        iqr = q3 - q1
        outliers = (s[(s < q1 - 1.5 * iqr) | (s > q3 + 1.5 * iqr)]).count()
        resumen.append(f'{col}: media={s.mean():.2f}, mediana={s.median():.2f}, std={s.std():.2f}, outliers={outliers}')
        
    for col in cats:
        top = df[col].value_counts().head(5)
        resumen.append(f'{col}: {dict(top)}')

    texto_resumen = '\n'.join(resumen)

    with st.expander('Resumen para Enviar al Modelo'):
        st.text(texto_resumen)

    #===GENERAR INFORME=================================
    if st.button('Generar Informe'):
        with st.spinner('Generando informe...'):
            try:
                prompt = f"""
                Actúa como un gerente responsable de la operación y la gestión del riesgo.

                Analiza:
                {texto_resumen}
                """

                respuesta = cliente.chat.completions.create(
                    model='llama-3.3-70b-versatile',
                    messages=[{'role': 'user', 'content': prompt}],
                    temperature=0.3,
                )

                st.session_state.informe = respuesta.choices[0].message.content

                st.success("✅ Informe generado")

            except Exception as e:
                st.error(f"❌ Error: {e}")

    #===MOSTRAR INFORME (SOLO UNA VEZ)===================
    if st.session_state.informe != "":
        st.subheader("📊 Informe generado")
        st.markdown(f"""
        <div style="background:rgba(255,255,255,0.05); padding:20px; border-radius:15px;">
        {st.session_state.informe}
        </div>
        """, unsafe_allow_html=True)

    #===CHAT=================================
    st.divider()
    pregunta = st.text_input('Pregunta sobre las estadísticas')

    if st.button('Consultar'):
        if not pregunta:
            st.warning("Escribe una pregunta")
        elif st.session_state.informe == "":
            st.warning("Primero debes generar el informe")
        else:
            with st.spinner('Consultando...'):
                try:
                    prompt_chat = f"""
                    Actúa como un gerente responsable de la operación y la gestión del riesgo.

                    Datos:
                    {texto_resumen}

                    Informe:
                    {st.session_state.informe}

                    Pregunta: {pregunta}
                    """

                    respuesta = cliente.chat.completions.create(
                        model='llama-3.3-70b-versatile',
                        messages=[{'role': 'user', 'content': prompt_chat}],
                        temperature=0.3,
                    )

                    st.markdown(respuesta.choices[0].message.content)

                except Exception as e:
                    st.error(f"❌ Error: {e}")
