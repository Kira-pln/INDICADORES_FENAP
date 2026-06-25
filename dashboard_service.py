from database.db import scalar
from services.producao_service import resumo_por_maquina,resumo_diario
from services.qualidade_service import resumo_tipo_maquina,resumo_motivos
from services.processos_service import resumo_maquina
def indicadores_gerais(data_ini=None,data_fim=None):
    params={}; wp=' WHERE 1=1 '; wr=' WHERE 1=1 '
    if data_ini: params['data_ini']=str(data_ini); wp+=' AND data >= :data_ini '; wr+=' AND data >= :data_ini '
    if data_fim: params['data_fim']=str(data_fim); wp+=' AND data <= :data_fim '; wr+=' AND data <= :data_fim '
    meta=scalar(f'SELECT SUM(meta) FROM producao {wp}',params,0); produzido=scalar(f'SELECT SUM(quantidade_produzida) FROM producao {wp}',params,0); refugo=scalar(f'SELECT SUM(refugo) FROM producao {wp}',params,0); retrabalho=scalar(f'SELECT SUM(retrabalho) FROM producao {wp}',params,0); setup_medio=scalar(f'SELECT AVG(tempo_setup) FROM processos {wr}',params,0); injecao_media=scalar(f'SELECT AVG(tempo_injecao) FROM processos {wr}',params,0)
    return {"meta":meta,"produzido":produzido,"atingimento":(produzido/meta*100) if meta else 0,"refugo":refugo,"retrabalho":retrabalho,"setup_medio":setup_medio,"injecao_media":injecao_media,"qualidade":((produzido-refugo)/produzido*100) if produzido else 0}
def datasets_dashboard(data_ini=None,data_fim=None):
    return {"prod_maquina":resumo_por_maquina(data_ini,data_fim),"prod_diario":resumo_diario(data_ini,data_fim),"qual_maquina":resumo_tipo_maquina(data_ini,data_fim),"qual_motivos":resumo_motivos(data_ini,data_fim),"proc_maquina":resumo_maquina(data_ini,data_fim)}
