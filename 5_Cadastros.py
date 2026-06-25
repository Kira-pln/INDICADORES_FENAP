import streamlit as st
from database.db import init_db
from services.cadastros_service import get_maquinas,get_produtos,get_motivos,add_produto,add_motivo
st.title("Cadastros")
if st.button("Reinicializar banco / aplicar seed"): init_db(); st.success("Banco inicializado.")
tab1,tab2,tab3=st.tabs(["Máquinas","Produtos","Motivos da qualidade"])
with tab1: st.dataframe(get_maquinas(),use_container_width=True,hide_index=True)
with tab2:
    with st.form("np",clear_on_submit=True):
        codigo=st.text_input("Código"); descricao=st.text_input("Descrição"); familia=st.text_input("Família"); unidade=st.text_input("Unidade",value="UN")
        if st.form_submit_button("Adicionar produto") and codigo and descricao: add_produto(codigo,descricao,familia,unidade); st.success("Produto adicionado.")
    st.dataframe(get_produtos(),use_container_width=True,hide_index=True)
with tab3:
    with st.form("nm",clear_on_submit=True):
        descricao=st.text_input("Motivo"); categoria=st.text_input("Categoria")
        if st.form_submit_button("Adicionar motivo") and descricao: add_motivo(descricao,categoria); st.success("Motivo adicionado.")
    st.dataframe(get_motivos(),use_container_width=True,hide_index=True)
