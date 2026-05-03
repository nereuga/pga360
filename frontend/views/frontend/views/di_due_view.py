import streamlit as st
import requests
import pandas as pd
import os
from datetime import datetime

# Limpeza da API_URL para evitar barras duplas // que causam erro 404
API_URL = os.getenv("API_URL", "http://backend-360:8000").rstrip("/")

def render():
    # Recupera o ID da sessão
    di_id = st.session_state.get("selected_di_id")
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    
    # 1. Validação de Segurança: Se não houver ID, volta para a lista
    if not di_id:
        st.warning("⚠️ Nenhum processo selecionado para detalhamento.")
        if st.button("Voltar para Lista de Importação"):
            st.session_state.current_page = "Importacao"
            st.rerun()
        return

    # --- 2. BUSCA DE DADOS COM TRATAMENTO ANTI-404 ---
    try:
        # Chamada da Capa (ID deve ser passado como string na URL)
        res_di = requests.get(f"{API_URL}/di-due/{str(di_id)}", headers=headers)
        
        if res_di.status_code == 404:
            st.error(f"❌ Erro 404: O processo ID {di_id} não foi encontrado no servidor.")
            if st.button("Voltar e tentar novamente"):
                st.session_state.current_page = "Importacao"
                st.rerun()
            return
        elif res_di.status_code != 200:
            st.error(f"⚠️ Erro na API ({res_di.status_code}): {res_di.text}")
            return

        di = res_di.json()

        # Busca Itens e Taxas
        res_itens = requests.get(f"{API_URL}/di-due/{str(di_id)}/produtos", headers=headers)
        itens = res_itens.json() if res_itens.status_code == 200 else []

        res_taxas = requests.get(f"{API_URL}/di-due/{str(di_id)}/taxas-moedas", headers=headers)
        taxas_negociadas = res_taxas.json() if res_taxas.status_code == 200 else []
        
    except Exception as e:
        st.error(f"💥 Falha de comunicação com o backend: {e}")
        return

    # --- 3. INTERFACE VISUAL (MANTIDA E BLINDADA) ---
    if st.button("⬅️ Voltar para Lista"):
        st.session_state.current_page = "Importacao"
        st.rerun()
    
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.markdown(f"**Tipo DI**\n\n{di.get('tipo_di', '-')}")
        c2.markdown(f"**DI/DUE**\n\n{di.get('di_due', '-')}")
        c3.markdown(f"**CNPJ**\n\n{di.get('cnpj_importador', '-')}")
        c4.markdown(f"**Importador**\n\n{di.get('importador', '-')[:20]}")
        c5.markdown(f"**Regime**\n\n{di.get('regime', '-')}")
        c6.markdown(f"**Versão**\n\n{di.get('versao', '-')}")

    aba1, aba2, aba3 = st.tabs(["📄 DI/DUIMP", "📊 Resumo Importação", "📦 Produtos"])

    with aba1:
        s1, s2, s3 = st.tabs(["Dados Principais", "Dados de Carga", "Tipos Embalagem"])
        with s1:
            ca, cb, cc = st.columns(3)
            ca.text_input("Endereço", value=di.get('endereco_importador') or "", disabled=True)
            cb.text_input("Canal", value=di.get('canal') or "", disabled=True)
            cc.text_input("Regime Aduaneiro", value=di.get('regime') or "", disabled=True)
            
            d_val = di.get('data_registro')
            try:
                d_reg = datetime.strptime(d_val, "%Y-%m-%d").date() if d_val else None
            except:
                d_reg = None
            st.date_input("Data Registro", value=d_reg, disabled=True)

        with s2:
            ci, cj, ck = st.columns(3)
            ci.text_input("RCR / Termo Resp.", value=di.get('rcr') or "", disabled=True)
            cj.text_input("Unidade Entrada", value=di.get('urf_entrada') or "", disabled=True)
            ck.text_input("AWB Master", value=di.get('awb_master') or "", disabled=True)
            
            cr, cs = st.columns(2)
            peso_b = float(di.get('peso_bruto') or 0)
            peso_l = float(di.get('peso_liquido') or 0)
            cr.metric("Peso Bruto (KG)", f"{peso_b:,.3f}")
            cs.metric("Peso Líquido (KG)", f"{peso_l:,.3f}")

        with s3:
            val_emb = di.get('tipos_embalagem') or "Não informado"
            st.info(f"Quantidade total de volumes/embalagens: **{val_emb}**")

    with aba2:
        st.subheader("Resumo Financeiro")
        t_dolar = float(di.get('taxa_dolar') or 1.0)
        total_fob = float(di.get('total_fob') or 0)
        data_fin = [
            ["Produto", "USD", f"{total_fob:,.2f}", f"{(total_fob * t_dolar):,.2f}"],
            ["Frete", "USD", f"{float(di.get('total_frete') or 0):,.2f}", f"{(float(di.get('total_frete') or 0) * t_dolar):,.2f}"],
            ["Seguro", "USD", f"{float(di.get('total_seguro') or 0):,.2f}", f"{(float(di.get('total_seguro') or 0) * t_dolar):,.2f}"]
        ]
        st.table(pd.DataFrame(data_fin, columns=["Rubrica", "Moeda", "Valor Moeda", "Valor BRL"]))
        
        if taxas_negociadas:
            st.write("**Taxas de Moedas nos Itens:**")
            st.dataframe(pd.DataFrame(taxas_negociadas), hide_index=True, use_container_width=True)

    with aba3:
        if itens:
            st.dataframe(pd.DataFrame(itens), hide_index=True, use_container_width=True)
        else:
            st.warning("Nenhum produto encontrado para esta declaração.")