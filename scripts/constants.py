COLS_TRAIN = ['atletas.rodada_id', 'atletas.status_id', 'atletas.pontos_num',
       'atletas.media_num', 'atletas.atleta_id',
       'atletas.posicao_id',
       'atletas.preco_num', 'atletas.minimo_para_valorizar',
       'aproveitamento_visitante',
       'aproveitamento_mandante',
       'clube_visitante_posicao', 'clube_visitante_id', 'clube_casa_posicao',
       'clube_casa_id', 'campeonato_id', 'valida', 'mandante', 'media_CA_5_rodadas','media_DS_5_rodadas','media_FC_5_rodadas',
       'media_FF_5_rodadas','media_FS_5_rodadas','media_I_5_rodadas','media_SG_5_rodadas','media_FD_5_rodadas','media_A_5_rodadas','media_G_5_rodadas',
       'media_CV_5_rodadas','media_FT_5_rodadas', 'media_PC_5_rodadas','media_PS_5_rodadas','media_DE_5_rodadas',
       'media_GS_5_rodadas','media_V_5_rodadas','media_DP_5_rodadas','media_PP_5_rodadas','media_GC_5_rodadas']
COLS_TARGET = 'atletas.pontos_num'

COLS_CUTOUT = 'atletas.rodada_id'
TEST_CUTOUT = 12
RODADA_ID = 'atletas.rodada_id'
ATLETAS_ID = 'atletas.atleta_id'
PONTOS_NUM = 'atletas.pontos_num'
PREVISAO_PONTOS = 'previsao_pontos'

SCOUT = ['CA','DS','FC','FF','FS','I','SG','FD','A','G','CV','FT','PC','PS','DE','GS','V','DP','PP','GC']