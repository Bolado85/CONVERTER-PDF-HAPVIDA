"""
Gerador de PDF — Rede Credenciada Hapvida Odonto
PDF por cidade/bairro com identidade visual Hapvida
"""

import io
from datetime import datetime
from typing import List, Optional

import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate, Frame, HRFlowable, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle, KeepTogether
)

# ── Paleta Hapvida Odonto ─────────────────────
HAP_AZUL      = colors.HexColor("#002B5C")   # azul corporativo Hapvida
HAP_VERDE     = colors.HexColor("#00A859")   # verde +Odonto
HAP_AZUL_MED  = colors.HexColor("#004B87")
HAP_AZUL_CLAR = colors.HexColor("#EBF2FA")
HAP_VERDE_CL  = colors.HexColor("#E8F5E9")
CINZA_CLARO   = colors.HexColor("#F5F7FA")
CINZA_BORDA   = colors.HexColor("#E0E6ED")
CINZA_TEXTO   = colors.HexColor("#5A6A7A")
BRANCO        = colors.white
PRETO         = colors.HexColor("#1A202C")

W, H = A4


# ── Estilos ───────────────────────────────────
def _estilos():
    return {
        "capa_titulo": ParagraphStyle("capa_titulo",
            fontName="Helvetica-Bold", fontSize=24, textColor=BRANCO,
            alignment=TA_CENTER, leading=30, spaceAfter=4),
        "capa_sub": ParagraphStyle("capa_sub",
            fontName="Helvetica", fontSize=12,
            textColor=colors.HexColor("#B3D0FF"),
            alignment=TA_CENTER, leading=18),
        "capa_info": ParagraphStyle("capa_info",
            fontName="Helvetica", fontSize=10,
            textColor=colors.HexColor("#CCE0FF"),
            alignment=TA_CENTER, leading=15),
        "sumario_titulo": ParagraphStyle("sumario_titulo",
            fontName="Helvetica-Bold", fontSize=13, textColor=HAP_AZUL,
            spaceBefore=4, spaceAfter=10),
        "sumario_item": ParagraphStyle("sumario_item",
            fontName="Helvetica", fontSize=9, textColor=PRETO, leading=14),
        "sumario_bold": ParagraphStyle("sumario_bold",
            fontName="Helvetica-Bold", fontSize=9, textColor=HAP_AZUL, leading=14),
        "bairro_titulo": ParagraphStyle("bairro_titulo",
            fontName="Helvetica-Bold", fontSize=13, textColor=BRANCO,
            leading=18, leftIndent=8),
        "esp_header": ParagraphStyle("esp_header",
            fontName="Helvetica-Bold", fontSize=10, textColor=BRANCO,
            leading=14, leftIndent=6),
        "prest_nome": ParagraphStyle("prest_nome",
            fontName="Helvetica-Bold", fontSize=9, textColor=HAP_AZUL,
            leading=13, spaceAfter=1),
        "prest_det": ParagraphStyle("prest_det",
            fontName="Helvetica", fontSize=8, textColor=PRETO, leading=12),
        "prest_label": ParagraphStyle("prest_label",
            fontName="Helvetica-Bold", fontSize=7.5, textColor=CINZA_TEXTO, leading=11),
        "stat_val": ParagraphStyle("stat_val",
            fontName="Helvetica-Bold", fontSize=18, textColor=HAP_AZUL,
            alignment=TA_CENTER, leading=22),
        "stat_lbl": ParagraphStyle("stat_lbl",
            fontName="Helvetica", fontSize=7.5, textColor=CINZA_TEXTO,
            alignment=TA_CENTER, leading=11),
        "nota": ParagraphStyle("nota",
            fontName="Helvetica-Oblique", fontSize=7.5,
            textColor=CINZA_TEXTO, leading=11),
    }


# ── Documento base ────────────────────────────
class DocHapvida(BaseDocTemplate):
    def __init__(self, buf, cidade, bairro, data_geracao, **kw):
        self.cidade      = cidade
        self.bairro      = bairro
        self.data_geracao = data_geracao
        super().__init__(buf, **kw)


def _template(doc: DocHapvida):
    mar = 1.7 * cm
    h_cab = 1.5 * cm
    h_rod = 0.9 * cm

    def _draw(canvas, doc):
        canvas.saveState()

        # ── Cabeçalho ──
        cy = H - mar - h_cab + 0.3 * cm

        canvas.setFillColor(HAP_AZUL)
        canvas.roundRect(mar - 6, cy - 3, W - 2*mar + 12, h_cab + 6,
                         radius=5, stroke=0, fill=1)
        canvas.setFillColor(HAP_VERDE)
        canvas.rect(mar - 6, cy - 3, 7, h_cab + 6, stroke=0, fill=1)

        canvas.setFillColor(BRANCO)
        canvas.setFont("Helvetica-Bold", 9)
        canvas.drawString(mar + 8, cy + 12, "HAPVIDA +ODONTO")
        canvas.setFillColor(HAP_VERDE)
        canvas.setFont("Helvetica-Bold", 7)
        canvas.drawString(mar + 8, cy + 3, "● REDE CREDENCIADA")

        canvas.setFillColor(colors.HexColor("#B3D0FF"))
        canvas.setFont("Helvetica", 7.5)
        info = doc.cidade
        if doc.bairro:
            info += f"  |  {doc.bairro}"
        canvas.drawRightString(W - mar + 5, cy + 12, info)
        canvas.setFillColor(colors.HexColor("#CCE0FF"))
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(W - mar + 5, cy + 3, doc.data_geracao)

        # ── Rodapé ──
        ry = mar - h_rod
        canvas.setStrokeColor(CINZA_BORDA)
        canvas.setLineWidth(0.5)
        canvas.line(mar, ry + 11, W - mar, ry + 11)

        canvas.setFillColor(HAP_AZUL)
        canvas.setFont("Helvetica-Bold", 6.5)
        canvas.drawString(mar, ry + 2, "HAPVIDA +ODONTO  ·  Rede Credenciada  ·  Documento de Uso Interno")
        canvas.setFillColor(CINZA_TEXTO)
        canvas.setFont("Helvetica", 7)
        canvas.drawRightString(W - mar, ry + 2, f"Página {doc.page}")

        canvas.restoreState()

    frame = Frame(
        mar, mar + h_rod + 0.3*cm,
        W - 2*mar,
        H - 2*mar - h_cab - h_rod - 0.5*cm,
        id="corpo"
    )
    return [PageTemplate(id="padrao", frames=[frame], onPage=_draw)]


def _capa(cidade, uf, bairro, data_geracao, stats, estilos):
    story = [Spacer(1, 1.2*cm)]

    linhas = [
        [Paragraph("HAPVIDA +ODONTO", ParagraphStyle("logo",
            fontName="Helvetica-Bold", fontSize=11,
            textColor=HAP_VERDE, alignment=TA_CENTER))],
        [Paragraph("REDE CREDENCIADA", estilos["capa_titulo"])],
        [Paragraph(
            f"Cidade: <b>{cidade}</b>  ·  UF: <b>{uf}</b>" +
            (f"  ·  Bairro: <b>{bairro}</b>" if bairro else ""),
            estilos["capa_sub"])],
        [Spacer(1, 0.3*cm)],
        [Paragraph(f"Gerado em: {data_geracao}", estilos["capa_info"])],
    ]
    tb = Table(linhas, colWidths=[W - 4*cm])
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), HAP_AZUL),
        ("TOPPADDING",    (0,0), (-1,-1), 14),
        ("BOTTOMPADDING", (0,0), (-1,-1), 14),
        ("LEFTPADDING",   (0,0), (-1,-1), 20),
        ("RIGHTPADDING",  (0,0), (-1,-1), 20),
    ]))
    story.append(tb)
    story.append(Spacer(1, 0.8*cm))

    lc = (W - 4*cm) / 4
    kpi_data = [
        [Paragraph(str(stats["prestadores"]), estilos["stat_val"]),
         Paragraph(str(stats["bairros"]),      estilos["stat_val"]),
         Paragraph(str(stats["especialidades"]),estilos["stat_val"]),
         Paragraph(str(stats["credenciados"]), estilos["stat_val"])],
        [Paragraph("PRESTADORES",   estilos["stat_lbl"]),
         Paragraph("BAIRROS",       estilos["stat_lbl"]),
         Paragraph("ESPECIALIDADES",estilos["stat_lbl"]),
         Paragraph("CREDENCIADOS",  estilos["stat_lbl"])],
    ]
    kt = Table(kpi_data, colWidths=[lc]*4)
    kt.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,-1), CINZA_CLARO),
        ("GRID",       (0,0), (-1,-1), 0.5, CINZA_BORDA),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("ALIGN",      (0,0), (-1,-1), "CENTER"),
        ("VALIGN",     (0,0), (-1,-1), "MIDDLE"),
        ("LINEABOVE",  (0,0), (-1,0), 3, HAP_VERDE),
    ]))
    story.append(kt)
    story.append(PageBreak())
    return story


def _sumario(df, por_bairro, estilos):
    story = []
    story.append(Paragraph("SUMÁRIO", estilos["sumario_titulo"]))
    story.append(HRFlowable(width="100%", thickness=2, color=HAP_AZUL, spaceAfter=8))

    if por_bairro:
        grp = (df.groupby(["BAIRRO","ESPECIALIDADE"])
               .size().reset_index(name="q")
               .sort_values(["BAIRRO","ESPECIALIDADE"]))
        bairro_atual = None
        dados = [[ Paragraph("BAIRRO / ESPECIALIDADE", estilos["prest_label"]),
                   Paragraph("QTD", estilos["prest_label"]) ]]
        for _, r in grp.iterrows():
            if r.BAIRRO != bairro_atual:
                bairro_atual = r.BAIRRO
                dados.append([Paragraph(f"📍 {r.BAIRRO}", estilos["sumario_bold"]), Paragraph("", estilos["sumario_item"])])
            dados.append([Paragraph(f"    {r.ESPECIALIDADE}", estilos["sumario_item"]),
                          Paragraph(str(r.q), estilos["sumario_item"])])
    else:
        grp = (df.groupby("ESPECIALIDADE").size()
               .reset_index(name="q").sort_values("ESPECIALIDADE"))
        dados = [[ Paragraph("#", estilos["prest_label"]),
                   Paragraph("ESPECIALIDADE", estilos["prest_label"]),
                   Paragraph("QTD", estilos["prest_label"]) ]]
        for i, r in enumerate(grp.itertuples(), 1):
            dados.append([Paragraph(str(i), estilos["sumario_item"]),
                          Paragraph(r.ESPECIALIDADE, estilos["sumario_bold"]),
                          Paragraph(str(r.q), estilos["sumario_item"])])

    cw = [W-4*cm-2*cm, 2*cm] if por_bairro else [1*cm, W-4*cm-2.5*cm, 2.5*cm]
    tb = Table(dados, colWidths=cw)
    tb.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), HAP_AZUL),
        ("TEXTCOLOR",  (0,0), (-1,0), BRANCO),
        ("ROWBACKGROUNDS", (0,1), (-1,-1), [BRANCO, CINZA_CLARO]),
        ("GRID",       (0,0), (-1,-1), 0.3, CINZA_BORDA),
        ("TOPPADDING",    (0,0), (-1,-1), 4),
        ("BOTTOMPADDING", (0,0), (-1,-1), 4),
        ("LEFTPADDING",   (0,0), (-1,-1), 7),
        ("RIGHTPADDING",  (0,0), (-1,-1), 7),
    ]))
    story.append(tb)
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        f"Total: <b>{len(df)}</b> prestadores · <b>{df['BAIRRO'].nunique()}</b> bairros · "
        f"<b>{df['ESPECIALIDADE'].nunique()}</b> especialidades",
        estilos["nota"]))
    story.append(PageBreak())
    return story


def _header_bairro(bairro, df_b, estilos):
    story = []
    total = len(df_b)
    esps  = df_b["ESPECIALIDADE"].nunique()

    dados = [[
        Paragraph(f"  📍  {bairro}", estilos["bairro_titulo"]),
        Paragraph(f"{total} prestadores  |  {esps} especialidades",
                  ParagraphStyle("bsub", fontName="Helvetica",
                                 fontSize=8, textColor=colors.HexColor("#B3D0FF"),
                                 alignment=TA_RIGHT, leading=12)),
    ]]
    tb = Table(dados, colWidths=[W-4*cm-5*cm, 5*cm])
    tb.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HAP_AZUL_MED),
        ("TOPPADDING",    (0,0), (-1,-1), 8),
        ("BOTTOMPADDING", (0,0), (-1,-1), 8),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "MIDDLE"),
        ("LINEBELOW",     (0,0), (-1,-1), 3, HAP_VERDE),
    ]))
    story.append(tb)
    story.append(Spacer(1, 4))
    return story


def _header_esp(esp, estilos):
    dados = [[Paragraph(f"  {esp}", estilos["esp_header"])]]
    tb = Table(dados, colWidths=[W-4*cm])
    tb.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), HAP_AZUL),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 4),
    ]))
    return [tb, Spacer(1, 2)]


def _bloco_prestador(row, idx, estilos):
    bg = HAP_AZUL_CLAR if idx % 2 == 0 else BRANCO

    nome    = getattr(row, "NOME_FANTASIA",     "") or getattr(row, "NOME FANTASIA", "") or "—"
    end     = getattr(row, "ENDERECO_COMPLETO", "") or ""
    tel     = getattr(row, "TELEFONE",  "") or ""
    tel1    = getattr(row, "TELEFONE1", "") or ""
    tipo    = getattr(row, "TIPO_PRESTADOR", "") or getattr(row, "TIPO PRESTADOR", "") or ""
    cred    = getattr(row, "CREDENCIADO", "") or ""
    cnpj    = getattr(row, "CNPJ_CPF",  "") or ""
    ref     = getattr(row, "PONTO_REFERENCIA", "") or getattr(row, "PONTO REFERENCIA", "") or ""

    tels = " · ".join(t for t in [tel, tel1] if t)

    esq = [Paragraph(nome, estilos["prest_nome"])]
    if end:  esq.append(Paragraph(end, estilos["prest_det"]))
    if tels: esq.append(Paragraph(f"☎ {tels}", estilos["prest_det"]))
    if ref:  esq.append(Paragraph(f"📌 Ref: {ref}", estilos["prest_label"]))
    if cnpj: esq.append(Paragraph(f"CNPJ/CPF: {cnpj}", estilos["prest_label"]))

    cred_upper = str(cred).upper()
    cor_cred = HAP_VERDE if cred_upper in ["SIM","S","YES","1","TRUE"] else colors.HexColor("#EF4444")
    icone = "✔" if cred_upper in ["SIM","S","YES","1","TRUE"] else "✘"

    dir_ = []
    if tipo: dir_.append(Paragraph(f"Tipo: {tipo}", estilos["prest_label"]))
    if cred: dir_.append(Paragraph(
        f'<font color="#{cor_cred.hexval()[2:]}">{icone}</font> {cred}',
        estilos["prest_label"]))

    dados = [[esq, dir_]]
    tb = Table(dados, colWidths=[11.5*cm, 4*cm])
    tb.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,-1), bg),
        ("TOPPADDING",    (0,0), (-1,-1), 5),
        ("BOTTOMPADDING", (0,0), (-1,-1), 5),
        ("LEFTPADDING",   (0,0), (-1,-1), 8),
        ("RIGHTPADDING",  (0,0), (-1,-1), 8),
        ("VALIGN",        (0,0), (-1,-1), "TOP"),
        ("LINEBELOW",     (0,0), (-1,-1), 0.3, CINZA_BORDA),
    ]))
    return [tb]


def _gerar_pdf(df: pd.DataFrame, cidade: str, bairro_filtro: str = "") -> Optional[bytes]:
    estilos      = _estilos()
    data_geracao = datetime.now().strftime("%d/%m/%Y  %H:%M")
    uf = df["UF"].mode().iloc[0] if not df["UF"].mode().empty else ""

    stats = {
        "prestadores":    len(df),
        "bairros":        df["BAIRRO"].nunique(),
        "especialidades": df["ESPECIALIDADE"].nunique(),
        "credenciados":   df[df["CREDENCIADO"].astype(str).str.upper()
                             .isin(["SIM","S","YES","1","TRUE"])].shape[0],
    }

    buf = io.BytesIO()
    doc = DocHapvida(
        buf, cidade=f"{cidade}/{uf}", bairro=bairro_filtro,
        data_geracao=f"Gerado em {data_geracao}",
        pagesize=A4,
        leftMargin=1.7*cm, rightMargin=1.7*cm,
        topMargin=2.5*cm,  bottomMargin=2.0*cm,
        title=f"Rede Credenciada Hapvida Odonto — {cidade}",
        author="Hapvida Odonto"
    )
    doc.addPageTemplates(_template(doc))

    story = []
    story.extend(_capa(cidade, uf, bairro_filtro, data_geracao, stats, estilos))

    por_bairro = not bairro_filtro
    story.extend(_sumario(df, por_bairro and df["BAIRRO"].nunique() > 1, estilos))

    bairros = sorted(df["BAIRRO"].dropna().unique())
    if not bairros:
        bairros = ["SEM BAIRRO"]

    for i_b, bairro in enumerate(bairros):
        df_b = df[df["BAIRRO"] == bairro].copy() if bairro != "SEM BAIRRO" else df.copy()
        if df_b.empty:
            continue

        if i_b > 0:
            story.append(PageBreak())

        story.extend(_header_bairro(bairro, df_b, estilos))

        esps = sorted(df_b["ESPECIALIDADE"].dropna().unique())
        for esp in esps:
            df_e = df_b[df_b["ESPECIALIDADE"] == esp].sort_values("NOME FANTASIA").reset_index(drop=True)
            bloco_esp = _header_esp(esp, estilos)
            for idx, row in enumerate(df_e.itertuples()):
                bloco_esp.extend(_bloco_prestador(row, idx, estilos))
            story.append(KeepTogether(bloco_esp[:4]))
            if len(bloco_esp) > 4:
                for item in bloco_esp[4:]:
                    story.append(item)
            story.append(Spacer(1, 0.3*cm))

    story.append(Spacer(1, 0.8*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=CINZA_BORDA))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph(
        f"Documento gerado pelo Sistema Hapvida +Odonto em {data_geracao}. "
        "Informações sujeitas a alteração. Confirme dados com os prestadores.",
        estilos["nota"]))

    doc.build(story)
    return buf.getvalue()


def gerar_pdf_cidade(df: pd.DataFrame, cidade: str) -> Optional[bytes]:
    try:
        return _gerar_pdf(df, cidade)
    except Exception:
        import traceback; traceback.print_exc(); return None


def gerar_pdf_bairro(df: pd.DataFrame, cidade: str, bairro: str) -> Optional[bytes]:
    try:
        df_b = df[df["BAIRRO"] == bairro].copy()
        return _gerar_pdf(df_b, cidade, bairro_filtro=bairro)
    except Exception:
        import traceback; traceback.print_exc(); return None


def gerar_pdf_multiplas_cidades(df: pd.DataFrame, cidades: List[str]) -> Optional[bytes]:
    try:
        from pypdf import PdfWriter, PdfReader
        writer = PdfWriter()
        for cidade in sorted(cidades):
            df_c = df[df["CIDADE"] == cidade]
            if df_c.empty: continue
            pdf = _gerar_pdf(df_c, cidade)
            if pdf:
                for page in PdfReader(io.BytesIO(pdf)).pages:
                    writer.add_page(page)
        if not writer.pages: return None
        out = io.BytesIO()
        writer.write(out)
        return out.getvalue()
    except Exception:
        import traceback; traceback.print_exc(); return None