# pylascontrol/pylascontrol.py

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

MONTHS_MAP = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAIO": 5,
    "JUN": 6, "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10,
    "NOV": 11, "DEZ": 12,
}

# rótulos que vamos ignorar como "categoria"
LABELS_TO_IGNORE = {
    "RECEITA", "DESPESAS", "DOMÉSTICAS", "Cotidiano", "TRANSPORTE",
    "ENTRETENIMENTO", "SAÚDE", "FÉRIAS", "LAZER", "MENSALIDADES",
    "PESSOAIS", "OBRIGAÇÕES FINANCEIRAS", "APORTES",
    "Total", "TOTAIS", "Despesas totais", "Diferença de caixa",
    "nan",
}

def load_budget_excel(path: str, year: int = 2025) -> pd.DataFrame:
    """
    Load personal budget data from an Excel file and convert to long format.
    
    Reads a budget spreadsheet in matrix format (categories in rows and months in columns)
    and transforms it into a long-format DataFrame, with one row per income/expense record.
    
    Parameters
    ----------
    path : str
        Path to the Excel file containing the "ORÇAMENTO PESSOAL" sheet.
    year : int, optional
        Year to be assigned to records (default: 2025).
    
    Returns
    -------
    pd.DataFrame
        DataFrame with columns: ['ano', 'mes', 'tipo', 'grupo', 'categoria', 'valor'].
        - ano: record year
        - mes: month number (1-12)
        - tipo: 'receita' (income), 'despesa' (expense), or 'aporte' (contribution)
        - grupo: category group (e.g., 'TRANSPORTE', 'ENTRETENIMENTO')
        - categoria: specific category name
        - valor: monetary value of the record
    
    Examples
    --------
    >>> df = load_budget_excel("orcamento.xlsx", year=2025)
    >>> df.head()
    """
    df = pd.read_excel(path, sheet_name="ORÇAMENTO PESSOAL")

    # linha 1 (índice 0) tem os códigos de mês: JAN, FEV, ...
    header_row = 0
    # colunas de meses: da 1 até a 13 (JAN..DEZ)
    mes_cols = df.columns[1:13]
    meses_siglas = df.iloc[header_row, 1:13].to_dict()

    registros = []
    grupo_atual = None

    for _, row in df.iterrows():
        label = str(row.get("Unnamed: 0", "")).strip()

        # detecta mudança de grupo: linhas com grupo sem números ainda
        if label in {
            "RECEITA", "DOMÉSTICAS", "Cotidiano", "TRANSPORTE",
            "ENTRETENIMENTO", "SAÚDE", "FÉRIAS", "LAZER", "MENSALIDADES",
            "PESSOAIS", "OBRIGAÇÕES FINANCEIRAS", "APORTES"
        }:
            grupo_atual = label
            continue

        # ignora linhas que não representam categoria de gasto/receita
        if label in LABELS_TO_IGNORE or label == "":
            continue

        # para cada mês, cria um registro
        for col in mes_cols:
            valor = row[col]
            if pd.isna(valor) or float(valor) == 0:
                continue

            mes_sigla = meses_siglas[col]
            mes_num = MONTHS_MAP.get(mes_sigla)

            registros.append({
                "ano": year,
                "mes": mes_num,
                "tipo": (
                    "receita" if grupo_atual == "RECEITA"
                    else "aporte" if grupo_atual == "APORTES"
                    else "despesa"
                ),
                "grupo": grupo_atual,
                "categoria": label,
                "valor": float(valor),
            })

    return pd.DataFrame(registros)

def plot_chart_by_type(df, year: int = 2025, type: str = "line"):
    """
    Plot financial charts from a long-format DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame with columns: ["ano", "mes", "tipo", "valor"].
    year : int, optional
        Year to filter for the chart (default: 2025).
    type : str, optional
        Chart type (default: "line"):
            - "line"  -> line chart of Income vs Expenses
            - "bar"   -> side-by-side bar chart of Income vs Expenses
            - "saldo" -> bar chart of monthly balance (income - expense)
    """

    # filtra ano e agrega por mês + tipo
    base = (
        df[df["ano"] == year]
        .groupby(["mes", "tipo"])["valor"]
        .sum()
        .unstack(fill_value=0)
    )

    # garante colunas existentes
    if "receita" not in base.columns:
        base["receita"] = 0.0
    if "despesa" not in base.columns:
        base["despesa"] = 0.0

    # saldo (pra usar em alguns gráficos)
    base["saldo"] = base["receita"] - base["despesa"]

    # --- gráfico de linhas ---
    if type == "line":
        plt.figure(figsize=(10, 5))
        plt.plot(base.index, base["receita"], marker="o", label="Receitas")
        plt.plot(base.index, base["despesa"], marker="o", label="Despesas")

        plt.fill_between(base.index, base["receita"], alpha=0.2)
        plt.fill_between(base.index, base["despesa"], alpha=0.2)

        plt.title(f"Receitas x Despesas — {year}")
        plt.xlabel("Mês")
        plt.ylabel("Valor (R$)")
        plt.xticks(range(1, 13))
        plt.grid(linestyle="--", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        return

    # --- gráfico de barras lado a lado ---
    if type == "bar":
        x = np.arange(len(base.index))
        largura = 0.35

        plt.figure(figsize=(10, 5))
        plt.bar(x - largura/2, base["receita"], width=largura, label="Receitas")
        plt.bar(x + largura/2, base["despesa"], width=largura, label="Despesas")

        plt.title(f"Receitas x Despesas — {year}")
        plt.xlabel("Mês")
        plt.ylabel("Valor (R$)")
        plt.xticks(x, base.index)
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.legend()
        plt.tight_layout()
        plt.show()
        return

    # --- gráfico de saldo mensal ---
    if type == "saldo":
        plt.figure(figsize=(10, 5))

        cores = np.where(base["saldo"] >= 0, "green", "red")
        plt.bar(base.index, base["saldo"], color=cores)

        plt.axhline(0, color="black", linewidth=1)
        plt.title(f"Saldo Mensal (Receita - Despesa) — {year}")
        plt.xlabel("Mês")
        plt.ylabel("Saldo (R$)")
        plt.xticks(range(1, 13))
        plt.grid(axis="y", linestyle="--", alpha=0.3)
        plt.tight_layout()
        plt.show()
        return

    # se não reconheceu o tipo:
    raise ValueError(f"chart_type inválido: {type!r}. Use 'line', 'bar' ou 'saldo'.")
