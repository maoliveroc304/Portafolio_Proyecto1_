# landing_streamlit.py
import streamlit as st
import streamlit.components.v1 as components

# ---------- CONFIG ----------
POWER_BI_EMBED_URL = "https://app.powerbi.com/view?r=REPLACE_WITH_YOUR_EMBED_URL"
DIALOGFLOW_AGENT_ID = "your-dialogflow-agent-id"  # reemplaza
CHAT_TITLE = "Mi ChatBot"
PYTHON_PROJECTS = [
    {"title":"Análisis ventas — Python", "desc":"Notebook ETL + forecast", "repo":"https://github.com/usuario/ventas-forecast", "demo":"https://share.streamlit.io/usuario/ventas-app/main/app.py"},
    {"title":"API model-deploy", "desc":"Flask + Docker", "repo":"https://github.com/usuario/model-deploy", "demo": None},
]
HTML_PROJECTS = {
    "mi-sitio-1": {"title":"Landing Adscript — Proyecto A", "url":"https://usuario.github.io/mi-sitio-1/"},
    "mi-sitio-2": {"title":"Mini-app HTML — Proyecto B", "url":"https://usuario.github.io/mi-sitio-2/"},
}
# ----------------------------

st.set_page_config(page_title="Portfolio · PowerBI · Dialogflow", layout="wide")
st.title("Landing — Proyectos: Power BI · Python · HTML · ChatBot")

col1, col2 = st.columns((2,1))

with col1:
    st.subheader("Power BI")
    st.write("Si tu informe es embebible, cámbialo aquí abajo.")
    # Opción simple: iframe via components.iframe
    components.iframe(POWER_BI_EMBED_URL, height=560, scrolling=True)

    st.subheader("Proyectos Python")
    for p in PYTHON_PROJECTS:
        st.markdown(f"**{p['title']}**  \n{p['desc']}")
        cols = st.columns([1,1,1])
        cols[0].markdown(f"[Repo]({p['repo']})")
        cols[1].markdown(f"[Demo]({p['demo']})" if p.get('demo') else "")
        st.divider()

with col2:
    st.subheader("HTML / Micro-sitios (Adscript)")
    st.write("Recomendación: aloja en GitHub Pages o Netlify y embebe con iframe.")
    for slug, meta in HTML_PROJECTS.items():
        st.markdown(f"**{meta['title']}**")
        st.markdown(f"[Abrir]({meta['url']})")
        st.markdown(f"Embed (preview abajo):")
        # embed preview, si URL pública
        components.iframe(meta['url'], height=260)
        st.divider()

    st.subheader("ChatBot — Dialogflow Messenger")
    st.write("Si la integración pública está habilitada, inyectamos df-messenger aquí.")
    df_html = f'''
    <script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
<df-messenger
  intent="WELCOME"
  chat-title="Antiqpa_ChatBot"
  agent-id="372a5eeb-31b9-4777-bfd4-a9a2af72e162"
  language-code="es"
></df-messenger>
    components.html(df_html, height=420)

st.caption("Nota: para embeds con tokens/ACL usa un backend seguro. Streamlit puede manejar lógica server-side, pero evita exponer secretos en el frontend.")
