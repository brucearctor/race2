"""race2 Streamlit analysis dashboard."""

import json
from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import streamlit as st

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="race2 · OBD Dashboard",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #0f1117; }
  [data-testid="stSidebar"] { background: #1a1d27; }
  .metric-card {
    background: linear-gradient(135deg, #1e2130, #252840);
    border: 1px solid #2e3250;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    margin-bottom: 0.5rem;
  }
  .metric-label { color: #8b92b8; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.08em; }
  .metric-value { color: #e8eaf6; font-size: 1.8rem; font-weight: 700; line-height: 1.1; }
  .metric-unit  { color: #5c6396; font-size: 0.8rem; }
  .warn { color: #ffb347; }
  .ok   { color: #69e08c; }
  .section-title {
    color: #8b92b8;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin: 1.5rem 0 0.5rem;
  }
</style>
""", unsafe_allow_html=True)

PLOT_THEME = dict(
    paper_bgcolor="#0f1117",
    plot_bgcolor="#0f1117",
    font_color="#c8cae8",
    xaxis=dict(gridcolor="#1e2130", showgrid=True),
    yaxis=dict(gridcolor="#1e2130", showgrid=True),
    margin=dict(l=10, r=10, t=30, b=10),
)

# ── Helpers ───────────────────────────────────────────────────────────────────

def load_csv(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["timestamp"])
    # Strip units from value strings if any got recorded
    for col in df.columns:
        if col == "timestamp":
            continue
        df[col] = pd.to_numeric(df[col].astype(str).str.extract(r"([-\d.]+)")[0], errors="coerce")
    return df


def load_snapshot(path: Path) -> dict:
    return json.loads(path.read_text())


def strip_unit(val: str | None) -> float | None:
    if not val:
        return None
    try:
        import re
        m = re.search(r"[-\d.]+", str(val))
        return float(m.group()) if m else None
    except Exception:
        return None


def metric_card(label: str, value, unit: str = "", warn: bool = False):
    cls = "warn" if warn else "ok"
    st.markdown(f"""
    <div class="metric-card">
      <div class="metric-label">{label}</div>
      <div class="metric-value {cls}">{value}</div>
      <div class="metric-unit">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("# 🏎️ race2")
    st.markdown("**OBD-II Analysis Dashboard**")
    st.divider()

    mode = st.radio("Data source", ["Live Recording (CSV)", "Snapshot (JSON)", "Demo Data"])
    st.divider()

    csv_file = None
    snap_file = None

    if mode == "Live Recording (CSV)":
        csvs = sorted(Path(".").glob("obd_live_*.csv")) + sorted(Path(".").glob("*.csv"))
        if csvs:
            chosen = st.selectbox("Select CSV", csvs, format_func=lambda p: p.name)
            csv_file = chosen
        else:
            st.warning("No CSV files found.\nRun `just record` first.")

    elif mode == "Snapshot (JSON)":
        snaps = sorted(Path(".").glob("obd_*.json")) + sorted(Path(".").glob("*.json"))
        if snaps:
            chosen = st.selectbox("Select snapshot", snaps, format_func=lambda p: p.name)
            snap_file = chosen
        else:
            st.warning("No JSON snapshots found.\nRun `just snapshot` first.")

    else:  # Demo
        from race2.sample_data import generate_sample_session
        import io
        rows = generate_sample_session()
        buf = io.StringIO()
        import csv as _csv
        w = _csv.DictWriter(buf, fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)
        buf.seek(0)
        csv_file = buf


# ── Main ──────────────────────────────────────────────────────────────────────
st.markdown("# 🏎️ race2 · Vehicle Analysis")

if csv_file is not None:
    df = load_csv(csv_file) if isinstance(csv_file, Path) else pd.read_csv(csv_file, parse_dates=["timestamp"])

    # KPI row
    st.markdown("## Latest Values")
    last = df.iloc[-1]
    c1, c2, c3, c4, c5, c6 = st.columns(6)

    with c1: metric_card("RPM", f"{last.get('RPM', 0):.0f}", "rpm")
    with c2: metric_card("Speed", f"{last.get('SPEED', 0):.0f}", "km/h")
    with c3: metric_card("Coolant", f"{last.get('COOLANT_TEMP', 0):.0f}", "°C",
                          warn=last.get("COOLANT_TEMP", 0) > 105)
    with c4: metric_card("Engine Load", f"{last.get('ENGINE_LOAD', 0):.1f}", "%")
    with c5:
        ltft = last.get("LONG_FUEL_TRIM_1", 0)
        metric_card("LTFT Bank 1", f"{ltft:+.1f}", "%", warn=abs(ltft) > 10)
    with c6:
        ltft2 = last.get("LONG_FUEL_TRIM_2", 0)
        metric_card("LTFT Bank 2", f"{ltft2:+.1f}", "%", warn=abs(ltft2) > 10)

    st.divider()

    # ── Tab layout ────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["⚙️ Engine", "⛽ Fuel Trims", "🔬 O2 Sensors", "📊 Full Overview"])

    with tab1:
        fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.06,
                            subplot_titles=("RPM", "Speed (km/h)", "Engine Load (%)"))
        t = df["timestamp"]
        fig.add_trace(go.Scatter(x=t, y=df["RPM"], line=dict(color="#7c83f5", width=1.5), name="RPM"), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=df["SPEED"], line=dict(color="#69e08c", width=1.5), name="Speed"), row=2, col=1)
        fig.add_trace(go.Scatter(x=t, y=df["ENGINE_LOAD"], line=dict(color="#ffb347", width=1.5), name="Load"), row=3, col=1)
        fig.update_layout(height=500, showlegend=False, **PLOT_THEME)
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)
        with col1:
            fig2 = px.scatter(df, x="RPM", y="ENGINE_LOAD", color="SPEED",
                              color_continuous_scale="Viridis", title="RPM vs Load (colored by Speed)")
            fig2.update_layout(**PLOT_THEME)
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            fig3 = px.line(df, x="timestamp", y=["COOLANT_TEMP", "INTAKE_TEMP"],
                           title="Temperatures (°C)", color_discrete_sequence=["#ff6b6b", "#ffa94d"])
            fig3.update_layout(**PLOT_THEME)
            st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.markdown("""
        > **⚠️ Both banks showing ~+18% LTFT** — the ECU has learned to consistently add 18% more fuel
        > than the base map expects. This indicates a lean condition. Likely causes: dirty MAF sensor or vacuum leak.
        """)
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True, vertical_spacing=0.08,
                            subplot_titles=("Short-Term Fuel Trim (Bank 1 & 2) — real-time correction",
                                            "Long-Term Fuel Trim (Bank 1 & 2) — learned correction"))
        t = df["timestamp"]
        fig.add_trace(go.Scatter(x=t, y=df.get("SHORT_FUEL_TRIM_1"), name="STFT B1",
                                  line=dict(color="#7c83f5")), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=df.get("SHORT_FUEL_TRIM_2"), name="STFT B2",
                                  line=dict(color="#69e08c")), row=1, col=1)
        fig.add_trace(go.Scatter(x=t, y=df.get("LONG_FUEL_TRIM_1"), name="LTFT B1",
                                  line=dict(color="#ff6b6b", width=2)), row=2, col=1)
        fig.add_trace(go.Scatter(x=t, y=df.get("LONG_FUEL_TRIM_2"), name="LTFT B2",
                                  line=dict(color="#ffb347", width=2)), row=2, col=1)
        # ±10% bands
        for row in [1, 2]:
            fig.add_hrect(y0=-10, y1=10, fillcolor="#69e08c", opacity=0.05,
                          annotation_text="Normal ±10%", row=row, col=1)
        fig.update_layout(height=500, **PLOT_THEME)
        st.plotly_chart(fig, use_container_width=True)

        # STFT distribution
        col1, col2 = st.columns(2)
        with col1:
            fig4 = px.histogram(df, x="SHORT_FUEL_TRIM_1", nbins=30,
                                title="STFT Bank 1 Distribution", color_discrete_sequence=["#7c83f5"])
            fig4.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
            fig4.update_layout(**PLOT_THEME)
            st.plotly_chart(fig4, use_container_width=True)
        with col2:
            fig5 = px.histogram(df, x="SHORT_FUEL_TRIM_2", nbins=30,
                                title="STFT Bank 2 Distribution", color_discrete_sequence=["#69e08c"])
            fig5.add_vline(x=0, line_dash="dash", line_color="white", opacity=0.5)
            fig5.update_layout(**PLOT_THEME)
            st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        if "O2_B1S1" in df.columns:
            fig = px.line(df, x="timestamp", y="O2_B1S1",
                          title="O2 Bank 1 Sensor 1 (upstream) — should switch 0.1–0.9V in closed loop",
                          color_discrete_sequence=["#ff6b6b"])
            fig.add_hrect(y0=0.1, y1=0.9, fillcolor="#69e08c", opacity=0.05,
                          annotation_text="Normal switching range")
            fig.update_layout(**PLOT_THEME)
            st.plotly_chart(fig, use_container_width=True)

            # Switching frequency analysis
            if df["O2_B1S1"].std() > 0.05:
                crossings = ((df["O2_B1S1"] > 0.45).astype(int).diff().abs() > 0).sum()
                duration_s = (df["timestamp"].max() - df["timestamp"].min()).total_seconds()
                hz = crossings / duration_s if duration_s > 0 else 0
                col1, col2, col3 = st.columns(3)
                with col1: metric_card("O2 Switch Rate", f"{hz:.2f}", "Hz (healthy: 0.5–2 Hz)", warn=hz < 0.3)
                with col2: metric_card("O2 Min", f"{df['O2_B1S1'].min():.3f}", "V")
                with col3: metric_card("O2 Max", f"{df['O2_B1S1'].max():.3f}", "V")
            else:
                st.info("O2 sensor appears static — engine may not have been in closed loop. Start engine and let fully warm up.")
        else:
            st.info("No O2 data in this recording.")

    with tab4:
        numeric = df.select_dtypes(include="number")
        available = [c for c in numeric.columns if c != "timestamp"]
        selected = st.multiselect("Channels to plot", available,
                                   default=[c for c in ["RPM", "SPEED", "ENGINE_LOAD", "COOLANT_TEMP"] if c in available])
        if selected:
            fig = px.line(df, x="timestamp", y=selected,
                          color_discrete_sequence=px.colors.qualitative.Bold)
            fig.update_layout(height=400, **PLOT_THEME)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Session Statistics")
        st.dataframe(
            numeric.describe().T.style.format("{:.2f}").background_gradient(cmap="Blues"),
            use_container_width=True,
        )

elif snap_file is not None:
    snap = load_snapshot(snap_file)
    st.markdown(f"### Snapshot · `{snap_file.name}`")
    st.markdown(f"**Captured:** {snap.get('timestamp', 'N/A')}")

    dtcs = snap.get("dtcs", [])
    if dtcs:
        st.error(f"⚠️ {len(dtcs)} DTC(s) found: {', '.join(dtcs)}")
    else:
        st.success("✅ No diagnostic trouble codes")

    sensors = snap.get("sensors", {})
    rows = [{"Sensor": k, "Value": v or "N/A"} for k, v in sensors.items()]
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

else:
    st.info("👈 Select a data source in the sidebar to get started.\n\nRun `just record` to capture live data, or choose **Demo Data** to explore.")
    st.markdown("""
    ### Getting started
    ```bash
    # In your car, engine running:
    just record --duration 300   # 5-minute session → CSV

    # Then open this dashboard:
    just dashboard
    ```
    """)
