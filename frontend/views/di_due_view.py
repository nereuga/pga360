import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    di_id = st.session_state.selected_di_id
    headers = {"Authorization": f"Bearer {st.session_state.auth_token}"}
    
    if not di_id:
        st.warning("Nenhum processo selecionado.")
        return

    try:
        res_di = requests.get(f"{API_URL}/di-due/{di_id}", headers=headers)
        di = res_di.json()
        res_itens = requests.get(f"{API_URL}/di-due/{di_id}/produtos", headers=headers)
        itens = res_itens.json()
        res_taxas = requests.get(f"{API_URL}/di-due/{di_id}/taxas-moedas", headers=headers)
        taxas_negociadas = res_taxas.json()
    except Exception as e:
        st.error(f"Erro de conexão: {e}")
        return

    # --- TOPO E VOLTAR ---
    if st.button("⬅️ Voltar para Lista"):
        st.session_state.current_page = "Importacao"
        st.rerun()
    
    # Cabeçalho com fontes uniformes (Markdown em vez de Metric)
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.markdown(f"**Tipo DI**  \n{di.get('tipo_di')}")
        c2.markdown(f"**DI/DUE**  \n{di.get('di_due')}")
        c3.markdown(f"**CNPJ**  \n{di.get('cnpj_importador')}")
        c4.markdown(f"**Importador**  \n{di.get('importador')[:20]}")
        c5.markdown(f"**Regime**  \n{di.get('regime')}")
        c6.markdown(f"**Versão**  \n{di.get('versao')}")

    aba1, aba2, aba3 = st.tabs(["📄 DI/DUIMP", "📊 Resumo Importação", "📦 Produtos"])

    with aba1:
        s1, s2, s3 = st.tabs(["Dados Principais", "Dados de Carga", "Tipos Embalagem"])
        with s1:
            ca, cb, cc = st.columns(3)
            ca.text_input("Endereço", value=di.get('endereco_importador'), disabled=True)
            cb.text_input("Canal", value=di.get('canal'), disabled=True)
            cc.text_input("Regime Aduaneiro", value=di.get('regime'), disabled=True)
            # Datas com tratamento para evitar erro se nulo
            d_reg = pd.to_datetime(di.get('data_registro')) if di.get('data_registro') else None
            st.date_input("Data Registro", value=d_reg, disabled=True)

        with s2:
            ci, cj, ck = st.columns(3)
            ci.text_input("RCR / Termo Resp.", value=di.get('rcr'), disabled=True)
            cj.text_input("Unidade Entrada", value=di.get('urf_entrada'), disabled=True)
            ck.text_input("AWB Master", value=di.get('awb_master'), disabled=True)
            
            # CORREÇÃO DO ERRO 6: Tratamento de None em valores numéricos
            cr, cs = st.columns(2)
            peso_b = float(di.get('peso_bruto') or 0)
            peso_l = float(di.get('peso_liquido') or 0)
            cr.metric("Peso Bruto (KG)", f"{peso_b:,.3f}")
            cs.metric("Peso Líquido (KG)", f"{peso_l:,.3f}")

        with s3: # CORREÇÃO: Forçando exibição mesmo que vazio
            val_emb = di.get('tipos_embalagem') or "Não informado"
            st.info(f"Quantidade total de volumes/embalagens: **{val_emb}**")
            st.text_input("Detalhe Embalagem", value="", disabled=True, placeholder="Dados adicionais de embalagem...")

    with aba2:
        st.subheader("Resumo Financeiro")
        t_dolar = float(di.get('taxa_dolar') or 1.0)
        data_fin = [
            ["Produto", "USD", di.get('total_fob'), (float(di.get('total_fob') or 0) * t_dolar)],
            ["Frete", "USD", di.get('total_frete'), (float(di.get('total_frete') or 0) * t_dolar)],
            ["Seguro", "USD", di.get('total_seguro'), (float(di.get('total_seguro') or 0) * t_dolar)]
        ]
        st.table(pd.DataFrame(data_fin, columns=["Rubrica", "Moeda", "Valor Moeda", "Valor BRL"]))
        
        if taxas_negociadas:
            st.write("**Taxas de Moedas nos Itens:**")
            st.dataframe(pd.DataFrame(taxas_negociadas), hide_index=True)

    with aba3:
        if itens:
            st.dataframe(pd.DataFrame(itens), hide_index=True)
        else:
            st.warning("Nenhum produto encontrado para esta declaração.")