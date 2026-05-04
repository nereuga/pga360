import streamlit as st
import requests
import os
import json
import plotly.express as px

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("🤖 Assistente de IA Analítico")
    st.markdown("Consulte a base de dados via linguagem natural e gere insights instantâneos.")

    # Cabeçalho de Autenticação
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # Lógica de Reuso da Biblioteca:
    # Se existir uma pergunta pendente, o chat inicia com ela automaticamente
    if st.session_state.get("pending_question"):
        prompt = st.session_state.pending_question
        st.session_state.pending_question = None # Limpa para a próxima
    else:
        prompt = st.chat_input("Ex: Qual o valor total de impostos por canal em 2024?")

    if prompt:
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        with st.spinner("IA traduzindo para SQL e analisando dados..."):
            try:
                res = requests.post(f"{API_URL}/ask-ai", headers=headers, json={"question": prompt}).json()
                
                # Processamento de Gráficos (Output Parsing)
                full_text = res['answer']
                chart_obj = None
                if "DATA_CHART:" in full_text:
                    parts = full_text.split("DATA_CHART:")
                    main_msg = parts[0].strip()
                    try:
                        chart_obj = json.loads(parts[1].strip())
                    except: chart_obj = None
                else:
                    main_msg = full_text

                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": main_msg,
                    "sql": res.get('sql'),
                    "chart": chart_obj
                })
            except Exception as e:
                st.error(f"Erro na IA: {e}")

    # Renderização do Histórico
    for m in st.session_state.chat_history:
        with st.chat_message(m["role"]):
            st.write(m["content"])
            
            # Se houver gráfico
            if m.get("chart"):
                c = m["chart"]
                if c["type"] == "pie":
                    st.plotly_chart(px.pie(names=c["labels"], values=c["values"], hole=0.4), use_container_width=True)
                elif c["type"] == "bar":
                    st.plotly_chart(px.bar(x=c["labels"], y=c["values"]), use_container_width=True)
            
            # Se houver SQL (Transparência para a TI)
            if m.get("sql"):
                with st.expander("👁️ Ver lógica SQL aplicada"):
                    st.code(m["sql"], language="sql")