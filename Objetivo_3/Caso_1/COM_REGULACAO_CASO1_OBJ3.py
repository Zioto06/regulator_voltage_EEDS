# Importa as bibliotecas necessárias
from google.colab import drive
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# ============================================================================
# 1. CONEXÃO COM O GOOGLE DRIVE E CONFIGURAÇÕES DA EXECUÇÃO
# ============================================================================
try:
    drive.mount('/content/drive')
except ValueError:
    pass # Ignora o erro se o drive já estiver montado

# ============================================================================
# ATENÇÃO: ALTERE ESTAS DUAS VARIÁVEIS ANTES DE RODAR PARA CADA CASO
# ============================================================================
caminho_pasta = '/content/drive/MyDrive/XXXX'
nome_do_caso = '[LDC Desligado]' # Mude o nome do caso de acordo com a pasta
# ============================================================================

prefixo = os.path.join(caminho_pasta, "FEEDER_Mon_")
arquivo_p10 = os.path.join(caminho_pasta, "FEEDER_Mon_vp10_1.csv")

# ============================================================================
# 2. DEFINIÇÕES DE BASES E CONFIGURAÇÕES DOS NÓS
# ============================================================================
vbase_mt = 13800 / (3**0.5)
vbase_bt_urbana = 127.0
vbase_bt_rural = 120.0

mt_configs = {
    'vp1': ('P1 - Subestação', vbase_mt),
    'vp2': ('P2 - Barramento (Pós-Regulador)', vbase_mt),
    'vp3': ('P3 - Primário trafo 75kVA', vbase_mt),
    'vp4': ('P4 - Fim do tronco MT', vbase_mt),
    'vp5': ('P5 - Ramal rural', vbase_mt)
}

bt_configs = {
    'vp6':  ('P6 - 120V perna B (rural)', vbase_bt_rural),
    'vp7':  ('P7 - BT (secundário trafo)', vbase_bt_urbana),
    'vp8':  ('P8 - BT', vbase_bt_urbana),
    'vp9':  ('P9 - BT (com GD)', vbase_bt_urbana),
    'vp10': ('P10 - BT (fim da rede)', vbase_bt_urbana)
}

# ============================================================================
# 3. FUNÇÕES DE EXTRAÇÃO E CÁLCULOS
# ============================================================================

# --- 3.1 Extração de Tensão (pu) para MT e BT ---
def compilar_dados_pu(configs, tipo):
    df_final = pd.DataFrame()
    for mon, (label, base) in configs.items():
        arquivo = f"{prefixo}{mon}_1.csv"
        if os.path.exists(arquivo):
            df = pd.read_csv(arquivo, skipinitialspace=True)
            col_v1 = [c for c in df.columns if 'V1' in c][0]
            if df_final.empty:
                df_final['Hora'] = df['hour'] + df['t(sec)'] / 3600.0
            df_final[label] = df[col_v1] / base
    return df_final

df_mt = compilar_dados_pu(mt_configs, "MÉDIA TENSÃO")
df_bt = compilar_dados_pu(bt_configs, "BAIXA TENSÃO")

# --- 3.2 Extração de Neutro e Cálculo de Desequilíbrio (Nó P10) CORRIGIDO ---
def processar_dados_p10(arquivo):
    if not os.path.exists(arquivo):
        print(f"❌ Arquivo do Nó P10 não encontrado: {arquivo}")
        return pd.DataFrame()

    df = pd.read_csv(arquivo, skipinitialspace=True)
    df.columns = df.columns.str.strip()

    df['Hora'] = df['hour'] + df['t(sec)'] / 3600.0

    # Conversão de Magnitude e Ângulo (Graus) para números complexos
    Va = df['V1'] * np.exp(1j * np.radians(df['VAngle1']))
    Vb = df['V2'] * np.exp(1j * np.radians(df['VAngle2']))
    Vc = df['V3'] * np.exp(1j * np.radians(df['VAngle3']))

    # Operador rotacional 'a' (120 graus)
    a = np.exp(1j * np.radians(120))
    a2 = np.exp(1j * np.radians(240))

    # Sequências Positiva, Negativa e Zero
    Vpos = (Va + a * Vb + a2 * Vc) / 3
    Vneg = (Va + a2 * Vb + a * Vc) / 3
    Vzero = (Va + Vb + Vc) / 3

    # Fator de Desequilíbrio de Tensão (FD%)
    df['FD_perc'] = (np.abs(Vneg) / np.abs(Vpos)) * 100

    # Tensão de Neutro: Se a coluna V4 não existir, usa a Sequência Zero
    if 'V4' in df.columns:
        df['V_Neutro'] = df['V4']
    else:
        df['V_Neutro'] = np.abs(Vzero)

    return df

df_p10 = processar_dados_p10(arquivo_p10)


# ============================================================================
# 4. FUNÇÕES DE PLOTAGEM
# ============================================================================

# --- Função 4.1: Plotagem dos Perfis de Tensão (MT e BT) ---
def plotar_perfil_estilo_relatorio(df, titulo, subtitulo, is_bt=False):
    fig, ax = plt.subplots(figsize=(12, 7.5), dpi=120)
    cor_fundo = '#f9f9f5'
    fig.patch.set_facecolor(cor_fundo)
    ax.set_facecolor(cor_fundo)

    cor_critica = '#f4cccc'
    cor_precaria = '#fce5cd'
    cor_adequada = '#d9ead3'

    if not is_bt:
        ax.axhspan(1.05, 1.10, facecolor=cor_critica, alpha=1)
        ax.axhspan(0.93, 1.05, facecolor=cor_adequada, alpha=1)
        ax.axhspan(0.90, 0.93, facecolor=cor_precaria, alpha=1)
        ax.axhspan(0.80, 0.90, facecolor=cor_critica, alpha=1)

        ax.axhline(1.05, color='#e06666', linestyle='--', linewidth=1, alpha=0.8)
        ax.axhline(0.93, color='#f6b26b', linestyle='--', linewidth=1, alpha=0.8)
        ax.axhline(0.90, color='#e06666', linestyle='--', linewidth=1, alpha=0.8)

        ax.text(0.1, 1.055, 'Crítica', color='#cc0000', fontsize=10)
        ax.text(0.1, 1.035, 'Adequada', color='#38761d', fontsize=10)
        ax.text(0.1, 0.915, 'Precária', color='#b45f06', fontsize=10)
        ax.text(0.1, 0.885, 'Crítica', color='#cc0000', fontsize=10)

        cores_linhas = ['#1f77b4', '#003366', '#556b2f', '#66cc00', '#8b4513']
    else:
        ax.axhspan(1.06, 1.10, facecolor=cor_critica, alpha=1)
        ax.axhspan(1.05, 1.06, facecolor=cor_precaria, alpha=1)
        ax.axhspan(0.92, 1.05, facecolor=cor_adequada, alpha=1)
        ax.axhspan(0.87, 0.92, facecolor=cor_precaria, alpha=1)
        ax.axhspan(0.80, 0.87, facecolor=cor_critica, alpha=1)

        ax.axhline(1.06, color='#e06666', linestyle='--', linewidth=1, alpha=0.8)
        ax.axhline(1.05, color='#f6b26b', linestyle='--', linewidth=1, alpha=0.8)
        ax.axhline(0.92, color='#f6b26b', linestyle='--', linewidth=1, alpha=0.8)
        ax.axhline(0.87, color='#e06666', linestyle='--', linewidth=1, alpha=0.8)

        ax.text(0.1, 1.062, 'Crítica', color='#cc0000', fontsize=10)
        ax.text(0.1, 1.042, 'Adequada', color='#38761d', fontsize=10)
        ax.text(0.1, 0.905, 'Precária', color='#b45f06', fontsize=10)
        ax.text(0.1, 0.855, 'Crítica', color='#cc0000', fontsize=10)

        cores_linhas = ['#d95f02', '#b8860b', '#7570b3', '#a0522d', '#e31a1c', '#1b9e77']

    idx_cor = 0
    for col in df.columns:
        if col != 'Hora':
            ax.plot(df['Hora'], df[col], label=col, linewidth=2, color=cores_linhas[idx_cor])
            idx_cor += 1

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')

    ax.set_xlim(0, 24)
    ax.set_ylim(0.84, 1.07)
    ax.set_xticks(range(0, 25, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 2)])
    ax.set_yticks([0.84, 0.90, 0.95, 1.00, 1.05, 1.07])

    ax.tick_params(axis='both', colors='#555555', length=0, pad=8)
    ax.grid(axis='x', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)
    ax.set_ylabel('Tensão (pu)', fontsize=11, color='#555555')

    plt.figtext(0.08, 0.93, titulo, fontsize=14, fontweight='bold', color='#333333')
    plt.figtext(0.08, 0.89, subtitulo, fontsize=11, color='#555555')

    plt.subplots_adjust(top=0.82, bottom=0.3, left=0.08, right=0.95)

    handles, labels = ax.get_legend_handles_labels()
    leg_linhas = ax.legend(handles, labels, loc='upper left', bbox_to_anchor=(0, -0.1), ncol=4, frameon=False, fontsize=10)

    patch_adeq = mpatches.Patch(color=cor_adequada, label='Adequada')
    patch_prec = mpatches.Patch(color=cor_precaria, label='Precária')
    patch_crit = mpatches.Patch(color=cor_critica, label='Crítica')
    ax.legend(handles=[patch_adeq, patch_prec, patch_crit], loc='upper left', bbox_to_anchor=(0, -0.22), ncol=3, frameon=False, fontsize=10, handlelength=1.5, handleheight=1.5)

    ax.add_artist(leg_linhas)
    plt.show()

# --- Função 4.2: Plotagem do Indicador (Neutro ou Desequilíbrio) ---
def plotar_indicador(df, coluna, titulo, subtitulo, ylabel, ylim_max, cor_linha, limite_prodist=None):
    fig, ax = plt.subplots(figsize=(12, 5), dpi=120)

    cor_fundo = '#f9f9f5'
    fig.patch.set_facecolor(cor_fundo)
    ax.set_facecolor(cor_fundo)

    ax.plot(df['Hora'], df[coluna], linewidth=2, color=cor_linha, label=coluna)

    if limite_prodist is not None:
        ax.axhline(limite_prodist, color='#e06666', linestyle='--', linewidth=1.5, alpha=0.8)
        ax.axhspan(limite_prodist, ylim_max, facecolor='#f4cccc', alpha=0.5)
        ax.text(0.1, limite_prodist + (ylim_max * 0.02), 'Limite Crítico (> 3%)', color='#cc0000', fontsize=10)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#cccccc')

    ax.set_xlim(0, 24)

    # Ajuste automático do eixo Y para a Tensão de Neutro caso ultrapasse 15V
    if coluna == 'V_Neutro' and df[coluna].max() > ylim_max:
        ylim_max = df[coluna].max() + 5

    ax.set_ylim(0, ylim_max)
    ax.set_xticks(range(0, 25, 2))
    ax.set_xticklabels([f"{h:02d}:00" for h in range(0, 25, 2)])

    ax.tick_params(axis='both', colors='#555555', length=0, pad=8)
    ax.grid(axis='y', color='gray', linestyle='--', linewidth=0.5, alpha=0.3)
    ax.grid(axis='x', color='gray', linestyle='-', linewidth=0.5, alpha=0.2)

    ax.set_ylabel(ylabel, fontsize=11, color='#555555')
    ax.set_xlabel('Horário do Dia (h)', fontsize=11, color='#555555')

    plt.figtext(0.08, 0.95, titulo, fontsize=14, fontweight='bold', color='#333333')
    plt.figtext(0.08, 0.89, subtitulo, fontsize=11, color='#555555')

    plt.subplots_adjust(top=0.82, bottom=0.18, left=0.08, right=0.95)
    plt.show()

# ============================================================================
# 5. EXECUÇÃO DE TODOS OS GRÁFICOS
# ============================================================================
sub_mt = "PRODIST Módulo 8 MT: Adequada 0,93–1,05 pu · Precária 0,90–0,93 pu · Crítica < 0,90 ou > 1,05 pu"
sub_bt = "PRODIST Módulo 8 BT: Adequada 0,92–1,05 pu · Precária 0,87–0,92 ou 1,05–1,06 pu · Crítica < 0,87 ou > 1,06 pu"

# Gráfico 1: Média Tensão
if not df_mt.empty:
    plotar_perfil_estilo_relatorio(df_mt, f"Média Tensão — Nós P1 a P5 (13,8 kV) {nome_do_caso}", sub_mt)

# Gráfico 2: Baixa Tensão
if not df_bt.empty:
    plotar_perfil_estilo_relatorio(df_bt, f"Baixa Tensão — Nós P6 a P10 (220/127 V e 240/120 V) {nome_do_caso}", sub_bt, is_bt=True)

# Gráficos de Neutro e Desequilíbrio
if not df_p10.empty:

    # Gráfico 3: Tensão de Neutro
    plotar_indicador(
        df=df_p10,
        coluna='V_Neutro',
        titulo=f'Deslocamento de Neutro (Seq. Zero) — Nó P10 {nome_do_caso}',
        subtitulo='Tensão de deslocamento do neutro refletindo a assimetria das fases (em Volts).',
        ylabel='Tensão do Neutro (V)',
        ylim_max=15,
        cor_linha='#003366'
    )

    # Gráfico 4: Desequilíbrio de Tensão (VUF)
    plotar_indicador(
        df=df_p10,
        coluna='FD_perc',
        titulo=f'Fator de Desequilíbrio de Tensão (VUF) — Nó P10 {nome_do_caso}',
        subtitulo='O PRODIST Módulo 8 estipula que o desequilíbrio na Baixa Tensão não deve ultrapassar 3%.',
        ylabel='Desequilíbrio de Tensão (%)',
        ylim_max=4.5,
        cor_linha='#d95f02',
        limite_prodist=3.0
    )
