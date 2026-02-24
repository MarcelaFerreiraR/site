import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from datetime import datetime

# ── CONFIG ─────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Macroeconômico · Brasil",
    page_icon="📊",
    layout="wide",
)

# ── ESTILO ─────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital@0;1&family=Playfair+Display:ital,wght@0,600;1,400&display=swap');

  html, body, [class*="css"] { font-family: 'DM Mono', monospace; background: #ffffff; }

  h1, h2, h3 { font-family: 'Playfair Display', serif !important; color: #111 !important; }

  .block-container { padding: 2rem 3rem; max-width: 1200px; }

  .metric-card {
    background: #f9f9f7;
    border: 1px solid #e8e8e3;
    border-left: 3px solid #1a6b4a;
    border-radius: 6px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.5rem;
  }
  .metric-label { font-size: 0.65rem; color: #888; letter-spacing: 0.1em; text-transform: uppercase; margin-bottom: 0.2rem; }
  .metric-value { font-size: 1.6rem; font-weight: 600; color: #111; }
  .metric-sub   { font-size: 0.7rem; color: #888; margin-top: 0.2rem; }

  .indicator-note {
    background: #f0f7f4;
    border-left: 3px solid #1a6b4a;
    padding: 0.7rem 1rem;
    border-radius: 0 6px 6px 0;
    font-size: 0.75rem;
    color: #444;
    margin-bottom: 1.2rem;
  }

  .section-label {
    font-size: 0.65rem;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    color: #1a6b4a;
    margin-bottom: 0.3rem;
  }

  footer { visibility: hidden; }
  #MainMenu { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ── DADOS ──────────────────────────────────────────────────────────────────────
EMERALD = "#1a6b4a"
EMERALD_LIGHT = "#2d9e6e"
GRAY = "#aaaaaa"

SERIES = {
    "IBC-Br":     {"id": 24363, "desc": "Índice de Atividade Econômica do Banco Central — proxy mensal do PIB.", "unidade": "índice"},
    "IPCA":       {"id": 433,   "desc": "Variação mensal do IPCA, inflação oficial do Brasil medida pelo IBGE.", "unidade": "% a.m."},
    "Selic":      {"id": 4189,  "desc": "Taxa Selic efetiva diária, principal instrumento de política monetária do BCB.", "unidade": "% a.a."},
    "Desemprego": {"id": 24369, "desc": "Taxa de desocupação da PNAD Contínua, divulgada pelo IBGE.", "unidade": "%"},
    "Dívida":     {"id": 4536,  "desc": "Dívida Líquida do Setor Público como % do PIB.", "unidade": "% PIB"},
    "PIB":        {"id": 1207,  "desc": "PIB nominal a preços de mercado, em R$ milhões.", "unidade": "R$ milhões"},
    "Dólar":      {"id": 3698,  "desc": "Taxa de câmbio USD/BRL — cotação de venda (média mensal).", "unidade": "R$/USD"},
    "Balança":    {"id": 22704, "desc": "Saldo da balança comercial brasileira em US$ milhões (exportações – importações).", "unidade": "US$ mi"},
}

@st.cache_data(ttl=3600)
def sgs(series_id: int, start: str, end: str) -> pd.DataFrame:
    url = f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados"
    params = {"formato": "json", "dataInicial": start, "dataFinal": end}
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["data"]  = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    df.set_index("data", inplace=True)
    return df

@st.cache_data(ttl=3600)
def load_all(start: str, end: str) -> pd.DataFrame:
    frames = {}
    for name, meta in SERIES.items():
        try:
            df = sgs(meta["id"], start, end)
            df.columns = [name]
            frames[name] = df
        except Exception:
            pass
    if frames:
        combined = pd.concat(frames.values(), axis=1)
        return combined
    return pd.DataFrame()

def sparkline(df: pd.DataFrame, col: str, color: str = EMERALD) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df.index, y=df[col],
        mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy",
        fillcolor=f"rgba(26,107,74,0.08)",
    ))
    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        height=80,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        showlegend=False,
    )
    return fig

def line_chart(df: pd.DataFrame, col: str, title: str, unidade: str, color: str = EMERALD) -> go.Figure:
    fig = go.Figure(go.Scatter(
        x=df.index, y=df[col],
        mode="lines",
        line=dict(color=color, width=2),
        name=col,
        hovertemplate=f"%{{x|%b %Y}}<br><b>%{{y:.2f}} {unidade}</b><extra></extra>",
    ))
    fig.update_layout(
        title=dict(text=title, font=dict(size=14, color="#111"), x=0),
        paper_bgcolor="#ffffff",
        plot_bgcolor="#fafaf8",
        font=dict(family="DM Mono", size=11, color="#444"),
        xaxis=dict(gridcolor="#eeeeee", tickformat="%Y"),
        yaxis=dict(gridcolor="#eeeeee", ticksuffix=f" {unidade}"),
        margin=dict(l=10, r=10, t=40, b=10),
        height=300,
        showlegend=False,
    )
    return fig

# ── HEADER ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="section-label">Monitor · Banco Central do Brasil</div>', unsafe_allow_html=True)
st.title("Dashboard Macroeconômico · Brasil")
st.markdown("Dados obtidos via API pública do **Banco Central do Brasil (BCB/SGS)**, atualizados automaticamente.")

st.divider()

# ── FILTRO DE PERÍODO ───────────────────────────────────────────────────────────
col_f1, col_f2, _ = st.columns([1, 1, 2])
with col_f1:
    ano_ini = st.slider("Ano inicial", min_value=2000, max_value=2023, value=2010, step=1)
with col_f2:
    ano_fim = st.slider("Ano final", min_value=2001, max_value=2025, value=2025, step=1)

if ano_ini >= ano_fim:
    st.warning("O ano inicial deve ser menor que o ano final.")
    st.stop()

start = f"01/01/{ano_ini}"
end   = f"31/12/{ano_fim}"

with st.spinner("Buscando dados do Banco Central..."):
    df = load_all(start, end)

if df.empty:
    st.error("Não foi possível carregar os dados. Verifique sua conexão.")
    st.stop()

# ── MÉTRICAS (ÚLTIMO VALOR) ─────────────────────────────────────────────────────
st.markdown("### Últimos valores disponíveis")

cols = st.columns(4)
highlights = [
    ("IBC-Br",     "Atividade Econômica",  "índice"),
    ("IPCA",       "Inflação Mensal",       "% a.m."),
    ("Selic",      "Taxa Selic",            "% a.a."),
    ("Desemprego", "Taxa de Desemprego",    "%"),
]
for i, (col_name, label, unit) in enumerate(highlights):
    if col_name in df.columns:
        series = df[col_name].dropna()
        last_val  = series.iloc[-1]
        last_date = series.index[-1].strftime("%b/%Y")
        with cols[i]:
            st.markdown(f"""
            <div class="metric-card">
              <div class="metric-label">{label}</div>
              <div class="metric-value">{last_val:.2f}</div>
              <div class="metric-sub">{unit} · {last_date}</div>
            </div>
            """, unsafe_allow_html=True)
            st.plotly_chart(sparkline(series.to_frame(), col_name), use_container_width=True, config={"displayModeBar": False})

st.divider()

# ── CICLO ECONÔMICO ─────────────────────────────────────────────────────────────
st.markdown("### Ciclo Econômico")
st.markdown('<div class="indicator-note">Crescimento da atividade econômica (IBC-Br, variação % anual) versus inflação acumulada em 12 meses — dois termômetros centrais do ciclo macroeconômico brasileiro.</div>', unsafe_allow_html=True)

df_ciclo = df.copy()
if "IBC-Br" in df_ciclo.columns:
    df_ciclo["IBC_YoY"] = df_ciclo["IBC-Br"].pct_change(12) * 100
if "IPCA" in df_ciclo.columns:
    df_ciclo["IPCA_12m"] = df_ciclo["IPCA"].rolling(12).sum()

c1, c2 = st.columns(2)
with c1:
    if "IBC_YoY" in df_ciclo.columns:
        s = df_ciclo["IBC_YoY"].dropna()
        fig = go.Figure(go.Scatter(x=s.index, y=s, mode="lines", line=dict(color=EMERALD, width=2),
                                   fill="tozeroy", fillcolor="rgba(26,107,74,0.08)",
                                   hovertemplate="%{x|%b %Y}<br><b>%{y:.2f}%</b><extra></extra>"))
        fig.add_hline(y=0, line_dash="dash", line_color=GRAY, line_width=1)
        fig.update_layout(title="Crescimento IBC-Br (% YoY)", paper_bgcolor="#fff", plot_bgcolor="#fafaf8",
                          font=dict(family="DM Mono", size=11), xaxis=dict(gridcolor="#eee", tickformat="%Y"),
                          yaxis=dict(gridcolor="#eee", ticksuffix=" %"), margin=dict(l=10,r=10,t=40,b=10), height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

with c2:
    if "IPCA_12m" in df_ciclo.columns:
        s = df_ciclo["IPCA_12m"].dropna()
        fig = go.Figure(go.Scatter(x=s.index, y=s, mode="lines", line=dict(color="#c0392b", width=2),
                                   hovertemplate="%{x|%b %Y}<br><b>%{y:.2f}%</b><extra></extra>"))
        fig.add_hline(y=3.0, line_dash="dot", line_color=EMERALD, line_width=1, annotation_text="Meta 3%")
        fig.update_layout(title="IPCA Acumulado 12 meses (%)", paper_bgcolor="#fff", plot_bgcolor="#fafaf8",
                          font=dict(family="DM Mono", size=11), xaxis=dict(gridcolor="#eee", tickformat="%Y"),
                          yaxis=dict(gridcolor="#eee", ticksuffix=" %"), margin=dict(l=10,r=10,t=40,b=10), height=300, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── INDICADORES COMPLETOS ───────────────────────────────────────────────────────
st.markdown("### Todos os Indicadores")

tab_labels = ["Atividade & PIB", "Inflação & Juros", "Mercado de Trabalho", "Fiscal & Externo"]
tabs = st.tabs(tab_labels)

with tabs[0]:
    st.markdown('<div class="indicator-note">O <b>IBC-Br</b> é o principal proxy mensal do crescimento econômico no Brasil, calculado pelo BCB com base em setores como indústria, serviços e agropecuária. O <b>PIB nominal</b> mede o valor total da produção a preços de mercado.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if "IBC-Br" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["IBC-Br"]), "IBC-Br", "IBC-Br — Atividade Econômica", "índice"), use_container_width=True)
    with c2:
        if "PIB" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["PIB"]), "PIB", "PIB Nominal (R$ milhões)", "R$ mi"), use_container_width=True)

with tabs[1]:
    st.markdown('<div class="indicator-note">O <b>IPCA</b> é a inflação oficial do Brasil. A <b>Selic</b> é a taxa básica de juros usada pelo BCB para controlar a inflação — quando a inflação sobe, o BCB tende a elevar a Selic para desaquecer a demanda.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if "IPCA" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["IPCA"]), "IPCA", "IPCA — Inflação Mensal (%)", "% a.m.", color="#c0392b"), use_container_width=True)
    with c2:
        if "Selic" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["Selic"]), "Selic", "Taxa Selic (% a.a.)", "% a.a."), use_container_width=True)

with tabs[2]:
    st.markdown('<div class="indicator-note">A <b>taxa de desemprego</b> da PNAD Contínua mede a proporção de pessoas desocupadas na força de trabalho. É um indicador defasado do ciclo econômico — costuma subir após recessões e cair com algum atraso nas recuperações.</div>', unsafe_allow_html=True)
    if "Desemprego" in df.columns:
        st.plotly_chart(line_chart(df.dropna(subset=["Desemprego"]), "Desemprego", "Taxa de Desemprego — PNAD (%)", "%"), use_container_width=True)

with tabs[3]:
    st.markdown('<div class="indicator-note">A <b>Dívida Líquida</b> do Setor Público como % do PIB mede o endividamento do governo descontando os ativos financeiros. O <b>saldo da Balança Comercial</b> mostra o resultado entre exportações e importações — superávit quando positivo.</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if "Dívida" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["Dívida"]), "Dívida", "Dívida Líquida Setor Público (% PIB)", "% PIB"), use_container_width=True)
    with c2:
        if "Balança" in df.columns:
            st.plotly_chart(line_chart(df.dropna(subset=["Balança"]), "Balança", "Balança Comercial (US$ milhões)", "US$ mi"), use_container_width=True)
    if "Dólar" in df.columns:
        st.plotly_chart(line_chart(df.dropna(subset=["Dólar"]), "Dólar", "Câmbio USD/BRL", "R$/USD"), use_container_width=True)

st.divider()

# ── TABELA ──────────────────────────────────────────────────────────────────────
with st.expander("📋 Ver tabela com últimos 24 meses"):
    df_show = df.tail(24).copy()
    df_show.index = df_show.index.strftime("%b/%Y")
    df_show = df_show.round(2)
    st.dataframe(df_show, use_container_width=True)

# ── RODAPÉ ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="margin-top:3rem; font-size:0.68rem; color:#aaa; border-top:1px solid #eee; padding-top:1rem;">
  Dados: API pública do Banco Central do Brasil (BCB/SGS) · Atualizado automaticamente a cada acesso ·
  Desenvolvido por <strong>Marcela Rocha</strong>
</div>
""", unsafe_allow_html=True)