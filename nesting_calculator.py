# app.py - Sheet Metal Nesting with Visual Layout & Password
import streamlit as st
import math
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# --- PASSWORD PROTECTION ---
st.sidebar.title("🔐 Login Security")
password = st.sidebar.text_input("Enter App Password", type="password")
CORRECT_PASSWORD = "admin"

if password != CORRECT_PASSWORD:
    st.warning("⚠️ Kripya aage badhne ke liye sahi password darj karein.")
    st.stop()

# --- MAIN APP ---
st.title("🛠️ Sheet Metal Nesting & Visual Layout Calculator")
st.write("Sheet aur part ke dimensions daalein aur visual nesting layout dekhein.")

st.header("1. Sheet & Part Dimensions")
col1, col2 = st.columns(2)

with col1:
    sheet_length = st.number_input("Sheet Length (mm)", value=2500.0)
    sheet_width = st.number_input("Sheet Width (mm)", value=1250.0)

with col2:
    part_length = st.number_input("Part Length (mm)", value=300.0)
    part_width = st.number_input("Part Width (mm)", value=200.0)

clearance = st.slider("Edge / Cutting Clearance (mm)", min_value=1.0, max_value=20.0, value=5.0)

# --- CALCULATION LOGIC ---
effective_length = sheet_length - (2 * clearance)
effective_width = sheet_width - (2 * clearance)

# Orientation 1: Normal (Part Length along Sheet Length)
cols_1 = effective_length // (part_length + clearance)
rows_1 = effective_width // (part_width + clearance)
total_1 = int(cols_1 * rows_1)

# Orientation 2: Rotated (Part Width along Sheet Length)
cols_2 = effective_length // (part_width + clearance)
rows_2 = effective_width // (part_length + clearance)
total_2 = int(cols_2 * rows_2)

# Choose best orientation
if total_1 >= total_2:
    max_parts = total_1
    p_len, p_wid = part_length, part_width
    num_cols, num_rows = int(cols_1), int(rows_1)
    orientation_used = "Normal (0°)"
else:
    max_parts = total_2
    p_len, p_wid = part_width, part_length
    num_cols, num_rows = int(cols_2), int(rows_2)
    orientation_used = "Rotated (90°)"

sheet_area = sheet_length * sheet_width
utilized_area = max_parts * (part_length * part_width)
utilization_percentage = (utilized_area / sheet_area) * 100.0 if sheet_area > 0 else 0
scrap_percentage = 100.0 - utilization_percentage

# --- RESULTS METRICS ---
st.markdown("---")
st.header("📊 Nesting Results & Efficiency")

mcol1, mcol2, mcol3, mcol4 = st.columns(4)
mcol1.metric(label="Max Parts", value=f"{max_parts}")
mcol2.metric(label="Utilization", value=f"{utilization_percentage:.2f}%")
mcol3.metric(label="Scrap", value=f"{scrap_percentage:.2f}%")
mcol4.metric(label="Orientation", value=orientation_used)

# --- VISUAL LAYOUT GENERATION (MATPLOTLIB) ---
st.markdown("---")
st.header("🎨 Visual Sheet Layout Diagram")

fig, ax = plt.subplots(figsize=(10, 5))

# Draw Sheet (Outer Boundary)
sheet_rect = patches.Rectangle((0, 0), sheet_length, sheet_width, linewidth=2, edgecolor='black', facecolor='#e6f2ff')
ax.add_patch(sheet_rect)

# Draw Parts inside Sheet based on calculated grid
start_x = clearance
start_y = clearance

for i in range(num_cols):
    for j in range(num_rows):
        x = start_x + i * (p_len + clearance)
        y = start_y + j * (p_wid + clearance)
        
        part_rect = patches.Rectangle((x, y), p_len, p_wid, linewidth=1, edgecolor='red', facecolor='#ff9999', alpha=0.7)
        ax.add_patch(part_rect)

# Plot settings
ax.set_xlim(-50, sheet_length + 50)
ax.set_ylim(-50, sheet_width + 50)
ax.set_aspect('equal')
ax.set_xlabel("Sheet Length (mm)")
ax.set_ylabel("Sheet Width (mm)")
ax.set_title(f"Nesting Layout: {num_cols} Columns x {num_rows} Rows ({max_parts} Parts)")
ax.grid(True, linestyle='--', alpha=0.5)

st.pyplot(fig)
