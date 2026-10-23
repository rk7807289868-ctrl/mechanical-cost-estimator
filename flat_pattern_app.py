import streamlit as math_app
import math

math_app.set_page_config(page_title="Sheet Metal Flat Pattern Calculator", page_icon="📐", layout="centered")

math_app.title("📐 Sheet Metal Flat Pattern & Bend Calculator")
math_app.markdown("Calculate **Bend Allowance (BA)**, **Bend Deduction (BD)**, and **Developed Flat Length** for precise sheet metal manufacturing.")

math_app.sidebar.header("⚙️ Input Parameters")

# Material Selection
material = math_app.sidebar.selectbox("Select Material", ["Mild Steel (MS)", "Stainless Steel (SS)", "Aluminium"])

# Default K-Factor based on material
default_k = 0.33 if material == "Aluminium" else (0.44 if material == "Mild Steel (MS)" else 0.45)

thickness = math_app.sidebar.number_input("Sheet Thickness (t) in mm", min_value=0.5, max_value=25.0, value=2.0, step=0.5)
inner_radius = math_app.sidebar.number_input("Inner Bend Radius (R) in mm", min_value=0.0, max_value=50.0, value=2.0, step=0.5)
bend_angle = math_app.sidebar.number_input("Bend Angle (Alpha) in Degrees", min_value=1.0, max_value=180.0, value=90.0, step=1.0)
k_factor = math_app.sidebar.slider("K-Factor", min_value=0.1, max_value=0.6, value=default_k, step=0.01)

math_app.sidebar.markdown("---")
math_app.sidebar.subheader("Flange Dimensions (Single Bend L-Shape)")
flange_1 = math_app.sidebar.number_input("Flange Length 1 (Leg A) in mm", min_value=0.0, max_value=1000.0, value=50.0, step=1.0)
flange_2 = math_app.sidebar.number_input("Flange Length 2 (Leg B) in mm", min_value=0.0, max_value=1000.0, value=50.0, step=1.0)

# Calculation Logic
# Bend Allowance Formula: BA = (Pi * Angle / 180) * (R + K * t)
rad_angle = math.radians(bend_angle)
bend_allowance = (rad_angle / math.pi) * (math.pi / 180 * 180) # Simplified radian conversion check
bend_allowance = (bend_angle * math.pi / 180.0) * (inner_radius + (k_factor * thickness))

# External Setback (OSSB) = (R + t) * tan(Angle / 2)
ossb = (inner_radius + thickness) * math.tan(math.radians(bend_angle / 2.0))

# Bend Deduction (BD) = 2 * OSSB - BA
bend_deduction = (2.0 * ossb) - bend_allowance

# Total Flat Length for L-Bend
total_flat_length = flange_1 + flange_2 - bend_deduction

# Main Screen Display
math_app.subheader("📊 Calculation Results")

col1, col2, col3 = math_app.columns(3)
col1.metric("Bend Allowance (BA)", f"{bend_allowance:.2f} mm")
col2.metric("Bend Deduction (BD)", f"{bend_deduction:.2f} mm")
col3.metric("Total Flat Length", f"{total_flat_length:.2f} mm")

math_app.markdown("---")
math_app.info(f"""
**Summary for Manufacturing:**
* **Material:** {material} (Thickness: {thickness} mm)
* **K-Factor Used:** {k_factor}
* **Inside Radius:** {inner_radius} mm | **Bend Angle:** {bend_angle}°
* **Cut Sheet Size Required:** **{total_flat_length:.2f} mm** (for a 90° single-bend bracket with legs {flange_1}mm & {flange_2}mm).
""")