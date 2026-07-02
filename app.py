"""
app.py — Hapvida +Odonto · Rede Credenciada
Interface principal Streamlit
"""

import os
import io
import streamlit as st
import pandas as pd

# ── Importa módulos do projeto ─────────────────────────────────────────────
from carregador_de_dados import carregar_dados, ARQUIVO_EXCEL
from gerador_de_excel    import exportar_excel
from gerador_de_pdf      import (
    gerar_pdf_cidade,
    gerar_pdf_bairro,
    gerar_pdf_bairros,
    gerar_pdf_multiplas_cidades,
)

# ══════════════════════════════════════════════════════════════════════════════
# CONFIGURAÇÃO DA PÁGINA
# ══════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="Hapvida +Odonto · Rede Credenciada",
    page_icon="🦷",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Estilos visuais (paleta Hapvida) ──────────────────────────────────────
st.markdown("""
<style>
/* ── Variáveis de cor ── */
:root {
    --hap-azul:       #002B5C;
    --hap-verde:      #00A859;
    --hap-azul-med:   #004B87;
    --hap-azul-clar:  #EBF2FA;
    --cinza-claro:    #F5F7FA;
    --cinza-borda:    #E0E6ED;
    --texto:          #1A202C;
    --subtexto:       #5A6A7A;
}

/* ── Cabeçalho da sidebar ── */
section[data-testid="stSidebar"] { background: var(--hap-azul) !important; }
section[data-testid="stSidebar"] * { color: #FFFFFF !important; }
section[data-testid="stSidebar"] .stSelectbox label,
section[data-testid="stSidebar"] .stMultiSelect label { color: #B3D0FF !important; font-size: 0.78rem; }
section[data-testid="stSidebar"] .stSelectbox > div > div,
section[data-testid="stSidebar"] .stMultiSelect > div > div { background: #004B87 !important; border-color: #336699 !important; }

/* ── KPI cards ── */
.kpi-card {
    background: var(--cinza-claro);
    border-top: 4px solid var(--hap-azul);
    border-radius: 8px;
    padding: 18px 16px 12px;
    text-align: center;
    box-shadow: 0 2px 8px rgba(0,43,92,0.08);
}
.kpi-card.verde { border-top-color: var(--hap-verde); }
.kpi-val  { font-size: 2rem; font-weight: 700; color: var(--hap-azul); line-height: 1.1; }
.kpi-val.verde { color: var(--hap-verde); }
.kpi-lbl  { font-size: 0.75rem; color: var(--subtexto); margin-top: 4px; letter-spacing: .04em; text-transform: uppercase; }

/* ── Banner topo ── */
.banner {
    background: linear-gradient(135deg, #002B5C 0%, #004B87 60%, #00A859 100%);
    border-radius: 10px;
    padding: 24px 32px;
    margin-bottom: 20px;
    display: flex;
    align-items: center;
    gap: 18px;
}
.banner-title { font-size: 1.6rem; font-weight: 800; color: #FFFFFF; line-height: 1.15; }
.banner-sub   { font-size: 0.9rem;  color: #B3D0FF; margin-top: 2px; }

/* ── Tabela resultado ── */
.stDataFrame { border: 1px solid var(--cinza-borda) !important; border-radius: 8px; overflow: hidden; }

/* ── Botões de download ── */
.stDownloadButton > button {
    background: var(--hap-azul) !important;
    color: #FFF !important;
    border-radius: 6px !important;
    font-weight: 600 !important;
    border: none !important;
    padding: 8px 18px !important;
}
.stDownloadButton > button:hover { background: var(--hap-azul-med) !important; }

/* ── Expanders ── */
.streamlit-expanderHeader { background: var(--hap-azul-clar) !important; color: var(--hap-azul) !important; font-weight: 600; border-radius: 6px; }

/* ── Abas ── */
.stTabs [data-baseweb="tab-list"]  { border-bottom: 2px solid var(--hap-azul) !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] {
    color: var(--hap-azul) !important;
    border-bottom: 3px solid var(--hap-verde) !important;
    font-weight: 700;
}

/* ── Barra de progresso ── */
.stProgress > div > div { background: var(--hap-verde) !important; }

/* ── Alertas ── */
div[data-testid="stAlert"] { border-radius: 8px !important; }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# CARREGAMENTO DE DADOS (cache)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_data(show_spinner=False)
def _carregar(caminho: str):
    return carregar_dados(caminho)


def _obter_df() -> pd.DataFrame | None:
    """Retorna o DataFrame cacheado ou exibe mensagem de erro."""
    caminho = ARQUIVO_EXCEL
    if not os.path.exists(caminho):
        return None

    with st.spinner("⏳ Carregando planilha…"):
        df, erros = _carregar(caminho)

    if erros:
        for e in erros:
            st.error(e)
    return df


# ══════════════════════════════════════════════════════════════════════════════
# BANNER / CABEÇALHO
# ══════════════════════════════════════════════════════════════════════════════
def _banner(df: pd.DataFrame | None):
    total = f"{len(df):,}".replace(",", ".") if df is not None else "—"
    cidades = f"{df['CIDADE'].nunique():,}".replace(",", ".") if df is not None else "—"
    st.markdown(f"""
    <div class="banner">
        <div style="font-size:2.4rem">🦷</div>
        <div>
            <div class="banner-title">HAPVIDA +ODONTO</div>
            <div class="banner-sub">
                Rede Credenciada &nbsp;·&nbsp; {total} prestadores
                em {cidades} municípios
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# SIDEBAR — FILTROS
# ══════════════════════════════════════════════════════════════════════════════
def _sidebar_filtros(df: pd.DataFrame):
    with st.sidebar:
        st.markdown("## 🔍 Filtros")
        st.markdown("---")

        ufs_disp = sorted(df["UF"].dropna().unique())
        uf_sel = st.selectbox("Estado (UF)", ["Todos"] + ufs_disp, index=0)

        df_uf = df if uf_sel == "Todos" else df[df["UF"] == uf_sel]

        cidades_disp = sorted(df_uf["CIDADE"].dropna().unique())
        cidade_sel = st.selectbox("Cidade", ["Todas"] + cidades_disp, index=0)

        df_cid = df_uf if cidade_sel == "Todas" else df_uf[df_uf["CIDADE"] == cidade_sel]

        bairros_disp = sorted(df_cid["BAIRRO"].replace("", pd.NA).dropna().unique())
        bairro_sel = st.selectbox("Bairro", ["Todos"] + bairros_disp, index=0)

        esps_disp = sorted(df_cid["ESPECIALIDADE"].dropna().unique())
        esp_sel = st.multiselect("Especialidade(s)", esps_disp, default=[])

        st.markdown("---")
        busca = st.text_input("🔎 Buscar prestador", placeholder="Nome, CNPJ, endereço…")

    # ── Aplicar filtros ──
    df_f = df.copy()
    if uf_sel     != "Todos":  df_f = df_f[df_f["UF"]    == uf_sel]
    if cidade_sel != "Todas":  df_f = df_f[df_f["CIDADE"] == cidade_sel]
    if bairro_sel != "Todos":  df_f = df_f[df_f["BAIRRO"] == bairro_sel]
    if esp_sel:                df_f = df_f[df_f["ESPECIALIDADE"].isin(esp_sel)]
    if busca.strip():
        q = busca.strip().upper()
        mask = (
            df_f["NOME FANTASIA"].str.upper().str.contains(q, na=False) |
            df_f["CNPJ_CPF"].str.upper().str.contains(q, na=False)     |
            df_f["ENDERECO_COMPLETO"].str.upper().str.contains(q, na=False)
        )
        df_f = df_f[mask]

    return df_f, cidade_sel, bairro_sel


# ══════════════════════════════════════════════════════════════════════════════
# KPIs
# ══════════════════════════════════════════════════════════════════════════════
def _kpis(df: pd.DataFrame, df_f: pd.DataFrame):
    credenciados = df_f[df_f["CREDENCIADO"].str.upper().isin(["SIM","S","YES","1","TRUE"])].shape[0]

    cols = st.columns(5)
    kpis = [
        ("Prestadores",    len(df_f),                      "azul"),
        ("Estados",        df_f["UF"].nunique(),            "azul"),
        ("Municípios",     df_f["CIDADE"].nunique(),        "azul"),
        ("Especialidades", df_f["ESPECIALIDADE"].nunique(), "azul"),
        ("Credenciados",   credenciados,                    "verde"),
    ]
    for col, (lbl, val, cor) in zip(cols, kpis):
        with col:
            cls_card = "kpi-card" + (" verde" if cor == "verde" else "")
            cls_val  = "kpi-val"  + (" verde" if cor == "verde" else "")
            st.markdown(f"""
            <div class="{cls_card}">
                <div class="{cls_val}">{val:,}".replace(",", ".")</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>
            """.replace('",".replace(",", ".")', f":{val:,}".replace(",", ".")), unsafe_allow_html=True)


def _kpis_v2(df_f: pd.DataFrame):
    """Versão corrigida dos KPIs sem f-string dupla."""
    credenciados = df_f[df_f["CREDENCIADO"].str.upper().isin(["SIM","S","YES","1","TRUE"])].shape[0]

    kpis = [
        ("Prestadores",    len(df_f),                       ""),
        ("Estados",        df_f["UF"].nunique(),             ""),
        ("Municípios",     df_f["CIDADE"].nunique(),         ""),
        ("Especialidades", df_f["ESPECIALIDADE"].nunique(),  ""),
        ("Credenciados",   credenciados,                     " verde"),
    ]
    cols = st.columns(5)
    for col, (lbl, val, extra) in zip(cols, kpis):
        with col:
            val_fmt = f"{val:,}".replace(",", ".")
            cls_val = "kpi-val" + extra
            st.markdown(f"""
            <div class="kpi-card{extra}">
                <div class="{cls_val}">{val_fmt}</div>
                <div class="kpi-lbl">{lbl}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
# ABAS PRINCIPAIS
# ══════════════════════════════════════════════════════════════════════════════
def _aba_consulta(df_f: pd.DataFrame):
    st.subheader(f"📋 Resultados — {len(df_f):,} prestadores".replace(",", "."))

    colunas_visiveis = [c for c in [
        "UF","CIDADE","BAIRRO","ESPECIALIDADE","NOME FANTASIA",
        "ENDERECO_COMPLETO","TELEFONE","TELEFONE1","CNPJ_CPF",
        "TIPO PRESTADOR","CREDENCIADO"
    ] if c in df_f.columns]

    renomear = {"ENDERECO_COMPLETO": "ENDEREÇO COMPLETO"}
    df_show  = df_f[colunas_visiveis].rename(columns=renomear)

    st.dataframe(
        df_show,
        use_container_width=True,
        height=520,
        column_config={
            "CREDENCIADO": st.column_config.TextColumn("✔ CRED.", width="small"),
            "TELEFONE":    st.column_config.TextColumn("TELEFONE 1", width="small"),
            "TELEFONE1":   st.column_config.TextColumn("TELEFONE 2", width="small"),
        }
    )


def _aba_ranking(df_f: pd.DataFrame):
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 🏙️ Top municípios por prestadores")
        top_cid = (
            df_f.groupby(["UF","CIDADE"])
            .size().reset_index(name="Qtd")
            .sort_values("Qtd", ascending=False).head(20)
        )
        st.dataframe(top_cid, use_container_width=True, hide_index=True)

    with col2:
        st.markdown("#### 🦷 Top especialidades")
        top_esp = (
            df_f.groupby("ESPECIALIDADE")
            .size().reset_index(name="Qtd")
            .sort_values("Qtd", ascending=False).head(20)
        )
        st.dataframe(top_esp, use_container_width=True, hide_index=True)

    st.markdown("---")
    st.markdown("#### 📊 Prestadores por estado")
    por_uf = (
        df_f.groupby("UF").size().reset_index(name="Prestadores")
        .sort_values("Prestadores", ascending=False)
    )
    st.bar_chart(por_uf.set_index("UF")["Prestadores"])


def _aba_exportar(df_f: pd.DataFrame, cidade_sel: str, bairro_sel: str):
    st.subheader("📥 Exportações")

    col1, col2 = st.columns(2)

    # ── Excel ──────────────────────────────────────────────────────────────
    with col1:
        with st.expander("📊 Exportar Excel", expanded=True):
            st.caption("Gera 3 abas: Dados Completos · Por Especialidade · Por Cidade")
            cidades_sel_xls = sorted(df_f["CIDADE"].dropna().unique().tolist())

            if st.button("⬇️ Gerar Excel", use_container_width=True, key="btn_xls"):
                with st.spinner("Gerando planilha…"):
                    xls = exportar_excel(df_f, cidades_sel_xls)
                if xls:
                    st.download_button(
                        "📥 Baixar Excel",
                        data=xls,
                        file_name="rede_credenciada_hapvida.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        use_container_width=True,
                    )
                else:
                    st.error("Falha ao gerar o Excel.")

            st.download_button(
                "📄 Baixar CSV",
                data=df_f.to_csv(index=False, encoding="utf-8-sig").encode("utf-8-sig"),
                file_name="rede_credenciada_hapvida.csv",
                mime="text/csv",
                use_container_width=True,
            )

    # ── PDF ────────────────────────────────────────────────────────────────
    with col2:
        with st.expander("📄 Exportar PDF", expanded=True):
            modo_pdf = st.radio(
                "Modo de exportação PDF",
                ["Cidade selecionada", "Bairro(s) selecionado(s)", "Múltiplas cidades"],
                horizontal=True,
            )

            if modo_pdf == "Cidade selecionada":
                cidades_pdf = sorted(df_f["CIDADE"].dropna().unique().tolist())
                cidade_pdf  = st.selectbox("Cidade para o PDF", cidades_pdf, key="cidade_pdf")

                if st.button("⬇️ Gerar PDF — cidade", use_container_width=True):
                    df_c = df_f[df_f["CIDADE"] == cidade_pdf]
                    with st.spinner(f"Gerando PDF de {cidade_pdf}…"):
                        pdf = gerar_pdf_cidade(df_c, cidade_pdf)
                    if pdf:
                        st.download_button(
                            f"📥 Baixar PDF — {cidade_pdf}",
                            data=pdf,
                            file_name=f"hapvida_{cidade_pdf.replace(' ','_')}.pdf",
                            mime="application/pdf",
                            use_container_width=True,
                        )
                    else:
                        st.error("Falha ao gerar o PDF.")

            elif modo_pdf == "Bairro(s) selecionado(s)":
                cidades_pdf = sorted(df_f["CIDADE"].dropna().unique().tolist())
                cidade_pdf  = st.selectbox("Cidade", cidades_pdf, key="cid_bairro_pdf")
                bairros_disp = sorted(
                    df_f[df_f["CIDADE"] == cidade_pdf]["BAIRRO"]
                    .replace("", pd.NA).dropna().unique()
                )
                bairros_pdf = st.multiselect(
                    "Bairro(s)", bairros_disp, key="bairros_pdf",
                    placeholder="Selecione um ou mais bairros…",
                )

                if st.button("⬇️ Gerar PDF — bairro(s)", use_container_width=True):
                    if not bairros_pdf:
                        st.warning("Selecione ao menos um bairro.")
                    else:
                        df_c = df_f[
                            (df_f["CIDADE"] == cidade_pdf) &
                            (df_f["BAIRRO"].isin(bairros_pdf))
                        ]
                        rotulo = bairros_pdf[0] if len(bairros_pdf) == 1 else f"{len(bairros_pdf)} bairros"
                        with st.spinner(f"Gerando PDF de {rotulo} em {cidade_pdf}…"):
                            pdf = gerar_pdf_bairros(df_c, cidade_pdf, bairros_pdf)
                        if pdf:
                            sufixo = "_".join(bairros_pdf[:2]).replace(" ", "_")
                            if len(bairros_pdf) > 2:
                                sufixo += "_e_mais"
                            st.download_button(
                                f"📥 Baixar PDF — {rotulo}",
                                data=pdf,
                                file_name=f"hapvida_{cidade_pdf}_{sufixo}.pdf".replace(" ", "_"),
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        else:
                            st.error("Falha ao gerar o PDF.")

            else:  # Múltiplas cidades
                cidades_disp = sorted(df_f["CIDADE"].dropna().unique().tolist())
                cidades_mult = st.multiselect("Selecione as cidades", cidades_disp, key="mult_pdf")

                if st.button("⬇️ Gerar PDF combinado", use_container_width=True):
                    if not cidades_mult:
                        st.warning("Selecione ao menos uma cidade.")
                    else:
                        with st.spinner(f"Gerando PDF de {len(cidades_mult)} cidade(s)…"):
                            pdf = gerar_pdf_multiplas_cidades(df_f, cidades_mult)
                        if pdf:
                            st.download_button(
                                "📥 Baixar PDF combinado",
                                data=pdf,
                                file_name="hapvida_multiplas_cidades.pdf",
                                mime="application/pdf",
                                use_container_width=True,
                            )
                        else:
                            st.error("Falha ao gerar o PDF.")


def _aba_resumo_esp(df_f: pd.DataFrame):
    st.subheader("📊 Resumo por especialidade × cidade")

    pivot = (
        df_f.groupby(["CIDADE","ESPECIALIDADE"])
        .size().unstack(fill_value=0)
    )
    st.dataframe(pivot, use_container_width=True, height=500)


# ══════════════════════════════════════════════════════════════════════════════
# TELA INICIAL — SEM ARQUIVO
# ══════════════════════════════════════════════════════════════════════════════
def _tela_sem_arquivo():
    st.markdown("""
    <div class="banner">
        <div style="font-size:2.8rem">🦷</div>
        <div>
            <div class="banner-title">HAPVIDA +ODONTO</div>
            <div class="banner-sub">Rede Credenciada · Sistema de Consulta</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning(
        f"⚠️ Arquivo **`{ARQUIVO_EXCEL}`** não encontrado na pasta do sistema.\n\n"
        "Coloque o arquivo Excel na mesma pasta que o `app.py` e atualize a página.",
        icon="📂",
    )

    with st.expander("ℹ️ Como configurar", expanded=True):
        st.markdown(f"""
**Estrutura esperada:**
```
📁 seu_projeto/
├── app.py
├── carregador_de_dados.py
├── gerador_de_excel.py
├── gerador_de_pdf.py
├── iniciar.bat
└── {ARQUIVO_EXCEL}
```

**Passos:**
1. Coloque o arquivo `{ARQUIVO_EXCEL}` na mesma pasta que o `app.py`
2. Execute novamente o `iniciar.bat`
3. A página carregará automaticamente os dados
        """)


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════
def main():
    df = _obter_df()

    if df is None:
        _tela_sem_arquivo()
        return

    _banner(df)
    df_f, cidade_sel, bairro_sel = _sidebar_filtros(df)

    if df_f.empty:
        st.info("Nenhum prestador encontrado com os filtros selecionados.")
        return

    _kpis_v2(df_f)
    st.markdown("<br>", unsafe_allow_html=True)

    aba_cons, aba_rank, aba_esp, aba_exp = st.tabs([
        "🔍 Consulta",
        "🏆 Rankings",
        "📊 Por Especialidade",
        "📥 Exportar",
    ])

    with aba_cons:
        _aba_consulta(df_f)

    with aba_rank:
        _aba_ranking(df_f)

    with aba_esp:
        _aba_resumo_esp(df_f)

    with aba_exp:
        _aba_exportar(df_f, cidade_sel, bairro_sel)

    # ── Rodapé ──
    st.markdown("---")
    st.markdown(
        "<small style='color:#5A6A7A'>Hapvida +Odonto · Rede Credenciada · Documento de Uso Interno</small>",
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
