# app.py - Streamlit Web App for Sheet Metal Nesting
import streamlit as st
import math

st.title("🛠️ Sheet Metal Nesting & Utilization Calculator")
st.write("Apne part aur sheet ke dimensions daalein aur instant efficiency check karein.")

# Sidebar ya Main inputs
st.header("1. Sheet & Part Dimensions")
col1, col2 = st.columns(2)

with col1:
    sheet_length = st.number_input("Sheet Length (mm)", value=2500.0)
    sheet_width = st.number_input("Sheet Width (mm)", value=1250.0)

with col2:
    part_length = st.number_input("Part Length (mm)", value=300.0)
    part_width = st.number_input("Part Width (mm)", value=200.0)

clearance = st.slider("Edge / Cutting Clearance (mm)", min_value=1.0, max_value=20.0, value=5.0)

# Calculation Logic
effective_length = sheet_length - (2 * clearance)
effective_width = sheet_width - (2 * clearance)

parts_1 = (effective_length // (part_length + clearance)) * (effective_width // (part_width + clearance))
parts_2 = (effective_length // (part_width + clearance)) * (effective_width // (part_length + clearance))
max_parts = int(max(parts_1, parts_2))

sheet_area = sheet_length * sheet_width
utilized_area = max_parts * (part_length * part_width)
utilization_percentage = (utilized_area / sheet_area) * 100.0 if sheet_area > 0 else 0
scrap_percentage = 100.0 - utilization_percentage

# Display Results in Style
st.markdown("---")
st.header("📊 Nesting Results & Efficiency")

mcol1, mcol2, mcol3 = st.columns(3)
mcol1.metric(label="Max Parts per Sheet", value=f"{max_parts}")
mcol2.metric(label="Sheet Utilization", value=f"{utilization_percentage:.2f}%")
mcol3.metric(label="Scrap / Wastage", value=f"{scrap_percentage:.2f}%")
