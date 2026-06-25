import streamlit as st
from datetime import date,timedelta
from services.cadastros_service import get_maquinas,get_produtos,get_motivos
from services.qualidade_service import inserir_qualidade,listar_qualidade,resumo_tipo_maquina,resumo_motivos
from components.graficos import bar
from utils.helpers import to_excel_bytes
st.title("Qualidade"); maquinas=get_maquinas(); produtos=get_produtos(); motivos=get_motivos(); tab1,tab2,tab3=st.tabs(["Lançamento","Consulta","Indicadores"])
with tab1:
    with st.form("fq",clear_on_submit=True):
        data=st.date_input("Data",value=date.today()); maq=st.selectbox("Máquina",maquinas["nome"].tolist() if not maquinas.empty else []); prod=st.selectbox("Produto",produtos["descricao"].tolist() if not produtos.empty else []); tipo=st.selectbox("Tipo",["Refugo","Retrabalho"]); mot=st.selectbox("Motivo",motivos["descricao"].tolist() if not motivos.empty else []); qtd=st.number_input("Quantidade",0.0,step=1.0); obs=st.text_area("Observação")
        if st.form_submit_button("Salvar") and maq and prod:
            mid=int(motivos.loc[motivos['descricao']==mot,'id'].iloc[0]) if mot else None
            inserir_qualidade(data,int(maquinas.loc[maquinas['nome']==maq,'id'].iloc[0]),int(produtos.loc[produtos['descricao']==prod,'id'].iloc[0]),tipo,mid,qtd,obs); st.success("Salvo.")
with tab2:
    dados=listar_qualidade(date.today()-timedelta(days=30),date.today()); st.dataframe(dados,use_container_width=True,hide_index=True)
    if not dados.empty: st.download_button("Baixar Excel",data=to_excel_bytes(dados),file_name="qualidade.xlsx")
with tab3:
    d1=resumo_tipo_maquina(date.today()-timedelta(days=30),date.today()); d2=resumo_motivos(date.today()-timedelta(days=30),date.today())
    if not d1.empty: st.plotly_chart(bar(d1,"maquina","quantidade","Refugo e retrabalho por máquina",color="tipo_registro"),use_container_width=True)
    if not d2.empty: st.plotly_chart(bar(d2,"motivo","quantidade","Pareto de motivos"),use_container_width=True)
