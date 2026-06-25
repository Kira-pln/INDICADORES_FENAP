import streamlit as st
from datetime import date,timedelta
from services.cadastros_service import get_maquinas,get_produtos
from services.producao_service import inserir_producao,listar_producao,resumo_por_maquina
from components.graficos import bar
from utils.helpers import to_excel_bytes
st.title("Produção"); maquinas=get_maquinas(); produtos=get_produtos(); tab1,tab2,tab3=st.tabs(["Lançamento","Consulta","Indicadores"])
with tab1:
    with st.form("f",clear_on_submit=True):
        data=st.date_input("Data",value=date.today()); maq=st.selectbox("Máquina",maquinas["nome"].tolist() if not maquinas.empty else []); prod=st.selectbox("Produto",produtos["descricao"].tolist() if not produtos.empty else [])
        meta=st.number_input("Meta",0.0,step=1.0); qtd=st.number_input("Quantidade produzida",0.0,step=1.0); hd=st.number_input("Horas disponíveis",0.0,step=0.5); hp=st.number_input("Horas paradas",0.0,step=0.5); ref=st.number_input("Refugo",0.0,step=1.0); retr=st.number_input("Retrabalho",0.0,step=1.0); obs=st.text_area("Observação")
        if st.form_submit_button("Salvar") and maq and prod:
            inserir_producao(data,int(maquinas.loc[maquinas['nome']==maq,'id'].iloc[0]),int(produtos.loc[produtos['descricao']==prod,'id'].iloc[0]),meta,qtd,hd,hp,ref,retr,obs); st.success("Salvo.")
with tab2:
    di=st.date_input("Data inicial",value=date.today()-timedelta(days=30),key="pi"); df=st.date_input("Data final",value=date.today(),key="pf"); dados=listar_producao(di,df); st.dataframe(dados,use_container_width=True,hide_index=True)
    if not dados.empty: st.download_button("Baixar Excel",data=to_excel_bytes(dados),file_name="producao.xlsx")
with tab3:
    dados=resumo_por_maquina(date.today()-timedelta(days=30),date.today())
    if not dados.empty: st.plotly_chart(bar(dados,"maquina","produzido","Produção por máquina"),use_container_width=True)
