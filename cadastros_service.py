from database.db import query_df, execute
def get_maquinas(): return query_df("SELECT * FROM maquinas WHERE ativo = 1 ORDER BY nome")
def get_produtos(): return query_df("SELECT * FROM produtos WHERE ativo = 1 ORDER BY descricao")
def get_motivos(): return query_df("SELECT * FROM motivos_qualidade ORDER BY descricao")
def add_produto(codigo, descricao, familia, unidade): execute('INSERT INTO produtos (codigo, descricao, familia, unidade) VALUES (:codigo,:descricao,:familia,:unidade)',{"codigo":codigo,"descricao":descricao,"familia":familia,"unidade":unidade})
def add_motivo(descricao, categoria): execute('INSERT INTO motivos_qualidade (descricao, categoria) VALUES (:descricao,:categoria)',{"descricao":descricao,"categoria":categoria})
