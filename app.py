import os, textwrap, zipfile, pathlib, shutil

# Recriar a versão corrigida diretamente
dst = pathlib.Path("/mnt/data/fabrica_erp_streamlit_cloud_corrigido")
if dst.exists():
    shutil.rmtree(dst)

for sub in ["pages", "database", "services", "components", "utils", "assets", ".streamlit"]:
    (dst / sub).mkdir(parents=True, exist_ok=True)

def w(rel, content):
    p = dst / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")

w("requirements.txt", """
streamlit
pandas
plotly
sqlalchemy
openpyxl
""")

w("app.py", """
import streamlit as st

st.set_page_config(
    page_title="ERP industrial",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.title("ERP industrial da fábrica")
st.markdown(
    '''
    Sistema web para **produção**, **qualidade** e **processos**.

    ### Módulos
    - **Dashboard geral**
    - **Produção**
    - **Qualidade**
    - **Processos**
    - **Cadastros**
    - **Relatórios**

    ### Primeiro uso
    1. Acesse **Cadastros**
    2. Clique em **Inicializar banco de dados**
    3. Cadastre ou revise os produtos
    4. Comece os lançamentos
    '''
)

st.info("Use o menu lateral para navegar entre os módulos do sistema.")
""")

w(".streamlit/config.toml", """
[server]
headless = true

[theme]
base = "light"
""")

w("database/db.py", """
from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp_fabrica.db"

ENGINE = create_engine(f"sqlite:///{DB_PATH}", future=True)

def get_engine():
    return ENGINE

def execute_script(sql_text: str):
    statements = [s.strip() for s in sql_text.split(";") if s.strip()]
    with ENGINE.begin() as conn:
        for stmt in statements:
            conn.execute(text(stmt))

def query_df(sql: str, params: dict | None = None) -> pd.DataFrame:
    with ENGINE.begin() as conn:
        return pd.read_sql(text(sql), conn, params=params or {})

def execute(sql: str, params: dict | None = None):
    with ENGINE.begin() as conn:
        conn.execute(text(sql), params or {})

def scalar(sql: str, params: dict | None = None, default=0):
    with ENGINE.begin() as conn:
        value = conn.execute(text(sql), params or {}).scalar()
    return default if value is None else value
""")

w("database/schema.sql", """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS maquinas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    processo TEXT NOT NULL,
    ativo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT NOT NULL UNIQUE,
    descricao TEXT NOT NULL,
    familia TEXT,
    unidade TEXT DEFAULT 'UN',
    ativo INTEGER NOT NULL DEFAULT 1
);

CREATE TABLE IF NOT EXISTS motivos_qualidade (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    descricao TEXT NOT NULL UNIQUE,
    categoria TEXT
);

CREATE TABLE IF NOT EXISTS producao (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    maquina_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    meta REAL NOT NULL DEFAULT 0,
    quantidade_produzida REAL NOT NULL DEFAULT 0,
    horas_disponiveis REAL NOT NULL DEFAULT 0,
    horas_paradas REAL NOT NULL DEFAULT 0,
    refugo REAL NOT NULL DEFAULT 0,
    retrabalho REAL NOT NULL DEFAULT 0,
    observacao TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);

CREATE TABLE IF NOT EXISTS qualidade_registros (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    maquina_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    tipo_registro TEXT NOT NULL CHECK (tipo_registro IN ('Refugo','Retrabalho')),
    motivo_id INTEGER,
    quantidade REAL NOT NULL DEFAULT 0,
    observacao TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id),
    FOREIGN KEY (motivo_id) REFERENCES motivos_qualidade(id)
);

CREATE TABLE IF NOT EXISTS processos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data DATE NOT NULL,
    maquina_id INTEGER NOT NULL,
    produto_id INTEGER NOT NULL,
    tempo_setup REAL NOT NULL DEFAULT 0,
    tempo_injecao REAL NOT NULL DEFAULT 0,
    quantidade_movimentada REAL NOT NULL DEFAULT 0,
    observacao TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (maquina_id) REFERENCES maquinas(id),
    FOREIGN KEY (produto_id) REFERENCES produtos(id)
);
""")

w("database/seed.sql", """
INSERT OR IGNORE INTO maquinas (nome, processo) VALUES
('INJ 01','RIM'),
('INJ 02','CORINGA'),
('INJ 03','ESTRUTURAL'),
('INJ 04','SEMI-RIM'),
('INJ 05','FLEXIVEL'),
('INJ 06','VISCO'),
('INJ 07','PELE INTEGRAL');

INSERT OR IGNORE INTO motivos_qualidade (descricao, categoria) VALUES
('Rebarba','Visual'),
('Bolha','Processo'),
('Falta de material','Processo'),
('Dimensional fora','Dimensional'),
('Queima','Processo'),
('Deformação','Dimensional');

INSERT OR IGNORE INTO produtos (codigo, descricao, familia, unidade) VALUES
('P001','Produto exemplo 1','Linha A','UN'),
('P002','Produto exemplo 2','Linha A','UN'),
('P003','Produto exemplo 3','Linha B','UN');
""")

w("utils/helpers.py", """
import pandas as pd

def to_excel_bytes(df: pd.DataFrame) -> bytes:
    from io import BytesIO
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="dados")
    buffer.seek(0)
    return buffer.getvalue()
""")

w("components/graficos.py", """
import plotly.express as px

def bar(df, x, y, title, color=None):
    fig = px.bar(df, x=x, y=y, title=title, color=color, text_auto=True)
    fig.update_layout(height=380)
    return fig

def line(df, x, y, title, color=None):
    fig = px.line(df, x=x, y=y, title=title, color=color, markers=True)
    fig.update_layout(height=380)
    return fig
""")

w("services/cadastros_service.py", """
from database.db import query_df, execute

def get_maquinas():
    return query_df("SELECT * FROM maquinas WHERE ativo = 1 ORDER BY nome")

def get_produtos():
    return query_df("SELECT * FROM produtos WHERE ativo = 1 ORDER BY descricao")

def get_motivos():
    return query_df("SELECT * FROM motivos_qualidade ORDER BY descricao")

def add_produto(codigo, descricao, familia, unidade):
    execute(
        '''
        INSERT INTO produtos (codigo, descricao, familia, unidade)
        VALUES (:codigo, :descricao, :familia, :unidade)
        ''',
        {"codigo": codigo, "descricao": descricao, "familia": familia, "unidade": unidade},
    )

def add_motivo(descricao, categoria):
    execute(
        "INSERT INTO motivos_qualidade (descricao, categoria) VALUES (:descricao, :categoria)",
        {"descricao": descricao, "categoria": categoria},
    )
""")

w("services/producao_service.py", """
from database.db import execute, query_df

def inserir_producao(data, maquina_id, produto_id, meta, quantidade, horas_disp, horas_paradas, refugo, retrabalho, observacao):
    execute(
        '''
        INSERT INTO producao
        (data, maquina_id, produto_id, meta, quantidade_produzida, horas_disponiveis, horas_paradas, refugo, retrabalho, observacao)
        VALUES
        (:data, :maquina_id, :produto_id, :meta, :quantidade, :horas_disp, :horas_paradas, :refugo, :retrabalho, :observacao)
        ''',
        {
            "data": data, "maquina_id": maquina_id, "produto_id": produto_id, "meta": meta,
            "quantidade": quantidade, "horas_disp": horas_disp, "horas_paradas": horas_paradas,
            "refugo": refugo, "retrabalho": retrabalho, "observacao": observacao
        }
    )

def listar_producao(data_ini=None, data_fim=None):
    sql = '''
    SELECT p.id, p.data, m.nome AS maquina, m.processo, pr.codigo, pr.descricao AS produto,
           p.meta, p.quantidade_produzida, p.horas_disponiveis, p.horas_paradas, p.refugo, p.retrabalho, p.observacao
    FROM producao p
    JOIN maquinas m ON m.id = p.maquina_id
    JOIN produtos pr ON pr.id = p.produto_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND p.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND p.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " ORDER BY p.data DESC, m.nome"
    return query_df(sql, params)

def resumo_por_maquina(data_ini=None, data_fim=None):
    sql = '''
    SELECT m.nome AS maquina,
           SUM(p.meta) AS meta,
           SUM(p.quantidade_produzida) AS produzido,
           SUM(p.refugo) AS refugo,
           SUM(p.retrabalho) AS retrabalho,
           SUM(p.horas_disponiveis) AS horas_disponiveis
    FROM producao p
    JOIN maquinas m ON m.id = p.maquina_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND p.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND p.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " GROUP BY m.nome ORDER BY m.nome"
    return query_df(sql, params)

def resumo_diario(data_ini=None, data_fim=None):
    sql = '''
    SELECT p.data,
           SUM(p.meta) AS meta,
           SUM(p.quantidade_produzida) AS produzido,
           SUM(p.refugo) AS refugo,
           SUM(p.retrabalho) AS retrabalho
    FROM producao p
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND p.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND p.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " GROUP BY p.data ORDER BY p.data"
    return query_df(sql, params)
""")

w("services/qualidade_service.py", """
from database.db import execute, query_df

def inserir_qualidade(data, maquina_id, produto_id, tipo_registro, motivo_id, quantidade, observacao):
    execute(
        '''
        INSERT INTO qualidade_registros
        (data, maquina_id, produto_id, tipo_registro, motivo_id, quantidade, observacao)
        VALUES
        (:data, :maquina_id, :produto_id, :tipo_registro, :motivo_id, :quantidade, :observacao)
        ''',
        {
            "data": data, "maquina_id": maquina_id, "produto_id": produto_id, "tipo_registro": tipo_registro,
            "motivo_id": motivo_id, "quantidade": quantidade, "observacao": observacao
        }
    )

def listar_qualidade(data_ini=None, data_fim=None):
    sql = '''
    SELECT q.id, q.data, m.nome AS maquina, m.processo, p.codigo, p.descricao AS produto,
           q.tipo_registro, COALESCE(mq.descricao, '') AS motivo, q.quantidade, q.observacao
    FROM qualidade_registros q
    JOIN maquinas m ON m.id = q.maquina_id
    JOIN produtos p ON p.id = q.produto_id
    LEFT JOIN motivos_qualidade mq ON mq.id = q.motivo_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND q.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND q.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " ORDER BY q.data DESC, m.nome"
    return query_df(sql, params)

def resumo_tipo_maquina(data_ini=None, data_fim=None):
    sql = '''
    SELECT m.nome AS maquina, q.tipo_registro, SUM(q.quantidade) AS quantidade
    FROM qualidade_registros q
    JOIN maquinas m ON m.id = q.maquina_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND q.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND q.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " GROUP BY m.nome, q.tipo_registro ORDER BY m.nome"
    return query_df(sql, params)

def resumo_motivos(data_ini=None, data_fim=None):
    sql = '''
    SELECT COALESCE(mq.descricao, 'Sem motivo') AS motivo, SUM(q.quantidade) AS quantidade
    FROM qualidade_registros q
    LEFT JOIN motivos_qualidade mq ON mq.id = q.motivo_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND q.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND q.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " GROUP BY COALESCE(mq.descricao, 'Sem motivo') ORDER BY quantidade DESC"
    return query_df(sql, params)
""")

w("services/processos_service.py", """
from database.db import execute, query_df

def inserir_processo(data, maquina_id, produto_id, tempo_setup, tempo_injecao, quantidade_movimentada, observacao):
    execute(
        '''
        INSERT INTO processos
        (data, maquina_id, produto_id, tempo_setup, tempo_injecao, quantidade_movimentada, observacao)
        VALUES
        (:data, :maquina_id, :produto_id, :tempo_setup, :tempo_injecao, :quantidade_movimentada, :observacao)
        ''',
        {
            "data": data, "maquina_id": maquina_id, "produto_id": produto_id, "tempo_setup": tempo_setup,
            "tempo_injecao": tempo_injecao, "quantidade_movimentada": quantidade_movimentada, "observacao": observacao
        }
    )

def listar_processos(data_ini=None, data_fim=None):
    sql = '''
    SELECT prc.id, prc.data, m.nome AS maquina, m.processo, p.codigo, p.descricao AS produto,
           prc.tempo_setup, prc.tempo_injecao, prc.quantidade_movimentada, prc.observacao
    FROM processos prc
    JOIN maquinas m ON m.id = prc.maquina_id
    JOIN produtos p ON p.id = prc.produto_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND prc.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND prc.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " ORDER BY prc.data DESC, m.nome"
    return query_df(sql, params)

def resumo_maquina(data_ini=None, data_fim=None):
    sql = '''
    SELECT m.nome AS maquina,
           AVG(prc.tempo_setup) AS setup_medio,
           AVG(prc.tempo_injecao) AS injecao_media,
           SUM(prc.quantidade_movimentada) AS qtd_movimentada
    FROM processos prc
    JOIN maquinas m ON m.id = prc.maquina_id
    WHERE 1=1
    '''
    params = {}
    if data_ini:
        sql += " AND prc.data >= :data_ini"
        params["data_ini"] = str(data_ini)
    if data_fim:
        sql += " AND prc.data <= :data_fim"
        params["data_fim"] = str(data_fim)
    sql += " GROUP BY m.nome ORDER BY m.nome"
    return query_df(sql, params)
""")

w("services/dashboard_service.py", """
from database.db import scalar
from services.producao_service import resumo_por_maquina, resumo_diario
from services.qualidade_service import resumo_tipo_maquina, resumo_motivos
from services.processos_service import resumo_maquina

def indicadores_gerais(data_ini=None, data_fim=None):
    params = {}
    where_p = " WHERE 1=1 "
    where_pr = " WHERE 1=1 "
    if data_ini:
        params["data_ini"] = str(data_ini)
        where_p += " AND data >= :data_ini "
        where_pr += " AND data >= :data_ini "
    if data_fim:
        params["data_fim"] = str(data_fim)
        where_p += " AND data <= :data_fim "
        where_pr += " AND data <= :data_fim "

    meta = scalar(f"SELECT SUM(meta) FROM producao {where_p}", params, 0)
    produzido = scalar(f"SELECT SUM(quantidade_produzida) FROM producao {where_p}", params, 0)
    refugo = scalar(f"SELECT SUM(refugo) FROM producao {where_p}", params, 0)
    retrabalho = scalar(f"SELECT SUM(retrabalho) FROM producao {where_p}", params, 0)
    setup_medio = scalar(f"SELECT AVG(tempo_setup) FROM processos {where_pr}", params, 0)
    injecao_media = scalar(f"SELECT AVG(tempo_injecao) FROM processos {where_pr}", params, 0)

    atingimento = (produzido / meta * 100) if meta else 0
    qualidade = ((produzido - refugo) / produzido * 100) if produzido else 0

    return {
        "meta": meta,
        "produzido": produzido,
        "atingimento": atingimento,
        "refugo": refugo,
        "retrabalho": retrabalho,
        "setup_medio": setup_medio,
        "injecao_media": injecao_media,
        "qualidade": qualidade,
    }

def datasets_dashboard(data_ini=None, data_fim=None):
    return {
        "prod_maquina": resumo_por_maquina(data_ini, data_fim),
        "prod_diario": resumo_diario(data_ini, data_fim),
        "qual_maquina": resumo_tipo_maquina(data_ini, data_fim),
        "qual_motivos": resumo_motivos(data_ini, data_fim),
        "proc_maquina": resumo_maquina(data_ini, data_fim),
    }
""")

w("pages/1_Dashboard_geral.py", """
import streamlit as st
from datetime import date, timedelta
from services.dashboard_service import indicadores_gerais, datasets_dashboard
from components.graficos import bar, line

st.title("Dashboard geral")

c1, c2 = st.columns(2)
with c1:
    data_ini = st.date_input("Data inicial", value=date.today() - timedelta(days=30), key="dash_ini")
with c2:
    data_fim = st.date_input("Data final", value=date.today(), key="dash_fim")

ind = indicadores_gerais(data_ini, data_fim)

a, b, c, d = st.columns(4)
a.metric("Produção total", f"{ind['produzido']:.0f}")
b.metric("Meta total", f"{ind['meta']:.0f}")
c.metric("Atingimento", f"{ind['atingimento']:.1f}%")
d.metric("Qualidade", f"{ind['qualidade']:.1f}%")

e, f, g, h = st.columns(4)
e.metric("Refugo", f"{ind['refugo']:.0f}")
f.metric("Retrabalho", f"{ind['retrabalho']:.0f}")
g.metric("Setup médio", f"{ind['setup_medio']:.2f}")
h.metric("Injeção média", f"{ind['injecao_media']:.2f}")

data = datasets_dashboard(data_ini, data_fim)

r1c1, r1c2 = st.columns(2)
with r1c1:
    df = data["prod_maquina"]
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "produzido", "Produção por máquina"), use_container_width=True)
with r1c2:
    df = data["prod_diario"]
    if not df.empty:
        st.plotly_chart(line(df, "data", "produzido", "Produção diária"), use_container_width=True)

r2c1, r2c2 = st.columns(2)
with r2c1:
    df = data["qual_maquina"]
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "quantidade", "Qualidade por máquina", color="tipo_registro"), use_container_width=True)
with r2c2:
    df = data["qual_motivos"]
    if not df.empty:
        st.plotly_chart(bar(df, "motivo", "quantidade", "Pareto de motivos"), use_container_width=True)

r3c1, r3c2 = st.columns(2)
with r3c1:
    df = data["proc_maquina"]
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "setup_medio", "Setup médio por máquina"), use_container_width=True)
with r3c2:
    df = data["proc_maquina"]
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "injecao_media", "Tempo médio de injeção"), use_container_width=True)
""")

w("pages/2_Producao.py", """
import streamlit as st
from datetime import date, timedelta
from services.cadastros_service import get_maquinas, get_produtos
from services.producao_service import inserir_producao, listar_producao, resumo_por_maquina
from components.graficos import bar
from utils.helpers import to_excel_bytes

st.title("Produção")

maquinas = get_maquinas()
produtos = get_produtos()

tab1, tab2, tab3 = st.tabs(["Lançamento", "Consulta", "Indicadores"])

with tab1:
    st.subheader("Novo lançamento de produção")
    with st.form("form_producao", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data", value=date.today())
        maquina_nome = c2.selectbox("Máquina", maquinas["nome"].tolist() if not maquinas.empty else [])
        produto_desc = c3.selectbox("Produto", produtos["descricao"].tolist() if not produtos.empty else [])

        c4, c5, c6 = st.columns(3)
        meta = c4.number_input("Meta", min_value=0.0, step=1.0)
        quantidade = c5.number_input("Quantidade produzida", min_value=0.0, step=1.0)
        horas_disp = c6.number_input("Horas disponíveis", min_value=0.0, step=0.5)

        c7, c8, c9 = st.columns(3)
        horas_paradas = c7.number_input("Horas paradas", min_value=0.0, step=0.5)
        refugo = c8.number_input("Refugo", min_value=0.0, step=1.0)
        retrabalho = c9.number_input("Retrabalho", min_value=0.0, step=1.0)

        observacao = st.text_area("Observação")
        enviar = st.form_submit_button("Salvar lançamento")

        if enviar and maquina_nome and produto_desc:
            maquina_id = int(maquinas.loc[maquinas["nome"] == maquina_nome, "id"].iloc[0])
            produto_id = int(produtos.loc[produtos["descricao"] == produto_desc, "id"].iloc[0])
            inserir_producao(data, maquina_id, produto_id, meta, quantidade, horas_disp, horas_paradas, refugo, retrabalho, observacao)
            st.success("Lançamento de produção salvo com sucesso.")

with tab2:
    st.subheader("Consulta de produção")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="prod_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="prod_fim")
    df = listar_producao(data_ini, data_fim)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        st.download_button("Baixar Excel", data=to_excel_bytes(df), file_name="producao.xlsx")

with tab3:
    st.subheader("Indicadores de produção")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="prod_ind_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="prod_ind_fim")
    df = resumo_por_maquina(data_ini, data_fim)
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "produzido", "Produção por máquina"), use_container_width=True)
        st.plotly_chart(bar(df, "maquina", "meta", "Meta por máquina"), use_container_width=True)
        st.plotly_chart(bar(df, "maquina", "refugo", "Refugo por máquina"), use_container_width=True)
""")

w("pages/3_Qualidade.py", """
import streamlit as st
from datetime import date, timedelta
from services.cadastros_service import get_maquinas, get_produtos, get_motivos
from services.qualidade_service import inserir_qualidade, listar_qualidade, resumo_tipo_maquina, resumo_motivos
from components.graficos import bar
from utils.helpers import to_excel_bytes

st.title("Qualidade")

maquinas = get_maquinas()
produtos = get_produtos()
motivos = get_motivos()

tab1, tab2, tab3 = st.tabs(["Lançamento", "Consulta", "Indicadores"])

with tab1:
    st.subheader("Novo lançamento de qualidade")
    with st.form("form_qualidade", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        data = c1.date_input("Data", value=date.today())
        maquina_nome = c2.selectbox("Máquina", maquinas["nome"].tolist() if not maquinas.empty else [])
        produto_desc = c3.selectbox("Produto", produtos["descricao"].tolist() if not produtos.empty else [])
        tipo = c4.selectbox("Tipo", ["Refugo", "Retrabalho"])

        c5, c6 = st.columns(2)
        motivo_desc = c5.selectbox("Motivo", motivos["descricao"].tolist() if not motivos.empty else [])
        quantidade = c6.number_input("Quantidade", min_value=0.0, step=1.0)

        observacao = st.text_area("Observação")
        enviar = st.form_submit_button("Salvar lançamento")

        if enviar and maquina_nome and produto_desc:
            maquina_id = int(maquinas.loc[maquinas["nome"] == maquina_nome, "id"].iloc[0])
            produto_id = int(produtos.loc[produtos["descricao"] == produto_desc, "id"].iloc[0])
            motivo_id = None
            if motivo_desc:
                motivo_id = int(motivos.loc[motivos["descricao"] == motivo_desc, "id"].iloc[0])
            inserir_qualidade(data, maquina_id, produto_id, tipo, motivo_id, quantidade, observacao)
            st.success("Lançamento de qualidade salvo com sucesso.")

with tab2:
    st.subheader("Consulta de qualidade")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="qual_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="qual_fim")
    df = listar_qualidade(data_ini, data_fim)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        st.download_button("Baixar Excel", data=to_excel_bytes(df), file_name="qualidade.xlsx")

with tab3:
    st.subheader("Indicadores de qualidade")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="qual_ind_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="qual_ind_fim")
    df1 = resumo_tipo_maquina(data_ini, data_fim)
    df2 = resumo_motivos(data_ini, data_fim)
    if not df1.empty:
        st.plotly_chart(bar(df1, "maquina", "quantidade", "Refugo e retrabalho por máquina", color="tipo_registro"), use_container_width=True)
    if not df2.empty:
        st.plotly_chart(bar(df2, "motivo", "quantidade", "Pareto de motivos"), use_container_width=True)
""")

w("pages/4_Processos.py", """
import streamlit as st
from datetime import date, timedelta
from services.cadastros_service import get_maquinas, get_produtos
from services.processos_service import inserir_processo, listar_processos, resumo_maquina
from components.graficos import bar
from utils.helpers import to_excel_bytes

st.title("Processos")

maquinas = get_maquinas()
produtos = get_produtos()

tab1, tab2, tab3 = st.tabs(["Lançamento", "Consulta", "Indicadores"])

with tab1:
    st.subheader("Novo lançamento de processo")
    with st.form("form_processos", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        data = c1.date_input("Data", value=date.today())
        maquina_nome = c2.selectbox("Máquina", maquinas["nome"].tolist() if not maquinas.empty else [])
        produto_desc = c3.selectbox("Produto", produtos["descricao"].tolist() if not produtos.empty else [])

        c4, c5, c6 = st.columns(3)
        tempo_setup = c4.number_input("Tempo de setup", min_value=0.0, step=0.1)
        tempo_injecao = c5.number_input("Tempo de injeção / ciclo", min_value=0.0, step=0.1)
        quantidade_movimentada = c6.number_input("Quantidade movimentada", min_value=0.0, step=1.0)

        observacao = st.text_area("Observação")
        enviar = st.form_submit_button("Salvar lançamento")

        if enviar and maquina_nome and produto_desc:
            maquina_id = int(maquinas.loc[maquinas["nome"] == maquina_nome, "id"].iloc[0])
            produto_id = int(produtos.loc[produtos["descricao"] == produto_desc, "id"].iloc[0])
            inserir_processo(data, maquina_id, produto_id, tempo_setup, tempo_injecao, quantidade_movimentada, observacao)
            st.success("Lançamento de processo salvo com sucesso.")

with tab2:
    st.subheader("Consulta de processos")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="proc_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="proc_fim")
    df = listar_processos(data_ini, data_fim)
    st.dataframe(df, use_container_width=True, hide_index=True)
    if not df.empty:
        st.download_button("Baixar Excel", data=to_excel_bytes(df), file_name="processos.xlsx")

with tab3:
    st.subheader("Indicadores de processos")
    c1, c2 = st.columns(2)
    data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30), key="proc_ind_ini")
    data_fim = c2.date_input("Data final", value=date.today(), key="proc_ind_fim")
    df = resumo_maquina(data_ini, data_fim)
    if not df.empty:
        st.plotly_chart(bar(df, "maquina", "setup_medio", "Setup médio por máquina"), use_container_width=True)
        st.plotly_chart(bar(df, "maquina", "injecao_media", "Tempo médio de injeção"), use_container_width=True)
        st.plotly_chart(bar(df, "maquina", "qtd_movimentada", "Quantidade movimentada por máquina"), use_container_width=True)
""")

w("pages/5_Cadastros.py", """
import streamlit as st
from pathlib import Path
from database.db import execute_script
from services.cadastros_service import get_maquinas, get_produtos, get_motivos, add_produto, add_motivo

st.title("Cadastros")

st.subheader("Inicialização do banco")
if st.button("Inicializar banco de dados"):
    schema = Path("database/schema.sql").read_text(encoding="utf-8")
    seed = Path("database/seed.sql").read_text(encoding="utf-8")
    execute_script(schema)
    execute_script(seed)
    st.success("Banco inicializado com sucesso.")

tab1, tab2, tab3 = st.tabs(["Máquinas", "Produtos", "Motivos da qualidade"])

with tab1:
    st.subheader("Máquinas cadastradas")
    st.dataframe(get_maquinas(), use_container_width=True, hide_index=True)

with tab2:
    st.subheader("Produtos")
    with st.form("novo_produto", clear_on_submit=True):
        c1, c2, c3, c4 = st.columns(4)
        codigo = c1.text_input("Código")
        descricao = c2.text_input("Descrição")
        familia = c3.text_input("Família")
        unidade = c4.text_input("Unidade", value="UN")
        enviar = st.form_submit_button("Adicionar produto")
        if enviar and codigo and descricao:
            add_produto(codigo, descricao, familia, unidade)
            st.success("Produto adicionado.")
    st.dataframe(get_produtos(), use_container_width=True, hide_index=True)

with tab3:
    st.subheader("Motivos da qualidade")
    with st.form("novo_motivo", clear_on_submit=True):
        c1, c2 = st.columns(2)
        descricao = c1.text_input("Motivo")
        categoria = c2.text_input("Categoria")
        enviar = st.form_submit_button("Adicionar motivo")
        if enviar and descricao:
            add_motivo(descricao, categoria)
            st.success("Motivo adicionado.")
    st.dataframe(get_motivos(), use_container_width=True, hide_index=True)
""")

w("pages/6_Relatorios.py", """
import streamlit as st
from datetime import date, timedelta
from services.producao_service import listar_producao
from services.qualidade_service import listar_qualidade
from services.processos_service import listar_processos
from utils.helpers import to_excel_bytes

st.title("Relatórios")

tipo = st.selectbox("Selecione o relatório", ["Produção", "Qualidade", "Processos"])
c1, c2 = st.columns(2)
data_ini = c1.date_input("Data inicial", value=date.today() - timedelta(days=30))
data_fim = c2.date_input("Data final", value=date.today())

if tipo == "Produção":
    df = listar_producao(data_ini, data_fim)
elif tipo == "Qualidade":
    df = listar_qualidade(data_ini, data_fim)
else:
    df = listar_processos(data_ini, data_fim)

st.dataframe(df, use_container_width=True, hide_index=True)
if not df.empty:
    st.download_button("Baixar Excel", data=to_excel_bytes(df), file_name=f"{tipo.lower()}.xlsx")
""")

w("README_STREAMLIT_CLOUD.md", """
# ERP industrial da fábrica — versão corrigida para Streamlit Cloud

## Correções aplicadas
- `app.py` limpo, sem criação de pastas/arquivos em tempo de execução
- banco SQLite salvo em `database/erp_fabrica.db`
- configuração básica em `.streamlit/config.toml`

## Como publicar
1. Suba a pasta do projeto para um repositório no GitHub
2. No Streamlit Cloud, escolha esse repositório
3. Defina o arquivo principal como `app.py`
4. Faça o deploy
5. Ao abrir o sistema, vá em **Cadastros** e clique em **Inicializar banco de dados**
""")

zip_path = "/mnt/data/fabrica_erp_streamlit_cloud_corrigido.zip"
with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as z:
    for p in dst.rglob("*"):
        z.write(p, p.relative_to(dst.parent))

print(f"Projeto corrigido em: {dst}")
print(f"ZIP: {zip_path}")
