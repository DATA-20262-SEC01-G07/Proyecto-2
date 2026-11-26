"""
Dashboard · Exposición a la IA generativa y mercado laboral de EE. UU. (2021-2026)

Ejecutar:   streamlit run dashboard.py
Librerías:  streamlit, plotly, pandas, numpy  (nada más)

Entrada: el CSV final del proyecto (el que resulta de unir CPS + BLS OEWS +
Eloundou et al. por SOC), con los nombres de columnas originales.
"""
from __future__ import annotations

import io
import math
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


# ════════════════════════════════════════════════════════════════════════════
# 0. CONFIGURACIÓN Y PALETA
# ════════════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="IA y empleo en EE. UU.",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)

C_ORANGE, C_RED, C_WINE, C_DARK = "#F05941", "#BE3144", "#872341", "#22092C"
C_TEAL, C_SLATE, C_LILAC, C_BG = "#2A9D8F", "#9AA5B1", "#B8A9BE", "#FBF7F8"

EXPO_ORDER = ["Baja", "Media", "Alta"]
EXPO_COLORS = {"Baja": C_SLATE, "Media": C_ORANGE, "Alta": C_WINE}

TRAY_ORDER = ["Subió", "Estable", "Bajó"]
TRAY_COLORS = {"Subió": C_RED, "Estable": C_LILAC, "Bajó": C_TEAL}

EDU_ORDER = [
    "Sin bachillerato", "Bachillerato", "Algo de universidad",
    "Técnico / asociado", "Pregrado", "Posgrado",
]
EDU_COLORS = dict(zip(EDU_ORDER, ["#F7D9D0", "#F5A692", C_ORANGE, C_RED, C_WINE, C_DARK]))
UNIV = ["Pregrado", "Posgrado"]
# ── Tema claro / oscuro ─────────────────────────────────────────────────────
try:
    DARK = st.context.theme.type == "dark"
except Exception:  # versiones de Streamlit sin st.context.theme
    DARK = False
INK = "#F4E9EE" if DARK else C_DARK
SURF = "#2B1633" if DARK else "#FFFFFF"
BORDER = "#4A2D55" if DARK else "#EFE2E7"
MUTED = "#BBA6C2" if DARK else "#7a6a80"
GRID = "#3A2444" if DARK else "#EFE6EA"
ACCENT = "#FF9B86" if DARK else "#872341"
TIP_BG = "#3A1F2B" if DARK else "#FFF1EC"
TIP_TX = "#F6D5CC" if DARK else "#5b2a34"
INS_TX = "#E8D9EE" if DARK else "#3a2a40"
BG_RULE = "" if DARK else ".stApp {background:#FBF7F8;}"
if DARK:  # colores con poco contraste sobre fondo oscuro
    EXPO_COLORS["Alta"] = "#E0527A"
    EDU_COLORS["Posgrado"] = "#E8D9EE"

METRICS = {
    "human_rating_beta": "Humanos · LLM + software básico (β) — principal",
    "human_rating_alpha": "Humanos · solo LLM (α)",
    "human_rating_gamma": "Humanos · potencial máximo (γ)",
    "dv_rating_beta": "GPT-4 · LLM + software básico (β)",
    "dv_rating_alpha": "GPT-4 · solo LLM (α)",
    "dv_rating_gamma": "GPT-4 · potencial máximo (γ)",
}
NEEDED = [
    "YEAR", "MONTH", "WTFINL", "AGE", "SEX", "EMPSTAT", "OCC", "DURUNEMP", "EDUC",
    "Major_Group", "Census_Title", "SOC_Code", "TOT_EMP", "A_MEDIAN", *METRICS.keys(),
]
ROOT = Path(__file__).resolve().parent.parent 
DEFAULT_PATHS = [
    str(ROOT / "data" / "dashboard" / "df_dashboard.parquet"),
    "data/processed/df_completo.pkl", "../data/processed/df_completo.pkl", "df_completo.pkl",
    "data/processed/df_completo.pkl", "../data/processed/df_completo.pkl", "df_completo.pkl",
    "data/processed/df_completo.csv", "../data/processed/df_completo.csv",
    "df_completo.csv", "dataset_final.csv",
]
MIN_CELL = 30          # mínimo de desempleados muestrales para mostrar una celda
LONG_TERM_WEEKS = 27   # definición oficial (BLS) de desempleo de larga duración

st.markdown(
    f"""
<style>
:root {{--ink:{INK}; --surf:{SURF}; --border:{BORDER}; --muted:{MUTED};
        --accent:{ACCENT}; --tipbg:{TIP_BG}; --tiptx:{TIP_TX}; --instx:{INS_TX};}}
{BG_RULE}
.block-container {{padding-top:1.1rem; max-width:1320px;}}
h1,h2,h3,h4 {{color:var(--ink); letter-spacing:-0.01em;}}
.hero {{background:linear-gradient(120deg,#22092C 0%,#872341 62%,#F05941 140%);
       border-radius:20px; padding:30px 36px; color:#fff; margin-bottom:18px;}}
.hero h1 {{color:#fff; font-size:2.3rem; margin:6px 0 6px 0; line-height:1.1;}}
.hero p {{color:#F6DDE0; font-size:1.02rem; margin:0; max-width:900px;}}
.hero .tag {{font-size:.74rem; letter-spacing:.12em; text-transform:uppercase; color:#FFB8A8; font-weight:700;}}
.kpi {{background:var(--surf); border:1px solid var(--border); border-radius:16px; padding:16px 18px;
      box-shadow:0 4px 16px -6px rgba(34,9,44,.15); height:100%;}}
.kpi-l {{font-size:.74rem; text-transform:uppercase; letter-spacing:.07em; color:var(--muted); font-weight:600;}}
.kpi-v {{font-size:2rem; font-weight:800; color:var(--ink); line-height:1.15; margin-top:4px;}}
.kpi-s {{font-size:.8rem; color:var(--accent); margin-top:2px;}}
.ins {{background:var(--surf); border:1px solid var(--border); border-left:5px solid #F05941; border-radius:12px;
      padding:14px 18px; height:100%; color:var(--instx); font-size:.95rem;}}
.ins b {{color:var(--accent);}}
.ins .ins-h {{font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; color:var(--accent); font-weight:700; margin-bottom:4px;}}
.tip {{background:var(--tipbg); border-radius:10px; padding:9px 14px; color:var(--tiptx); font-size:.86rem; margin:-4px 0 14px 0;}}
.stTabs [data-baseweb="tab"] {{font-weight:600;}}
.stTabs [aria-selected="true"] {{color:#F05941 !important;}}
.stTabs [data-baseweb="tab-highlight"] {{background-color:#F05941;}}
.small {{font-size:.8rem; color:var(--muted);}}
</style>
""",
    unsafe_allow_html=True,
)


# ════════════════════════════════════════════════════════════════════════════
# 1. CARGA Y PREPARACIÓN DE DATOS (misma lógica del notebook)
# ════════════════════════════════════════════════════════════════════════════
@st.cache_resource(show_spinner="Leyendo el dataset…")
def load_raw(path: str | None, file_bytes: bytes | None, name: str = "") -> pd.DataFrame:
    """Lee CSV, pickle (.pkl) o parquet (.parquet)."""
    ext = Path(name or path or "").suffix.lower()
    src = io.BytesIO(file_bytes) if file_bytes else path
    if ext in (".pkl", ".pickle"):
        df = pd.read_pickle(src)
    elif ext == ".parquet":
        df = pd.read_parquet(src)
    else:
        df = pd.read_csv(
            src, usecols=lambda c: c in set(NEEDED), low_memory=False,
            dtype={"SOC_Code": str, "Major_Group": str, "Census_Title": str},
        )
    missing = [c for c in NEEDED if c not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas en el archivo: {missing}")
    return df[NEEDED]


def edu_group(e: pd.Series) -> pd.Series:
    """Agrupa EDUC (códigos IPUMS-CPS) en 6 niveles legibles."""
    e = pd.to_numeric(e, errors="coerce")
    return pd.cut(e, bins=[-np.inf, 72, 80, 90, 100, 111, 998], labels=EDU_ORDER).astype(object)


@st.cache_resource(show_spinner="Preparando variables…")
def prepare(_raw: pd.DataFrame, source_id: str, metric: str) -> pd.DataFrame:
    d = _raw[(_raw["OCC"].fillna(0) != 0) & _raw["EMPSTAT"].between(10, 22)].copy()
    d = d.dropna(subset=["SOC_Code", "Census_Title", metric])

    # Terciles de exposición calculados sobre ocupaciones únicas (SOC), como en el notebook
    expo_soc = d.drop_duplicates("SOC_Code").set_index("SOC_Code")[metric]
    try:
        q = pd.qcut(expo_soc, 3, labels=EXPO_ORDER)
    except ValueError:  # demasiados empates en el borde del tercil
        q = pd.qcut(expo_soc.rank(method="first"), 3, labels=EXPO_ORDER)
    nivel = d["SOC_Code"].map(q.astype(object))

    unemp = d["EMPSTAT"].isin([20, 21, 22])
    out = pd.DataFrame(
        {
            "anio": d["YEAR"].astype("int16"),
            "mes": d["MONTH"].astype("int8"),
            "edad": d["AGE"],
            "sexo": d["SEX"].map({1: "Hombre", 2: "Mujer"}),
            "desempleado": unemp.astype("int8"),
            "peso": d["WTFINL"].astype("float32"),
            "semanas": d["DURUNEMP"].where(unemp & (d["DURUNEMP"] < 999)),
            "educ": edu_group(d["EDUC"]),
            "ocupacion": d["Census_Title"],
            "grupo": d["Major_Group"],
            "empleo_total": d["TOT_EMP"],
            "salario": d["A_MEDIAN"],
            "expo": d[metric],
            "nivel": nivel,
        }
    ).dropna(subset=["nivel"]).query("peso > 0")
    out["peso_desemp"] = out["peso"] * out["desempleado"]
    return out.reset_index(drop=True)


# ════════════════════════════════════════════════════════════════════════════
# 2. FUNCIONES ANALÍTICAS
# ════════════════════════════════════════════════════════════════════════════
def tasa(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    g = df.groupby(by, observed=True).agg(
        des=("peso_desemp", "sum"), fl=("peso", "sum"),
        n_des=("desempleado", "sum"), n=("peso", "size"),
    ).reset_index()
    g["tasa"] = 100 * g["des"] / g["fl"]
    return g


def wmedian(v: np.ndarray, w: np.ndarray) -> float:
    o = np.argsort(v)
    v, w = v[o], w[o]
    c = np.cumsum(w)
    return float(v[min(np.searchsorted(c, c[-1] / 2), len(v) - 1)])


def dur_stats(df: pd.DataFrame, by: list[str]) -> pd.DataFrame:
    """Duración del desempleo (semanas) ponderada: mediana, media y % de larga duración."""
    cols = by + ["mediana", "media", "largo_plazo", "n"]
    d = df[df["semanas"].notna()]
    rows = []
    for key, g in d.groupby(by, observed=True):
        key = key if isinstance(key, tuple) else (key,)
        v, w = g["semanas"].to_numpy(float), g["peso"].to_numpy(float)
        if w.sum() <= 0:
            continue
        rows.append({
            **dict(zip(by, key)),
            "mediana": wmedian(v, w),
            "media": float(np.average(v, weights=w)),
            "largo_plazo": 100 * w[v >= LONG_TERM_WEEKS].sum() / w.sum(),
            "n": len(g),
        })
    return pd.DataFrame(rows, columns=cols)


def survival_curve(d: pd.DataFrame, weeks: np.ndarray) -> np.ndarray:
    """% de desempleados que siguen sin empleo después de t semanas (ponderado)."""
    v, w = d["semanas"].to_numpy(float), d["peso"].to_numpy(float)
    o = np.argsort(v)
    v, w = v[o], w[o]
    cw = np.concatenate([[0], np.cumsum(w)])
    idx = np.searchsorted(v, weeks, side="right")
    return 100 * (cw[-1] - cw[idx]) / cw[-1]


def perfil_ocupaciones(d: pd.DataFrame) -> pd.DataFrame:
    d = d.assign(
        m=d["peso"] * (d["sexo"] == "Mujer"),
        e=d["peso"] * d["edad"],
        u=d["peso"] * d["educ"].isin(UNIV),
    )
    g = d.groupby("ocupacion").agg(
        fl=("peso", "sum"), m=("m", "sum"), e=("e", "sum"), u=("u", "sum"),
        expo=("expo", "first"), empleo=("empleo_total", "first"),
        salario=("salario", "first"), grupo=("grupo", "first"),
    )
    g["pct_mujeres"] = 100 * g["m"] / g["fl"]
    g["edad_media"] = g["e"] / g["fl"]
    g["pct_universitarios"] = 100 * g["u"] / g["fl"]
    return g[["expo", "empleo", "salario", "grupo", "pct_mujeres", "edad_media", "pct_universitarios"]].reset_index()


def trayectorias(f: pd.DataFrame, antes: list[int], despues: list[int],
                 min_n: int, umbral: float) -> pd.DataFrame:
    """¿Subió, bajó o se mantuvo el desempleo de cada ocupación entre dos periodos?"""
    empty = pd.DataFrame()
    mapa = {**{y: "antes" for y in antes}, **{y: "despues" for y in despues}}
    d = f.assign(periodo=f["anio"].map(mapa)).dropna(subset=["periodo"])
    if d.empty:
        return empty
    g = d.groupby(["ocupacion", "nivel", "periodo"]).agg(
        des=("peso_desemp", "sum"), fl=("peso", "sum"), n=("desempleado", "sum"),
    ).reset_index()
    g["tasa"] = 100 * g["des"] / g["fl"]
    t = g.pivot_table(index=["ocupacion", "nivel"], columns="periodo",
                      values=["tasa", "n"], aggfunc="first")
    t.columns = [f"{a}_{b}" for a, b in t.columns]
    need = ["tasa_antes", "tasa_despues", "n_antes", "n_despues"]
    if not all(c in t.columns for c in need):
        return empty
    t = t.dropna(subset=need).reset_index()
    t["n_total"] = t["n_antes"] + t["n_despues"]
    t = t[t["n_total"] >= min_n].copy()
    if t.empty:
        return empty
    t["cambio_pp"] = t["tasa_despues"] - t["tasa_antes"]
    t["trayectoria"] = np.select(
        [t["cambio_pp"] >= umbral, t["cambio_pp"] <= -umbral], ["Subió", "Bajó"], default="Estable"
    )
    return t.merge(perfil_ocupaciones(d), on="ocupacion", how="left")


# ── utilidades de formato / estilo ──────────────────────────────────────────
def fnum(x, d=1, sign=False, suf="") -> str:
    if x is None or pd.isna(x):
        return "n/d"
    return f"{x:+.{d}f}{suf}" if sign else f"{x:.{d}f}{suf}"


def getv(df: pd.DataFrame, i, c) -> float:
    try:
        return float(df.loc[i, c])
    except Exception:
        return np.nan

def chi2_p(a: int, b: int, c: int, d: int) -> float:
    """p-valor de la prueba chi-cuadrado 2x2 (con corrección de Yates), sin librerías extra."""
    n = a + b + c + d
    den = (a + b) * (c + d) * (a + c) * (b + d)
    if den == 0:
        return np.nan
    chi = n * max(0, abs(a * d - b * c) - n / 2) ** 2 / den
    return math.erfc(math.sqrt(chi / 2))

def style(fig: go.Figure, h: int = 420) -> go.Figure:
    fig.update_layout(
        template="simple_white", height=h,
        font=dict(family="Inter, Segoe UI, Helvetica, sans-serif", size=13, color=INK),   
        margin=dict(l=8, r=8, t=28, b=8),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0, title_text=""),
        hoverlabel=dict(bgcolor=SURF, font_color=INK, font_size=12),
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(gridcolor=GRID)
    return fig


def show(fig: go.Figure, key: str) -> None:
    st.plotly_chart(fig, key=key, config={"displaylogo": False, "modeBarButtonsToRemove": ["lasso2d", "select2d"]})


def kpi(label: str, value: str, sub: str = "") -> str:
    return f'<div class="kpi"><div class="kpi-l">{label}</div><div class="kpi-v">{value}</div><div class="kpi-s">{sub}</div></div>'


def insight(head: str, body: str) -> str:
    return f'<div class="ins"><div class="ins-h">{head}</div>{body}</div>'


# ════════════════════════════════════════════════════════════════════════════
# 3. BARRA LATERAL: DATOS Y FILTROS
# ════════════════════════════════════════════════════════════════════════════
path = next((p for p in DEFAULT_PATHS if Path(p).exists()), DEFAULT_PATHS[0])
up = None
file_bytes = None
if not Path(path).exists():
    st.markdown(
        '<div class="hero"><div class="tag">Falta el dataset</div>'
        "<h1>IA y mercado laboral en EE. UU.</h1>"
        "<p>No encontré el CSV final. Indica su ruta en la barra lateral o súbelo directamente.</p></div>",
        unsafe_allow_html=True,
    )
    st.stop()

try:
    raw = load_raw(None if file_bytes else path, file_bytes, up.name if up else "")
except Exception as e:  # noqa: BLE001
    st.error(f"No pude leer el dataset: {e}")
    st.stop()

source_id = (f"{up.name}-{len(file_bytes)}" if up else f"{path}-{Path(path).stat().st_mtime}")

with st.sidebar:
    st.markdown("### Medida de exposición")
    metric = st.selectbox(
        "Índice de Eloundou et al.", list(METRICS), format_func=METRICS.get,
        help="La principal del proyecto es human_rating_beta. Cambiarla recalcula los terciles Baja / Media / Alta.",
    )

df = prepare(raw, source_id, metric)
years = sorted(df["anio"].unique().tolist())

with st.sidebar:
    st.markdown("### Filtros")
    y0, y1 = st.select_slider("Años a mostrar", options=years, value=(years[0], years[-1]))
    base_year = st.selectbox("Año base para los índices", years, index=years.index(2022) if 2022 in years else 0,
                             help="2022 = salida de la pandemia y recuperación económica (criterio del notebook).")
    sexo_sel = st.radio("Sexo", ["Todos", "Hombre", "Mujer"], horizontal=True)
    a_min, a_max = int(df["edad"].min()), int(df["edad"].max())
    edad_rng = st.slider("Edad", a_min, a_max, (a_min, a_max))
    grupos_all = sorted(df["grupo"].dropna().unique().tolist())
    grupos_sel = st.multiselect("Gran grupo ocupacional", grupos_all, default=grupos_all)

    with st.expander("Parámetros: ¿subió o se mantuvo el desempleo?"):
        antes = st.multiselect("Periodo inicial", years, default=[y for y in (2022, 2023) if y in years])
        despues = st.multiselect("Periodo reciente", years, default=[y for y in (2025, 2026) if y in years])
        umbral = st.slider("Umbral de cambio (puntos porcentuales)", 0.5, 3.0, 1.0, 0.5)
        min_n = st.slider("Mín. desempleados muestrales por ocupación", 10, 200, 30, 10)
        if set(antes) & set(despues):
            st.warning("Un año está en ambos periodos; se asignará al reciente.")

    EXPLAIN = st.toggle("Mostrar guías de lectura", value=True,
                        help="Notas en lenguaje sencillo bajo cada gráfico, pensadas para público no técnico.")


def tip(txt: str) -> None:
    if EXPLAIN:
        st.markdown(f'<div class="tip"><b>Cómo leerlo.</b> {txt}</div>', unsafe_allow_html=True)


# ── aplicación de filtros ───────────────────────────────────────────────────
f = df
if sexo_sel != "Todos":
    f = f[f["sexo"] == sexo_sel]
f = f[f["edad"].between(*edad_rng) & f["grupo"].isin(grupos_sel)]
fy = f[f["anio"].between(y0, y1)]
fy22 = fy[fy["anio"] >= 2022]
if fy.empty:
    st.warning("Los filtros dejaron la muestra vacía. Ajusta la barra lateral.")
    st.stop()

with st.sidebar:
    st.caption(f"Muestra filtrada: {len(fy):,} registros · {fy['ocupacion'].nunique()} ocupaciones")

# ── cálculos compartidos ────────────────────────────────────────────────────
piv_all = tasa(f, ["anio", "nivel"]).pivot(index="anio", columns="nivel", values="tasa").reindex(columns=EXPO_ORDER)
piv_all.columns.name = None
piv = piv_all.loc[(piv_all.index >= y0) & (piv_all.index <= y1)]
base = base_year if base_year in piv_all.index else piv_all.index.min()
idx = 100 * (piv_all / piv_all.loc[base] - 1)          # % de cambio vs. año base
last = int(piv.index.max())

cambio = trayectorias(f, antes, despues, min_n, umbral)
dur_nivel = dur_stats(fy22, ["nivel"]).set_index("nivel")

lf_last = fy[fy["anio"] == last].groupby("nivel")["peso"].sum()
share_alta = 100 * lf_last.get("Alta", np.nan) / lf_last.sum()

tmp = fy.assign(pu=fy["peso"] * fy["educ"].isin(UNIV)).groupby("nivel").agg(pu=("pu", "sum"), fl=("peso", "sum"))
univ_share = 100 * tmp["pu"] / tmp["fl"]

if not cambio.empty:
    alta = cambio[cambio["nivel"] == "Alta"]
    p_sube = 100 * (alta["trayectoria"] == "Subió").mean() if len(alta) else np.nan
    p_baja = 100 * (alta["trayectoria"] == "Bajó").mean() if len(alta) else np.nan
    try:
        rho = cambio["expo"].corr(cambio["cambio_pp"], method="spearman")
    except Exception:  # noqa: BLE001
        rho = np.nan
else:
    p_sube = p_baja = rho = np.nan

# ════════════════════════════════════════════════════════════════════════════
# 4. ENCABEZADO
# ════════════════════════════════════════════════════════════════════════════
st.markdown(
    f"""<div class="hero">
    <div class="tag">CPS · BLS OEWS · Eloundou et al. ("GPTs are GPTs") · {years[0]}–{years[-1]}</div>
    <h1>IA y desempleo en Estados Unidos: ¿reemplazo u optimización?</h1>
    <p>¿Cómo se relacionan el nivel educativo y el tiempo que tardan en reemplearse los trabajadores desempleados 
    con la exposición a la inteligencia artificial en Estados Unidos desde 2021, y qué ocupaciones altamente expuestas 
    han visto subir su desempleo frente a las que lo mantuvieron estable entre 2021 y 2026, junto con las características 
    que distinguen a cada grupo?</p>
    </div>""",
    unsafe_allow_html=True,
)

tabs = st.tabs([
    "Resumen", "Evolución del desempleo", "Educación y reempleo",
    "Ocupaciones", "¿Subió o se mantuvo?", "Conclusiones","Método y datos",
])

# ════════════════════════════════════════════════════════════════════════════
# 5. TAB 1 · RESUMEN (público general)
# ════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    k = st.columns(5)
    k[0].markdown(kpi("Fuerza laboral en ocupaciones de exposición alta", fnum(share_alta, 0, suf="%"),
                      f"año {last}"), unsafe_allow_html=True)
    k[1].markdown(kpi(f"Desempleo · exposición alta vs. {base}", fnum(getv(idx, last, "Alta"), 0, True, "%"),
                      f"Tasa {last}: {fnum(getv(piv_all, last, 'Alta'), 1, suf='%')}"), unsafe_allow_html=True)
    k[2].markdown(kpi(f"Desempleo · exposición baja vs. {base}", fnum(getv(idx, last, "Baja"), 0, True, "%"),
                      f"Tasa {last}: {fnum(getv(piv_all, last, 'Baja'), 1, suf='%')}"), unsafe_allow_html=True)
    k[3].markdown(kpi("Semanas sin empleo (mediana) · exposición alta",
                      fnum(getv(dur_nivel, "Alta", "mediana"), 1),
                      f"Baja: {fnum(getv(dur_nivel, 'Baja', 'mediana'), 1)} semanas"), unsafe_allow_html=True)
    k[4].markdown(kpi("Ocupaciones muy expuestas con más desempleo", fnum(p_sube, 0, suf="%"),
                      f"Bajaron: {fnum(p_baja, 0, suf='%')}"), unsafe_allow_html=True)

    st.write("")
    i1, i2, i3 = st.columns(3)
    i1.markdown(insight(
        "Desempleo en el tiempo",
        f"Desde {base}, el desempleo en ocupaciones de exposición <b>alta</b> cambió "
        f"<b>{fnum(getv(idx, last, 'Alta'), 0, True, '%')}</b>; en la <b>media</b>, "
        f"{fnum(getv(idx, last, 'Media'), 0, True, '%')}, y en la <b>baja</b>, "
        f"{fnum(getv(idx, last, 'Baja'), 0, True, '%')}.",
    ), unsafe_allow_html=True)
    i2.markdown(insight(
        "Educación y reempleo",
        f"El <b>{fnum(getv(univ_share.to_frame('v'), 'Alta', 'v'), 0, suf='%')}</b> de la fuerza laboral en ocupaciones "
        f"de exposición alta tiene pregrado o más (frente a {fnum(getv(univ_share.to_frame('v'), 'Baja', 'v'), 0, suf='%')} "
        f"en exposición baja). Los desempleados de exposición alta llevan una mediana de "
        f"<b>{fnum(getv(dur_nivel, 'Alta', 'mediana'), 1)}</b> semanas buscando.",
    ), unsafe_allow_html=True)
    i3.markdown(insight(
        "Quiénes subieron",
        f"<b>{fnum(p_sube, 0, suf='%')}</b> de las ocupaciones muy expuestas aumentó su desempleo "
        f"(≥ {umbral:g} pp) y {fnum(p_baja, 0, suf='%')} lo redujo. Aun así, la correlación entre exposición y "
        f"cambio es de solo <b>{fnum(rho, 2)}</b>: <b>asociación, no causalidad</b>.",
    ), unsafe_allow_html=True)

    st.write("")
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader(f"¿Cuánto cambió el desempleo desde {base}?")
        d = idx.loc[(idx.index >= y0) & (idx.index <= y1)].reset_index().melt(
            id_vars="anio", var_name="nivel", value_name="cambio")
        fig = px.line(d, x="anio", y="cambio", color="nivel", markers=True,
                      color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                      labels={"cambio": f"Cambio vs. {base} (%)", "anio": "", "nivel": "Exposición a la IA"})
        for tr in fig.data:
            ys = list(tr.y)
            tr.text = [""] * (len(ys) - 1) + [f"{ys[-1]:+.0f}%"]
            tr.textposition = "middle right"
            tr.mode = "lines+markers+text"
            tr.line.width = 3.5
        fig.add_hline(y=0, line_dash="dot", line_color="#999")
        fig.update_yaxes(ticksuffix="%", zeroline=False)
        fig.update_xaxes(dtick=1, range=[y0 - 0.2, y1 + 0.6])
        show(style(fig, 400), "res_idx")
        tip(f"Cada línea muestra cuánto subió o bajó la tasa de desempleo respecto a {base}. "
            "Por encima de 0%: hay más desempleo que en el año base.")
    with c2:
        st.subheader(f"Desempleo en {last}, por nivel")
        d = piv_all.loc[[last]].melt(var_name="nivel", value_name="tasa")
        fig = px.bar(d, x="nivel", y="tasa", color="nivel", text=d["tasa"].map(lambda v: f"{v:.1f}%"),
                     color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                     labels={"tasa": "Tasa de desempleo (%)", "nivel": ""})
        fig.update_traces(textposition="outside")
        fig.update_layout(showlegend=False)
        fig.update_yaxes(ticksuffix="%")
        show(style(fig, 400), "res_bar")
        tip("Nivel absoluto de desempleo. Un nivel alto no implica que la IA sea la causa: "
            "hay oficios con mucho desempleo por estacionalidad.")

    st.info(
        "**Lectura prudente.** Los datos muestran asociaciones entre exposición teórica a la IA y resultados laborales. "
        "No miden uso real de IA en cada empleo, así que no permiten afirmar que la IA cause el desempleo."
    )

# ════════════════════════════════════════════════════════════════════════════
# 6. TAB 2 · EVOLUCIÓN
# ════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Tasa de desempleo por nivel de exposición")
        d = piv.reset_index().melt(id_vars="anio", var_name="nivel", value_name="tasa")
        fig = px.line(d, x="anio", y="tasa", color="nivel", markers=True,
                      color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                      labels={"tasa": "Tasa de desempleo (%)", "anio": "", "nivel": "Exposición"})
        fig.update_traces(line_width=3.5)
        fig.update_yaxes(ticksuffix="%").update_xaxes(dtick=1)
        show(style(fig), "evo_lvl")
        tip("Nivel de desempleo año a año. Las ocupaciones se agrupan en tres terciles según su exposición a los LLM.")
    with c2:
        st.subheader(f"Índice de cambio vs. {base}")
        d = idx.loc[(idx.index >= y0) & (idx.index <= y1)].reset_index().melt(
            id_vars="anio", var_name="nivel", value_name="cambio")
        fig = px.bar(d, x="anio", y="cambio", color="nivel", barmode="group",
                     color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                     labels={"cambio": f"Cambio vs. {base} (%)", "anio": "", "nivel": "Exposición"})
        fig.update_yaxes(ticksuffix="%").update_xaxes(dtick=1)
        show(style(fig), "evo_idx")
        tip("Barras hacia arriba = más desempleo que en el año base; hacia abajo = menos.")

    st.subheader("Serie mensual (promedio móvil de 3 meses)")
    m = fy.groupby(["anio", "mes", "nivel"]).agg(des=("peso_desemp", "sum"), fl=("peso", "sum")).reset_index()
    m["tasa"] = 100 * m["des"] / m["fl"]
    m["fecha"] = pd.to_datetime(dict(year=m["anio"], month=m["mes"], day=1))
    m = m.sort_values("fecha")
    m["suav"] = m.groupby("nivel")["tasa"].transform(lambda s: s.rolling(3, min_periods=1).mean())
    fig = px.line(m, x="fecha", y="suav", color="nivel", color_discrete_map=EXPO_COLORS,
                  category_orders={"nivel": EXPO_ORDER},
                  labels={"suav": "Tasa de desempleo (%)", "fecha": "", "nivel": "Exposición"})
    fig.update_traces(line_width=2.5).update_yaxes(ticksuffix="%")
    show(style(fig, 360), "evo_month")
    tip("Permite ver estacionalidad y confirmar hasta qué mes llegan los datos (el último año puede estar incompleto).")

    st.subheader("Desglose por característica del trabajador")
    dim = st.radio("Desglosar por", ["Sexo", "Nivel educativo"], horizontal=True, key="evo_dim")
    col, order = ("sexo", ["Hombre", "Mujer"]) if dim == "Sexo" else ("educ", EDU_ORDER)
    d = tasa(fy, ["anio", "nivel", col])
    d = d[d["n_des"] >= 10]
    fig = px.line(d, x="anio", y="tasa", color="nivel", markers=True, facet_col=col,
                  facet_col_wrap=3 if col == "educ" else 2, color_discrete_map=EXPO_COLORS,
                  category_orders={"nivel": EXPO_ORDER, col: order},
                  labels={"tasa": "Desempleo (%)", "anio": "", "nivel": "Exposición"})
    fig.for_each_annotation(lambda a: a.update(text=a.text.split("=")[-1]))
    fig.update_yaxes(ticksuffix="%").update_xaxes(dtick=1)
    show(style(fig, 560 if col == "educ" else 400), "evo_facet")
    tip("Compara si el patrón entre niveles de exposición se repite dentro de cada grupo. "
        "Se omiten celdas con menos de 10 desempleados muestrales.")

# ════════════════════════════════════════════════════════════════════════════
# 7. TAB 3 · EDUCACIÓN Y REEMPLEO (primera mitad de la pregunta analítica)
# ════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    vista = st.radio("Mapa de calor", ["Tasa de desempleo (%)", f"% desempleo de larga duración (≥ {LONG_TERM_WEEKS} sem.)"],
                     horizontal=True, key="edu_heat_sel")
    c1, c2 = st.columns(2)
    with c1:
        if vista.startswith("Tasa"):
            st.subheader("Desempleo según educación y exposición")
            h = tasa(fy, ["educ", "nivel"]).pivot(index="educ", columns="nivel", values="tasa")
            etiqueta = "Desempleo %"
            explicacion = "Cada casilla es la tasa de desempleo (%) de un cruce educación × exposición. Más oscuro = más desempleo."
        else:
            st.subheader("Larga duración según educación y exposición")
            dh = dur_stats(fy22, ["educ", "nivel"])
            h = dh[dh["n"] >= MIN_CELL].pivot(index="educ", columns="nivel", values="largo_plazo")
            etiqueta = "% larga duración"
            explicacion = (f"Cada casilla es el % de desempleados que lleva {LONG_TERM_WEEKS} semanas o más buscando trabajo, "
                           f"para un cruce educación × exposición (desde 2022). Más oscuro = búsquedas más largas.")
        h = h.reindex(index=EDU_ORDER, columns=EXPO_ORDER)
        fig = px.imshow(h, text_auto=".1f", aspect="auto",
                        color_continuous_scale=["#FFF1EC", C_ORANGE, C_WINE, C_DARK],
                        labels=dict(x="Exposición a la IA", y="", color=etiqueta))
        fig.update_layout(coloraxis_showscale=False)
        show(style(fig, 400), "edu_heat")
        tip(explicacion)
    with c2:
        st.subheader("¿Quién trabaja en cada nivel de exposición?")
        comp = fy.groupby(["nivel", "educ"])["peso"].sum().reset_index()
        comp["pct"] = 100 * comp["peso"] / comp.groupby("nivel")["peso"].transform("sum")
        fig = px.bar(comp, x="nivel", y="pct", color="educ", color_discrete_map=EDU_COLORS,
                     category_orders={"nivel": EXPO_ORDER, "educ": EDU_ORDER},
                     labels={"pct": "% de la fuerza laboral", "nivel": "Exposición a la IA", "educ": "Educación"})
        fig.update_yaxes(ticksuffix="%")
        show(style(fig, 400), "edu_comp")
        tip("Composición educativa de la fuerza laboral en cada nivel. Las ocupaciones más expuestas suelen requerir más estudios.")

    st.subheader("Tiempo que tardan en reemplearse los desempleados")
    medida = st.radio(
        "Medida", ["Mediana de semanas", "Media de semanas", f"% desempleo de larga duración (≥ {LONG_TERM_WEEKS} sem.)"],
        horizontal=True, key="edu_meas",
    )
    col_m = {"Mediana de semanas": "mediana", "Media de semanas": "media"}.get(medida, "largo_plazo")
    ds = dur_stats(fy22, ["educ", "nivel"])
    ds = ds[ds["n"] >= MIN_CELL]
    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(ds, x="educ", y=col_m, color="nivel", barmode="group",
                     color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER, "educ": EDU_ORDER},
                     labels={col_m: medida, "educ": "", "nivel": "Exposición"})
        if col_m == "largo_plazo":
            fig.update_yaxes(ticksuffix="%")
        show(style(fig, 420), "edu_dur")
        tip(f"Cuánto lleva buscando empleo cada grupo. Se ocultan celdas con menos de {MIN_CELL} desempleados muestrales. "
            "La duración mide el tiempo transcurrido hasta la encuesta, no la duración final del episodio.")
    with c4:
        comp_by = st.radio("Curvas por", ["Exposición", "Educación"], horizontal=True, key="edu_surv")
        scol, sorder, scolors = (("nivel", EXPO_ORDER, EXPO_COLORS) if comp_by == "Exposición"
                                 else ("educ", EDU_ORDER, EDU_COLORS))
        weeks = np.arange(0, 105)
        fig = go.Figure()
        dd = fy22[fy22["semanas"].notna()]
        for g_name in sorder:
            sub = dd[dd[scol] == g_name]
            if len(sub) >= MIN_CELL:
                fig.add_trace(go.Scatter(x=weeks, y=survival_curve(sub, weeks), mode="lines", name=g_name,
                                         line=dict(color=scolors[g_name], width=3, shape="hv")))
        fig.add_vline(x=LONG_TERM_WEEKS, line_dash="dot", line_color="#777",
                      annotation_text="27 sem.", annotation_position="top right")
        fig.update_xaxes(title="Semanas buscando empleo")
        fig.update_yaxes(title="% que sigue sin empleo", ticksuffix="%", range=[0, 100])
        show(style(fig, 420), "edu_surv_fig")
        tip("Cada curva dice qué porcentaje de desempleados sigue sin empleo tras X semanas. "
            "Una curva más alta = reempleo más lento.")
    st.subheader("¿Quién lleva más tiempo buscando empleo?")
    ver = st.radio("Ver por", ["Edad", "Sexo", "Exposición a la IA", "Educación", "Grupo ocupacional"],
                   horizontal=True, key="edu_quien")
    ddur = fy22[fy22["semanas"].notna()].copy()
    if ddur.empty:
        st.info("No hay datos de duración para los años seleccionados (se usan desde 2022).")
    else:
        edades = ["16-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        ddur["grupo_edad"] = pd.cut(ddur["edad"], bins=[15, 24, 34, 44, 54, 64, 120], labels=edades)
        col_v, orden = {
            "Edad": ("grupo_edad", edades), "Sexo": ("sexo", ["Hombre", "Mujer"]),
            "Exposición a la IA": ("nivel", EXPO_ORDER), "Educación": ("educ", EDU_ORDER),
            "Grupo ocupacional": ("grupo", None),
        }[ver]
        dv = dur_stats(ddur, [col_v])
        dv = dv[dv["n"] >= MIN_CELL]
        total_lp = 100 * ddur.loc[ddur["semanas"] >= LONG_TERM_WEEKS, "peso"].sum() / ddur["peso"].sum()
        if ver == "Grupo ocupacional":
            fig = px.bar(dv.sort_values("largo_plazo"), x="largo_plazo", y=col_v, orientation="h",
                         color_discrete_sequence=[C_RED], hover_data={"n": True},
                         labels={"largo_plazo": f"% con ≥ {LONG_TERM_WEEKS} semanas buscando", col_v: ""})
            fig.add_vline(x=total_lp, line_dash="dash", line_color="#777")
            fig.update_xaxes(ticksuffix="%")
        else:
            fig = px.bar(dv, x=col_v, y="largo_plazo", color=col_v if ver == "Exposición a la IA" else None,
                         color_discrete_map=EXPO_COLORS, color_discrete_sequence=[C_RED],
                         category_orders={col_v: orden}, hover_data={"n": True},
                         labels={"largo_plazo": f"% con ≥ {LONG_TERM_WEEKS} semanas buscando", col_v: ver})
            fig.add_hline(y=total_lp, line_dash="dash", line_color="#777")
            fig.update_yaxes(ticksuffix="%").update_layout(showlegend=False)
        show(style(fig, 420), "edu_quien_fig")
        tip(f"Porcentaje de desempleados que lleva {LONG_TERM_WEEKS} semanas o más buscando trabajo (desempleo de larga duración). "
            f"La línea punteada es el promedio general: {total_lp:.1f}%.")

# ════════════════════════════════════════════════════════════════════════════
# 8. TAB 4 · OCUPACIONES
# ════════════════════════════════════════════════════════════════════════════
occ = fy.groupby(["ocupacion", "grupo", "nivel"]).agg(
    expo=("expo", "first"), empleo=("empleo_total", "first"),
    salario=("salario", "first"), fl=("peso", "sum"),
).reset_index()

with tabs[3]:
    st.subheader("Mapa del empleo: tamaño = trabajadores, color = exposición a la IA")
    tm = occ.dropna(subset=["empleo"]).nlargest(250, "empleo")
    fig = px.treemap(tm, path=[px.Constant("EE. UU."), "grupo", "ocupacion"], values="empleo",
                     color="nivel", color_discrete_map=EXPO_COLORS)
    fig.update_traces(root_color=BORDER, marker_line_width=1, marker_line_color="white")
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=520, paper_bgcolor="rgba(0,0,0,0)",
                      font=dict(color="white"))
    show(fig, "occ_tree")
    tip("Cada rectángulo es una ocupación (las 250 más grandes); haz clic en un grupo para acercarte. "
        "Los tonos vino indican alta exposición.")

    st.subheader("Las 10 ocupaciones más y menos expuestas")
    top_hi = occ.sort_values(["expo", "empleo"], ascending=[False, False]).head(10)
    top_lo = occ.sort_values(["expo", "empleo"], ascending=[True, False]).head(10)
    ex = pd.concat([top_lo, top_hi]).sort_values("expo")
    fig = px.bar(ex, x="expo", y="ocupacion", color="nivel", orientation="h",
                 text=ex["expo"].map(lambda v: f"{v:.2f}"), hover_data={"empleo": ":,.0f"},
                 color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                 labels={"expo": "Exposición a la IA (0 a 1)", "ocupacion": "", "nivel": "Nivel", "empleo": "Empleo total"})
    fig.update_traces(textposition="outside").update_xaxes(range=[0, max(0.1, ex["expo"].max() * 1.12)])
    show(style(fig, 560), "occ_rank")
    tip("Arriba: ocupaciones de lenguaje y análisis (redactar, traducir, comunicar). Abajo: trabajos físicos o presenciales. "
        "Muchas ocupaciones empatan en exposición 0; se muestran las de mayor empleo. Exposición alta no significa que el "
        "trabajo desaparezca, sino que parte de sus tareas es automatizable.")

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Exposición vs. salario")
        sc = occ.dropna(subset=["salario", "empleo"])
        fig = px.scatter(sc, x="expo", y="salario", size="empleo", color="nivel", hover_name="ocupacion",
                         size_max=38, opacity=0.75, color_discrete_map=EXPO_COLORS,
                         category_orders={"nivel": EXPO_ORDER},
                         labels={"expo": "Exposición a la IA (0 a 1)", "salario": "Salario mediano anual (USD)", "nivel": "Nivel"})
        fig.update_yaxes(tickprefix="$", tickformat=",")
        show(style(fig, 450), "occ_sal")
        rho_s = sc["expo"].corr(sc["salario"], method="spearman") if len(sc) > 3 else np.nan
        tip(f"Cada burbuja es una ocupación (tamaño = empleo). Correlación de Spearman exposición–salario: {fnum(rho_s, 2)}.")
    with c2:
        st.subheader("Ocupaciones con mayor desempleo")
        to = tasa(fy22, ["ocupacion", "nivel"])
        to = to[to["n_des"] >= 100].nlargest(15, "tasa").sort_values("tasa")
        fig = px.bar(to, x="tasa", y="ocupacion", color="nivel", orientation="h",
                     color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                     labels={"tasa": "Tasa de desempleo (%)", "ocupacion": "", "nivel": "Exposición"})
        fig.update_xaxes(ticksuffix="%")
        show(style(fig, 450), "occ_unemp")
        tip("Solo ocupaciones con ≥ 100 desempleados muestrales (con menos, la tasa es inestable). "
            "Predominan oficios estacionales o de demanda variable, no los más expuestos a la IA.")

# ════════════════════════════════════════════════════════════════════════════
# 9. TAB 5 · SUBIÓ vs. SE MANTUVO (segunda mitad de la pregunta analítica)
# ════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    st.caption(f"Comparación de ocupaciones entre {', '.join(map(str, sorted(antes)))} y "
               f"{', '.join(map(str, sorted(despues)))} · umbral ±{umbral:g} pp · mínimo {min_n} desempleados muestrales.")
    if cambio.empty:
        st.warning("No hay ocupaciones que cumplan los parámetros. Ajusta los periodos o baja el mínimo de desempleados.")
    else:
        sel = st.radio("Nivel de exposición a analizar", ["Alta", "Media", "Baja", "Todas"], horizontal=True, key="tr_sel")
        cs = cambio if sel == "Todas" else cambio[cambio["nivel"] == sel]

        c1, c2 = st.columns([2, 3])
        with c1:
            st.subheader("¿Qué proporción subió?")
            ct = (pd.crosstab(cambio["nivel"], cambio["trayectoria"], normalize="index") * 100)
            ct = ct.reindex(index=EXPO_ORDER, columns=TRAY_ORDER).fillna(0).reset_index().melt(
                id_vars="nivel", var_name="trayectoria", value_name="pct")
            fig = px.bar(ct, x="pct", y="nivel", color="trayectoria", orientation="h", barmode="stack",
                         text=ct["pct"].map(lambda v: f"{v:.0f}%" if v >= 4 else ""),
                         color_discrete_map=TRAY_COLORS, category_orders={"nivel": EXPO_ORDER, "trayectoria": TRAY_ORDER},
                         labels={"pct": "% de ocupaciones", "nivel": "Exposición", "trayectoria": ""})
            fig.update_xaxes(ticksuffix="%", range=[0, 100])
            show(style(fig, 360), "tr_stack")
            tip("Cada barra suma 100% de las ocupaciones de ese nivel. Rojo = subió el desempleo; violeta = estable; verde = bajó.")
        with c2:
            st.subheader("Cambio del desempleo por nivel de exposición")
            fig = px.box(cambio, x="nivel", y="cambio_pp", points="all", hover_name="ocupacion", color="nivel",
                         color_discrete_map=EXPO_COLORS, category_orders={"nivel": EXPO_ORDER},
                         labels={"cambio_pp": "Cambio en la tasa (puntos %)", "nivel": "Exposición a la IA"})
            fig.add_hline(y=0, line_dash="dot", line_color="#777")
            fig.update_layout(showlegend=False)
            show(style(fig, 360), "tr_box")
            tip("Cada punto es una ocupación. La caja marca dónde está la mitad central. Dispersión grande en 'Baja' "
                "suele reflejar ocupaciones pequeñas con tasas inestables.")

        st.subheader(f"Exposición vs. cambio en el desempleo ({sel.lower() if sel != 'Todas' else 'todas las ocupaciones'})")
        scx = cs.assign(empleo_s=cs["empleo"].fillna(cs["empleo"].median() if cs["empleo"].notna().any() else 1))
        fig = px.scatter(scx, x="expo", y="cambio_pp", color="trayectoria", size="empleo_s", size_max=34,
                         hover_name="ocupacion", opacity=0.8, color_discrete_map=TRAY_COLORS,
                         category_orders={"trayectoria": TRAY_ORDER},
                         hover_data={"empleo_s": False, "tasa_antes": ":.2f", "tasa_despues": ":.2f", "expo": ":.2f"},
                         labels={"expo": "Exposición a la IA (0 a 1)", "cambio_pp": "Cambio en la tasa (puntos %)",
                                 "trayectoria": "", "tasa_antes": "Tasa inicial", "tasa_despues": "Tasa reciente"})
        fig.add_hline(y=0, line_color="#777", line_dash="dot")
        show(style(fig, 440), "tr_scatter")
        tip("Cada burbuja es una ocupación (tamaño = empleo). Por encima de la línea 0, el desempleo subió. "
            "Si la IA empujara el desempleo, esperaríamos más burbujas rojas hacia la derecha.")

        st.subheader("¿Qué distingue a cada grupo?")
        grp = cs.groupby("trayectoria").agg(
            ocupaciones=("ocupacion", "count"), cambio_pp=("cambio_pp", "median"), expo=("expo", "median"),
            salario=("salario", "median"), empleo=("empleo", "median"), empleo_suma=("empleo", "sum"),
            pct_mujeres=("pct_mujeres", "median"), edad_media=("edad_media", "median"),
            pct_universitarios=("pct_universitarios", "median"),
        ).reindex(TRAY_ORDER)
        # Edad, % mujeres y % pregrado+: promedio ponderado de los TRABAJADORES de cada grupo (igual que el notebook)
        tmap = cs.set_index("ocupacion")["trayectoria"]
        wk = f[f["ocupacion"].isin(tmap.index)]
        wk = wk.assign(tray=wk["ocupacion"].map(tmap), mujer=(wk["sexo"] == "Mujer").astype(float),
                       univ=wk["educ"].isin(UNIV).astype(float)).dropna(subset=["tray"])
        prof = {}
        for nombre, g in wk.groupby("tray", observed=True):
            w = g["peso"].to_numpy(float)
            prof[nombre] = {"pct_mujeres": 100 * np.average(g["mujer"], weights=w),
                            "edad_media": np.average(g["edad"], weights=w),
                            "pct_universitarios": 100 * np.average(g["univ"], weights=w)}
        prof = pd.DataFrame(prof).T.reindex(TRAY_ORDER)
        for c_ in ["pct_mujeres", "edad_media", "pct_universitarios"]:
            grp[c_] = prof[c_]
        opciones = {
            "Exposición a la IA (0 a 1)": "expo", "Empleo total de la ocupación": "empleo",
            "Salario mediano anual (USD)": "salario", "Tasa de desempleo inicial (%)": "tasa_antes",
            "% de mujeres": "pct_mujeres", "Edad media": "edad_media", "% con pregrado o más": "pct_universitarios",
        }
        cc1, cc2 = st.columns([2, 3])
        with cc1:
            carac = st.selectbox("Característica", list(opciones), key="tr_car")
            fig = px.box(cs, x="trayectoria", y=opciones[carac], color="trayectoria", points="all",
                         hover_name="ocupacion", color_discrete_map=TRAY_COLORS,
                         category_orders={"trayectoria": TRAY_ORDER}, log_y=(opciones[carac] == "empleo"),
                         labels={opciones[carac]: carac, "trayectoria": ""})
            fig.update_layout(showlegend=False)
            show(style(fig, 380), "tr_car_fig")
            tip("Cada punto es una ocupación; la caja marca el 50 % central y la línea interior, la mediana. "
                "El empleo total se muestra en escala logarítmica.")
        with cc2:
            tabla = grp.reset_index().rename(columns={
                "trayectoria": "Grupo", "ocupaciones": "# ocupaciones", "cambio_pp": "Cambio mediano (pp)",
                "expo": "Exposición", "salario": "Salario mediano (USD)", "empleo": "Empleo mediano",
                "empleo_suma": "Trabajadores en el grupo", "pct_mujeres": "% mujeres",
                "edad_media": "Edad media", "pct_universitarios": "% pregrado+",
            })
            st.dataframe(tabla, hide_index=True, column_config={
                "Cambio mediano (pp)": st.column_config.NumberColumn(format="%+.2f"),
                "Exposición": st.column_config.NumberColumn(format="%.2f"),
                "Salario mediano (USD)": st.column_config.NumberColumn(format="$%,.0f"),
                "Empleo mediano": st.column_config.NumberColumn(format="%,.0f"),
                "Trabajadores en el grupo": st.column_config.NumberColumn(format="%,.0f"),
                "% mujeres": st.column_config.NumberColumn(format="%.1f"),
                "Edad media": st.column_config.NumberColumn(format="%.1f"),
                "% pregrado+": st.column_config.NumberColumn(format="%.1f"),
            })
            st.markdown('<span class="small">Salario, empleo y exposición: mediana entre las ocupaciones del grupo (BLS OEWS). '
                        "Edad, % mujeres y % pregrado+: promedio ponderado de los trabajadores de esas ocupaciones (CPS, WTFINL).</span>",
                        unsafe_allow_html=True)
        st.subheader("Composición por grupo ocupacional")
        presentes = [t for t in TRAY_ORDER if t in set(cs["trayectoria"])]
        comp_g = (pd.crosstab(cs["grupo"], cs["trayectoria"], normalize="columns").mul(100)
                  .reindex(columns=presentes).reset_index()
                  .melt(id_vars="grupo", var_name="trayectoria", value_name="pct"))
        fig = px.bar(comp_g, x="pct", y="grupo", color="trayectoria", barmode="group", orientation="h",
                     color_discrete_map=TRAY_COLORS, category_orders={"trayectoria": TRAY_ORDER},
                     labels={"pct": "% de las ocupaciones del grupo", "grupo": "", "trayectoria": ""})
        fig.update_xaxes(ticksuffix="%")
        show(style(fig, 380), "tr_comp")
        tip("Dentro de cada grupo (subió / estable / bajó), qué porcentaje de sus ocupaciones pertenece a cada gran grupo ocupacional.")
        
        cols_show = {"ocupacion": "Ocupación", "nivel": "Exposición", "expo": "Índice IA", "tasa_antes": "Tasa inicial %",
                     "tasa_despues": "Tasa reciente %", "cambio_pp": "Cambio (pp)", "empleo": "Empleo total",
                     "salario": "Salario mediano"}
        cfg = {
            "Índice IA": st.column_config.NumberColumn(format="%.2f"),
            "Tasa inicial %": st.column_config.NumberColumn(format="%.2f"),
            "Tasa reciente %": st.column_config.NumberColumn(format="%.2f"),
            "Cambio (pp)": st.column_config.NumberColumn(format="%+.2f"),
            "Empleo total": st.column_config.NumberColumn(format="%,.0f"),
            "Salario mediano": st.column_config.NumberColumn(format="$%,.0f"),
        }
        t1, t2 = st.columns(2)
        with t1:
            st.markdown("**Las que más subieron**")
            st.dataframe(cs.sort_values("cambio_pp", ascending=False).head(10)[list(cols_show)].rename(columns=cols_show),
                         hide_index=True, column_config=cfg)
        with t2:
            st.markdown("**Las más estables** (menor cambio absoluto)")
            est = cs.assign(a=cs["cambio_pp"].abs()).sort_values("a").head(10)
            st.dataframe(est[list(cols_show)].rename(columns=cols_show), hide_index=True, column_config=cfg)
        st.download_button("Descargar tabla completa (CSV)", cambio.to_csv(index=False).encode("utf-8"),
                           "trayectorias_ocupaciones.csv", "text/csv")
        
# ════════════════════════════════════════════════════════════════════════════
# 10. TAB 5 · CONLUSIONES
# ════════════════════════════════════════════════════════════════════════════

with tabs[5]:
    lp = dur_stats(fy22, ["nivel"]).set_index("nivel")["largo_plazo"].to_frame("v")
    lp_edu = dur_stats(fy22, ["educ"]).set_index("educ")["largo_plazo"]
    de = dur_stats(fy22, ["educ", "nivel"])
    de = de[de["n"] >= MIN_CELL]
    pv = de.pivot(index="educ", columns="nivel", values="largo_plazo") if not de.empty else pd.DataFrame()
    gap = (pv["Alta"] - pv["Baja"]).dropna() if {"Alta", "Baja"} <= set(pv.columns) else pd.Series(dtype=float)
    ps = (cambio.groupby("nivel")["trayectoria"].apply(lambda s: 100 * (s == "Subió").mean()).to_frame("v")
          if not cambio.empty else pd.DataFrame({"v": []}))
    if not cambio.empty:
        sube_, alta_ = cambio["trayectoria"] == "Subió", cambio["nivel"] == "Alta"
        p_val = chi2_p(int((alta_ & sube_).sum()), int((alta_ & ~sube_).sum()),
                       int((~alta_ & sube_).sum()), int((~alta_ & ~sube_).sum()))
    else:
        p_val = np.nan
    txt_p = ("" if pd.isna(p_val) else
             f" La diferencia frente al resto {'no ' if p_val >= 0.05 else ''}es estadísticamente significativa (p = {fnum(p_val, 2)}).")

    st.subheader("Respuesta a la pregunta analítica")
    a, b = st.columns(2)
    a.markdown(insight(
        "Parte A · Educación, tiempo buscando empleo y exposición",
        f"El <b>{fnum(getv(lp, 'Alta', 'v'), 1, suf='%')}</b> de los desempleados de ocupaciones de exposición alta lleva "
        f"{LONG_TERM_WEEKS} semanas o más buscando trabajo, frente a {fnum(getv(lp, 'Baja', 'v'), 1, suf='%')} en exposición baja. "
        f"La brecha es mayor en <b>{gap.idxmax() if len(gap) else 'n/d'}</b> "
        f"({fnum(gap.max() if len(gap) else np.nan, 1, True, ' pp')}). "
        f"La duración <b>aumenta con la educación</b> ({fnum(lp_edu.get('Sin bachillerato', np.nan), 1, suf='%')} sin bachillerato "
        f"vs {fnum(lp_edu.get('Posgrado', np.nan), 1, suf='%')} con posgrado): lo contrario a lo que suponía nuestra hipótesis.",
    ), unsafe_allow_html=True)
    b.markdown(insight(
        "Parte B · Ocupaciones que subieron vs. estables",
        f"El desempleo subió ≥ {umbral:g} pp en el <b>{fnum(getv(ps, 'Alta', 'v'), 0, suf='%')}</b> de las ocupaciones de exposición alta, "
        f"frente a {fnum(getv(ps, 'Media', 'v'), 0, suf='%')} (media) y {fnum(getv(ps, 'Baja', 'v'), 0, suf='%')} (baja). "
        f"La correlación exposición–cambio es débil (<b>{fnum(rho, 2)}</b>).{txt_p} Dentro de las muy expuestas, las que subieron tienen "
        "más trabajadores con pregrado o más, menos mujeres, menos empleo total y mayor peso del grupo "
        "<i>Management, Business, Science, and Arts</i> (ver pestaña anterior).",
    ), unsafe_allow_html=True)

    st.subheader("Qué significa")
    st.markdown(
        "- **Hay una señal, pero es débil y no concluyente.** Con las seis medidas de exposición la correlación va de 0,06 a 0,12, y la diferencia en la proporción de ocupaciones que subieron no es estadísticamente significativa.\n"
        "- **No es causalidad.** La exposición mide qué tareas *podría* hacer la IA, no si las empresas la usan; en los mismos años "
        "subieron las tasas de interés y hubo recortes en tecnología.\n"
        "- **Mayor educación no protege del desempleo prolongado** en las ocupaciones más expuestas: el riesgo se concentra en "
        "perfiles técnicos, profesionales y de posgrado.\n"
        "- **Ojo con lo que no es IA:** las ocupaciones con más desempleo son estacionales y de exposición baja."
    )

    st.subheader("Recomendaciones")
    st.markdown(
        """
| # | Acción | Para quién | Qué la respalda | Cómo medir si funciona |
|---|---|---|---|---|
| 1 | Programa de **recapacitación y reubicación** en habilidades complementarias a la IA | Desempleados con formación técnica, pregrado o posgrado de ocupaciones de exposición alta | Mayor desempleo de larga duración que en exposición baja en esos niveles | % de desempleados de larga duración en exposición alta |
| 2 | **Campaña de reempleo** para personas mayores | 55–64 años (27,5 % lleva ≥ 27 semanas buscando, vs 14,7 % entre 16 y 24) | Duración de desempleo por edad | Semanas medianas de búsqueda en 55–64 |
| 3 | **Monitoreo periódico** de ocupaciones de exposición alta, poco empleo total y perfil gerencial/profesional | Entidades de empleo y formación | Son las que más suben | Lista de alerta trimestral por ocupación |
| 4 | **No limitar la política a la exposición alta** | Diseñadores de política | Exposición baja tiene la mayor tasa de desempleo (5,65 % vs 2,95 %) | Tasa de desempleo por nivel de exposición |
| 5 | **Incorporar formación en uso de IA como herramienta** en programas técnicos, universitarios y de posgrado | Instituciones de educación y formación | La brecha de desempleo de larga duración entre exposición alta y baja es mayor en técnico o asociado (27,6 % vs 20,6 %) y en posgrado (28,7 % vs 21,3 %) | % de desempleados de larga duración con formación técnica o de posgrado en exposición alta |
"""
    )
    st.caption("Los textos interpretativos y las cifras de las recomendaciones 2 y 4 corresponden a los parámetros por defecto "
               "(filtros sin tocar); las cifras de las tarjetas sí se actualizan con los filtros. "
               "Todos los resultados son asociaciones, no efectos causales.")
    
    
# ════════════════════════════════════════════════════════════════════════════
# 11. TAB 6 · MÉTODO Y DATOS
# ════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    st.subheader("Cómo se construyó")
    st.markdown(
        f"""
- **Fuentes.** Microdatos mensuales del *Current Population Survey* (IPUMS CPS), estadísticas de empleo y salario por
  ocupación del BLS (OEWS) e índices de exposición a LLM de Eloundou et al. (*GPTs are GPTs*), unidos por código SOC.
- **Población.** Personas en la fuerza laboral con ocupación declarada (`OCC ≠ 0`, `EMPSTAT < 30`).
  Desempleado = `EMPSTAT` 20, 21 o 22.
- **Nivel de exposición.** Terciles (Baja / Media / Alta) de la medida elegida (`{metric}`), calculados sobre ocupaciones únicas.
- **Tasas.** Ponderadas con `WTFINL`: desempleados ponderados ÷ fuerza laboral ponderada.
- **Índice de cambio.** Tasa del año ÷ tasa del año base ({base}) − 1.
- **Duración.** `DURUNEMP` en semanas (999 = no aplica, excluido). Mediana ponderada; larga duración = ≥ {LONG_TERM_WEEKS} semanas.
- **Subió / Estable / Bajó.** Cambio en la tasa de la ocupación entre dos periodos, con umbral de ±{umbral:g} pp y mínimo de
  {min_n} desempleados muestrales para evitar tasas inestables.
- **Educación.** `EDUC` agrupada en 6 niveles (sin bachillerato, bachillerato, algo de universidad, técnico/asociado, pregrado, posgrado).
"""
    )
    st.subheader("Limitaciones")
    st.warning(
        "- La exposición mide **potencial teórico** de automatización de tareas, no adopción real de IA.\n"
        "- Las ocupaciones tienen exposición idéntica en muchos casos (empates, sobre todo en 0), por lo que los terciles son aproximados.\n"
        "- El último año puede tener menos meses y la comparación entre años mezcla estacionalidad.\n"
        "- Con filtros muy estrictos (sexo, edad, grupo) las celdas se vuelven pequeñas y las tasas inestables.\n"
        "- La duración del desempleo es la de un episodio en curso al momento de la encuesta.\n"
        "- Los resultados describen asociaciones; no establecen causalidad."
    )
    with st.expander("Diccionario de variables de salida (después de preparar)"):
        st.dataframe(pd.DataFrame({
            "Variable": ["anio / mes", "sexo", "edad", "educ", "desempleado", "semanas", "ocupacion", "grupo",
                         "empleo_total", "salario", "expo", "nivel"],
            "Origen": ["YEAR / MONTH", "SEX", "AGE", "EDUC (agrupada)", "EMPSTAT ∈ {20,21,22}", "DURUNEMP (≠999)",
                       "Census_Title", "Major_Group", "TOT_EMP (BLS)", "A_MEDIAN (BLS)", f"{metric} (Eloundou)",
                       "Tercil de la exposición"],
        }), hide_index=True)
    