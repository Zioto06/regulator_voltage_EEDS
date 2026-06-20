# Estudo de Caso: Regulador de Tensão em Sistemas de Distribuição

Este repositório contém todo o material, scripts e resultados obtidos durante a execução da **Situação Problema 2 (PBL2)** da disciplina de **Distribuição de Energia Elétrica (2026/1)** do curso de Engenharia Elétrica do IFES - Campus Guarapari.

O objetivo central do projeto foi analisar o impacto de dispositivos de regulação de tensão em um sistema de distribuição hipotético, avaliando diferentes topologias, estratégias de controle (**LDC – Line Drop Compensation**) e condições de operação, considerando tensão nominal e tensão incrementada.

---

## Diagrama do Sistema

Abaixo é apresentado o esquema do sistema de distribuição hipotético utilizado nas simulações.

![Diagrama do Sistema](circuito_dee.png)

---

## Estrutura do Repositório

A organização dos arquivos do projeto segue a estrutura abaixo:

```text
.
├── Objetivo_1/
├── Objetivo_2/
│   ├── Caso_1/
│   └── Caso_2/
├── Objetivo_3/
│   ├── Caso_1/
│   └── Caso_2/
├── Objetivo_4/
│   ├── Objetivo_1/
│   ├── Objetivo_2/
│   └── Objetivo_3/
├── DEE - PBL2 - 2026-1.pdf
└── Circuito REV1.pdf
```

Dentro de cada pasta ou subpasta de caso, encontram-se:

* **Imagens/**: gráficos e perfis de tensão resultantes;
* **Arquivos `.csv`**: saídas brutas das simulações do OpenDSS;
* **Arquivos `.dss`**: modelagem do sistema e definições de carga;
* **Scripts `.py`**: processamento dos dados e geração dos gráficos.

---

## Requisitos e Execução

### Ferramentas Utilizadas

* **OpenDSS** para realização dos fluxos de potência;
* **Python 3.x** para automação, leitura dos arquivos `.csv` e geração dos gráficos.

### Configuração no Google Colab

Os scripts em Python foram desenvolvidos considerando a estrutura de diretórios do Google Drive. Para executá-los no Google Colab:

1. **Faça o upload** da estrutura do repositório para o Google Drive;
2. **Monte o Drive** no início dos scripts:

```python
from google.colab import drive
drive.mount('/content/drive')
```

3. **Configure os caminhos (paths)** presentes nos arquivos `.py`, informando o diretório correspondente no seu Drive, por exemplo:

```text
/content/drive/MyDrive/Pasta_Do_Projeto/
```

---

## Contexto do Projeto

O sistema em estudo representa um alimentador de **13,8 kV** utilizado para avaliar o comportamento de reguladores de tensão em cenários de carga industrial.

As análises foram conduzidas com foco na conformidade com o **PRODIST – Módulo 8 da ANEEL**, buscando manter os níveis de tensão dentro dos limites normativos e mitigar problemas relacionados ao desequilíbrio de fase e ao deslocamento de neutro.

---

## Finalidade

Projeto desenvolvido para fins acadêmicos na disciplina **Distribuição de Energia Elétrica (2026/1)** do curso de **Engenharia Elétrica do IFES – Campus Guarapari**.
