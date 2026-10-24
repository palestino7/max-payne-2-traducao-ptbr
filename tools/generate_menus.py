# -*- coding: utf-8 -*-
import os

def write_cp1252(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w', encoding='cp1252', errors='replace') as f:
        f.write(content)

dialogtexts_content = """[DialogTexts]
{
	[MainDialog]
	{
		[PlayButton]				String = "&Jogar";
		[AdvancedButton]			String = "&Opções...";
		[QuitButton]				String = "&Sair";
			
		[VideoSettings]				String = "&Configurações de Vídeo";
		[DisplayAdapter]			String = "&Adaptador de Vídeo:";
		[ScreenMode]				String = "&Modo de Tela:";
		[Acceleration]				String = "&Aceleração:";
		[CustomizedGame]			String = "Escolher Jogo Customizado (&Mod)";
		[PlayUnmodifiedGame]		String = "<nenhum selecionado>";
		
		[DisclaimerText]			String = "Os nomes dos produtos são marcas registradas de seus respectivos proprietários, e não da Rockstar Games, Inc., sendo incluídos exclusivamente para fins de entretenimento. Nenhum produto, pessoa ou estabelecimento mencionado ou exibido neste jogo endossou este título ou qualquer uma das ações aqui descritas, nem possui qualquer vínculo com a Rockstar Games, Inc.";
	}

	[NotEnoughVidMemDialog]
	{
		[Title]						String = "Max Payne 2 - Aviso";
		
		[Text]						String = "A resolução de tela e as opções gráficas selecionadas exigirão aproximadamente %iMB de memória de vídeo, mas sua placa gráfica dispõe de apenas %iMB. É provável que ocorra falta de memória de vídeo. Por favor, utilize uma resolução menor e/ou reduza os ajustes gráficos no menu Opções.";
		[Text2]						String = "Deseja tentar executar o jogo mesmo assim?";

		[OKButton]					String = "Sim";
		[CancelButton]				String = "Não";
	}

	[AdvancedDialog]
	{
		[Title]						String = "Max Payne 2 - Opções";

		[VideoSettings]				String = "&Configurações de Vídeo";
		[Antialiasing]				String = "Antisserrilhamento:";
		[AntialiasingOff]			String = "Desligado";
		[AntialiasingSamples]		String = "%i amostras";
		
		[TextureColorDepth]			String = "Profundidade de Cor das Texturas:";
		[TextureColorDepthLow]		String = "Baixa";
		[TextureColorDepthMedium]	String = "Média";
		[TextureColorDepthHigh]		String = "Alta";
		
		[TextureResolution]			String = "Resolução das Texturas:";
		[TextureResolutionLow]		String = "Baixa";
		[TextureResolutionMedium]	String = "Média";
		[TextureResolutionHigh]		String = "Alta";
		[TextureFiltering]			String = "Filtragem de Texturas:";
		[TextureFilteringBilinear]	String = "Bilinear";
		[TextureFilteringTrilinear]	String = "Trilinear";
		[TextureFilteringAnisotropic] String = "Anisotrópica";
		
		[TripleScreenBuffers]		String = "Buffer Triplo na Tela:";
		[AllowTaskSwitching]		String = "Permitir Teclas do Windows:";

		[AudioSettings]				String = "&Configurações de Áudio";
		[Sounds]					String = "Efeitos Sonoros:";
		[EAXEffects]				String = "Efeitos Ambientais EAX:";
		[SoundChannels]				String = "Canais de Som:";
		[SoundChannelsLow]			String = "Baixo";
		[SoundChannelsMedium]		String = "Médio";
		[SoundChannelsHigh]			String = "Alto";
		
		[ContentScalability]		String = "&Escalabilidade de Conteúdo";
		[CharacterShadows]			String = "Sombras dos Personagens:";
		[CharacterShadowsLow]		String = "Baixa";
		[CharacterShadowsMedium]	String = "Média";
		[CharacterShadowsHigh]		String = "Alta";
		[Decals]					String = "Marcas de Tiros (Decals):";
		[DecalsLow]					String = "Baixo";
		[DecalsMedium]				String = "Médio";
		[DecalsHigh]				String = "Alto";
		[Projectiles]				String = "Estilhaços e Projéteis:";
		[ProjectilesLow]			String = "Baixo";
		[ProjectilesMedium]			String = "Médio";
		[ProjectilesHigh]			String = "Alto";
		[CharacterVariations]		String = "Variações de Personagens:";
		[CharacterVariationsLow]	String = "Baixa";
		[CharacterVariationsMedium]	String = "Média";
		[CharacterVariationsHigh]	String = "Alta";
		[MaterialVariations]		String = "Variações de Materiais:";
		[MaterialVariationsLow]		String = "Baixa";
		[MaterialVariationsMedium]	String = "Média";
		[MaterialVariationsHigh]	String = "Alta";
		[Fogging]					String = "Efeito de Névoa:";
		[Flares]					String = "Reflexos de Luz (Flares):";
		[Mirrors]					String = "Espelhos:";
		[HighDetailRagdolls]		String = "Física Ragdoll Detalhada:";
		[HighDetailParticles]		String = "Partículas Detalhadas:";
		[CubicEnvironmentMaps]		String = "Mapeamento Cúbico de Ambiente:";
		[MultiChannelAudio]			String = "Áudio Multicanal:";
		[PostProcessEffects]		String = "Efeitos de Pós-Processamento:";
		[PostProcessEffectsOff]		String = "Desligado";
		[PostProcessEffectsMedium]	String = "Médio";
		[PostProcessEffectsHigh]	String = "Alto";
		[PixelShaderSkinning]		String = "Skins com Pixel Shader:";

		[ResetAllSettingsTo]		String = "Redefinir Tudo Para:";
		[ResetLow]					String = "&Baixo";
		[ResetMedium]				String = "&Médio";
		[ResetHigh]					String = "&Alto";

		[OKButton]					String = "OK";
		[CancelButton]				String = "Cancelar";

		[TipAntialiasing]			String = "O Antisserrilhamento suaviza bordas serrilhadas, exigindo maior poder de processamento da placa de vídeo. Se notar quedas de desempenho, recomenda-se desativá-lo.";
		[TipTextTextureColorDepth]	String = "Altera a profundidade de cor das texturas e o consumo de memória. Texturas compactadas são usadas sempre que suportadas. Defina como Alto apenas se tiver memória de vídeo e RAM suficientes.";
		[TipTextureResolution]		String = "Altera a nitidez das texturas em todo o jogo e influencia diretamente o uso de memória.";
		[TipTextFilteringMode]		String = "Altera a filtragem de texturas. Trilinear e Anisotrópica oferecem ganho nítido na qualidade visual à distância, com impacto leve no desempenho.";
		[TipTripleBuffering]		String = "Alterna entre Buffer Duplo e Triplo. O Buffer Duplo é o padrão recomendado. O Buffer Triplo consome mais memória, mas pode tornar a taxa de quadros mais estável em certos cenários.";
		[TipTextTaskSwitching]		String = "Permite o funcionamento de combinações de teclas do Windows, como ALT+F4 (fechar jogo) e ALT+ENTER (alternar modo janela).";

		[TipSounds]					String = "Liga ou desliga todos os sons do jogo.";
		[TipTextEAX]				String = "Adiciona reverberação e eco ambiental realista via Creative Labs EAX. Caso ocorram problemas de áudio, desative para maior compatibilidade.";
		[TipMultiChannelAudio]		String = "Melhora o posicionamento do áudio em configurações com caixas 5.1. Mantenha desativado caso esteja utilizando fones de ouvido ou som estéreo padrão.";
		[TipSoundChannels]			String = "Ajusta a quantidade simultânea de canais de áudio. Níveis mais altos produzem um ambiente sonoro mais rico e denso.";

		[TipTextCharacterShadows]	String = "Controla a qualidade das sombras projetadas pelos personagens. Requer suporte a Pixel Shader 1.1 para níveis médio e alto.";
		[TipDecals]					String = "Define o limite máximo de marcas de tiros e impactos exibidos nas paredes e superfícies.";
		[TipProjectiles]			String = "Controla os detritos físicos no combate, como cápsulas de balas ejetadas e estilhaços pelo cenário.";
		[TipMaterialVariations]		String = "Níveis mais altos oferecem maior variedade de sons e efeitos visuais ao atingir diferentes materiais (vidro, madeira, metal, concreto).";
		[TipPostProcessEffects]		String = "Controla os efeitos visuais de Desfoque de Movimento e Remapeamento de Tons durante o Bullet Time.";

		[TipCubicEnvironmentMaps]	String = "Mapeamento cúbico para reflexos em superfícies metálicas e espelhadas. Desative em caso de problemas visuais.";
		[TipTextFogging]			String = "Névoa de distância volumétrica. Mantenha ativada para preservar a atmosfera sombria original do jogo.";
		[TipFlares]					String = "Brilho e reflexo em torno de lâmpadas e focos intensos de luz.";
		[TipMirrors]				String = "Permite reflexos em tempo real nos espelhos de banheiros e provadores.";
		[TipHighDetailRagdolls]		String = "Aprimora o realismo das quedas e reações físicas dos corpos ao serem alvejados.";
		[TipTextParticleDetail]		String = "Intensidade das faíscas, fumaça e poeira geradas em explosões e tiroteios.";
		[TipPixelShaderSkinning]	String = "Iluminação avançada sobre a pele e roupas dos personagens via Pixel Shader.";
	}	
}
"""

stringtable_content = """[HUDPRINT_SURVIVAL_KILL]			String = "+2 seg";
[HUDPRINT_PICKUP_BERETTA_AMMO]		String = "Munição de Pistola 9mm";
[HUDPRINT_PICKUP_DESERTEAGLE_AMMO]	String = "Munição de Desert Eagle";
[HUDPRINT_PICKUP_SHOTGUN_AMMO]		String = "Munição de Escopeta";
[HUDPRINT_PICKUP_STRIKER_AMMO]		String = "Munição de Striker";
[HUDPRINT_PICKUP_INGRAM_AMMO]		String = "Munição de Ingram";
[HUDPRINT_PICKUP_MP5_AMMO]			String = "Munição de MP5";
[HUDPRINT_PICKUP_KALASHNIKOV_AMMO]	String = "Munição de Kalashnikov";
[HUDPRINT_PICKUP_COLTCOMMANDO_AMMO]	String = "Munição de Carabina M4";
[HUDPRINT_PICKUP_SNIPER_AMMO]     	String = "Munição de Fuzil de Precisão";
[HUDPRINT_PICKUP_DRAGUNOV_AMMO]    	String = "Munição de Dragunov";

[HUDPRINT_PICKUP_BERETTA]			String = "Pistola 9mm";
[HUDPRINT_PICKUP_BERETTADUAL]		String = "Pistolas 9mm Duplas";
[HUDPRINT_PICKUP_DESERTEAGLE]		String = "Desert Eagle";
[HUDPRINT_PICKUP_SAWEDSHOTGUN]		String = "Escopeta de Cano Serrado";
[HUDPRINT_PICKUP_PUMPSHOTGUN]		String = "Escopeta Pump-Action";
[HUDPRINT_PICKUP_STRIKER]			String = "Striker";
[HUDPRINT_PICKUP_INGRAM]			String = "Ingram";
[HUDPRINT_PICKUP_INGRAMDUAL]		String = "Ingrams Duplas";
[HUDPRINT_PICKUP_MP5]				String = "MP5";
[HUDPRINT_PICKUP_KALASHNIKOV]		String = "Kalashnikov";
[HUDPRINT_PICKUP_COLTCOMMANDO]		String = "Carabina M4";
[HUDPRINT_PICKUP_SNIPER]		    String = "Fuzil de Precisão";
[HUDPRINT_PICKUP_DRAGUNOV]		    String = "Dragunov";
[HUDPRINT_PICKUP_PAINKILLERS]	   	String = "Analgésicos";
[HUDPRINT_PICKUP_MOLOTOV]			String = "Coquetel Molotov";
[HUDPRINT_PICKUP_GRENADE]			String = "Granada";

[HUDPRINT_PICKUP_BERETTA_AMMO_FULL]			String = "Munição de 9mm cheia";
[HUDPRINT_PICKUP_DESERTEAGLE_AMMO_FULL]		String = "Munição de Desert Eagle cheia";
[HUDPRINT_PICKUP_SHOTGUN_AMMO_FULL]			String = "Munição de Escopeta cheia";
[HUDPRINT_PICKUP_STRIKER_AMMO_FULL]			String = "Munição de Striker cheia";
[HUDPRINT_PICKUP_INGRAM_AMMO_FULL]			String = "Munição de Ingram cheia";
[HUDPRINT_PICKUP_MP5_AMMO_FULL]				String = "Munição de MP5 cheia";
[HUDPRINT_PICKUP_KALASHNIKOV_AMMO_FULL]		String = "Munição de Kalashnikov cheia";
[HUDPRINT_PICKUP_COLTCOMMANDO_AMMO_FULL]	String = "Munição de Carabina M4 cheia";
[HUDPRINT_PICKUP_SNIPER_AMMO_FULL]			String = "Munição de Fuzil de Precisão cheia";
[HUDPRINT_PICKUP_DRAGUNOV_AMMO_FULL]		String = "Munição de Dragunov cheia";
[HUDPRINT_PICKUP_PAINKILLERS_FULL]			String = "Analgésicos cheios";
[HUDPRINT_PICKUP_MOLOTOV_AMMO_FULL]			String = "Coquetéis Molotov cheios";
[HUDPRINT_PICKUP_GRENADE_AMMO_FULL]			String = "Granadas cheias";

[NoPauseCameraPathText]				String = "Pausado"; 
[QuickSaveGameDescriptionPrefix]	String = "Rápido: ";
[AutoSaveGameDescriptionPrefix]		String = "Automático: ";
[QuickLoadQueryText]				String = "Pressione F9 novamente para Carregamento Rápido, Esc para Cancelar";

[HUDPRINT_PRESS_USE_TO_LOAD]		String = "Pressione a tecla de usar (#USE#) para carregar o último jogo salvo.";
[HUDPRINT_PRESS_F9_TO_LOAD]			String = "Pressione a tecla de carregamento rápido (F9) para carregar o último jogo salvo.";
[TIP_PAUSECAMERA]					String = "Dica: Pressione #PAUSE# para desativar o modo de pausa.";
[TIP_SNIPER]					    String = "Dica: Mantenha pressionada a tecla de usar (#USE#) para aproximar a mira do fuzil de precisão.";
[TIP_PAINKILLER]					String = "Dica: Pressione #PAINKILLER# para tomar analgésicos e aliviar a dor.";
[TIP_EXAMINE]						String = "Dica: Pressione a tecla de usar (#USE#) para examinar ou interagir com itens interessantes.";
[TIP_SHOOTDODGE]					String = "Dica: Pressione a tecla de Salto com Tiro (#DODGEMODIFIER#) e uma direção para executar o Shootdodge.";
[TIP_BULLETTIME]					String = "Dica: Pressione Bullet Time (#SLOWMOTION#) para entrar em câmera lenta.";
[TIP_DODGE]							String = "Dica: Pressione #JUMP# e uma tecla de direção para realizar esquivas e rolamentos.";

[STRING_NORMAL_COMPLETED1]			String = "Parabéns! Você concluiu Max Payne 2: The Fall of Max Payne.";
[STRING_NORMAL_COMPLETED2]			String = "Os modos Homem Morto Andando e Minuto de Nova York, além do";
[STRING_NORMAL_COMPLETED3]			String = "nível de dificuldade Casca-Grossa, foram desbloqueados para desafios ainda maiores.";

[STRING_NIGHTMARE_COMPLETED1]		String = "Parabéns!";
[STRING_NIGHTMARE_COMPLETED2]		String = "Você concluiu o modo Casca-Grossa. Agora prepare-se para";
[STRING_NIGHTMARE_COMPLETED3]		String = "o desafio definitivo no modo Morto ao Chegar.";

[STRING_HELL_COMPLETED1]			String = "Parabéns!";
[STRING_HELL_COMPLETED2]			String = "Você concluiu o modo Morto ao Chegar —";
[STRING_HELL_COMPLETED3]			String = "o maior e mais implacável desafio de todos.";

[STRING_NYM_MAP]					String = "Seu tempo atual é: #TOTALTIME#";
[STRING_NYM_PART1_PAR]				String = "Tempo de referência da Remedy neste ponto: 0:16:19";
[STRING_NYM_PART2_PAR]				String = "Tempo de referência da Remedy neste ponto: 0:27:41";

[STRING_TIMEDMODE_COMPLETED1]		String = "Parabéns! Minuto de Nova York Concluído —";
[STRING_TIMEDMODE_COMPLETED2]		String = "Você venceu a corrida implacável contra o relógio.";
[STRING_TIMEDMODE_COMPLETED3]		String = "Seu tempo total foi de #TOTALTIME#";
[STRING_TIMEDMODE_COMPLETED4]		String = "Tempo de referência da Remedy: 0:46:29";
"""

write_cp1252('translation_ptbr/data/dialogtexts.txt', dialogtexts_content)
write_cp1252('translation_ptbr/data/database/stringtable.txt', stringtable_content)
print("dialogtexts.txt and stringtable.txt written.")
