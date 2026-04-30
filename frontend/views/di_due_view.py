import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    di_id = st.session_state.selected_di_id
    
    if not di_id:
        st.warning("Nenhum processo selecionado.")
        if st.button("Ir para lista de Importação"):
            st.session_state.current_page = "Importacao"
            st.rerun()
        return

    # --- 1. BUSCA DE DADOS ---
    try:
        # Busca Capa
        res_di = requests.get(f"{API_URL}/di-due/{di_id}")
        if res_di.status_code != 200:
            st.error("Erro ao carregar detalhes da DI.")
            return
        di = res_di.json()
        
        # Busca Itens (para Aba 3 e Taxas)
        res_itens = requests.get(f"{API_URL}/di-due/{di_id}/produtos")
        itens = res_itens.json() if res_itens.status_code == 200 else []
        
        # Busca Taxas Distintas (Sub-aba 2.1)
        res_taxas = requests.get(f"{API_URL}/di-due/{di_id}/taxas-moedas")
        taxas_negociadas = res_taxas.json() if res_taxas.status_code == 200 else []

    except Exception as e:
        st.error(f"Falha de conexão: {e}")
        return

    # --- 2. TOPO: BOTÃO VOLTAR E CABEÇALHO (REQUISITO 4.3) ---
    col_v1, col_v2 = st.columns([1, 8])
    if col_v1.button("⬅️ Voltar"):
        st.session_state.current_page = "Importacao"
        st.rerun()
    
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("Tipo DI", di.get('tipo_di'))
        c2.metric("DI/DUE", di.get('di_due'))
        c3.write(f"**CNPJ Importador**  \n{di.get('cnpj_importador')}")
        c4.write(f"**Importador**  \n{di.get('importador')}")
        c5.write(f"**Regime Aduaneiro**  \n{di.get('regime')}")
        c6.write(f"**Versão**  \n{di.get('versao')}")

    # --- 3. TABELA PRINCIPAL COM ABAS ---
    aba1, aba2, aba3 = st.tabs(["📄 DI/DUIMP", "📊 Resumo Importação", "📦 Produtos"])

    # --- CONTEÚDO ABA 1: DI/DUIMP ---
    with aba1:
        sub_aba1_1, sub_aba1_2, sub_aba1_3 = st.tabs(["Dados Principais", "Dados de Carga", "Tipos Embalagem"])
        
        with sub_aba1_1:
            col_a, col_b, col_c = st.columns(3)
            col_a.text_input("Endereço", value=di.get('endereco_importador'), disabled=True)
            col_b.text_input("Canal", value=di.get('canal'), disabled=True)
            col_c.text_input("Regime Aduaneiro", value=di.get('regime'), disabled=True)
            
            col_d, col_e, col_f = st.columns(3)
            col_d.date_input("Data Embarque (ATD)", value=pd.to_datetime(di.get('data_atd')), disabled=True)
            col_e.date_input("Data Chegada (ATA)", value=pd.to_datetime(di.get('data_ata')), disabled=True)
            col_f.date_input("Data no Sistema", value=pd.to_datetime(di.get('data_no_sistema')), disabled=True)
            
            col_g, col_h = st.columns(2)
            col_g.date_input("Data Registro", value=pd.to_datetime(di.get('data_registro')), disabled=True)
            col_h.date_input("Data Desembaraço", value=pd.to_datetime(di.get('data_desembaraco')), disabled=True)

        with sub_aba1_2:
            col_i, col_j, col_k = st.columns(3)
            col_i.text_input("RCR / Termo Resp.", value=di.get('rcr'), disabled=True)
            col_j.text_input("Unidade Entrada/Despacho", value=di.get('urf_entrada'), disabled=True)
            col_k.text_input("Unidade Despacho", value=di.get('unidade_despacho'), disabled=True)
            
            col_l, col_m, col_n = st.columns(3)
            col_l.text_input("Recinto Alfandegado", value=di.get('recinto'), disabled=True)
            col_m.text_input("Bandeira", value=di.get('bandeira'), disabled=True)
            col_n.text_input("AWB Master", value=di.get('awb_master'), disabled=True)
            
            col_o, col_p, col_q = st.columns(3)
            col_o.text_input("AWB House", value=di.get('awb_house'), disabled=True)
            col_p.text_input("País Procedência", value=di.get('pais_procedencia'), disabled=True)
            col_q.text_input("Local Embarque", value=di.get('local_embarque'), disabled=True)
            
            col_r, col_s = st.columns(2)
            col_r.metric("Peso Bruto (KG)", f"{di.get('peso_bruto'):,.3f}")
            col_s.metric("Peso Líquido (KG)", f"{di.get('peso_liquido'):,.3f}")

        with sub_aba1_3:
            st.info(f"Quantidade total de volumes/embalagens: **{di.get('tipos_embalagem')}**")

    # --- CONTEÚDO ABA 2: RESUMO IMPORTAÇÃO ---
    with aba2:
        sub_aba2_1, sub_aba2_2 = st.tabs(["Taxas Cambiais", "Resumo Comercial"])
        
        with sub_aba2_1:
            c_t1, c_t2, c_t3 = st.columns(3)
            c_t1.write(f"**Data Conversão:** {di.get('data_registro')}")
            c_t2.metric("Taxa Dólar", f"{di.get('taxa_dolar'):,.4f}")
            c_t3.metric("Taxa Real", "1.0000")
            
            st.write("**Moedas Negociadas nos Itens:**")
            if taxas_negociadas:
                st.table(pd.DataFrame(taxas_negociadas))

        with sub_aba2_2:
            st.caption(f"Ref: {di.get('di_due')} | Incoterm: {di.get('incoterm')}")
            sub_sub_aba1, sub_sub_aba2 = st.tabs(["Valores Comerciais", "Impostos"])
            
            with sub_sub_aba1:
                # Montagem da matriz de valores (Requisito 4.2.2.1)
                t_dolar = float(di.get('taxa_dolar') or 1)
                data_comercial = [
                    ["Produto", "USD", di.get('total_fob'), di.get('total_fob'), float(di.get('total_fob')) * t_dolar],
                    ["Frete", "USD", di.get('total_frete'), di.get('total_frete'), float(di.get('total_frete')) * t_dolar],
                    ["Seguro", "USD", di.get('total_seguro'), di.get('total_seguro'), float(di.get('total_seguro')) * t_dolar]
                ]
                df_comercial = pd.DataFrame(data_comercial, columns=["Rubrica", "Moeda", "Negociado", "Total Dólar", "Total Real"])
                st.table(df_comercial)

            with sub_sub_aba2:
                # Matriz de Impostos (Requisito 4.2.2.2)
                data_impostos = [
                    ["II", di.get('total_fob'), di.get('valor_ii'), di.get('valor_ii_devido'), di.get('valor_ii_recolher')],
                    ["IPI", di.get('total_fob'), di.get('valor_ipi'), di.get('valor_ipi_devido'), di.get('valor_ipi_recolher')],
                    ["PIS", di.get('total_fob'), di.get('valor_pis'), di.get('valor_pis_devido'), di.get('valor_pis_recolher')],
                    ["COFINS", di.get('total_fob'), di.get('valor_cofins'), di.get('valor_cofins_devido'), di.get('valor_cofins_recolher')]
                ]
                df_impostos = pd.DataFrame(data_impostos, columns=["Tributo", "Base Cálculo", "Calculado", "Devido", "A Recolher"])
                st.table(df_impostos)

    # --- CONTEÚDO ABA 3: PRODUTOS ---
    with aba3:
        st.subheader("Itens da Declaração")
        if itens:
            df_itens = pd.DataFrame(itens)
            # Criamos uma exibição customizada com botão para cada item
            for _, row in df_itens.iterrows():
                with st.container(border=True):
                    c1, c2, c3, c4 = st.columns([1, 2, 4, 1])
                    c1.write(f"**Seq:** {row['seq_item']}")
                    c2.write(f"**NCM:** {row['ncm']}")
                    c3.write(f"**Descrição:** {row['descricao_mercadoria'][:100]}...")
                    if c4.button("🔍 Ver Produto", key=f"btn_item_{row['id']}"):
                        st.session_state.selected_item_id = row['id']
                        st.session_state.current_page = "Produto"
                        st.rerun()
        else:
            st.info("Nenhum item vinculado a esta DI.")