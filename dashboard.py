"""
AgriRisk-Sat | Module 5: Interactive Dashboard
===============================================
FIXES APPLIED:
  1. TypeError line 488: fill_between() got multiple values for 'where'
     CAUSE:  ax.fill_between(x, y1, y2, where=[...])  — matplotlib's
             fill_between signature is fill_between(x, y1, y2=0, ...)
             so the 4th positional arg was being interpreted as 'where'
             AND we also passed where= as a keyword → conflict.
     FIX:    Draw each gauge segment as a filled polygon using
             ax.fill() instead of fill_between(). Much simpler.

  2. DeprecationWarning: use_column_width → use_container_width

  3. DeprecationWarning: st.image with placeholder URL
     FIX:    Replaced with st.markdown styled header.

Run: streamlit run dashboard.py
"""

import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import seaborn as sns
from datetime import datetime, timedelta
import json

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="AgriRisk-Sat | Crop Loss Intelligence",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Space Grotesk', sans-serif; }
    .alert-extreme  { background:#ff000033; border:1px solid #ff4444; border-radius:8px; padding:10px; }
    .alert-high     { background:#ff660033; border:1px solid #ff8800; border-radius:8px; padding:10px; }
    .alert-moderate { background:#ffff0022; border:1px solid #ffcc00; border-radius:8px; padding:10px; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# DATA
# ─────────────────────────────────────────────
@st.cache_data
def load_district_data():
    np.random.seed(42)
    districts_by_state = {
        'Gujarat':     ['Anand','Kheda','Vadodara','Surat','Rajkot','Amreli',
                        'Junagadh','Kutch','Banaskantha','Patan'],
        'Maharashtra': ['Akola','Amravati','Yavatmal','Washim','Buldhana',
                        'Latur','Osmanabad','Solapur','Nashik','Ahmednagar'],
        'MP':          ['Indore','Dewas','Ujjain','Sehore','Hoshangabad',
                        'Narsinghpur','Chhindwara','Betul','Vidisha','Raisen']
    }
    rows = []
    for state, dists in districts_by_state.items():
        for dist in dists:
            for year in range(2018, 2024):
                vci_deficit = np.random.beta(2, 3) * 100
                flood_days  = np.random.exponential(5) * np.random.choice([0,1], p=[0.55,0.45])
                heat_days   = np.random.poisson(6)
                vci_norm    = vci_deficit / 100
                flood_norm  = min(flood_days / 40, 1.0)
                heat_norm   = min(heat_days / 20, 1.0)
                cli         = (0.45*vci_norm + 0.35*flood_norm + 0.20*heat_norm) * 100
                pmfby       = max(0, cli * 28 + np.random.normal(0, 120))
                rows.append({
                    'state': state, 'district': dist, 'year': year,
                    'crop': np.random.choice(['Cotton','Groundnut','Soybean','Wheat']),
                    'CLI': round(cli, 1),
                    'vci_deficit': round(vci_deficit, 1),
                    'flood_days': round(float(flood_days), 1),
                    'heat_stress_days': heat_days,
                    'pmfby_claims_per_ha': round(max(0, pmfby), 1),
                    'insured_area_ha': round(np.random.uniform(5000, 80000), 0),
                    'rainfall_anomaly_mm': round(np.random.normal(-18, 75), 1),
                    'soil_moisture_pct': round(np.random.uniform(8, 45), 1),
                    'lst_max_c': round(np.random.normal(36, 5), 1),
                })
    return pd.DataFrame(rows)

@st.cache_data
def get_current_alerts():
    return pd.DataFrame([
        {'district':'Amreli',     'state':'Gujarat',     'stress':'Drought',  'severity':'Extreme',  'vci':18, 'alert_date': datetime.now()-timedelta(days=2)},
        {'district':'Yavatmal',   'state':'Maharashtra', 'stress':'Drought',  'severity':'Severe',   'vci':22, 'alert_date': datetime.now()-timedelta(days=1)},
        {'district':'Latur',      'state':'Maharashtra', 'stress':'Heatwave', 'severity':'High',     'vci':31, 'alert_date': datetime.now()-timedelta(days=3)},
        {'district':'Kutch',      'state':'Gujarat',     'stress':'Drought',  'severity':'Moderate', 'vci':34, 'alert_date': datetime.now()-timedelta(days=5)},
        {'district':'Hoshangabad','state':'MP',          'stress':'Flood',    'severity':'High',     'vci':55, 'alert_date': datetime.now()-timedelta(days=1)},
        {'district':'Betul',      'state':'MP',          'stress':'Flood',    'severity':'Moderate', 'vci':48, 'alert_date': datetime.now()-timedelta(days=4)},
        {'district':'Osmanabad',  'state':'Maharashtra', 'stress':'Drought',  'severity':'High',     'vci':27, 'alert_date': datetime.now()-timedelta(days=2)},
        {'district':'Rajkot',     'state':'Gujarat',     'stress':'Heatwave', 'severity':'Moderate', 'vci':42, 'alert_date': datetime.now()-timedelta(days=6)},
    ])

df        = load_district_data()
alerts_df = get_current_alerts()

# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    # FIX 2: replaced use_column_width with use_container_width
    st.markdown("## 🛰️ AgriRisk-Sat")
    st.markdown("### 🎛️ Dashboard Controls")

    selected_state = st.selectbox("State", ['All States','Gujarat','Maharashtra','MP'])
    selected_year  = st.slider("Kharif Season Year", 2018, 2023, 2023)
    selected_crop  = st.multiselect("Crop Type",
                                    ['Cotton','Groundnut','Soybean','Wheat'],
                                    default=['Cotton','Groundnut','Soybean','Wheat'])
    cli_threshold  = st.slider("CLI Alert Threshold", 20, 80, 40,
                               help="Districts above this CLI flagged as high-risk")

    st.markdown("---")
    st.markdown("### 💰 Payout Simulator")
    max_payout_rate = st.number_input("Sum Insured (₹/ha)", 1000, 8000, 3500, 500)
    trigger_thresh  = st.number_input("Trigger Threshold (CLI)", 10, 50, 25, 5)

    st.markdown("---")
    st.markdown("### 📡 Data Sources")
    st.markdown("""
- 🛰️ **Sentinel-2** MSI (NDVI/VCI)
- 📡 **Sentinel-1** SAR (Floods)
- 🌡️ **Landsat 9** LST (Heat)
- 🌧️ **CHIRPS** Rainfall
- 💧 **SMAP** Soil Moisture
- 🌍 **ERA5-Land** Temperature
""")
    st.caption(f"Last updated: {datetime.now().strftime('%d %b %Y, %H:%M IST')}")

# ─────────────────────────────────────────────
# FILTER
# ─────────────────────────────────────────────
filtered = df[df['year'] == selected_year].copy()
if selected_state != 'All States':
    filtered = filtered[filtered['state'] == selected_state]
if selected_crop:
    filtered = filtered[filtered['crop'].isin(selected_crop)]

# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown("# 🛰️ AgriRisk-Sat")
st.markdown("### Satellite-Driven Crop Stress & Agricultural Loss Intelligence")
c1, c2, c3 = st.columns(3)
with c1: st.info(f"📅 Season: Kharif {selected_year}")
with c2: st.info(f"🗺️ Coverage: {selected_state}")
with c3: st.success("🟢 Pipeline: Active")
st.markdown("---")

# ─────────────────────────────────────────────
# ALERTS
# ─────────────────────────────────────────────
st.markdown("## 🚨 Real-Time Stress Alerts")
severity_icons = {'Extreme':'🔴','Severe':'🟠','High':'🟡','Moderate':'🔵'}
cols_alert = st.columns(min(len(alerts_df), 4))
for i, (_, alert) in enumerate(alerts_df.iterrows()):
    if i < 4:
        with cols_alert[i]:
            icon = severity_icons.get(alert['severity'], '⚪')
            st.metric(
                label=f"{icon} {alert['district']}, {alert['state']}",
                value=str(alert['stress']),
                delta=f"{alert['severity']} | VCI={alert['vci']}"
            )
if len(alerts_df) > 4:
    with st.expander(f"📋 Show all {len(alerts_df)} active alerts"):
        st.dataframe(
            alerts_df[['district','state','stress','severity','vci','alert_date']],
            use_container_width=True
        )
st.markdown("---")

# ─────────────────────────────────────────────
# METRICS ROW
# ─────────────────────────────────────────────
st.markdown(f"## 📊 Season Summary — Kharif {selected_year}")
m1, m2, m3, m4, m5 = st.columns(5)
with m1: st.metric("Avg CLI",            f"{filtered['CLI'].mean():.1f}",
                    delta=f"±{filtered['CLI'].std():.1f} std")
with m2: st.metric("High-Risk Districts", f"{(filtered['CLI']>cli_threshold).sum()}",
                    delta=f"of {len(filtered)} total")
with m3: st.metric("Avg VCI Deficit",    f"{filtered['vci_deficit'].mean():.1f}%",
                    delta="drought proxy")
with m4: st.metric("Avg Flood Days",     f"{filtered['flood_days'].mean():.1f}",
                    delta="per district")
with m5: st.metric("Avg PMFBY Claims",   f"₹{filtered['pmfby_claims_per_ha'].mean():.0f}/ha",
                    delta="estimated")
st.markdown("---")

# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs(
    ["🗺️ CLI Map", "📈 Trend Analysis", "🌾 Crop Comparison", "💰 Payout Simulator"]
)

# ══════════════ TAB 1: CLI MAP ══════════════
with tab1:
    col1, col2 = st.columns([2, 1])

    with col1:
        st.markdown("### 🗺️ District CLI Risk Map")
        fig, ax = plt.subplots(figsize=(10, 7))
        fig.patch.set_facecolor('#0a0a1a')
        ax.set_facecolor('#0a0a1a')

        states_list = ['Gujarat','Maharashtra','MP'] if selected_state == 'All States' \
                      else [selected_state]
        grid_data, grid_labels = [], []
        for sn in states_list:
            sd = filtered[filtered['state']==sn].sort_values('CLI', ascending=False)
            if sd.empty:
                sd = df[(df['state']==sn)&(df['year']==selected_year)].sort_values('CLI', ascending=False)
            grid_data.append(sd['CLI'].values[:10])
            grid_labels.append(sd['district'].values[:10])

        grid_arr = np.array(grid_data)
        cmap = mcolors.LinearSegmentedColormap.from_list(
            'cli', ['#1a9850','#91cf60','#fee08b','#fc8d59','#d73027','#7f0000'])
        im = ax.imshow(grid_arr, cmap=cmap, vmin=0, vmax=100, aspect='auto')
        ax.set_xticks(range(grid_arr.shape[1]))
        ax.set_xticklabels(grid_labels[0] if grid_labels else [],
                           rotation=45, ha='right', fontsize=9, color='white')
        ax.set_yticks(range(len(states_list)))
        ax.set_yticklabels(states_list, color='white', fontsize=11, fontweight='bold')
        for i in range(grid_arr.shape[0]):
            for j in range(grid_arr.shape[1]):
                val = grid_arr[i, j] if j < len(grid_arr[i]) else 0
                ax.text(j, i, f'{val:.0f}', ha='center', va='center',
                        fontsize=9, color='white' if val > 50 else 'black', fontweight='bold')
        plt.colorbar(im, ax=ax, label='CLI', shrink=0.8)
        ax.set_title(f'District CLI Risk Map — Kharif {selected_year}',
                     color='white', fontsize=13, pad=15)
        ax.tick_params(colors='white')
        for sp in ax.spines.values(): sp.set_edgecolor('#0f3460')
        plt.tight_layout()
        st.pyplot(fig); plt.close()

    with col2:
        st.markdown("### 📋 Risk Classification")
        risk_dist = pd.cut(filtered['CLI'], bins=[0,20,40,60,80,100],
                           labels=['Low','Moderate','High','Severe','Extreme']
                           ).value_counts()
        risk_colors = {'Extreme':'#7f0000','Severe':'#d73027','High':'#fc8d59',
                       'Moderate':'#fee08b','Low':'#1a9850'}
        fig2, ax2 = plt.subplots(figsize=(5, 4))
        fig2.patch.set_facecolor('#0a0a1a'); ax2.set_facecolor('#0a0a1a')
        bars = ax2.barh(risk_dist.index, risk_dist.values,
                        color=[risk_colors.get(r,'gray') for r in risk_dist.index])
        ax2.set_xlabel('Number of Districts', color='white')
        ax2.tick_params(colors='white')
        for sp in ['top','right']: ax2.spines[sp].set_visible(False)
        for sp in ['bottom','left']: ax2.spines[sp].set_color('#0f3460')
        for bar, val in zip(bars, risk_dist.values):
            ax2.text(val+0.2, bar.get_y()+bar.get_height()/2, str(val),
                     va='center', color='white', fontweight='bold')
        ax2.set_title('Risk Category Distribution', color='white')
        st.pyplot(fig2); plt.close()

        st.markdown("### ⚠️ Top Risk Districts")
        top5 = filtered.nlargest(5, 'CLI')[['district','state','CLI','crop']].reset_index(drop=True)
        top5.index += 1
        st.dataframe(top5, use_container_width=True)

# ══════════════ TAB 2: TREND ══════════════
with tab2:
    st.markdown("### 📈 Multi-Year CLI & PMFBY Trend")
    trend = df.groupby('year').agg(
        CLI=('CLI','mean'), claims=('pmfby_claims_per_ha','mean'),
        drought=('vci_deficit','mean'), flood=('flood_days','mean')
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig3, ax3 = plt.subplots(figsize=(8, 5))
        ax3b = ax3.twinx()
        fig3.patch.set_facecolor('#0a0a1a'); ax3.set_facecolor('#0a0a1a')
        ax3.plot(trend['year'], trend['CLI'], 'o-', color='#e94560',
                 linewidth=2.5, markersize=8, label='Avg CLI', zorder=5)
        ax3.fill_between(trend['year'], trend['CLI']-5, trend['CLI']+5,
                         alpha=0.15, color='#e94560')
        ax3b.plot(trend['year'], trend['claims'], 's--', color='#64ffda',
                  linewidth=2, markersize=7, label='PMFBY Claims')
        ax3.set_xlabel('Year', color='white')
        ax3.set_ylabel('Crop Loss Index', color='#e94560')
        ax3b.set_ylabel('PMFBY Claims (₹/ha)', color='#64ffda')
        ax3.set_title('CLI vs PMFBY Claims Trend', color='white', fontsize=12)
        for sp in ax3.spines.values(): sp.set_edgecolor('#0f3460')
        ax3.tick_params(colors='white'); ax3b.tick_params(colors='#64ffda')
        lines = ax3.get_legend_handles_labels()[0] + ax3b.get_legend_handles_labels()[0]
        labs  = ax3.get_legend_handles_labels()[1] + ax3b.get_legend_handles_labels()[1]
        ax3.legend(lines, labs, facecolor='#0f3460', labelcolor='white')
        ax3.grid(True, alpha=0.1, color='white')
        st.pyplot(fig3); plt.close()

    with col2:
        fig4, ax4 = plt.subplots(figsize=(8, 5))
        fig4.patch.set_facecolor('#0a0a1a'); ax4.set_facecolor('#0a0a1a')
        years = trend['year'].values
        np.random.seed(0)
        ax4.stackplot(years,
                      trend['drought'].values * 0.45,
                      trend['flood'].values * 0.35 / 40 * 100,
                      np.random.uniform(3, 8, len(years)),
                      labels=['Drought (VCI)','Flood (SAR)','Heat (LST)'],
                      colors=['#FF6B6B','#4ECDC4','#FFE66D'], alpha=0.85)
        ax4.set_xlabel('Year', color='white')
        ax4.set_ylabel('CLI Component Contribution', color='white')
        ax4.set_title('Stress Driver Decomposition', color='white', fontsize=12)
        ax4.tick_params(colors='white')
        for sp in ax4.spines.values(): sp.set_edgecolor('#0f3460')
        ax4.legend(facecolor='#0f3460', labelcolor='white')
        ax4.grid(True, alpha=0.1)
        st.pyplot(fig4); plt.close()

    st.markdown("### 🌵 VCI Dekadal Profile (Current Season)")
    np.random.seed(selected_year)
    dekads = np.arange(1, 19)
    vci_profile = np.clip(45 + 25*np.sin(np.pi*dekads/18) + np.random.normal(0,5,18), 0, 100)
    fig5, ax5 = plt.subplots(figsize=(14, 4))
    fig5.patch.set_facecolor('#0a0a1a'); ax5.set_facecolor('#0a0a1a')
    ax5.plot(dekads, vci_profile, 'o-', color='#64ffda', linewidth=2, markersize=6)
    ax5.axhline(35, color='#FF6B6B', linestyle='--', linewidth=1.5, label='Drought threshold (35)')
    ax5.fill_between(dekads, vci_profile, 35, where=(vci_profile < 35),
                     alpha=0.3, color='#FF6B6B', label='Drought stress', interpolate=True)
    ax5.fill_between(dekads, vci_profile, alpha=0.1, color='#64ffda')
    month_labels = ['Jun D1','Jun D2','Jun D3','Jul D1','Jul D2','Jul D3',
                    'Aug D1','Aug D2','Aug D3','Sep D1','Sep D2','Sep D3',
                    'Oct D1','Oct D2','Oct D3','Nov D1','Nov D2','Nov D3']
    ax5.set_xticks(dekads)
    ax5.set_xticklabels(month_labels, rotation=45, ha='right', fontsize=8, color='white')
    ax5.set_ylabel('VCI (%)', color='white'); ax5.tick_params(colors='white')
    ax5.set_title(f'VCI Dekadal Profile | Kharif {selected_year}', color='white')
    for sp in ax5.spines.values(): sp.set_edgecolor('#0f3460')
    ax5.legend(facecolor='#0f3460', labelcolor='white')
    ax5.grid(True, alpha=0.1)
    st.pyplot(fig5); plt.close()

# ══════════════ TAB 3: CROP COMPARISON ══════════════
with tab3:
    st.markdown("### 🌾 Crop-Type Stress Profile")
    crop_stats = filtered.groupby('crop').agg(
        CLI=('CLI','mean'), VCI=('vci_deficit','mean'),
        Flood=('flood_days','mean'), Heat=('heat_stress_days','mean')
    ).reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig6, ax6 = plt.subplots(figsize=(7, 5))
        fig6.patch.set_facecolor('#0a0a1a'); ax6.set_facecolor('#0a0a1a')
        x = np.arange(len(crop_stats)); w = 0.25
        ax6.bar(x-w, crop_stats['VCI']/100*50, width=w, label='Drought', color='#FF6B6B', alpha=0.85)
        ax6.bar(x,   crop_stats['Flood'],       width=w, label='Flood (days)', color='#4ECDC4', alpha=0.85)
        ax6.bar(x+w, crop_stats['Heat'],        width=w, label='Heat (days)', color='#FFE66D', alpha=0.85)
        ax6.set_xticks(x); ax6.set_xticklabels(crop_stats['crop'], color='white', fontweight='bold')
        ax6.set_ylabel('Stress Magnitude', color='white'); ax6.tick_params(colors='white')
        ax6.set_title('Stress by Crop Type', color='white')
        for sp in ax6.spines.values(): sp.set_edgecolor('#0f3460')
        ax6.legend(facecolor='#0f3460', labelcolor='white')
        ax6.grid(True, alpha=0.1, axis='y')
        st.pyplot(fig6); plt.close()

    with col2:
        fig7, ax7 = plt.subplots(figsize=(7, 5))
        fig7.patch.set_facecolor('#0a0a1a'); ax7.set_facecolor('#0a0a1a')
        crop_colors = {'Cotton':'#FF6B6B','Groundnut':'#FFE66D',
                       'Soybean':'#4ECDC4','Wheat':'#A8E6CF'}
        for crop_name in crop_stats['crop']:
            subset = filtered[filtered['crop']==crop_name]
            ax7.scatter(subset['vci_deficit'], subset['CLI'],
                        alpha=0.4, s=30, c=crop_colors.get(crop_name,'gray'), label=crop_name)
        ax7.axhline(cli_threshold, color='#e94560', linestyle='--',
                    alpha=0.7, label=f'CLI Alert ({cli_threshold})')
        ax7.set_xlabel('VCI Deficit (%)', color='white')
        ax7.set_ylabel('CLI', color='white')
        ax7.set_title('CLI vs Drought Severity by Crop', color='white')
        ax7.tick_params(colors='white')
        for sp in ax7.spines.values(): sp.set_edgecolor('#0f3460')
        ax7.legend(facecolor='#0f3460', labelcolor='white', markerscale=2)
        ax7.grid(True, alpha=0.1)
        st.pyplot(fig7); plt.close()

    st.markdown("### 📅 Crop Phenology Calendar")
    ph_df = pd.DataFrame({
        'Crop': ['Cotton','Groundnut','Soybean','Wheat'],
        'Sowing': ['Jun 1-15','Jun 15-30','Jun 15-Jul 1','Nov 1-15'],
        'Vegetative': ['Jun-Aug','Jun-Jul','Jun-Jul','Nov-Dec'],
        'Anthesis/Flowering': ['Aug-Sep','Jul-Aug','Jul-Aug','Jan-Feb'],
        'Grain Fill/Boll': ['Sep-Oct','Aug-Sep','Aug-Sep','Feb-Mar'],
        'Harvest': ['Nov-Dec','Sep-Oct','Sep-Oct','Mar-Apr'],
        'Key Stress Window': ['Aug-Sep (drought/heat)','Jul-Aug (drought)',
                              'Jul (flood)','Feb (frost/heat)']
    })
    st.dataframe(ph_df, use_container_width=True, hide_index=True)

# ══════════════ TAB 4: PAYOUT SIMULATOR ══════════════
with tab4:
    st.markdown("### 💰 PMFBY Insurance Payout Simulator")
    st.info("Simulates payouts based on satellite-derived CLI. Adjust trigger threshold and sum insured in the sidebar.")

    col1, col2 = st.columns(2)

    with col1:
        district_list = sorted(filtered['district'].unique())
        if not district_list:
            st.warning("No districts found for current filter. Adjust state/crop/year.")
            st.stop()

        selected_dist = st.selectbox("Select District", district_list)
        mask      = filtered['district'] == selected_dist
        dist_data = filtered[mask].iloc[0] if mask.any() else filtered.iloc[0]

        cli_val      = float(dist_data['CLI'])
        insured_area = float(dist_data['insured_area_ha'])
        crop_type    = dist_data['crop']

        st.markdown(f"**District:** {selected_dist} | **State:** {dist_data['state']}")
        st.markdown(f"**Dominant Crop:** {crop_type} | **Insured Area:** {insured_area:,.0f} ha")

        # ── GAUGE — FIXED ────────────────────────────────
        # FIX: use ax.fill() with polygon vertices instead of
        # fill_between() which caused the "multiple values for where" error.
        fig8, ax8 = plt.subplots(figsize=(6, 4))
        fig8.patch.set_facecolor('#0a0a1a')
        ax8.set_facecolor('#0a0a1a')

        # Draw 5 coloured arc segments as filled wedges
        segments = [(0, 20, '#1a9850'), (20, 40, '#91cf60'),
                    (40, 60, '#fee08b'), (60, 80, '#fc8d59'), (80, 100, '#d73027')]

        for lo, hi, clr in segments:
            # Convert CLI range → angle range (0=left π, 100=right 0)
            a_lo = np.pi * (1 - hi / 100)   # note: reversed so 0 is left
            a_hi = np.pi * (1 - lo / 100)
            t    = np.linspace(a_lo, a_hi, 40)

            # Build ring polygon: outer arc then inner arc reversed
            outer_x = np.cos(t) * 1.0
            outer_y = np.sin(t) * 1.0
            inner_x = np.cos(t[::-1]) * 0.65
            inner_y = np.sin(t[::-1]) * 0.65

            xs = np.concatenate([outer_x, inner_x])
            ys = np.concatenate([outer_y, inner_y])
            ax8.fill(xs, ys, color=clr, alpha=0.90)

        # Needle
        angle = np.pi * (1 - cli_val / 100)
        ax8.annotate(
            '', xy=(np.cos(angle)*0.80, np.sin(angle)*0.80),
            xytext=(0, 0),
            arrowprops=dict(arrowstyle='->', color='white', lw=2.5)
        )
        ax8.plot(0, 0, 'o', color='white', markersize=6, zorder=5)

        risk_label = ('Extreme' if cli_val > 80 else 'Severe' if cli_val > 60
                      else 'High' if cli_val > 40 else 'Moderate' if cli_val > 20 else 'Low')
        ax8.text(0, -0.15, f'CLI = {cli_val:.1f}', ha='center', va='center',
                 fontsize=18, color='white', fontweight='bold')
        ax8.text(0, -0.38, f'Risk: {risk_label}', ha='center',
                 fontsize=12, color='#e94560')

        ax8.set_xlim(-1.25, 1.25)
        ax8.set_ylim(-0.55, 1.15)
        ax8.axis('off')
        ax8.set_title(f'CLI Risk Gauge — {selected_dist}', color='white', fontsize=12)
        st.pyplot(fig8); plt.close()

    with col2:
        # Payout calculation
        if cli_val > trigger_thresh:
            payout_pct    = min((cli_val - trigger_thresh) / (100 - trigger_thresh), 1.0)
            payout_per_ha = payout_pct * max_payout_rate
            total_payout  = payout_per_ha * insured_area / 1e7
        else:
            payout_pct = payout_per_ha = total_payout = 0.0

        st.markdown("#### 💳 Payout Calculation")
        ca, cb = st.columns(2)
        with ca:
            st.metric("CLI Score",     f"{cli_val:.1f}/100")
            st.metric("Payout %",      f"{payout_pct*100:.1f}%")
            st.metric("Payout per Ha", f"₹{payout_per_ha:,.0f}")
        with cb:
            st.metric("Trigger Threshold", f"{trigger_thresh}")
            st.metric("Insured Area",       f"{insured_area:,.0f} ha")
            st.metric("Total Payout",       f"₹{total_payout:.2f} Cr")

        if cli_val > trigger_thresh:
            st.success(f"✅ Payout TRIGGERED — CLI ({cli_val:.1f}) > Threshold ({trigger_thresh})")
        else:
            st.warning(f"❌ No payout — CLI ({cli_val:.1f}) ≤ Threshold ({trigger_thresh})")

        st.markdown("#### 📊 CLI Sensitivity Analysis")
        cli_range = np.linspace(0, 100, 200)
        payouts   = [max(0, min((c-trigger_thresh)/(100-trigger_thresh), 1)) * max_payout_rate
                     for c in cli_range]
        fig9, ax9 = plt.subplots(figsize=(6, 3))
        fig9.patch.set_facecolor('#0a0a1a'); ax9.set_facecolor('#0a0a1a')
        ax9.plot(cli_range, payouts, color='#64ffda', linewidth=2)
        ax9.axvline(cli_val,       color='#e94560', linestyle='--', label=f'Current CLI={cli_val:.1f}')
        ax9.axvline(trigger_thresh,color='orange',  linestyle=':',  label=f'Trigger={trigger_thresh}')
        ax9.fill_between(cli_range, payouts, alpha=0.15, color='#64ffda')
        ax9.set_xlabel('CLI', color='white'); ax9.set_ylabel('Payout (₹/ha)', color='white')
        ax9.tick_params(colors='white')
        for sp in ax9.spines.values(): sp.set_edgecolor('#0f3460')
        ax9.legend(facecolor='#0f3460', labelcolor='white', fontsize=8)
        ax9.grid(True, alpha=0.1)
        st.pyplot(fig9); plt.close()

    st.markdown("### 📋 All Districts — Payout Estimates")
    filtered2 = filtered.copy()
    filtered2['payout_triggered'] = filtered2['CLI'] > trigger_thresh
    filtered2['payout_per_ha']    = filtered2['CLI'].apply(
        lambda c: max(0, min((c-trigger_thresh)/(100-trigger_thresh), 1)) * max_payout_rate
        if c > trigger_thresh else 0
    )
    filtered2['total_payout_cr'] = filtered2['payout_per_ha'] * filtered2['insured_area_ha'] / 1e7

    st.dataframe(
        filtered2[['district','state','crop','CLI','payout_triggered',
                   'payout_per_ha','total_payout_cr','insured_area_ha']]
        .sort_values('CLI', ascending=False)
        .style
        .background_gradient(subset=['CLI'], cmap='RdYlGn_r')
        .format({'CLI':'{:.1f}','payout_per_ha':'₹{:,.0f}',
                 'total_payout_cr':'₹{:.2f}Cr','insured_area_ha':'{:,.0f}'}),
        use_container_width=True
    )
    total_all = filtered2['total_payout_cr'].sum()
    n_trig    = filtered2['payout_triggered'].sum()
    st.markdown(f"**Total Estimated Payout: ₹{total_all:.1f} Crore** "
                f"across {n_trig} districts above CLI={trigger_thresh}")

# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center;color:#8892b0;padding:20px;'>
    <b>AgriRisk-Sat</b> | Satellite-Driven Agricultural Loss Intelligence |
    Data: ESA Copernicus · NASA EarthData · ECMWF ERA5 · UCSB CHIRPS · ISRO Bhuvan<br>
    Built on Google Earth Engine + Python | For academic &amp; research use
</div>
""", unsafe_allow_html=True)