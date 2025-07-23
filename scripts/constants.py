COLS_TRAIN = ['atletas.rodada_id', 'atletas.status_id', 'atletas.pontos_num',
       'atletas.media_num', 'atletas.atleta_id',
       'atletas.jogos_num', 'atletas.posicao_id',
       'atletas.preco_num', 'atletas.minimo_para_valorizar',
       'aproveitamento_visitante',
       'aproveitamento_mandante', 'partida_id',
       'clube_visitante_posicao', 'clube_visitante_id', 'clube_casa_posicao',
       'clube_casa_id', 'campeonato_id', 'valida', 'mandante']
COLS_TARGET = 'atletas.pontos_num'

COLS_CUTOUT = 'atletas.rodada_id'
TEST_CUTOUT = 12