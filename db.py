from pathlib import Path
from sqlalchemy import create_engine, text
import pandas as pd
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "erp_fabrica.db"
ENGINE = create_engine(f"sqlite:///{DB_PATH}", future=True)
SCHEMA_SQL = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS maquinas (id INTEGER PRIMARY KEY AUTOINCREMENT,nome TEXT NOT NULL UNIQUE,processo TEXT NOT NULL,ativo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS produtos (id INTEGER PRIMARY KEY AUTOINCREMENT,codigo TEXT NOT NULL UNIQUE,descricao TEXT NOT NULL,familia TEXT,unidade TEXT DEFAULT 'UN',ativo INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS motivos_qualidade (id INTEGER PRIMARY KEY AUTOINCREMENT,descricao TEXT NOT NULL UNIQUE,categoria TEXT);
CREATE TABLE IF NOT EXISTS producao (id INTEGER PRIMARY KEY AUTOINCREMENT,data DATE NOT NULL,maquina_id INTEGER NOT NULL,produto_id INTEGER NOT NULL,meta REAL NOT NULL DEFAULT 0,quantidade_produzida REAL NOT NULL DEFAULT 0,horas_disponiveis REAL NOT NULL DEFAULT 0,horas_paradas REAL NOT NULL DEFAULT 0,refugo REAL NOT NULL DEFAULT 0,retrabalho REAL NOT NULL DEFAULT 0,observacao TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (maquina_id) REFERENCES maquinas(id),FOREIGN KEY (produto_id) REFERENCES produtos(id));
CREATE TABLE IF NOT EXISTS qualidade_registros (id INTEGER PRIMARY KEY AUTOINCREMENT,data DATE NOT NULL,maquina_id INTEGER NOT NULL,produto_id INTEGER NOT NULL,tipo_registro TEXT NOT NULL CHECK (tipo_registro IN ('Refugo','Retrabalho')),motivo_id INTEGER,quantidade REAL NOT NULL DEFAULT 0,observacao TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (maquina_id) REFERENCES maquinas(id),FOREIGN KEY (produto_id) REFERENCES produtos(id),FOREIGN KEY (motivo_id) REFERENCES motivos_qualidade(id));
CREATE TABLE IF NOT EXISTS processos (id INTEGER PRIMARY KEY AUTOINCREMENT,data DATE NOT NULL,maquina_id INTEGER NOT NULL,produto_id INTEGER NOT NULL,tempo_setup REAL NOT NULL DEFAULT 0,tempo_injecao REAL NOT NULL DEFAULT 0,quantidade_movimentada REAL NOT NULL DEFAULT 0,observacao TEXT,created_at DATETIME DEFAULT CURRENT_TIMESTAMP,FOREIGN KEY (maquina_id) REFERENCES maquinas(id),FOREIGN KEY (produto_id) REFERENCES produtos(id));
"""
SEED_SQL = """
INSERT OR IGNORE INTO maquinas (nome, processo) VALUES ('INJ 01','RIM'),('INJ 02','CORINGA'),('INJ 03','ESTRUTURAL'),('INJ 04','SEMI-RIM'),('INJ 05','FLEXIVEL'),('INJ 06','VISCO'),('INJ 07','PELE INTEGRAL');
INSERT OR IGNORE INTO motivos_qualidade (descricao, categoria) VALUES ('Rebarba','Visual'),('Bolha','Processo'),('Falta de material','Processo'),('Dimensional fora','Dimensional'),('Queima','Processo'),('Deformação','Dimensional');
INSERT OR IGNORE INTO produtos (codigo, descricao, familia, unidade) VALUES ('P001','Produto exemplo 1','Linha A','UN'),('P002','Produto exemplo 2','Linha A','UN'),('P003','Produto exemplo 3','Linha B','UN');
"""
def db_exists(): return DB_PATH.exists()
def execute_script(sql_text:str):
    with ENGINE.begin() as conn:
        for stmt in [s.strip() for s in sql_text.split(";") if s.strip()]:
            conn.execute(text(stmt))
def init_db():
    execute_script(SCHEMA_SQL); execute_script(SEED_SQL)
def query_df(sql, params=None):
    with ENGINE.begin() as conn: return pd.read_sql(text(sql), conn, params=params or {})
def execute(sql, params=None):
    with ENGINE.begin() as conn: conn.execute(text(sql), params or {})
def scalar(sql, params=None, default=0):
    with ENGINE.begin() as conn: v=conn.execute(text(sql), params or {}).scalar()
    return default if v is None else v
