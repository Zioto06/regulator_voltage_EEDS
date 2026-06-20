# Importa a biblioteca para conectar com o Google Drive
from google.colab import drive
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import os

# 1. Conecta ao Google Drive
drive.mount('/content/drive')

# ============================================================================
caminho_pasta = '/content/drive/MyDrive/XXXXXXXXX'
prefixo = os.path.join(caminho_pasta, "FEEDER_Mon_")
# ============================================================================

vbase_mt = 13800 / (3**0.5)
vbase_bt_urbana = 127.0
vbase_bt_rural = 120.0

mt_configs = {
    'vp1': ('P1 - Subestação', vbase_mt),
    'vp2': ('P2 - Barramento (cargas ind.)', vbase_mt),
    'vp3': ('P3 - Primário trafo 75 kVA', vbase_mt),
    'vp4': ('P4 - Fim do tronco MT', vbase_mt),
    'vp5': ('P5 - Ramal rural monofásico', vbase_mt)
}

bt_configs = {
    'vp6':  ('P6 - 120V perna B (rural)', vbase_bt_rural),
    'vp7':  ('P7 - BT (secundário trafo)', vbase_bt_urbana),
    'vp8':  ('P8 - BT', vbase_bt_urbana),
    'vp9':  ('P9 - BT (com GD)', vbase_bt_urbana),
    'vp10': ('P10 - BT (fim da rede)', vbase_bt_urbana)
}

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

    # Plota os dados (CORRIGIDO AQUI)
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

# 5. Executa os gráficos
sub_mt = "PRODIST Módulo 8 MT: Adequada 0,93–1,05 pu · Precária 0,90–0,93 pu · Crítica < 0,90 ou > 1,05 pu"
sub_bt = "PRODIST Módulo 8 BT: Adequada 0,92–1,05 pu · Precária 0,87–0,92 ou 1,05–1,06 pu · Crítica < 0,87 ou > 1,06 pu"

if not df_mt.empty:
    plotar_perfil_estilo_relatorio(df_mt, "Média Tensão — Nós P1 a P5 (13,8 kV) [SEM Regulador]", sub_mt)
if not df_bt.empty:
    plotar_perfil_estilo_relatorio(df_bt, "Baixa Tensão — Nós P6 a P10 (220/127 V e 240/120 V) [SEM Regulador]", sub_bt, is_bt=True)
