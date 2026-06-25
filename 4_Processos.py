import streamlit as st
from datetime import date,timedelta
from services.cadastros_service import get_maquinas,get_produtos
from services.processos_service import inserir_processo,listar_processos,resumo_maquina
from components.graficos import bar
from utils.helpers import to_excel_bytes
st.title("Processos"); maquinas=get_maquinas(); produtos=get_produtos(); tab1,tab2,tab3=st.tabs(["Lançamento","Consulta","Indicadores"])
with tab1:
    with st.form("fp",clear_on_submit=True):
        data=st.date_input("Data",value=date.today()); maq=st.selectbox("Máquina",maquinas["nome"].tolist() if not maquinas.empty else []); prod=st.selectbox("Produto",produtos["descricao"].tolist() if not produtos.empty else []); setup=st.number_input("Tempo de setup",0.0,step=0.1); inj=st.number_input("Tempo de injeção / ciclo",0.0,step=0.1); qtd=st.number_input("Quantidade movimentada",0.0,step=1.0); obs=st.text_area("Observação")
        if st.form_submit_button("Salvar") and maq and prod:
            inserir_processo(data,int(maquinas.loc[maquinas['nome']==maq,'id'].iloc[0]),int(produtos.loc[produtos['descricao']==prod,'id'].iloc[0]),setup,inj,qtd,obs); st.success("Salvo.")
with tab2:
    dados=listar_processos(date.today()-timedelta(days=30),date.today()); st.dataframe(dados,use_container_width=True,hide_index=True)
    if not dados.empty: st.download_button("Baixar Excel",data=to_excel_bytes(dados),file_name="processos.xlsx")
with tab3:
    dados=resumo_maquina(date.today()-timedelta(days=30),date.today())
    if not dados.empty: st.plotly_chart(bar(dados,"maquina","setup_medio","Setup médio por máquina"),use_container_width=True)
