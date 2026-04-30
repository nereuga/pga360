import streamlit as st
import os
from PIL import Image
# Importação de todas as views, incluindo a nova Biblioteca
from views import (
    login_view, 
    importacao_view, 
    di_due_view, 
    produto_view, 
    assistente_ia_view, 
    biblioteca_insights_view
)

# 1. Configurações da Página
st.set_page_config(
    page_title="PGA-360 | Gestão Aduaneira Inteligente", 
    page_icon="🚢", 
    layout="wide"
)

# 2. Inicialização de Estados Globais (Contexto de Sessão)
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None # Para reuso da Biblioteca de Insights

# 3. Função da Sidebar (Painel de Navegação Lateral)
def render_sidebar():
    with st.sidebar:
        # Logo Centralizado
        try:
            # Pasta assets deve existir no diretório frontend
            logo = Image.open("assets/logo_pga360_neg.png")
            st.image(logo, use_column_width=True)
        except:
            st.title("🚢 PGA-360")
        
        st.divider()
        
        # Menu: Fluxo de Operações
        st.subheader("🔄 Fases Aduaneiras")
        st.button("📦 Embarque...", disabled=True, use_container_width=True)
        st.button("📄 Invoice...", disabled=True, use_container_width=True)
        
        if st.button("📥 Importação (DI/DUE)", use_container_width=True):
            st.session_state.current_page = "Importacao"
            st.rerun()
            
        st.button("💰 Financeiro...", disabled=True, use_container_width=True)
        
        st.divider()
        
        # Menu: Inteligência e Dados
        st.subheader("🤖 Inteligência Analítica")
        if st.button("💬 Assistente de IA", use_container_width=True):
            st.session_state.current_page = "IA"
            st.rerun()

        if st.button("📚 Biblioteca de Insights", use_container_width=True):
            st.session_state.current_page = "Biblioteca"
            st.rerun()

        st.sidebar.divider()
        
        # Rodapé da Sidebar: Info do Usuário e Logout
        if st.session_state.auth_token:
            st.caption(f"Logado como: {st.session_state.get('user_email', 'Usuário')}")
            if st.button("🚪 Sair do Sistema", use_container_width=True):
                # Limpa todo o estado para segurança
                st.session_state.auth_token = None
                st.session_state.chat_history = []
                st.session_state.current_page = "Home"
                st.rerun()

# 4. Controle de Fluxo (Roteamento de Páginas)
def main():
    if st.session_state.auth_token is None:
        # ETAPA 1: Autenticação Supabase
        login_view.render()
    else:
        # ETAPA 2: Acesso ao Sistema Operacional
        render_sidebar()
        page = st.session_state.current_page
        
        if page == "Home":
            st.title("Bem-vindo ao PGA-360")
            st.info("Utilize o menu lateral para gerenciar as operações ou consultar a inteligência de dados.")
            st.markdown("""
            ### Resumo do Ambiente
            - **Base de Dados:** PostgreSQL (Sincronizada via ETL Oracle)
            - **IA:** Motor Gemini 1.5 (Analítico)
            - **Segurança:** Supabase Auth + Aprovação Manual
            """)
            
        elif page == "Importacao":
            importacao_view.render()
            
        elif page == "di_due":
            di_due_view.render()
            
        elif page == "Produto":
            produto_view.render()
            
        elif page == "IA":
            assistente_ia_view.render()
            
        elif page == "Biblioteca":
            biblioteca_insights_view.render()

if __name__ == "__main__":
    main()