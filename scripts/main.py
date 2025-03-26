import os
import pandas as pd
from pathlib import Path

# --- Configuração de caminhos ABSOLUTOS --- #
# Caminho base do projeto (ajuste conforme sua estrutura)
CAMINHO_BASE = Path("/Users/cassioaragao/analise-vendas/analise-vendas")

# Pastas de dados e saída
PASTA_DADOS = CAMINHO_BASE / "dados"
PASTA_OUTPUT = CAMINHO_BASE / "outputs"

# Garante que as pastas existam
PASTA_DADOS.mkdir(parents=True, exist_ok=True)
PASTA_OUTPUT.mkdir(parents=True, exist_ok=True)

# Nome do arquivo de saída (com data)
ARQUIVO_SAIDA = PASTA_OUTPUT / f"relatorio_{pd.Timestamp('today').strftime('%Y%m%d')}.xlsx"


def carregar_dados():
    """Carrega o último CSV da pasta dados/"""
    arquivos = list(PASTA_DADOS.glob("*.csv"))
    
    if not arquivos:
        raise FileNotFoundError(f"Nenhum CSV encontrado em {PASTA_DADOS}")
    
    ultimo_arquivo = max(arquivos, key=lambda x: x.stat().st_mtime)
    print(f"📂 Arquivo selecionado: {ultimo_arquivo.name}")

    # Primeiro: ler tudo como string
    df = pd.read_csv(
        ultimo_arquivo,
        decimal=",",
        thousands=".",
        encoding='utf-8',  # Encoding corrigido
        dtype=str
    )

    # Função para limpar valores numéricos
    def clean_number(x):
        if pd.isna(x) or x.strip() == '':
            return 0.0
        x = x.replace('"', '').replace("'", "").replace("%", "").replace(".", "").replace(",", ".")
        try:
            return float(x)
        except:
            return 0.0

    # Versão robusta que encontra colunas automaticamente
    numeric_cols = [col for col in df.columns if any(x in col for x in ['Fat.', 'Valor'])]
    percent_cols = [col for col in df.columns if '%' in col]

    print("\n🔍 DEBUG - Colunas detectadas:")
    print("Numéricas:", numeric_cols)
    print("Percentuais:", percent_cols)
    print("\n")

    # Aplicar conversões
    for col in numeric_cols:
        df[col] = df[col].apply(clean_number)
    
    for col in percent_cols:
        df[col] = df[col].apply(clean_number) / 100

    return df


if __name__ == "__main__":
    print("🔍 Iniciando análise...")
    try:
        dados = carregar_dados()
        dados.to_excel(ARQUIVO_SAIDA, index=False)
        print(f"✅ Relatório salvo em: {ARQUIVO_SAIDA}")
    except Exception as e:
        print(f"❌ Erro: {e}")