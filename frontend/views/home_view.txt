import streamlit as st

def render():
    st.title("🚢 PGA-360 | Gestão Aduaneira")
    st.subheader("Bem-vindo ao centro de comando operacional.")
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        with st.container(border=True):
            st.markdown("### 📊 Status do Ambiente")
            st.success("Conectado à Nuvem (PostgreSQL)")
            st.success("Conectado à Intranet (Oracle 8i)")
            st.info("Última sincronização ETL: Hoje às 06:00")
            
    with col2:
        with st.container(border=True):
            st.markdown("### 🤖 Sugestão da IA (Insight Ativo)")
            st.warning("⚠️ Detectamos 3 processos em Canal Vermelho com Lead Time acima da média histórica.")
            if st.button("Analisar Atrasos"):
                st.session_state.pending_question = "Quais processos em canal vermelho estão com lead time de despacho acima da média?"
                st.session_state.current_page = "IA"
                st.rerun()