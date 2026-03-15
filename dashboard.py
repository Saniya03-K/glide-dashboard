import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Glide Dashboard", layout="wide")
st.title("🛩️ Glide Performance Dashboard")
st.markdown("### Cessna 172 (POH) + NACA 2412 Airfoil")

# Data loading
@st.cache_data
def load_data():
    cessna = pd.read_csv('cessna_glide.csv')
    nasa = pd.read_csv('airfoil_data.csv', skiprows=10)
    nasa['GlideRatio'] = nasa['Cl'] / nasa['Cd']
    nasa_pos = nasa[nasa['Alpha'] >= 0].copy()
    return cessna, nasa_pos

cessna, nasa_pos = load_data()

# Sidebar controls
st.sidebar.header("Controls")
altitude = st.sidebar.slider("Cessna Altitude (ft)", 2000, 12000, 6000, step=1000)
angle = st.sidebar.slider("Angle of Attack (°)", 0.0, 15.0, 5.0, step=0.5)

# Cessna calculations
cessna_ratio = cessna['GlideRatio'].iloc[0]  # 9.1
distance_nm = altitude * cessna_ratio / 6076    # 1 NM = 6076 feet

# NASA calculations
closest_idx = (nasa_pos['Alpha'] - angle).abs().idxmin()
closest_ratio = nasa_pos.loc[closest_idx, 'GlideRatio']
best_idx = nasa_pos['GlideRatio'].idxmax()
best_angle = nasa_pos.loc[best_idx, 'Alpha']
best_ratio = nasa_pos.loc[best_idx, 'GlideRatio']

# columns
col1, col2 = st.columns(2)

with col1:
    fig1, ax1 = plt.subplots()
    ax1.plot(cessna['Altitude_ft'], cessna['GlideRatio'], 'go-', label='POH data')
    ax1.plot(altitude, cessna_ratio, 'ro', markersize=10, label=f'Selected {altitude} ft')  # red dot
    ax1.set_xlabel('Altitude (ft)')
    ax1.set_ylabel('Glide Ratio')
    ax1.set_title('Cessna Glide Ratio')
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)
    st.metric("Cessna Glide Ratio", f"{cessna_ratio}", delta=None)
    st.metric("Estimated Glide Distance", f"{distance_nm:.1f} NM", delta=None)

with col2:
    fig2, ax2 = plt.subplots()
    ax2.plot(nasa_pos['Alpha'], nasa_pos['GlideRatio'], 'bo-', label='Airfoil data')
    ax2.axvline(x=best_angle, color='r', linestyle='--', label=f'Best {best_angle}°')
    ax2.plot(angle, closest_ratio, 'ro', markersize=10, label=f'Selected {angle}°')  # red dot
    ax2.set_xlabel('Angle of Attack (°)')
    ax2.set_ylabel('Cl/Cd')
    ax2.set_title('Airfoil Efficiency')
    ax2.legend()
    ax2.grid(True)
    st.pyplot(fig2)
    st.metric(f"At {angle}° angle", f"Ratio = {closest_ratio:.2f}")
    st.metric("Best angle", f"{best_angle}° (ratio = {best_ratio:.2f})")

# Comparison
st.markdown("---")
st.subheader("📊 Comparison")
st.write(f"- **Cessna** (full aircraft): {cessna_ratio}")
st.write(f"- **NASA** (wing only): Best {best_ratio:.2f} at {best_angle}°")