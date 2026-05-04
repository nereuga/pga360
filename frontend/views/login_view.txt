import streamlit as st
from supabase import create_client, Client
import os
import requests

# Configurações do Supabase extraídas do ambiente
url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)
API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("🔒 Acesso ao Sistema PGA-360")
    st.caption("Gestão Aduaneira Integrada com Inteligência Artificial")
    
    aba_login, aba_registro = st.tabs(["Fazer Login", "Solicitar Novo Acesso"])

    # --- TAB 1: LOGIN ---
    with aba_login:
        with st.form("form_login"):
            email = st.text_input("E-mail corporativo")
            password = st.text_input("Senha", type="password")
            btn_login = st.form_submit_button("Entrar no Sistema", use_container_width=True)

            if btn_login:
                try:
                    # Tenta autenticar no Supabase
                    res = supabase.auth.sign_in_with_password({"email": email, "password": password})
                    
                    # Se logou, guardamos o token JWT e o e-mail na sessão
                    st.session_state.auth_token = res.session.access_token
                    st.session_state.user_email = email
                    
                    st.success("✅ Autenticação realizada! Carregando ambiente operacional...")
                    st.rerun()
                except Exception as e:
                    st.error("❌ Acesso negado: Verifique seu e-mail, senha ou se seu cadastro já foi aprovado.")
                    st.info("Dica: Verifique se você confirmou o link enviado para seu e-mail.")

    # --- TAB 2: REGISTRO (CREDENCIAMENTO EM 2 ETAPAS) ---
    with aba_registro:
        st.markdown("### Solicitação de Credenciamento")
        st.write("O acesso ao PGA-360 é restrito e exige validação em duas etapas.")
        
        with st.form("form_registro"):
            new_email = st.text_input("E-mail corporativo (será seu login)")
            new_password = st.text_input("Crie uma senha forte (mín. 6 caracteres)", type="password")
            perfil_desejado = st.selectbox(
                "Nível de acesso solicitado", 
                ["consulta", "operacional", "diretoria"],
                help="Sujeito à alteração pelo administrador conforme cargo."
            )
            
            st.divider()
            btn_reg = st.form_submit_button("🚀 Iniciar Credenciamento", use_container_width=True)

            if btn_reg:
                if len(new_password) < 6:
                    st.warning("A senha deve ter no mínimo 6 caracteres.")
                else:
                    try:
                        # ETAPA 1: Registro no Supabase (Dispara e-mail de confirmação automaticamente)
                        res = supabase.auth.sign_up({"email": new_email, "password": new_password})
                        
                        if res.user:
                            # ETAPA 2: Registro no banco local do PGA-360 via API do Backend
                            # O usuário é criado com 'is_aprovado = False'
                            payload = {
                                "supabase_uid": res.user.id,
                                "email": new_email,
                                "perfil": perfil_desejado
                            }
                            
                            reg_res = requests.post(f"{API_URL}/auth/registrar-perfil", json=payload)
                            
                            if reg_res.status_code == 200:
                                st.success("📩 **Etapa 1 concluída com sucesso!**")
                                st.info(f"""
                                **Próximos passos:**
                                1. Acesse o e-mail **{new_email}** e clique no link de confirmação.
                                2. Após confirmar, a diretoria será notificada para realizar a **Etapa 2 (Aprovação de Perfil)**.
                                3. Você receberá um aviso assim que o acesso for liberado.
                                """)
                                st.balloons()
                            else:
                                st.error("Erro ao sincronizar perfil local. Contate a TI.")
                    except Exception as e:
                        # Trata erro de e-mail já existente ou outros erros do Supabase
                        st.error(f"Não foi possível realizar o cadastro: {str(e)}")

    # Rodapé da tela de login
    st.sidebar.warning("⚠️ Sistema restrito a funcionários autorizados. Todas as consultas são monitoradas via log de auditoria.")