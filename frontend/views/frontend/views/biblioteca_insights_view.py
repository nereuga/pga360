import streamlit as st
import requests
import os
import pandas as pd

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("📚 Biblioteca de Insights")
    st.markdown("Reutilize consultas e análises estratégicas já validadas pelo sistema.")

    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # --- 1. PAINEL DE CONTROLE (SYNC) ---
    with st.expander("⚙️ Painel de Controle de Dados", expanded=False):
        st.subheader("Sincronização com Oracle 8i")
        st.write("Última atualização: Hoje às 06:00 (Agendado)")
        if st.button("🔄 Forçar Sincronização Agora", type="primary"):
            with st.spinner("Solicitando carga ao motor de ETL..."):
                res = requests.post(f"{API_URL}/admin/sync-oracle", headers=headers)
                if res.status_code == 200:
                    st.success(res.json()['status'])
                else:
                    st.error("Erro ao disparar sincronização.")

    st.divider()

    # --- 2. FILTRO DE CONSULTAS ANTERIORES ---
    st.subheader("🔍 Pesquisar no Histórico de Inteligência")
    busca = st.text_input("Filtrar por termo (ex: Halliburton, Canal Vermelho, Impostos...)")

    try:
        res = requests.get(f"{API_URL}/admin/ai-history", headers=headers, params={"search": busca})
        if res.status_code == 200:
            history_data = res.json()
            if history_data:
                df_hist = pd.DataFrame(history_data)
                
                # Exibição elegante das consultas
                for _, row in df_hist.iterrows():
                    with st.container(border=True):
                        c1, c2 = st.columns([4, 1])
                        c1.write(f"**Pergunta:** {row['question']}")
                        c1.caption(f"Frequência de uso: {row['usage_count']} vezes")
                        
                        # Botão para reutilizar a pergunta
                        if c2.button("🔁 Reutilizar", key=f"reuse_{row['id']}"):
                            # Injeta a pergunta no chat da IA e redireciona
                            st.session_state.pending_question = row['question']
                            st.session_state.current_page = "IA"
                            st.rerun()
                            
                        with st.expander("Ver lógica SQL aplicada"):
                            st.code(row['sql_query'], language="sql")
            else:
                st.info("Nenhuma consulta encontrada com este termo.")
    except Exception as e:
        st.error(f"Erro ao carregar biblioteca: {e}")