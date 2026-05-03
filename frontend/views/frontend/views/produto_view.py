import streamlit as st
import requests
import pandas as pd
import os

API_URL = os.getenv("API_URL", "http://backend-360:8000")

def render():
    item_id = st.session_state.selected_item_id
    di_id = st.session_state.selected_di_id
    
    if not item_id:
        st.warning("Nenhum produto selecionado.")
        if st.button("Voltar para DI/DUE"):
            st.session_state.current_page = "di_due"
            st.rerun()
        return

    # --- 1. BUSCA DE DADOS ---
    try:
        # Busca Capa (para o cabeçalho de contexto)
        res_di = requests.get(f"{API_URL}/di-due/{di_id}")
        di = res_di.json() if res_di.status_code == 200 else {}

        # Busca Detalhe do Item
        res_item = requests.get(f"{API_URL}/produto/{item_id}")
        if res_item.status_code != 200:
            st.error("Erro ao carregar detalhes do produto.")
            return
        item = res_item.json()

    except Exception as e:
        st.error(f"Falha de conexão: {e}")
        return

    # --- 2. TOPO: BOTÃO VOLTAR E CABEÇALHO DE CONTEXTO ---
    col_v1, col_v2 = st.columns([1, 8])
    if col_v1.button("⬅️ Voltar"):
        st.session_state.current_page = "di_due"
        st.rerun()
    
    with st.container(border=True):
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.write(f"**Tipo DI**  \n{di.get('tipo_di')}")
        c2.write(f"**DI/DUE**  \n{di.get('di_due')}")
        c3.write(f"**CNPJ Importador**  \n{di.get('cnpj_importador')}")
        c4.write(f"**Importador**  \n{di.get('importador')}")
        c5.write(f"**Regime Aduaneiro**  \n{di.get('regime')}")
        c6.write(f"**Versão**  \n{di.get('versao')}")

    # --- 3. ESTRUTURA DE ABAS PRINCIPAIS ---
    st.subheader(f"Produto: Seq {item.get('seq_item')} | NCM: {item.get('ncm')}")
    aba1, aba2, aba3 = st.tabs(["📄 Dados Principais", "🏢 Op. Estrangeiro", "💰 Impostos"])

    # --- CONTEÚDO ABA 1: DADOS PRINCIPAIS ---
    with aba1:
        sub_aba1_1, sub_aba1_2 = st.tabs(["Item/Produto", "Negociação Comercial"])
        
        with sub_aba1_1:
            c_a, c_b, c_c, c_d = st.columns(4)
            c_a.text_input("Seq Item", value=item.get('seq_item'), disabled=True)
            c_b.text_input("NCM", value=item.get('ncm'), disabled=True)
            c_c.text_input("ID RFB (Serpro)", value=item.get('id_serpro'), disabled=True)
            c_d.text_input("ID Importador", value=item.get('id_importador'), disabled=True)

            c_e, c_f, c_g, c_h = st.columns(4)
            c_e.text_input("Número de Série", value=item.get('serie'), disabled=True)
            c_f.text_input("Incoterm", value=item.get('incoterm'), disabled=True)
            c_g.text_input("Qtde Comercial", value=item.get('quantidade_comercial'), disabled=True)
            c_h.text_input("Unidade Comercial", value=item.get('unidade_medida'), disabled=True)

            c_i, c_j, c_k, c_l = st.columns(4)
            c_i.text_input("Qtde Estatística", value=item.get('quantidade_estatistica'), disabled=True)
            c_l.text_input("Unidade Estatística", value=item.get('unidade_estatistica'), disabled=True)
            c_k.text_input("Peso Líquido Unit.", value=item.get('peso_liquido_unitario'), disabled=True)
            c_j.text_input("Peso Líquido Total", value=item.get('peso_liquido_total'), disabled=True)

            st.text_input("Denominação", value=item.get('denominacao'), disabled=True)
            st.text_area("Detalhamento", value=item.get('descricao_mercadoria'), height=100, disabled=True)
            st.text_area("Descrição Complementar", value=item.get('descricao_complementar'), height=60, disabled=True)

        with sub_aba1_2:
            # Matriz de Negociação (Requisito 4.3.1.2)
            t_dolar = float(di.get('taxa_dolar') or 1)
            t_real = float(di.get('taxa_real') or 1) # Assumindo taxa_real no modelo ou calculada
            q_com = float(item.get('quantidade_comercial') or 0)
            
            data_neg = [
                ["Produto", item.get('moeda_fob'), item.get('valor_unitario'), item.get('total_na_moeda'), 
                 float(item.get('valor_unitario')) * t_dolar, float(item.get('total_na_moeda')) * t_dolar,
                 float(item.get('valor_unitario')) * t_real, float(item.get('total_na_moeda')) * t_real],
                
                ["Frete", "USD", item.get('valor_frete'), float(item.get('valor_frete')) * q_com,
                 float(item.get('valor_frete')) * t_dolar, (float(item.get('valor_frete')) * q_com) * t_dolar,
                 float(item.get('valor_frete')) * t_real, (float(item.get('valor_frete')) * q_com) * t_real],
                
                ["Seguro", "USD", item.get('valor_seguro'), float(item.get('valor_seguro')) * q_com,
                 float(item.get('valor_seguro')) * t_dolar, (float(item.get('valor_seguro')) * q_com) * t_dolar,
                 float(item.get('valor_seguro')) * t_real, (float(item.get('valor_seguro')) * q_com) * t_real]
            ]
            df_neg = pd.DataFrame(data_neg, columns=["Rubrica", "Moeda", "Unit. Negoc.", "Total Negoc.", "Unit. Dólar", "Total Dólar", "Unit. Real", "Total Real"])
            st.table(df_neg)

    # --- CONTEÚDO ABA 2: OP. ESTRANGEIRO ---
    with aba2:
        st.subheader("Dados do Operador")
        st.text_input("Denominação do Produto (Ref)", value=item.get('denominacao'), disabled=True)
        st.text_area("Detalhamento Técnico (Ref)", value=item.get('descricao_mercadoria'), disabled=True)
        
        st.divider()
        # Matriz de Fornecedor/Fabricante (Requisito 4.3.2)
        data_ops = [
            ["Fornecedor", item.get('op_estrang_fornec'), item.get('op_estrang_ende_fornec'), item.get('op_estrang_pais_origem'), item.get('op_estrang_vinc_impo_expo')],
            ["Fabricante", item.get('op_estrang_fabricante'), item.get('op_estrang_ende_fabric'), item.get('op_estrang_pais_origem'), item.get('op_estrang_vinc_impo_expo')]
        ]
        df_ops = pd.DataFrame(data_ops, columns=["Tipo Operador", "Nome Operador", "Endereço", "País Origem", "Vínculo Imp/Exp"])
        st.table(df_ops)

    # --- CONTEÚDO ABA 3: IMPOSTOS ---
    with aba3:
        st.subheader("Tributação por Item")
        sub_aba3_1, sub_aba3_2 = st.tabs(["Impostos", "Serviços"])
        
        with sub_aba3_1:
            # Matriz de Impostos do Item (Requisito 4.3.3.1)
            data_imp_item = [
                ["II", item.get('base_calc_ii'), f"{item.get('percentual_ii')}%", item.get('valor_ii'), item.get('valor_ii_devido'), item.get('valor_ii_recolher')],
                ["IPI", item.get('base_calc_ipi'), f"{item.get('percentual_ipi')}%", item.get('valor_ipi'), item.get('valor_ipi_devido'), item.get('valor_ipi_recolher')],
                ["PIS", item.get('base_calc_pis'), f"{item.get('percentual_pis')}%", item.get('valor_pis'), item.get('valor_pis_devido'), item.get('valor_pis_recolher')],
                ["COFINS", item.get('base_calc_cofins'), f"{item.get('percentual_cofins')}%", item.get('valor_cofins'), item.get('valor_ii_devido'), item.get('valor_ii_recolher')] # Usando II como ref se COFINS nulo
            ]
            df_imp_item = pd.DataFrame(data_imp_item, columns=["Tributo", "Base Cálculo", "Aliquota", "Calculado", "Devido", "A Recolher"])
            st.table(df_imp_item)
            
        with sub_aba3_2:
            st.info("ℹ️ Informação de serviços não disponível no momento.")