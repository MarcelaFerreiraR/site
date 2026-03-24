import streamlit as st
import pandas as pd
import requests
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard Macroeconômico · Brasil", page_icon="📊", layout="wide")

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=DM+Mono:ital@0;1&family=Playfair+Display:wght@600&display=swap');

  html, body, [class*="css"] { font-family: 'DM Mono', monospace !important; background:#f5f5f0 !important; }
  .block-container { padding: 2.5rem 3rem !important; max-width: 1200px; }
  footer, #MainMenu, header { visibility: hidden; }

  /* ── HEADER ── */
  .dash-header { margin-bottom: 2rem; }
  .dash-tag { font-size:0.75rem; letter-spacing:0.18em; text-transform:uppercase; color:#1a6b4a; margin-bottom:0.3rem; }
  .dash-title { font-family:'Playfair Display',serif; font-size:2.2rem; color:#111; margin:0; }
  .dash-sub { font-size:0.88rem; color:#999; margin-top:0.2rem; }

  /* ── CARDS (idênticos ao site) ── */
  .macro-grid { display:grid; grid-template-columns:repeat(3,1fr); gap:1px; background:#e0e0d8; border:1px solid #e0e0d8; border-radius:4px; overflow:hidden; margin-bottom:2rem; }
  .macro-card { background:#fff; padding:1.5rem 1.8rem; }
  .macro-indicator { font-size:0.88rem; letter-spacing:0.14em; text-transform:uppercase; color:#999; margin-bottom:0.8rem; }
  .macro-value { font-size:2.4rem; font-weight:600; color:#111; letter-spacing:-0.02em; line-height:1; }
  .macro-unit { font-size:0.85rem; color:#888; margin-left:0.3rem; font-weight:400; }
  .macro-change { font-size:0.82rem; margin-top:0.5rem; }
  .macro-change.up   { color:#1a6b4a; }
  .macro-change.down { color:#c0392b; }
  .macro-change.neutral { color:#999; }
  .macro-period { font-size:0.75rem; color:#bbb; margin-top:0.2rem; }

  /* ── SEÇÃO ── */
  .section-tag { font-size:0.75rem; letter-spacing:0.18em; text-transform:uppercase; color:#1a6b4a; margin-bottom:0.2rem; margin-top:2rem; }
  .section-title { font-family:'Playfair Display',serif; font-size:1.6rem; color:#111; margin:0 0 0.5rem 0; }
  .section-note { font-size:0.88rem; color:#666; border-left:2px solid #1a6b4a; padding-left:0.8rem; margin:0.5rem 0 1.2rem 0; line-height:1.7; }

  hr { border:none; border-top:1px solid #e8e8e3; margin:1.5rem 0; }

  /* ── TABS ── */
  .stTabs [data-baseweb="tab-list"] { gap:0; border-bottom:1px solid #e8e8e3; background:transparent; }
  .stTabs [data-baseweb="tab"] { font-size:0.82rem !important; letter-spacing:0.1em; text-transform:uppercase; padding:0.6rem 1.4rem; color:#888 !important; background:transparent !important; }
  .stTabs [aria-selected="true"] { color:#1a6b4a !important; border-bottom:2px solid #1a6b4a !important; background:transparent !important; }
</style>
""", unsafe_allow_html=True)

EMERALD = "#1a6b4a"
RED = "#c0392b"
GRAY = "#cccccc"

SERIES = {
    "IBC-Br":     {"id": 24363, "unidade": "índice",  "label": "IBC-Br — Atividade Econômica",  "desc": "Proxy mensal do PIB calculado pelo Banco Central. Reflete a evolução da atividade econômica com base em indústria, serviços e agropecuária. É o termômetro mais rápido do crescimento brasileiro."},
    "IPCA":       {"id": 433,   "unidade": "% a.m.",  "label": "IPCA — Inflação Mensal",         "desc": "Inflação oficial do Brasil, medida pelo IBGE. Variação mensal do custo de vida. Quando acumulada em 12 meses, é o principal indicador usado pelo BCB para calibrar a política monetária."},
    "Selic":      {"id": 432,  "unidade": "% a.a.",  "label": "Taxa Selic",                     "desc": "Taxa básica de juros da economia brasileira. Principal instrumento do Banco Central para controlar a inflação — quando a inflação acelera, o BCB eleva a Selic para desaquecer a demanda."},
    "Desemprego": {"id": 24369, "unidade": "%",        "label": "Desemprego — PNAD",              "desc": "Taxa de desocupação da PNAD Contínua (IBGE). Indicador defasado do ciclo econômico — costuma subir após recessões e cair com algum atraso nas recuperações."},
    "Dívida":     {"id": 4536,  "unidade": "% PIB",   "label": "Dívida Líquida do Setor Público","desc": "Dívida líquida do governo como % do PIB. Mede o endividamento público descontando os ativos financeiros. Indicador central da sustentabilidade fiscal brasileira."},
    "PIB":        {"id": 1207,  "unidade": "R$ mi",   "label": "PIB Nominal",                    "desc": "PIB a preços de mercado, em R$ milhões. Mede o valor total da produção da economia brasileira em determinado período."},
    "Dólar":      {"id": 3698,  "unidade": "R$/USD",  "label": "Câmbio USD/BRL",                 "desc": "Taxa de câmbio entre o dólar americano e o real brasileiro, cotação média mensal de venda. Reflete percepções de risco, fluxo de capitais e política monetária."},
    "Balança":    {"id": 22704, "unidade": "US$ mi",  "label": "Balança Comercial",              "desc": "Resultado entre exportações e importações em US$ milhões. Superávit quando positivo — indica que o Brasil exporta mais do que importa."},
}

@st.cache_data(ttl=3600)
def sgs(series_id, start, end):
    r = requests.get(f"https://api.bcb.gov.br/dados/serie/bcdata.sgs.{series_id}/dados",
                     params={"formato":"json","dataInicial":start,"dataFinal":end}, timeout=15)
    r.raise_for_status()
    df = pd.DataFrame(r.json())
    df["data"]  = pd.to_datetime(df["data"], dayfirst=True)
    df["valor"] = pd.to_numeric(df["valor"], errors="coerce")
    return df.set_index("data")["valor"]

@st.cache_data(ttl=3600)
def load_all(start, end):
    frames = {}
    for name, meta in SERIES.items():
        try: frames[name] = sgs(meta["id"], start, end)
        except: pass
    return pd.DataFrame(frames) if frames else pd.DataFrame()

def fmt_change(val, prev, unit):
    if pd.isna(prev): return '<span class="macro-change neutral">—</span>'
    diff = val - prev
    arrow = "▲" if diff >= 0 else "▼"
    cls   = "up" if diff >= 0 else "down"
    return f'<span class="macro-change {cls}">{arrow} {abs(diff):.2f} {unit} vs anterior</span>'

def line_chart(series, unidade, color=EMERALD, hline=None):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=series.index, y=series.values, mode="lines",
        line=dict(color=color, width=2),
        fill="tozeroy", fillcolor=f"rgba(26,107,74,0.07)" if color==EMERALD else "rgba(192,57,43,0.07)",
        hovertemplate="%{x|%b %Y}<br><b>%{y:.2f} " + unidade + "</b><extra></extra>",
    ))
    if hline is not None:
        fig.add_hline(y=hline, line_dash="dot", line_color="#aaa", line_width=1,
                      annotation_text=f"  {hline}%", annotation_font_size=10, annotation_font_color="#aaa")
    fig.add_hline(y=0, line_color="#ebebeb", line_width=1)
    fig.update_layout(
        paper_bgcolor="#fff", plot_bgcolor="#fff",
        font=dict(family="DM Mono", size=11, color="#666"),
        xaxis=dict(showgrid=False, tickformat="%Y", linecolor="#eee", tickfont=dict(size=10), tickcolor="#ddd"),
        yaxis=dict(showgrid=True, gridcolor="#f2f2f2", ticksuffix=f" {unidade}", tickfont=dict(size=10), zeroline=False),
        margin=dict(l=0, r=10, t=20, b=0), height=260,
        showlegend=False, hovermode="x unified",
    )
    return fig

# ── HEADER
st.markdown("""
<div class="dash-header">
  <div class="dash-tag">Monitor · Banco Central do Brasil</div>
  <div class="dash-title">Dashboard Macroeconômico</div>
  <div class="dash-sub">Brasil · API pública BCB/SGS · Atualizado automaticamente</div>
</div>
""", unsafe_allow_html=True)

# ── FILTRO
col1, col2, _ = st.columns([1,1,2])
with col1: ano_ini = st.slider("De", 2000, 2023, 2010)
with col2: ano_fim = st.slider("Até", 2001, 2026, 2026)

if ano_ini >= ano_fim:
    st.warning("Ano inicial deve ser menor que o ano final.")
    st.stop()

with st.spinner("Buscando dados do Banco Central..."):
    df = load_all(f"01/01/{ano_ini}", f"31/12/{ano_fim}")

if df.empty:
    st.error("Não foi possível carregar os dados.")
    st.stop()

st.markdown("<hr>", unsafe_allow_html=True)

# ── CARDS (estilo site)
cards_config = [
    ("IBC-Br",     "IBC-Br — Atividade Econômica",  "índice"),
    ("IPCA",       "IPCA — Acumulado 12m",           "%"),
    ("Selic",      "Taxa Selic — Meta",              "% a.a."),
    ("Dólar",      "Câmbio USD/BRL",                 "R$"),
    ("Desemprego", "Desemprego — PNAD",              "%"),
    ("Dívida",     "Dívida Líquida",                 "% PIB"),
]

cards_html = '<div class="macro-grid">'
for nome, label, unit in cards_config:
    if nome in df.columns:
        s    = df[nome].dropna()
        val  = s.iloc[-1]
        prev = s.iloc[-2] if len(s) > 1 else float("nan")
        date = s.index[-1].strftime("%b/%Y")

        # IPCA acumulado 12m
        display_val = val
        if nome == "IPCA" and len(s) >= 12:
            display_val = s.rolling(12).sum().iloc[-1]

        change_html = fmt_change(val, prev, unit)

        cards_html += f"""
        <div class="macro-card">
          <div class="macro-indicator">{label}</div>
          <div class="macro-value">{display_val:.2f}<span class="macro-unit">{unit}</span></div>
          {change_html}
          <div class="macro-period">Ref: {date}</div>
        </div>"""

cards_html += "</div>"
st.markdown(cards_html, unsafe_allow_html=True)

st.markdown('<div style="font-size:0.8rem;color:#aaa;margin-top:-1.5rem;margin-bottom:2rem;">Dados obtidos via API pública do Banco Central do Brasil (BCB/SGS). Atualizados automaticamente a cada acesso.</div>', unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)

# ── CICLO ECONÔMICO
st.markdown('<div class="section-tag">Ciclo Econômico</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">IBC-Br × Inflação</div>', unsafe_allow_html=True)
st.markdown('<div class="section-note">Crescimento da atividade econômica (IBC-Br, variação % anual) versus inflação acumulada em 12 meses — os dois termômetros centrais do ciclo macroeconômico brasileiro.</div>', unsafe_allow_html=True)

df_ciclo = df.copy()
if "IBC-Br" in df_ciclo: df_ciclo["IBC_YoY"] = df_ciclo["IBC-Br"].pct_change(12) * 100
if "IPCA"   in df_ciclo: df_ciclo["IPCA_12m"] = df_ciclo["IPCA"].rolling(12).sum()

c1, c2 = st.columns(2, gap="large")
with c1:
    st.markdown('<p style="font-size:0.8rem;color:#999;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.2rem">Crescimento IBC-Br (% YoY)</p>', unsafe_allow_html=True)
    if "IBC_YoY" in df_ciclo:
        st.plotly_chart(line_chart(df_ciclo["IBC_YoY"].dropna(), "%", EMERALD, hline=0), use_container_width=True, config={"displayModeBar":False})
with c2:
    st.markdown('<p style="font-size:0.8rem;color:#999;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.2rem">IPCA Acumulado 12 meses (%)</p>', unsafe_allow_html=True)
    if "IPCA_12m" in df_ciclo:
        st.plotly_chart(line_chart(df_ciclo["IPCA_12m"].dropna(), "%", RED, hline=3.0), use_container_width=True, config={"displayModeBar":False})

st.markdown("<hr>", unsafe_allow_html=True)

# ── ABAS DE INDICADORES
st.markdown('<div class="section-tag">Todos os Indicadores</div>', unsafe_allow_html=True)
st.markdown('<div class="section-title">Painel Completo</div>', unsafe_allow_html=True)

tabs = st.tabs(["Atividade & PIB", "Inflação & Juros", "Trabalho", "Fiscal", "Câmbio & Comércio"])

def mini_label(txt):
    st.markdown(f'<p style="font-size:0.8rem;color:#999;text-transform:uppercase;letter-spacing:0.12em;margin-bottom:0.1rem">{txt}</p>', unsafe_allow_html=True)

with tabs[0]:
    st.markdown(f'<div class="section-note">{SERIES["IBC-Br"]["desc"]}<br><br>{SERIES["PIB"]["desc"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_label("IBC-Br — Índice de Atividade")
        if "IBC-Br" in df: st.plotly_chart(line_chart(df["IBC-Br"].dropna(), "índice"), use_container_width=True, config={"displayModeBar":False})
    with c2:
        mini_label("PIB Nominal (R$ milhões)")
        if "PIB" in df: st.plotly_chart(line_chart(df["PIB"].dropna(), "R$ mi"), use_container_width=True, config={"displayModeBar":False})

with tabs[1]:
    st.markdown(f'<div class="section-note">{SERIES["IPCA"]["desc"]}<br><br>{SERIES["Selic"]["desc"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_label("IPCA — Variação Mensal (%)")
        if "IPCA" in df: st.plotly_chart(line_chart(df["IPCA"].dropna(), "% a.m.", RED), use_container_width=True, config={"displayModeBar":False})
    with c2:
        mini_label("Taxa Selic (% a.a.)")
        if "Selic" in df: st.plotly_chart(line_chart(df["Selic"].dropna(), "% a.a."), use_container_width=True, config={"displayModeBar":False})

with tabs[2]:
    st.markdown(f'<div class="section-note">{SERIES["Desemprego"]["desc"]}</div>', unsafe_allow_html=True)
    mini_label("Taxa de Desemprego — PNAD (%)")
    if "Desemprego" in df: st.plotly_chart(line_chart(df["Desemprego"].dropna(), "%"), use_container_width=True, config={"displayModeBar":False})

with tabs[3]:
    st.markdown(f'<div class="section-note">{SERIES["Dívida"]["desc"]}</div>', unsafe_allow_html=True)
    mini_label("Dívida Líquida do Setor Público (% PIB)")
    if "Dívida" in df: st.plotly_chart(line_chart(df["Dívida"].dropna(), "% PIB"), use_container_width=True, config={"displayModeBar":False})

with tabs[4]:
    st.markdown(f'<div class="section-note">{SERIES["Dólar"]["desc"]}<br><br>{SERIES["Balança"]["desc"]}</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        mini_label("Câmbio USD/BRL")
        if "Dólar" in df: st.plotly_chart(line_chart(df["Dólar"].dropna(), "R$/USD"), use_container_width=True, config={"displayModeBar":False})
    with c2:
        mini_label("Balança Comercial (US$ milhões)")
        if "Balança" in df: st.plotly_chart(line_chart(df["Balança"].dropna(), "US$ mi"), use_container_width=True, config={"displayModeBar":False})

st.markdown("<hr>", unsafe_allow_html=True)

with st.expander("📋 Ver tabela — últimos 24 meses"):
    df_show = df.tail(24).copy().round(2)
    df_show.index = df_show.index.strftime("%b/%Y")
    st.dataframe(df_show, use_container_width=True)

st.markdown('<div style="margin-top:2rem;font-size:0.8rem;color:#bbb;text-align:center;">Dados: API pública do Banco Central do Brasil (BCB/SGS) &nbsp;·&nbsp; Desenvolvido por <strong style="color:#1a6b4a">Marcela Rocha</strong></div>', unsafe_allow_html=True)
