import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Prueba ChatBot flotante", layout="wide")
st.title("Landing con ChatBot flotante")

DIALOGFLOW_AGENT_ID = "372a5eeb-31b9-4777-bfd4-a9a2af72e162"
CHAT_TITLE = "Antiqpa_ChatBot"

df_injection = f"""
<script src="https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1"></script>
<style>
  df-messenger {{
    position: fixed;
    bottom: 16px;
    right: 16px;
    z-index: 999999;
  }}
</style>
<df-messenger
  intent="WELCOME"
  chat-title="{CHAT_TITLE}"
  agent-id="{DIALOGFLOW_AGENT_ID}"
  language-code="es"
></df-messenger>
"""

# inyectamos directamente el snippet (sin iframe)
components.html(df_injection, height=0, width=0)
