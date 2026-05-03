import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("📥 GESTÃO DE IMPORTAÇÕES")

    # --- 1. INICIALIZAÇÃO DE ESTADO ---
    if "filter_params" not in st.session_state:
        st.session_state.filter_params = {
            "data_reg_ini": None, "data_reg_fim": None,
            "numero": "", "regime": "Todos", "modal": "Todos"
        }
    
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False

    if "limit_list" not in st.session_state:
        st.session_state.limit_list = 30

    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # --- 2. FORMULÁRIO DE FILTROS ---
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 2, 2])
        f_reg_ini = col1.date_input("Registro Inicial", value=st.session_state.filter_params["data_reg_ini"])
        f_reg_fim = col2.date_input("Registro Final", value=st.session_state.filter_params["data_reg_fim"])
        f_numero = col3.text_input("Número DI/DUIMP", value=st.session_state.filter_params["numero"])

        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        if col_btn1.button("🔍 Consultar", use_container_width=True, type="primary"):
            st.session_state.filter_params = {
                "data_reg_ini": f_reg_ini, "data_reg_fim": f_reg_fim,
                "numero": f_numero
            }
            st.session_state.search_performed = True
            st.rerun()

        if col_btn2.button("🧹 Limpar", use_container_width=True):
            st.session_state.filter_params = {"data_reg_ini": None, "data_reg_fim": None, "numero": ""}
            st.session_state.search_performed = False
            st.rerun()

    # --- 3. EXIBIÇÃO DOS RESULTADOS (APENAS APÓS CONSULTAR) ---
    if st.session_state.search_performed:
        params = st.session_state.filter_params
        clean_params = {k: v for k, v in params.items() if v}
        clean_params["limit"] = st.session_state.limit_list

        try:
            response = requests.get(f"{API_URL}/importacoes", params=clean_params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                
                if data:
                    st.subheader(f"📋 {len(data)} Declarações Localizadas")
                    
                    # Cabeçalho da Lista Estilizada
                    c_h1, c_h2, c_h3, c_h4, c_h5 = st.columns([2, 1, 3, 2, 1.5])
                    c_h1.write("**DI/DUE**")
                    c_h2.write("**Tipo**")
                    c_h3.write("**Importador**")
                    c_h4.write("**Data Reg.**")
                    c_h5.write("**Ação**")
                    st.divider()

                    # Renderização das Linhas (Uma a uma com botão próprio)
                    for item in data:
                        r1, r2, r3, r4, r5 = st.columns([2, 1, 3, 2, 1.5])
                        r1.write(f"**{item['di_due']}**")
                        r2.write(item.get('tipo_di', '-'))
                        r3.write(item.get('importador', '-')[:30])
                        r4.write(item.get('data_registro', '-'))
                        
                        # A mágica acontece aqui: botão direto na linha
                        if r5.button("Ver Detalhes", key=f"det_{item['id']}", use_container_width=True):
                            st.session_state.selected_di_id = item['id']
                            st.session_state.current_page = "di_due"
                            st.rerun()
                else:
                    st.info("Nenhum registro encontrado para os filtros aplicados.")
            else:
                st.error(f"Erro na API ({response.status_code})")
        except Exception as e:
            st.error(f"Falha na comunicação: {e}")

    # --- 4. EXPORTAÇÃO ---
    if st.session_state.search_performed:
        st.divider()
        c1, c2, _ = st.columns([2, 2, 4])
        if c1.button("📄 Relatório PDF", use_container_width=True):
            st.toast("Gerando PDF...")
        if c2.button("📊 Planilha Excel", use_container_width=True):
            st.toast("Gerando Excel...")