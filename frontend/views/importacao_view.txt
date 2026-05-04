import streamlit as st
import requests
import pandas as pd
import os
from datetime import date, datetime

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("📥 GESTÃO DE IMPORTAÇÕES")
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # --- 1. INICIALIZAÇÃO DE ESTADO ---
    if "filter_params" not in st.session_state:
        st.session_state.filter_params = {
            "data_reg_ini": None, "data_reg_fim": None,
            "data_des_ini": None, "data_des_fim": None,
            "numero": "", "regime": "Todos", "modal": "Todos", "canal": "Todos"
        }
    if "search_performed" not in st.session_state:
        st.session_state.search_performed = False
    if "limit_list" not in st.session_state:
        st.session_state.limit_list = 30

    # --- 2. BUSCA DINÂMICA DE OPÇÕES PARA OS FILTROS ---
    @st.cache_data(ttl=600) # Cache de 10 minutos para não sobrecarregar
    def get_filtros_dinamicos():
        try:
            res = requests.get(f"{API_URL}/importacoes/opcoes-filtros", headers=headers)
            if res.status_code == 200: return res.json()
        except: pass
        return {"modais": [], "regimes": [], "canais": []}

    opcoes = get_filtros_dinamicos()

    # --- 3. FORMULÁRIO DE FILTROS ---
    with st.container(border=True):
        c1, c2, c3, c4 = st.columns(4)
        f_reg_ini = c1.date_input("Registro De", value=st.session_state.filter_params["data_reg_ini"])
        f_reg_fim = c2.date_input("Registro Até", value=st.session_state.filter_params["data_reg_fim"])
        f_des_ini = c3.date_input("Desembaraço De", value=st.session_state.filter_params["data_des_ini"])
        f_des_fim = c4.date_input("Desembaraço Até", value=st.session_state.filter_params["data_des_fim"])

        c5, c6, c7, c8 = st.columns(4)
        f_numero = c5.text_input("Número DI/DUIMP", value=st.session_state.filter_params["numero"])
        
        # Filtros Dinâmicos baseados no Banco de Dados
        lista_regimes = ["Todos"] + sorted(opcoes["regimes"])
        f_regime = c6.selectbox("Regime", lista_regimes, index=0)
        
        lista_modais = ["Todos"] + sorted(opcoes["modais"])
        f_modal = c7.selectbox("Modal", lista_modais, index=0)
        
        lista_canais = ["Todos"] + sorted(opcoes["canais"])
        f_canal = c8.selectbox("Canal", lista_canais, index=0)

        col_btn1, col_btn2, _ = st.columns([1, 1, 4])
        if col_btn1.button("🔍 Consultar", use_container_width=True, type="primary"):
            st.session_state.filter_params = {
                "data_reg_ini": f_reg_ini, "data_reg_fim": f_reg_fim,
                "data_des_ini": f_des_ini, "data_des_fim": f_des_fim,
                "numero": f_numero, "regime": f_regime, "modal": f_modal, "canal": f_canal
            }
            st.session_state.search_performed = True
            st.rerun()

        if col_btn2.button("🧹 Limpar", use_container_width=True):
            st.session_state.filter_params = {k: (None if "data" in k else "Todos") for k in st.session_state.filter_params}
            st.session_state.filter_params["numero"] = ""
            st.session_state.search_performed = False
            st.rerun()

    # --- 4. EXIBIÇÃO DOS RESULTADOS ---
    if st.session_state.search_performed:
        params = {}
        for k, v in st.session_state.filter_params.items():
            if v and v != "Todos":
                params[k] = v.isoformat() if isinstance(v, (date, datetime)) else v
        params["limit"] = st.session_state.limit_list

        try:
            response = requests.get(f"{API_URL}/importacoes", params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if data:
                    st.subheader(f"📋 {len(data)} Declarações Localizadas")
                    cols = st.columns([1.5, 0.8, 1.3, 2, 1, 1, 1, 1, 1, 1.2])
                    labels = ["DI/DUE", "Tipo", "CNPJ", "Importador", "Registro", "Desemb.", "Regime", "Modal", "Canal", "Ação"]
                    for col, label in zip(cols, labels): col.write(f"**{label}**")
                    st.divider()

                    for item in data:
                        r = st.columns([1.5, 0.8, 1.3, 2, 1, 1, 1, 1, 1, 1.2])
                        r[0].write(item.get('di_due', '-'))
                        r[1].write(item.get('tipo_di', '-'))
                        r[2].write(item.get('cnpj_importador', '-'))
                        r[3].write(item.get('importador', '-')[:15])
                        r[4].write(item.get('data_registro', '-'))
                        r[5].write(item.get('data_desembaraco', '-'))
                        r[6].write(item.get('regime', '-'))
                        
                        # CORREÇÃO MODAL: Removido o truncamento agressivo para garantir que o dado apareça
                        modal_val = item.get('modal')
                        r[7].write(modal_val if modal_val else '-')
                        
                        r[8].write(item.get('canal', '-'))
                        
                        if r[9].button("Detalhes", key=f"det_{item['id']}", use_container_width=True):
                            st.session_state.selected_di_id = item['id']
                            st.session_state.current_page = "di_due"
                            st.rerun()
                else:
                    st.info("Nenhum registro encontrado para os filtros aplicados.")
            else:
                st.error(f"Erro na API: {response.status_code}")
        except Exception as e:
            st.error(f"Falha de conexão: {e}")