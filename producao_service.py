from database.db import execute, query_df
def inserir_producao(data, maquina_id, produto_id, meta, quantidade, horas_disp, horas_paradas, refugo, retrabalho, observacao):
    execute('INSERT INTO producao (data,maquina_id,produto_id,meta,quantidade_produzida,horas_disponiveis,horas_paradas,refugo,retrabalho,observacao) VALUES (:data,:maquina_id,:produto_id,:meta,:quantidade,:horas_disp,:horas_paradas,:refugo,:retrabalho,:observacao)',locals())
def listar_producao(data_ini=None,data_fim=None):
    sql='SELECT p.id,p.data,m.nome AS maquina,m.processo,pr.codigo,pr.descricao AS produto,p.meta,p.quantidade_produzida,p.horas_disponiveis,p.horas_paradas,p.refugo,p.retrabalho,p.observacao FROM producao p JOIN maquinas m ON m.id=p.maquina_id JOIN produtos pr ON pr.id=p.produto_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND p.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND p.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' ORDER BY p.data DESC,m.nome',params)
def resumo_por_maquina(data_ini=None,data_fim=None):
    sql='SELECT m.nome AS maquina,SUM(p.meta) AS meta,SUM(p.quantidade_produzida) AS produzido,SUM(p.refugo) AS refugo,SUM(p.retrabalho) AS retrabalho,SUM(p.horas_disponiveis) AS horas_disponiveis FROM producao p JOIN maquinas m ON m.id=p.maquina_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND p.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND p.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' GROUP BY m.nome ORDER BY m.nome',params)
def resumo_diario(data_ini=None,data_fim=None):
    sql='SELECT p.data,SUM(p.meta) AS meta,SUM(p.quantidade_produzida) AS produzido,SUM(p.refugo) AS refugo,SUM(p.retrabalho) AS retrabalho FROM producao p WHERE 1=1'; params={}
    if data_ini: sql+=' AND p.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND p.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' GROUP BY p.data ORDER BY p.data',params)
