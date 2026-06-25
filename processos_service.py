from database.db import execute, query_df
def inserir_processo(data, maquina_id, produto_id, tempo_setup, tempo_injecao, quantidade_movimentada, observacao):
    execute('INSERT INTO processos (data,maquina_id,produto_id,tempo_setup,tempo_injecao,quantidade_movimentada,observacao) VALUES (:data,:maquina_id,:produto_id,:tempo_setup,:tempo_injecao,:quantidade_movimentada,:observacao)',locals())
def listar_processos(data_ini=None,data_fim=None):
    sql='SELECT prc.id,prc.data,m.nome AS maquina,m.processo,p.codigo,p.descricao AS produto,prc.tempo_setup,prc.tempo_injecao,prc.quantidade_movimentada,prc.observacao FROM processos prc JOIN maquinas m ON m.id=prc.maquina_id JOIN produtos p ON p.id=prc.produto_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND prc.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND prc.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' ORDER BY prc.data DESC,m.nome',params)
def resumo_maquina(data_ini=None,data_fim=None):
    sql='SELECT m.nome AS maquina,AVG(prc.tempo_setup) AS setup_medio,AVG(prc.tempo_injecao) AS injecao_media,SUM(prc.quantidade_movimentada) AS qtd_movimentada FROM processos prc JOIN maquinas m ON m.id=prc.maquina_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND prc.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND prc.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' GROUP BY m.nome ORDER BY m.nome',params)
