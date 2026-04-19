import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="Glide Dashboard", layout="wide")
st.title("🛩️ Glide Performance Dashboard")
st.markdown("### Cessna 172 (POH) + NACA 2412 Airfoil")

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

# NASA calculations
closest_idx = (nasa_pos['Alpha'] - angle).abs().idxmin()
closest_ratio = nasa_pos.loc[closest_idx, 'GlideRatio']
best_idx = nasa_pos['GlideRatio'].idxmax()
best_angle = nasa_pos.loc[best_idx, 'Alpha']
best_ratio = nasa_pos.loc[best_idx, 'GlideRatio']

percent_drop = ((best_ratio - closest_ratio) / best_ratio) * 100

# Cessna calculations (using percent_drop)
cessna_original_ratio = cessna['GlideRatio'].iloc[0]   # 9.1
adjusted_ratio = cessna_original_ratio * (1 - percent_drop / 100)
original_distance_nm = altitude * cessna_original_ratio / 6076
adjusted_distance_nm = altitude * adjusted_ratio / 6076

# Columns
col1, col2 = st.columns(2)

with col1:
    # Cessna plot
    fig1, ax1 = plt.subplots()
    ax1.plot(cessna['Altitude_ft'], cessna['GlideRatio'], 'go-', label='POH data')
    ax1.plot(altitude, cessna_original_ratio, 'ro', markersize=10, label=f'Selected {altitude} ft')
    ax1.set_xlabel('Altitude (ft)')
    ax1.set_ylabel('Glide Ratio')
    ax1.set_title('Cessna Glide Ratio')
    ax1.legend()
    ax1.grid(True)
    st.pyplot(fig1)

    st.write(f"**At {altitude} ft, with current angle {angle}°:**")
    st.write(f"- Original book glide ratio: {cessna_original_ratio}")
    st.write(f"- Penalty from airfoil: {percent_drop:.1f}%")
    st.write(f"- **Effective glide ratio:** {adjusted_ratio:.2f}")
    st.write(f"- **Adjusted glide distance:** {adjusted_distance_nm:.1f} NM")
    st.write(f"- (Original distance if at best angle: {original_distance_nm:.1f} NM)")

    # === NEW: Recovery / fallback advice ===
    if angle > best_angle:
        st.error(
            f"⚠️ **Above best angle ({best_angle}°)** – you are slower than best glide speed.\n\n"
            f"**Recovery:** Gently lower the nose to reduce angle of attack to {best_angle}° if altitude permits.\n\n"
            f"**If insufficient altitude:** Accept the lower performance and select a **closer landing spot**. "
            f"Do not pitch up further – risk of stall."
        )
    elif angle < best_angle:
        st.info(
            f"ℹ️ **Below best angle ({best_angle}°)** – you are faster than best glide speed.\n\n"
            f"**Recovery:** Gently raise the nose to increase angle of attack to {best_angle}° if altitude permits.\n\n"
            f"**If insufficient altitude:** Maintain current attitude and prioritize landing spot selection."
        )
    else:
        st.success(
            f"✅ **Optimum glide angle** – maximum range.\n\n"
            f"Maintain this attitude for best performance."
        )

with col2:
    # NASA plot
    fig2, ax2 = plt.subplots()
    ax2.plot(nasa_pos['Alpha'], nasa_pos['GlideRatio'], 'bo-', label='Airfoil data')
    ax2.axvline(x=best_angle, color='r', linestyle='--', label=f'Best {best_angle}°')
    ax2.plot(angle, closest_ratio, 'ro', markersize=10, label=f'Selected {angle}°')
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
st.write(f"- **Cessna** (full aircraft): {cessna_original_ratio}")
st.write(f"- **NASA** (wing only): Best {best_ratio:.2f} at {best_angle}°")
