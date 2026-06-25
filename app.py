import streamlit as st
from database.db import init_db, db_exists
st.set_page_config(page_title="ERP industrial", page_icon="🏭", layout="wide", initial_sidebar_state="expanded")
if not db_exists():
    init_db()
st.title("ERP industrial da fábrica")
st.caption("Gestão de produção, qualidade e processos")
st.info("Use o menu lateral para acessar Dashboard, Produção, Qualidade, Processos, Cadastros e Relatórios.")
