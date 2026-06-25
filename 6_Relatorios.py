import streamlit as st
from datetime import date,timedelta
from services.producao_service import listar_producao
from services.qualidade_service import listar_qualidade
from services.processos_service import listar_processos
from utils.helpers import to_excel_bytes
st.title("Relatórios")
tipo=st.selectbox("Selecione o relatório",["Produção","Qualidade","Processos"]); di=st.date_input("Data inicial",value=date.today()-timedelta(days=30)); df=st.date_input("Data final",value=date.today())
dados=listar_producao(di,df) if tipo=="Produção" else listar_qualidade(di,df) if tipo=="Qualidade" else listar_processos(di,df)
st.dataframe(dados,use_container_width=True,hide_index=True)
if not dados.empty: st.download_button("Baixar Excel",data=to_excel_bytes(dados),file_name=f"{tipo.lower()}.xlsx")
