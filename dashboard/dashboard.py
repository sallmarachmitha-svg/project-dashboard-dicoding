import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem; padding-bottom: 2rem; }
    .metric-card {
        background: #f8f9fa;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border: 1px solid #e9ecef;
    }
    .insight-card {
        background: #ffffff;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        border: 1px solid #e9ecef;
        margin-bottom: 0.75rem;
    }
    .section-title {
        font-size: 0.75rem;
        font-weight: 600;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), "main_data.csv"))
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load_data()

# ── Sidebar filters ───────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🚴 Bike Sharing")
    st.markdown("Dashboard analisis data harian 2011–2012, Washington D.C.")
    st.divider()

    st.markdown("### Filter Data")

    year_options = {0: "2011", 1: "2012", "Semua": "Semua"}
    selected_year = st.selectbox(
        "Tahun",
        options=["Semua", 0, 1],
        format_func=lambda x: year_options[x],
    )

    selected_seasons = st.multiselect(
        "Musim",
        options=["Spring", "Summer", "Fall", "Winter"],
        default=["Spring", "Summer", "Fall", "Winter"],
    )

    selected_weather = st.multiselect(
        "Cuaca",
        options=["Clear", "Mist", "Light Snow/Rain"],
        default=["Clear", "Mist", "Light Snow/Rain"],
    )

   
# ── Apply filters ─────────────────────────────────────────────────────────────
df_filtered = df.copy()
if selected_year != "Semua":
    df_filtered = df_filtered[df_filtered["yr"] == selected_year]
if selected_seasons:
    df_filtered = df_filtered[df_filtered["season"].isin(selected_seasons)]
if selected_weather:
    df_filtered = df_filtered[df_filtered["weathersit"].isin(selected_weather)]

# ── Header ────────────────────────────────────────────────────────────────────
st.title("🚴 Bike Sharing Dashboard")
st.caption(f"Data harian · {len(df_filtered):,} hari ditampilkan · Washington D.C.")
st.divider()

# ── KPI cards ─────────────────────────────────────────────────────────────────
col1, col2, col3, col4, col5 = st.columns(5)

total = df_filtered["cnt"].sum()
daily_avg = df_filtered["cnt"].mean()
peak = df_filtered["cnt"].max()
peak_date = df_filtered.loc[df_filtered["cnt"].idxmax(), "dteday"].strftime("%d %b %Y")
pct_registered = df_filtered["registered"].sum() / df_filtered["cnt"].sum() * 100
pct_casual = 100 - pct_registered

yr0 = df[df["yr"] == 0]["cnt"].sum()
yr1 = df[df["yr"] == 1]["cnt"].sum()
growth = (yr1 - yr0) / yr0 * 100

col1.metric("Total Penyewaan", f"{total:,.0f}")
col2.metric("Rata-rata/Hari", f"{daily_avg:,.0f}")
col3.metric("Puncak Tertinggi", f"{peak:,}", f"{peak_date}")
col4.metric("Member Terdaftar", f"{pct_registered:.1f}%")
col5.metric("Pertumbuhan YoY", f"+{growth:.1f}%", "2011 → 2012")

st.divider()

# ── Row 1: Monthly trend + Season ─────────────────────────────────────────────
st.markdown('<p class="section-title">Tren Waktu</p>', unsafe_allow_html=True)
col_l, col_r = st.columns([2, 1])

with col_l:
    month_names = {1:"Jan",2:"Feb",3:"Mar",4:"Apr",5:"Mei",6:"Jun",
                   7:"Jul",8:"Ags",9:"Sep",10:"Okt",11:"Nov",12:"Des"}
    monthly = df_filtered.groupby("mnth")["cnt"].mean().reset_index()
    monthly["bulan"] = monthly["mnth"].map(month_names)

    fig_month = px.bar(
        monthly, x="bulan", y="cnt",
        title="Rata-rata Penyewaan per Bulan",
        color="cnt",
        color_continuous_scale=["#B5D4F4", "#185FA5"],
        labels={"cnt": "Rata-rata Penyewaan", "bulan": "Bulan"},
    )
    fig_month.update_traces(marker_line_width=0)
    fig_month.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14,
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(categoryorder="array",
                   categoryarray=list(month_names.values()),
                   showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_month, use_container_width=True)

with col_r:
    season_avg = df_filtered.groupby("season")["cnt"].mean().reset_index()
    season_order = ["Spring", "Summer", "Fall", "Winter"]
    season_avg["season"] = pd.Categorical(season_avg["season"], categories=season_order, ordered=True)
    season_avg = season_avg.sort_values("season")

    fig_season = px.bar(
        season_avg, x="season", y="cnt",
        title="Rata-rata per Musim",
        color="cnt",
        color_continuous_scale=["#9FE1CB", "#085041"],
        labels={"cnt": "Rata-rata", "season": "Musim"},
    )
    fig_season.update_traces(marker_line_width=0)
    fig_season.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14,
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_season, use_container_width=True)

# ── Row 2: Weekday + User type + Weather ──────────────────────────────────────
st.markdown('<p class="section-title">Pola Pengguna & Cuaca</p>', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)

with col1:
    day_names = {0:"Min",1:"Sen",2:"Sel",3:"Rab",4:"Kam",5:"Jum",6:"Sab"}
    weekday_avg = df_filtered.groupby("weekday")["cnt"].mean().reset_index()
    weekday_avg["hari"] = weekday_avg["weekday"].map(day_names)

    fig_week = px.bar(
        weekday_avg, x="hari", y="cnt",
        title="Rata-rata per Hari",
        color="cnt",
        color_continuous_scale=["#CECBF6", "#534AB7"],
        labels={"cnt": "Rata-rata", "hari": "Hari"},
    )
    fig_week.update_traces(marker_line_width=0)
    fig_week.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14,
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=False,
                   categoryorder="array",
                   categoryarray=list(day_names.values())),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_week, use_container_width=True)

with col2:
    casual_total = df_filtered["casual"].sum()
    reg_total = df_filtered["registered"].sum()

    fig_donut = go.Figure(go.Pie(
        labels=["Casual", "Terdaftar"],
        values=[casual_total, reg_total],
        hole=0.65,
        marker_colors=["#EF9F27", "#1D9E75"],
        textinfo="percent",
        hovertemplate="%{label}: %{value:,}<extra></extra>",
    ))
    fig_donut.update_layout(
        title="Casual vs Terdaftar",
        title_font_size=14,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        legend=dict(orientation="h", yanchor="bottom", y=-0.15),
        margin=dict(t=40, b=20, l=0, r=0),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

with col3:
    weather_avg = df_filtered.groupby("weathersit")["cnt"].mean().reset_index()
    weather_order = ["Clear", "Mist", "Light Snow/Rain"]
    weather_avg["weathersit"] = pd.Categorical(
        weather_avg["weathersit"], categories=weather_order, ordered=True
    )
    weather_avg = weather_avg.sort_values("weathersit")

    fig_weather = px.bar(
        weather_avg, x="cnt", y="weathersit",
        orientation="h",
        title="Rata-rata per Kondisi Cuaca",
        color="cnt",
        color_continuous_scale=["#F5C4B3", "#378ADD"],
        labels={"cnt": "Rata-rata", "weathersit": "Cuaca"},
    )
    fig_weather.update_traces(marker_line_width=0)
    fig_weather.update_layout(
        coloraxis_showscale=False,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14,
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_weather, use_container_width=True)

# ── Row 3: Scatter suhu vs penyewaan + workday comparison ─────────────────────
st.markdown('<p class="section-title">Analisis Faktor Cuaca</p>', unsafe_allow_html=True)
col_l, col_r = st.columns([3, 2])

with col_l:
    fig_scatter = px.scatter(
        df_filtered,
        x="temp", y="cnt",
        color="season",
        color_discrete_map={
            "Spring": "#9FE1CB",
            "Summer": "#1D9E75",
            "Fall": "#085041",
            "Winter": "#B5D4F4",
        },
        title="Hubungan Suhu vs Jumlah Penyewaan",
        labels={"temp": "Suhu (ternormalisasi)", "cnt": "Jumlah Penyewaan", "season": "Musim"},
        opacity=0.6,
        trendline="ols",
        trendline_color_override="#D85A30",
    )
    fig_scatter.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        title_font_size=14,
        margin=dict(t=40, b=0, l=0, r=0),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
        yaxis=dict(showgrid=True, gridcolor="#f0f0f0"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

with col_r:
    corr_data = {
        "Faktor": ["Suhu", "Kelembapan", "Kecepatan Angin"],
        "Korelasi": [
            round(df_filtered["temp"].corr(df_filtered["cnt"]), 2),
            round(df_filtered["hum"].corr(df_filtered["cnt"]), 2),
            round(df_filtered["windspeed"].corr(df_filtered["cnt"]), 2),
        ],
    }
    corr_df = pd.DataFrame(corr_data)
    colors = ["#378ADD" if v > 0 else "#D85A30" for v in corr_df["Korelasi"]]

    fig_corr = go.Figure(go.Bar(
        x=corr_df["Korelasi"],
        y=corr_df["Faktor"],
        orientation="h",
        marker_color=colors,
        text=[f"{v:+.2f}" for v in corr_df["Korelasi"]],
        textposition="outside",
        hovertemplate="%{y}: %{x:+.2f}<extra></extra>",
    ))
    fig_corr.add_vline(x=0, line_width=1, line_color="gray")
    fig_corr.update_layout(
        title="Korelasi Faktor Cuaca",
        title_font_size=14,
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        margin=dict(t=40, b=0, l=0, r=50),
        xaxis=dict(showgrid=True, gridcolor="#f0f0f0", range=[-0.4, 0.9]),
        yaxis=dict(showgrid=False),
    )
    st.plotly_chart(fig_corr, use_container_width=True)

# ── Insight section ────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p class="section-title">Insight & Temuan Kunci</p>', unsafe_allow_html=True)

ic1, ic2, ic3 = st.columns(3)

with ic1:
    st.info("""
**📈 Pertumbuhan 64.9% dalam setahun**

Dari 1.24 juta (2011) menjadi 2.05 juta (2012). Menunjukkan adopsi bike sharing yang sangat pesat.
""")
    st.warning("""
**🌧️ Hujan/salju memangkas penyewaan -63%**

Dari rata-rata 4.877 (cerah) anjlok ke 1.803 saat hujan/salju. Faktor risiko terbesar operasional harian.
""")

with ic2:
    st.success("""
**🌡️ Suhu adalah prediktor terkuat (r = 0.63)**

Dari tiga faktor cuaca, suhu paling berpengaruh. Bisa dipakai sebagai dasar forecasting demand harian.
""")
    st.info("""
**🏆 Juni–September adalah masa panen**

Tiga bulan terbaik berturut-turut: Juni (5.772), September (5.767), Agustus (5.664) penyewaan/hari.
""")

with ic3:
    st.warning("""
**🎉 Hari libur justru lebih sepi (-17%)**

Rata-rata 3.735 saat libur vs 4.527 hari biasa. Commuter berhenti, casual tidak cukup menutupi.
""")
    st.success("""
**👥 Casual vs member: dua karakter berbeda**

Casual naik +126% di akhir pekan (rekreasi). Member justru lebih aktif di hari kerja (commuting).
""")

# ── Rekomendasi ───────────────────────────────────────────────────────────────
st.divider()
st.markdown('<p class="section-title">Rekomendasi Berbasis Data</p>', unsafe_allow_html=True)

rc1, rc2, rc3, rc4 = st.columns(4)
rc1.markdown("**01 · Armada musim panas**\n\nTingkatkan ketersediaan sepeda di Juni–Sep saat demand puncak.")
rc2.markdown("**02 · Promo hari libur**\n\nBuat paket khusus hari libur untuk mendorong penyewaan casual.")
rc3.markdown("**03 · Retensi member**\n\nFokus program loyalitas untuk 81% pengguna terdaftar.")
rc4.markdown("**04 · Manajemen cuaca**\n\nKurangi operasional saat prediksi hujan/salju untuk efisiensi biaya.")

# ── Raw data expander ──────────────────────────────────────────────────────────
with st.expander("Lihat Data Mentah"):
    st.dataframe(
        df_filtered[["dteday","season","weathersit","temp","hum","windspeed",
                      "casual","registered","cnt"]].rename(columns={
            "dteday": "Tanggal", "season": "Musim", "weathersit": "Cuaca",
            "temp": "Suhu", "hum": "Kelembapan", "windspeed": "Angin",
            "casual": "Casual", "registered": "Terdaftar", "cnt": "Total",
        }),
        use_container_width=True,
        hide_index=True,
    )