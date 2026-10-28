"""Dashboard Kualitas Udara Beijing (Maret 2013 – Februari 2017).

Proyek akhir "Belajar Fundamental Analisis Data" – Dicoding.
Jalankan dengan:  streamlit run dashboard/dashboard.py
"""
import os

import folium
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
import streamlit as st
from streamlit_folium import st_folium

# ------------------------------------------------------------------ Konfigurasi
st.set_page_config(page_title="Dashboard Kualitas Udara Beijing", page_icon="🌫️", layout="wide")
sns.set_theme(style="whitegrid")

DATA_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main_data.csv")

HIGHLIGHT = "#C0392B"
BASE = "#B8C4CE"
ACCENT = "#2E86AB"

POLLUTANTS = ["PM2.5", "PM10", "SO2", "NO2", "CO", "O3"]
# Baku mutu rata-rata 24 jam China (GB 3095-2012, Grade II), µg/m³.
# O3 tidak memiliki baku mutu rata-rata 24 jam (hanya 1 jam & 8 jam), sehingga tidak ditampilkan.
DAILY_STANDARD = {"PM2.5": 75, "PM10": 150, "SO2": 150, "NO2": 80, "CO": 4000, "O3": None}

SEASON_ORDER = ["Semi", "Panas", "Gugur", "Dingin"]
SEASON_COLORS = {"Semi": "#8FB996", "Panas": "#F4A259", "Gugur": "#BC8034", "Dingin": HIGHLIGHT}
MONTH_ORDER = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 1, 2]
MONTH_NAMES = ["Mar", "Apr", "Mei", "Jun", "Jul", "Agu", "Sep", "Okt", "Nov", "Des", "Jan", "Feb"]
COMPASS = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
           "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]

WIND_BINS = [-0.01, 1, 2, 3, 4, np.inf]
WIND_LABELS = ["Tenang (≤1)", "Lemah (1–2]", "Sedang (2–3]", "Cukup kencang (3–4]", "Kencang (>4)"]

AQI_BINS = [0, 35, 75, 115, 150, 250, np.inf]
AQI_LABELS = ["Baik", "Sedang", "Tidak Sehat (Sensitif)", "Tidak Sehat", "Sangat Tidak Sehat", "Berbahaya"]
AQI_COLORS = ["#00A65A", "#F2C80F", "#F39C12", "#E74C3C", "#8E44AD", "#7B241C"]

STATION_COORDS = {
    "Aotizhongxin": (39.982, 116.397), "Changping": (40.217, 116.230), "Dingling": (40.292, 116.220),
    "Dongsi": (39.929, 116.417), "Guanyuan": (39.929, 116.339), "Gucheng": (39.914, 116.184),
    "Huairou": (40.328, 116.628), "Nongzhanguan": (39.937, 116.461), "Shunyi": (40.127, 116.655),
    "Tiantan": (39.886, 116.407), "Wanliu": (39.987, 116.287), "Wanshouxigong": (39.878, 116.352),
}


# ------------------------------------------------------------------ Helper functions
@st.cache_data
def load_data(path):
    df = pd.read_csv(path, parse_dates=["datetime"])
    df["date"] = df["datetime"].dt.floor("D")
    df["musim"] = pd.Categorical(df["musim"], categories=SEASON_ORDER, ordered=True)
    df["kategori_angin"] = pd.cut(df["WSPM"], bins=WIND_BINS, labels=WIND_LABELS)
    return df


def create_daily_df(df):
    """Rata-rata harian per stasiun (baku mutu didefinisikan untuk rata-rata 24 jam)."""
    daily = df.groupby(["station", "date"], observed=True)[POLLUTANTS].mean().reset_index()
    daily["musim"] = pd.Categorical(
        daily["date"].dt.month.map({12: "Dingin", 1: "Dingin", 2: "Dingin", 3: "Semi", 4: "Semi", 5: "Semi",
                                    6: "Panas", 7: "Panas", 8: "Panas", 9: "Gugur", 10: "Gugur", 11: "Gugur"}),
        categories=SEASON_ORDER, ordered=True)
    daily["kategori_aqi"] = pd.cut(daily["PM2.5"], bins=AQI_BINS, labels=AQI_LABELS, include_lowest=True)
    return daily


def create_station_summary(daily, pollutant):
    std = DAILY_STANDARD[pollutant]
    summary = daily.groupby("station")[pollutant].agg(rata2="mean", maks_harian="max", total_hari="count")
    if std is not None:
        summary["persen_hari_melampaui"] = daily.groupby("station")[pollutant].apply(lambda s: (s > std).mean() * 100)
    return summary.sort_values("rata2", ascending=False)


def add_standard_line(ax, pollutant, orientation="h"):
    std = DAILY_STANDARD[pollutant]
    if std is None:
        return
    line = ax.axhline if orientation == "h" else ax.axvline
    line(std, color="#555555", ls="--", lw=1.2, label=f"Baku mutu harian ({std:,} µg/m³)")


def fmt(value, decimals=1):
    return f"{value:,.{decimals}f}".replace(",", "_").replace(".", ",").replace("_", ".")


# ------------------------------------------------------------------ Load data
all_df = load_data(DATA_PATH)
min_date, max_date = all_df["date"].min().date(), all_df["date"].max().date()
all_stations = sorted(all_df["station"].unique())

# ------------------------------------------------------------------ Sidebar
with st.sidebar:
    st.title("🌫️ Air Quality Beijing")
    st.caption("Data per jam dari 12 stasiun pemantauan, Mar 2013 – Feb 2017")

    date_range = st.date_input("Rentang waktu", value=[min_date, max_date],
                               min_value=min_date, max_value=max_date)
    if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = min_date, max_date

    region = st.radio("Wilayah", ["Semua", "Pusat Kota", "Pinggiran Kota"], horizontal=True)
    station_options = all_stations if region == "Semua" else sorted(
        all_df.loc[all_df["wilayah"] == region, "station"].unique())
    stations = st.multiselect("Stasiun", station_options, default=station_options)

    pollutant = st.selectbox("Polutan", POLLUTANTS, index=0,
                             help="Polutan yang ditampilkan pada tab Stasiun, Tren, dan Angin.")

    st.divider()
    st.markdown(
        "**Baku mutu harian (GB 3095-2012)**  \n"
        "PM2.5: 75 · PM10: 150 · SO2: 150 · NO2: 80 · CO: 4.000 µg/m³"
    )

if not stations:
    st.warning("Pilih minimal satu stasiun pada sidebar.")
    st.stop()

main_df = all_df[(all_df["date"] >= pd.Timestamp(start_date)) &
                 (all_df["date"] <= pd.Timestamp(end_date)) &
                 (all_df["station"].isin(stations))]
if main_df.empty:
    st.warning("Tidak ada data untuk filter yang dipilih.")
    st.stop()

daily_df = create_daily_df(main_df)
station_summary = create_station_summary(daily_df, pollutant)
std = DAILY_STANDARD[pollutant]

# ------------------------------------------------------------------ Header & KPI
st.title("Dashboard Kualitas Udara Beijing")
st.markdown(
    f"Periode **{start_date:%d %b %Y} – {end_date:%d %b %Y}** · **{len(stations)} stasiun** · "
    f"polutan **{pollutant}** (µg/m³)"
)

col1, col2, col3, col4 = st.columns(4)
mean_val = daily_df[pollutant].mean()
col1.metric(f"Rata-rata {pollutant}", f"{fmt(mean_val)} µg/m³",
            delta=None if std is None else f"{fmt(mean_val - std)} vs baku mutu", delta_color="inverse")
if std is not None:
    col2.metric("Hari melampaui baku mutu", f"{fmt((daily_df[pollutant] > std).mean() * 100)}%")
else:
    col2.metric("Hari melampaui baku mutu", "–", help="O3 tidak memiliki baku mutu rata-rata 24 jam.")
col3.metric("Stasiun tertinggi", station_summary.index[0], f"{fmt(station_summary['rata2'].iloc[0])} µg/m³",
            delta_color="off")
col4.metric("Hari kategori 'Berbahaya' (PM2.5)", f"{fmt((daily_df['kategori_aqi'] == 'Berbahaya').mean() * 100)}%")

tab1, tab2, tab3, tab4 = st.tabs(["📍 Perbandingan Stasiun", "📈 Tren & Pola Waktu",
                                  "💨 Pengaruh Angin", "🏷️ Kategori Kualitas Udara"])

# ------------------------------------------------------------------ Tab 1: Stasiun
with tab1:
    st.subheader(f"Stasiun mana yang memiliki {pollutant} tertinggi?")
    left, right = st.columns([1.15, 1])

    with left:
        plot_df = station_summary.sort_values("rata2")
        fig, ax = plt.subplots(figsize=(8, 0.5 * len(plot_df) + 1.5))
        colors = [HIGHLIGHT if s == plot_df["rata2"].idxmax() else BASE for s in plot_df.index]
        ax.barh(plot_df.index, plot_df["rata2"], color=colors)
        for i, v in enumerate(plot_df["rata2"]):
            ax.text(v, i, f" {v:,.1f}", va="center", fontsize=9)
        add_standard_line(ax, pollutant, orientation="v")
        ax.set_xlim(0, max(plot_df["rata2"].max(), std or 0) * 1.15)
        ax.set_xlabel(f"Rata-rata {pollutant} (µg/m³)")
        ax.set_title(f"Rata-rata {pollutant} per stasiun", fontsize=12)
        if std is not None:
            ax.legend(loc="lower right", fontsize=8)
        st.pyplot(fig)

        if std is not None:
            plot_ex = station_summary.sort_values("persen_hari_melampaui")
            fig, ax = plt.subplots(figsize=(8, 0.5 * len(plot_ex) + 1.5))
            colors = [HIGHLIGHT if s == plot_ex["persen_hari_melampaui"].idxmax() else BASE for s in plot_ex.index]
            ax.barh(plot_ex.index, plot_ex["persen_hari_melampaui"], color=colors)
            for i, v in enumerate(plot_ex["persen_hari_melampaui"]):
                ax.text(v, i, f" {v:.1f}%", va="center", fontsize=9)
            ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
            ax.set_xlim(0, max(plot_ex["persen_hari_melampaui"].max() * 1.15, 1))
            ax.set_xlabel("Persentase hari (%)")
            ax.set_title(f"Persentase hari dengan rata-rata {pollutant} > {std:,} µg/m³", fontsize=12)
            st.pyplot(fig)

    with right:
        st.markdown("**Peta sebaran** – ukuran & warna lingkaran = rata-rata konsentrasi")
        vmin, vmax = station_summary["rata2"].min(), station_summary["rata2"].max()
        span = (vmax - vmin) or 1
        cmap = plt.get_cmap("OrRd")
        fmap = folium.Map(location=[40.07, 116.40], zoom_start=9, tiles="OpenStreetMap")
        for st_name, row in station_summary.iterrows():
            lat, lon = STATION_COORDS[st_name]
            scale = (row["rata2"] - vmin) / span
            color = "#%02x%02x%02x" % tuple(int(c * 255) for c in cmap(0.3 + 0.7 * scale)[:3])
            popup = f"<b>{st_name}</b><br>Rata-rata {pollutant}: {row['rata2']:,.1f} µg/m³"
            if std is not None:
                popup += f"<br>Hari > baku mutu: {row['persen_hari_melampaui']:.1f}%"
            folium.CircleMarker([lat, lon], radius=8 + 14 * scale, color="#333333", weight=1,
                                fill=True, fill_color=color, fill_opacity=0.85,
                                tooltip=st_name, popup=folium.Popup(popup, max_width=250)).add_to(fmap)
        st_folium(fmap, height=520, use_container_width=True, returned_objects=[])

        table = station_summary.rename(columns={"rata2": "Rata-rata", "maks_harian": "Maks. harian",
                                                "total_hari": "Jumlah hari",
                                                "persen_hari_melampaui": "% hari > baku mutu"})
        table = table.join(main_df.groupby("station")["wilayah"].first())
        st.dataframe(table.style.format(precision=1), use_container_width=True)

    with st.expander("💡 Insight"):
        st.markdown(
            "- Stasiun **pusat kota** (Dongsi, Nongzhanguan, Wanshouxigong, Gucheng) secara konsisten memiliki PM2.5 "
            "tertinggi, sedangkan stasiun **pinggiran utara** (Dingling, Huairou, Changping) paling rendah.\n"
            "- Selama Mar 2013 – Feb 2017, **Dongsi** mencatat rata-rata PM2.5 tertinggi (86,1 µg/m³) dengan "
            "43,5% hari melampaui baku mutu → prioritas utama intervensi."
        )

# ------------------------------------------------------------------ Tab 2: Tren & pola waktu
with tab2:
    st.subheader(f"Bagaimana tren dan pola waktu {pollutant}?")

    monthly = main_df.set_index("datetime")[pollutant].resample("MS").mean()
    yearly = main_df.groupby("tahun_pemantauan")[pollutant].mean()

    c1, c2 = st.columns([1.6, 1])
    with c1:
        fig, ax = plt.subplots(figsize=(10, 4.3))
        ax.plot(monthly.index, monthly.values, color=ACCENT, marker="o", ms=3, lw=1.8, label="Rata-rata bulanan")
        ax.fill_between(monthly.index, monthly.values, alpha=0.1, color=ACCENT)
        add_standard_line(ax, pollutant)
        if not monthly.empty:
            peak = monthly.idxmax()
            ax.annotate(f"Puncak {peak:%b %Y}\n{monthly.max():,.1f}", xy=(peak, monthly.max()),
                        xytext=(10, -5), textcoords="offset points", fontsize=9, color=HIGHLIGHT)
            ax.scatter([peak], [monthly.max()], color=HIGHLIGHT, zorder=5)
        ax.set_ylim(0, None)
        ax.set_ylabel(f"{pollutant} (µg/m³)")
        ax.set_title(f"Tren rata-rata bulanan {pollutant}", fontsize=12)
        ax.legend(fontsize=8, loc="upper left")
        st.pyplot(fig)
    with c2:
        fig, ax = plt.subplots(figsize=(6, 4.3))
        bars = ax.bar(yearly.index, yearly.values, color=BASE)
        if len(yearly):
            bars[int(np.argmin(yearly.values))].set_color(ACCENT)
        changes = yearly.pct_change() * 100
        for i, (v, chg) in enumerate(zip(yearly.values, changes.values)):
            label = f"{v:,.1f}" if np.isnan(chg) else f"{v:,.1f}\n({chg:+.1f}%)"
            ax.text(i, v, label, ha="center", va="bottom", fontsize=9)
        add_standard_line(ax, pollutant)
        ax.set_ylim(0, max(yearly.max(), std or 0) * 1.3)
        ax.set_ylabel(f"{pollutant} (µg/m³)")
        ax.set_xlabel("Tahun pemantauan (Mar–Feb)")
        ax.set_title("Rata-rata per tahun pemantauan", fontsize=12)
        st.pyplot(fig)
        st.caption("Tahun pemantauan yang tidak penuh 12 bulan (akibat filter tanggal) perlu ditafsirkan hati-hati.")

    c3, c4 = st.columns(2)
    with c3:
        hourly_season = main_df.pivot_table(index="hour", columns="musim", values=pollutant,
                                            aggfunc="mean", observed=True)
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        for s in hourly_season.columns:
            ax.plot(hourly_season.index, hourly_season[s], color=SEASON_COLORS[s],
                    lw=3 if s == "Dingin" else 1.8, label=s)
        ax.plot(hourly_season.index, main_df.groupby("hour")[pollutant].mean(), color="black", ls=":", lw=2,
                label="Semua musim")
        add_standard_line(ax, pollutant)
        ax.set_xticks(range(0, 24, 2))
        ax.set_xlim(0, 23)
        ax.set_ylim(0, None)
        ax.set_xlabel("Jam (waktu lokal)")
        ax.set_ylabel(f"{pollutant} (µg/m³)")
        ax.set_title(f"Pola harian {pollutant} menurut musim", fontsize=12)
        ax.legend(fontsize=8, ncol=3, loc="lower left")
        st.pyplot(fig)
    with c4:
        heat = main_df.pivot_table(index="month", columns="hour", values=pollutant, aggfunc="mean")
        heat = heat.reindex([m for m in MONTH_ORDER if m in heat.index])
        fig, ax = plt.subplots(figsize=(7.5, 4.5))
        sns.heatmap(heat, cmap="Reds", ax=ax, cbar_kws={"label": f"{pollutant} (µg/m³)"})
        ax.set_yticklabels([MONTH_NAMES[MONTH_ORDER.index(m)] for m in heat.index], rotation=0)
        ax.set_xlabel("Jam (waktu lokal)")
        ax.set_ylabel("Bulan")
        ax.set_title(f"Heatmap rata-rata {pollutant} (bulan × jam)", fontsize=12)
        st.pyplot(fig)

    with st.expander("💡 Insight"):
        st.markdown(
            "- Rata-rata PM2.5 turun **16,3%** dari 2013/14 (87,0) ke 2015/16 (72,9 µg/m³), lalu naik lagi **7,2%** "
            "pada 2016/17 akibat episode haze Desember 2016 – Januari 2017.\n"
            "- PM2.5 tertinggi terjadi pada **musim dingin** (puncak **Desember**) dan pada **pukul 20.00–01.00**; "
            "terendah pada musim panas dan sekitar pukul 07.00."
        )

# ------------------------------------------------------------------ Tab 3: Angin
with tab3:
    st.subheader(f"Bagaimana kondisi angin memengaruhi {pollutant}?")
    ws = main_df.groupby("kategori_angin", observed=False)[pollutant].agg(["mean", "count"])
    ws["persen_jam"] = ws["count"] / ws["count"].sum() * 100
    wd = main_df.groupby("wd")[pollutant].mean().reindex(COMPASS)

    k1, k2, k3 = st.columns(3)
    calm, strong = ws.loc["Tenang (≤1)", "mean"], ws.loc["Kencang (>4)", "mean"]
    k1.metric("Rata-rata saat angin tenang (≤1 m/s)", f"{fmt(calm)} µg/m³")
    k2.metric("Rata-rata saat angin kencang (>4 m/s)", f"{fmt(strong)} µg/m³")
    if pd.notna(calm) and pd.notna(strong) and calm > 0:
        k3.metric("Penurunan saat angin kencang", f"{fmt((1 - strong / calm) * 100)}%")

    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(7.5, 5))
        colors = [HIGHLIGHT if i == int(np.nanargmax(ws["mean"].values)) else BASE for i in range(len(ws))]
        ax.bar(ws.index.astype(str), ws["mean"], color=colors)
        for i, (v, p) in enumerate(zip(ws["mean"], ws["persen_jam"])):
            if pd.notna(v):
                ax.text(i, v, f"{v:,.1f}\n({p:.0f}% jam)", ha="center", va="bottom", fontsize=9)
        add_standard_line(ax, pollutant)
        ax.set_ylim(0, max(np.nanmax(ws["mean"].values), std or 0) * 1.25)
        ax.set_xlabel("Kecepatan angin (m/s)")
        ax.set_ylabel(f"{pollutant} (µg/m³)")
        ax.set_title(f"Rata-rata {pollutant} menurut kecepatan angin", fontsize=12)
        ax.tick_params(axis="x", labelsize=8)
        if std is not None:
            ax.legend(fontsize=8)
        st.pyplot(fig)
    with c2:
        fig = plt.figure(figsize=(7.5, 5.4))
        ax = fig.add_subplot(projection="polar")
        theta = np.deg2rad(np.arange(0, 360, 22.5))
        vals = wd.values
        norm = plt.Normalize(np.nanmin(vals), np.nanmax(vals))
        ax.bar(theta, np.nan_to_num(vals), width=np.deg2rad(20), color=plt.cm.Reds(norm(np.nan_to_num(vals))),
               edgecolor="white")
        ax.set_theta_zero_location("N")
        ax.set_theta_direction(-1)
        ax.set_xticks(theta)
        ax.set_xticklabels(COMPASS, fontsize=9)
        ax.set_rlabel_position(225)
        ax.tick_params(axis="y", labelsize=8)
        ax.set_title(f"Rata-rata {pollutant} (µg/m³) menurut arah datangnya angin", fontsize=12, pad=18)
        fig.colorbar(plt.cm.ScalarMappable(cmap="Reds", norm=norm), ax=ax, pad=0.1, shrink=0.75,
                     label=f"{pollutant} (µg/m³)")
        st.pyplot(fig)

    with st.expander("💡 Insight"):
        st.markdown(
            "- PM2.5 saat **angin tenang (≤1 m/s)** rata-rata 101,9 µg/m³, sedangkan saat **angin kencang (>4 m/s)** "
            "hanya 28,7 µg/m³ (**72% lebih rendah**).\n"
            "- Angin dari **timur–tenggara** membawa PM2.5 tertinggi, sedangkan angin **barat laut** membersihkan udara. "
            "Prakiraan angin tenang / angin timur–tenggara dapat dijadikan pemicu peringatan dini."
        )

# ------------------------------------------------------------------ Tab 4: Kategori AQI (binning)
with tab4:
    st.subheader("Clustering (binning): kategori kualitas udara harian berdasarkan PM2.5")
    st.markdown(
        "Setiap hari di setiap stasiun dikelompokkan dengan `pd.cut` ke dalam kategori AQI China (HJ 633-2012) "
        "berdasarkan rata-rata PM2.5 harian: **Baik** (0–35), **Sedang** (35–75), **Tidak Sehat (Sensitif)** "
        "(75–115), **Tidak Sehat** (115–150), **Sangat Tidak Sehat** (150–250), **Berbahaya** (>250 µg/m³)."
    )

    overall = daily_df["kategori_aqi"].value_counts(normalize=True).reindex(AQI_LABELS).fillna(0) * 100
    cols = st.columns(len(AQI_LABELS))
    for col, label in zip(cols, AQI_LABELS):
        col.metric(label, f"{fmt(overall[label])}%")

    c1, c2 = st.columns([1.3, 1])
    with c1:
        by_station = pd.crosstab(daily_df["station"], daily_df["kategori_aqi"], normalize="index") * 100
        by_station = by_station.reindex(columns=AQI_LABELS, fill_value=0)
        by_station = by_station.loc[daily_df.groupby("station")["PM2.5"].mean().sort_values().index]
        fig, ax = plt.subplots(figsize=(8, 0.45 * len(by_station) + 1.8))
        by_station.plot(kind="barh", stacked=True, color=AQI_COLORS, ax=ax, width=0.8, legend=False)
        ax.xaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
        ax.set_xlim(0, 100)
        ax.set_xlabel("Persentase hari (%)")
        ax.set_ylabel(None)
        ax.set_title("Komposisi kategori harian per stasiun", fontsize=12)
        ax.legend(AQI_LABELS, loc="upper center", bbox_to_anchor=(0.5, -0.12), ncol=3, fontsize=8)
        st.pyplot(fig)
    with c2:
        by_season = pd.crosstab(daily_df["musim"], daily_df["kategori_aqi"], normalize="index") * 100
        by_season = by_season.reindex(columns=AQI_LABELS, fill_value=0)
        fig, ax = plt.subplots(figsize=(6, 5.6))
        by_season.plot(kind="bar", stacked=True, color=AQI_COLORS, ax=ax, width=0.7, legend=False, rot=0)
        ax.yaxis.set_major_formatter(mtick.PercentFormatter(decimals=0))
        ax.set_ylim(0, 100)
        ax.set_xlabel("Musim")
        ax.set_ylabel("Persentase hari (%)")
        ax.set_title("Komposisi kategori harian per musim", fontsize=12)
        st.pyplot(fig)

    with st.expander("💡 Insight"):
        st.markdown(
            "- Hanya sekitar **30% hari** berkategori *Baik*; ±40% hari berada pada kategori tidak sehat atau lebih buruk.\n"
            "- **Musim dingin** memiliki porsi hari *Berbahaya* terbesar, dan stasiun pusat kota memiliki hari *Baik* "
            "lebih sedikit dibanding pinggiran kota."
        )

st.divider()
st.caption("Sumber data: Beijing Multi-Site Air Quality Dataset (PRSA, 2013–2017) · "
           "Proyek Akhir Belajar Fundamental Analisis Data – Dicoding")
