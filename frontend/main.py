import streamlit as st
import os
from PIL import Image
# Importação de todas as views
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

# --- 5. ESTILIZAÇÃO CUSTOMIZADA (CSS) ---
# Aqui definimos o Azul Marinho para a Sidebar e ajustamos as cores dos textos/botões
# Caso o tom de azul do logo seja diferente, basta ajustar o código Hexadecimal #002147
st.markdown("""
    <style>
        /* Cor de fundo da Sidebar */
        [data-testid="stSidebar"] {
            background-color: #002147;
        }

        /* Cor dos textos e ícones na Sidebar */
        [data-testid="stSidebar"] .stMarkdown, 
        [data-testid="stSidebar"] p, 
        [data-testid="stSidebar"] span,
        [data-testid="stSidebar"] h3 {
            color: white !important;
        }

        /* Estilização dos botões da Sidebar para combinar com o fundo escuro */
        [data-testid="stSidebar"] .stButton > button {
            background-color: transparent;
            color: white;
            border: 1px solid rgba(255, 255, 255, 0.2);
        }
        
        [data-testid="stSidebar"] .stButton > button:hover {
            border-color: white;
            background-color: rgba(255, 255, 255, 0.1);
            color: white;
        }

        /* Ajuste do Divider na Sidebar */
        [data-testid="stSidebar"] hr {
            border-top: 1px solid rgba(255, 255, 255, 0.2);
        }
    </style>
""", unsafe_allow_html=True)

# 2. Inicialização de Estados Globais (MANTIDO)
if "auth_token" not in st.session_state:
    st.session_state.auth_token = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# 3. Função da Sidebar (Painel de Navegação Lateral)
def render_sidebar():
    with st.sidebar:
        # Logo Centralizado
        try:
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
                st.session_state.auth_token = None
                st.session_state.chat_history = []
                st.session_state.current_page = "Home"
                st.rerun()

# 4. Controle de Fluxo (Roteamento de Páginas)
def main():
    if st.session_state.auth_token is None:
        login_view.render()
    else:
        render_sidebar()
        page = st.session_state.current_page
        
        if page == "Home":
            # Aqui você pode optar por usar o seu home_view.render() 
            # ou manter o markdown abaixo que já estava no seu main.py
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