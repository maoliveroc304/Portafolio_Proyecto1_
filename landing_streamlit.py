import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Prueba ChatBot flotante", layout="wide")
st.title("Prueba: Dialogflow Messenger flotante")

# ---------------------------------------------------------------------
# Sustituye por tu agent-id EXACTO (cópialo desde Dialogflow Console)
DIALOGFLOW_AGENT_ID = "372a5eeb-31b9-4777-bfd4-a9a2af72e162"
CHAT_TITLE = "Antiqpa_ChatBot"
# ---------------------------------------------------------------------

# Texto informativo (opcional)
st.write("Cargando widget Dialogflow Messenger — si no aparece, revisa consola del navegador (F12).")

# HTML que inyectamos: script dinámico + df-messenger + estilos para forzar visibilidad
injection = f"""
<style>
/* Forzamos que el df-messenger se muestre por encima de todo y en esquina */
df-messenger {{
  position: fixed !important;
  right: 20px !important;
  bottom: 20px !important;
  z-index: 2147483647 !important; /* número grande para sobreponer */
  box-shadow: 0 6px 24px rgba(0,0,0,0.2);
}}
/* Ajuste responsivo si quieres verlo más grande en móvil */
@media (max-width: 600px) {{
  df-messenger {{ right: 8px !important; bottom: 8px !important; width: calc(100% - 16px) !important; }}
}}
</style>

<div id="df-root"></div>
<script>
(function() {{
  // Si ya existe, no lo inyectamos de nuevo
  if (document.querySelector('df-messenger')) {{
    console.info("df-messenger ya presente");
    return;
  }}

  // Cargamos el script de Dialogflow dinámicamente para evitar bloqueos de carga prematura
  var s = document.createElement('script');
  s.src = "https://www.gstatic.com/dialogflow-console/fast/messenger/bootstrap.js?v=1";
  s.onload = function() {{
    console.info("Dialogflow script cargado");
    // Creamos el elemento df-messenger tras cargar el script
    var df = document.createElement('df-messenger');
    df.setAttribute('intent', 'WELCOME');
    df.setAttribute('chat-title', "{CHAT_TITLE}");
    df.setAttribute('agent-id', "{DIALOGFLOW_AGENT_ID}");
    df.setAttribute('language-code', 'es');
    document.body.appendChild(df);

    // Pequeño retardo para forzar re-render y luego forzar estilos (por si acaso)
    setTimeout(function() {{
      var el = document.querySelector('df-messenger');
      if(el) {{
        el.style.position = 'fixed';
        el.style.right = '20px';
        el.style.bottom = '20px';
        el.style.zIndex = '2147483647';
      }} else {{
        console.warn("No se encontró df-messenger tras la carga");
      }}
    }}, 300);
  }};
  s.onerror = function(err) {{
    console.error("Error cargando script Dialogflow:", err);
  }};
  document.head.appendChild(s);
}})();
</script>
"""

# Inyectamos el HTML. Height pequeño para no romper el layout; el widget es flotante.
components.html(injection, height=10)
