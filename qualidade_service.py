from database.db import execute, query_df
def inserir_qualidade(data, maquina_id, produto_id, tipo_registro, motivo_id, quantidade, observacao):
    execute('INSERT INTO qualidade_registros (data,maquina_id,produto_id,tipo_registro,motivo_id,quantidade,observacao) VALUES (:data,:maquina_id,:produto_id,:tipo_registro,:motivo_id,:quantidade,:observacao)',locals())
def listar_qualidade(data_ini=None,data_fim=None):
    sql='SELECT q.id,q.data,m.nome AS maquina,m.processo,p.codigo,p.descricao AS produto,q.tipo_registro,COALESCE(mq.descricao,"") AS motivo,q.quantidade,q.observacao FROM qualidade_registros q JOIN maquinas m ON m.id=q.maquina_id JOIN produtos p ON p.id=q.produto_id LEFT JOIN motivos_qualidade mq ON mq.id=q.motivo_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND q.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND q.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' ORDER BY q.data DESC,m.nome',params)
def resumo_tipo_maquina(data_ini=None,data_fim=None):
    sql='SELECT m.nome AS maquina,q.tipo_registro,SUM(q.quantidade) AS quantidade FROM qualidade_registros q JOIN maquinas m ON m.id=q.maquina_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND q.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND q.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' GROUP BY m.nome,q.tipo_registro ORDER BY m.nome',params)
def resumo_motivos(data_ini=None,data_fim=None):
    sql='SELECT COALESCE(mq.descricao,"Sem motivo") AS motivo,SUM(q.quantidade) AS quantidade FROM qualidade_registros q LEFT JOIN motivos_qualidade mq ON mq.id=q.motivo_id WHERE 1=1'; params={}
    if data_ini: sql+=' AND q.data >= :data_ini'; params["data_ini"]=str(data_ini)
    if data_fim: sql+=' AND q.data <= :data_fim'; params["data_fim"]=str(data_fim)
    return query_df(sql+' GROUP BY COALESCE(mq.descricao,"Sem motivo") ORDER BY quantidade DESC',params)
