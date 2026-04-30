import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    st.title("📥 IMPORTAÇÃO")

    # --- 1. INICIALIZAÇÃO DE ESTADO DE FILTROS E PAGINAÇÃO ---
    if "filter_params" not in st.session_state:
        st.session_state.filter_params = {
            "data_reg_ini": None, "data_reg_fim": None,
            "data_des_ini": None, "data_des_fim": None,
            "numero": "", "regime": "Todos", "modal": "Todos", "canal": "Todos"
        }
    if "limit_list" not in st.session_state:
        st.session_state.limit_list = 30

    # Preparação do Header de Autenticação (Requisito de Segurança Passo 11/12)
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}

    # --- 2. FORMULÁRIO DE FILTROS ---
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns(4)
        f_reg_ini = col1.date_input("Data Registro Inicial", value=None)
        f_reg_fim = col2.date_input("Data Registro Final", value=None)
        f_des_ini = col3.date_input("Data Desembaraço Inicial", value=None)
        f_des_fim = col4.date_input("Data Desembaraço Final", value=None)

        col5, col6, col7, col8 = st.columns(4)
        f_numero = col5.text_input("Número DI/DUIMP", placeholder="Ex: 24/...")
        f_regime = col6.selectbox("Regime", ["Todos", "CONSUMO", "ADMISSAO TEMPORARIA", "DRAWBACK"])
        f_modal = col7.selectbox("Modal", ["Todos", "(Z1)OCEAN-CONTAINER", "(Z2)AIR", "(Z3)ROAD"])
        f_canal = col8.selectbox("Canal", ["Todos", "Verde", "Amarelo", "Vermelho", "Cinza"])

        btn_col1, btn_col2, _ = st.columns([1, 1, 4])
        if btn_col1.button("🔍 Consultar", use_container_width=True, type="primary"):
            st.session_state.filter_params = {
                "data_reg_ini": f_reg_ini, "data_reg_fim": f_reg_fim,
                "data_des_ini": f_des_ini, "data_des_fim": f_des_fim,
                "numero": f_numero, "regime": f_regime, "modal": f_modal, "canal": f_canal
            }
            st.session_state.limit_list = 30 
            st.rerun()

        if btn_col2.button("🧹 Limpar Filtro", use_container_width=True):
            for key in st.session_state.filter_params:
                st.session_state.filter_params[key] = None if "data" in key else "Todos"
            st.session_state.limit_list = 30
            st.rerun()

    # --- 3. BUSCA DE DADOS VIA API (COM TOKEN) ---
    params = st.session_state.filter_params
    clean_params = {k: (v if v != "Todos" else None) for k, v in params.items()}
    clean_params["limit"] = st.session_state.limit_list

    data = []
    try:
        # Note o uso de headers=headers para passar o Token JWT
        response = requests.get(f"{API_URL}/importacoes", params=clean_params, headers=headers)
        if response.status_code == 200:
            data = response.json()
        elif response.status_code == 403:
            st.error("Acesso Negado: Usuário ainda não aprovado na Etapa 2.")
        else:
            st.error(f"Erro ao consultar base: {response.text}")
    except Exception as e:
        st.error(f"Falha de conexão com o backend: {e}")

    # --- 4. TABELA DE RESULTADOS ---
    if data:
        df = pd.DataFrame(data)
        df_display = df.rename(columns={
            "di_due": "Número DI/DUIMP",
            "tipo_di": "Tipo",
            "cnpj_importador": "CNPJ",
            "importador": "Importador",
            "data_registro": "Data Registro",
            "data_desembaraco": "Data Desembaraço"
        })

        st.subheader("Lista de Declarações Localizadas")
        event = st.dataframe(
            df_display,
            column_order=("Número DI/DUIMP", "Tipo", "CNPJ", "Importador", "Data Registro", "Data Desembaraço"),
            hide_index=True,
            use_container_width=True,
            on_select="rerun",
            selection_mode="single-row"
        )

        if event.selection.rows:
            selected_index = event.selection.rows[0]
            st.session_state.selected_di_id = df.iloc[selected_index]['id']
            st.session_state.current_page = "di_due"
            st.rerun()

        if len(data) >= st.session_state.limit_list:
            if st.button(f"Mostrar mais 50 registros..."):
                st.session_state.limit_list += 50
                st.rerun()
    else:
        st.info("Nenhum registro encontrado para os filtros aplicados.")

    # --- 5. BOTÕES DE RODAPÉ E EXPORTAÇÃO (MERGE PASSO 13) ---
    st.divider()
    footer_col1, footer_col2, footer_col3, _ = st.columns([1.5, 1.5, 1, 3])
    
    # Botão de Exportação PDF
    if footer_col1.button("📄 Gerar Relatório (PDF)", use_container_width=True):
        if data:
            with st.spinner("Gerando arquivo profissional..."):
                try:
                    res_pdf = requests.post(
                        f"{API_URL}/exportar/pdf", 
                        headers=headers, 
                        json={"data": data, "title": "Lista_Importacoes_PGA360"}
                    )
                    if res_pdf.status_code == 200:
                        st.download_button(
                            label="📥 Baixar PDF",
                            data=res_pdf.content,
                            file_name=f"pga360_importacao_{datetime.now().strftime('%Y%m%d')}.pdf",
                            mime="application/pdf",
                            use_container_width=True
                        )
                    else:
                        st.error("Erro do servidor ao gerar PDF.")
                except Exception as e:
                    st.error(f"Erro na exportação: {e}")
        else:
            st.warning("Não há dados na lista para exportar.")

    # Botão de Exportação Excel
    if footer_col2.button("📊 Gerar Planilha (XLSX)", use_container_width=True):
        if data:
            with st.spinner("Preparando Excel..."):
                try:
                    res_xls = requests.post(
                        f"{API_URL}/exportar/excel", 
                        headers=headers, 
                        json={"data": data}
                    )
                    if res_xls.status_code == 200:
                        st.download_button(
                            label="📥 Baixar Excel",
                            data=res_xls.content,
                            file_name=f"pga360_dados_{datetime.now().strftime('%Y%m%d')}.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                            use_container_width=True
                        )
                except Exception as e:
                    st.error(f"Erro na exportação: {e}")

    if footer_col3.button("🚪 Sair", use_container_width=True):
        st.session_state.current_page = "Home"
        st.rerun()