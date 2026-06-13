"""
Módulo de carregamento OTIMIZADO.
Utiliza 'calamine' para leitura ultrarrápida e vetorização do Pandas.
"""

import pandas as pd
import numpy as np
import re
from typing import Tuple, List, Optional
import os

ARQUIVO_EXCEL = "Rede Credenciada RT - Junho 2026.xlsx"

COLUNAS_MAPA = {
    "UF":                     ["UF", "ESTADO", "SIGLA"],
    "CIDADE":                 ["CIDADE", "MUNICIPIO", "MUNICÍPIO"],
    "BAIRRO":                 ["BAIRRO", "BAIRRO/DIST"],
    "ENDEREÇO":               ["ENDEREÇO", "ENDERECO", "LOGRADOURO", "END"],
    "NÚMERO":                 ["NÚMERO", "NUMERO", "NUM", "NR", "N°"],
    "COMPLEMENTO":            ["COMPLEMENTO", "COMPL"],
    "PONTO REFERENCIA":       ["PONTO REFERENCIA", "PONTO DE REFERÊNCIA", "REFERENCIA"],
    "TELEFONE":               ["TELEFONE", "TEL", "FONE", "TELEFONE 1"],
    "TELEFONE1":              ["TELEFONE1", "TELEFONE 2", "TEL2", "CELULAR"],
    "NOME CLINICA VINCULADA": ["NOME CLINICA VINCULADA", "CLINICA VINCULADA", "CLÍNICA VINCULADA"],
    "ESPECIALIDADE":          ["ESPECIALIDADE", "ESP"],
    "TIPO PRESTADOR":         ["TIPO PRESTADOR", "TIPO", "CATEGORIA"],
    "CREDENCIADO":            ["CREDENCIADO", "CRED", "STATUS"],
    "NOME FANTASIA":          ["NOME FANTASIA", "FANTASIA", "NOME COMERCIAL"],
    "CNPJ_CPF":               ["CNPJ_CPF", "CNPJ/CPF", "CNPJ", "CPF", "DOCUMENTO"],
}

COLUNAS_CRITICAS = ["CIDADE", "ESPECIALIDADE", "NOME FANTASIA"]

def _limpar_nome_coluna(nome) -> str:
    if pd.isna(nome): return ""
    return re.sub(r'[\t\r\n]+', '', str(nome)).strip().upper()

def _encontrar_linha_cabecalho(caminho: str) -> int:
    try:
        # Detecta se Calamine está instalado para leitura expressa
        try:
            df_sample = pd.read_excel(caminho, nrows=30, header=None, engine="calamine")
        except Exception:
            df_sample = pd.read_excel(caminho, nrows=30, header=None, engine="openpyxl")
        
        for i, row in df_sample.iterrows():
            valores = [_limpar_nome_coluna(v) for v in row.values]
            if any(v in ["CIDADE", "UF", "ESPECIALIDADE"] for v in valores):
                return i
    except Exception:
        pass
    return 0

def _mapear_colunas(df: pd.DataFrame) -> dict:
    mapeamento = {}
    colunas_limpas = {_limpar_nome_coluna(c): c for c in df.columns}

    for col_padrao, variantes in COLUNAS_MAPA.items():
        for variante in variantes:
            variante_limpa = _limpar_nome_coluna(variante)
            if variante_limpa in colunas_limpas:
                nome_original = colunas_limpas[variante_limpa]
                mapeamento[nome_original] = col_padrao
                break
    return mapeamento

def carregar_dados(caminho: str) -> Tuple[Optional[pd.DataFrame], List[str]]:
    erros = []

    if not os.path.exists(caminho):
        return None, [f"Arquivo não encontrado: {caminho}"]

    try:
        header_row = _encontrar_linha_cabecalho(caminho)

        # Fallback de leitura automática se calamine não carregar
        try:
            df = pd.read_excel(caminho, header=header_row, dtype=str, engine="calamine")
        except Exception:
            df = pd.read_excel(caminho, header=header_row, dtype=str, engine="openpyxl")

    except Exception as e:
        return None, [f"Erro ao ler o Excel: {e}"]

    if df.empty:
        return None, ["O arquivo Excel está vazio."]

    df = df.dropna(how="all").reset_index(drop=True)

    mapeamento = _mapear_colunas(df)
    df = df.rename(columns=mapeamento)

    faltando = [c for c in COLUNAS_CRITICAS if c not in df.columns]
    if faltando:
        return None, [f"Coluna crítica não encontrada: {c}" for c in faltando]

    for col in COLUNAS_MAPA.keys():
        if col not in df.columns:
            df[col] = ""

    cols_texto = [c for c in df.columns if c in COLUNAS_MAPA.keys()]
    for col in cols_texto:
        df[col] = df[col].fillna("").astype(str)
        df[col] = df[col].str.replace(r'[\t\r\n]+', ' ', regex=True)
        df[col] = df[col].str.replace(r' {2,}', ' ', regex=True).str.strip()

    for col in ["TELEFONE", "TELEFONE1"]:
        if col in df.columns:
            s = df[col].str.replace(r'\D', '', regex=True)
            mask_11 = s.str.len() == 11
            mask_10 = s.str.len() == 10
            
            df.loc[mask_11, col] = "(" + s[mask_11].str[:2] + ") " + s[mask_11].str[2:7] + "-" + s[mask_11].str[7:]
            df.loc[mask_10, col] = "(" + s[mask_10].str[:2] + ") " + s[mask_10].str[2:6] + "-" + s[mask_10].str[6:]

    df["UF"]     = df["UF"].str.upper().str[:2]
    df["CIDADE"] = df["CIDADE"].str.upper()
    df = df[df["CIDADE"].str.len() > 0].reset_index(drop=True)

    df["ESPECIALIDADE"] = df["ESPECIALIDADE"].str.upper().replace("", "NÃO INFORMADO")
    
    mask_vazio = df["NOME FANTASIA"] == ""
    df.loc[mask_vazio, "NOME FANTASIA"] = df.loc[mask_vazio, "NOME CLINICA VINCULADA"]
    df.loc[df["NOME FANTASIA"] == "", "NOME FANTASIA"] = "NÃO INFORMADO"

    end = df["ENDEREÇO"] + np.where(df["NÚMERO"] != "", ", " + df["NÚMERO"], "")
    partes = [end, df["COMPLEMENTO"], df["BAIRRO"], df["CIDADE"] + "/" + df["UF"]]
    
    df["ENDERECO_COMPLETO"] = pd.Series([" - ".join(filter(None, x)) for x in zip(*partes)])

    return df, erros