import streamlit as st
import pandas as pd
import ezdxf
import tempfile
import os
from fpdf import FPDF
import matplotlib.pyplot as plt

# Page Configuration
st.set_page_config(page_title="Mechanical Cost Estimator", layout="wide")

# 1. Password Lock / Security Access
def check_password():
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False

    if not st.session_state["authenticated"]:
        st.title("🔒 Security Access Required")
        password_input = st.text_input("Enter Access Password:", type="password")
        if st.button("Unlock App"):
            if password_input == "admin123":  # Aapka password
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("Incorrect Password! Please try again.")
        return False
    return True

# 2. PDF Generator Function with Cost Breakdown
def create_pdf_quotation(summary_df, total_cost):
    pdf = FPDF(orientation='L', unit='mm', format='A4')
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Mechanical Manufacturing Cost Quotation", 0, 1, "C")
    pdf.ln(5)
    
    # Total Price
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total Estimated Cost: Rs. {total_cost:,.2f}", 0, 1, "L")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", "B", 9)
    pdf.cell(45, 10, "File Name", 1)
    pdf.cell(25, 10, "Material", 1)
    pdf.cell(18, 10, "Thick", 1)
    pdf.cell(35, 10, "Blank Size", 1)
    pdf.cell(22, 10, "Weight", 1)
    pdf.cell(25, 10, "Cut Len", 1)
    pdf.cell(25, 10, "Mat. Cost", 1)
    pdf.cell(25, 10, "Cut Cost", 1)
    pdf.cell(25, 10, "Total (Rs.)", 1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", "", 8)
    for _, row in summary_df.iterrows():
        file_nm = str(row.get('File Name', 'Part'))[:18]
        pdf.cell(45, 8, file_nm, 1)
        pdf.cell(25, 8, str(row.get('Material', '')), 1)
        pdf.cell(18, 8, str(row.get('Thick (mm)', '')), 1)
        pdf.cell(35, 8, str(row.get('Blank Size (mm)', '')), 1)
        pdf.cell(22, 8, f"{row.get('Weight (kg)', 0):.2f}", 1)
        pdf.cell(25, 8, f"{row.get('Cut Length (mm)', 0):.1f}", 1)
        pdf.cell(25, 8, f"{row.get('Mat. Cost (Rs.)', 0):.1f}", 1)
        pdf.cell(25, 8, f"{row.get('Cut Cost (Rs.)', 0):.1f}", 1)
        pdf.cell(25, 8, f"{row.get('Total Cost (Rs.)', 0):.1f}", 1)
        pdf.ln()
        
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# 3. Robust DXF Visual Preview Function (Supports LWPOLYLINE & Circles)
def plot_dxf_file(tmp_path):
    fig, ax = plt.subplots(figsize=(5, 5))
    try:
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()
        for e in msp:
            if e.dxftype() == 'LINE':
                p1, p2 = e.dxf.start, e.dxf.end
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=1)
            elif e.dxftype() == 'LWPOLYLINE':
                points = list(e.get_points(format='xy'))
                for i in range(len(points) - 1):
                    p1, p2 = points[i], points[i+1]
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=1)
                if e.closed and len(points) > 2:
                    p1, p2 = points[-1], points[0]
                    ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color='blue', linewidth=1)
            elif e.dxftype() == 'CIRCLE':
                center = e.dxf.center
                radius = e.dxf.radius
                circle = plt.Circle((center[0], center[1]), radius, color='red', fill=False, linewidth=1)
                ax.add_patch(circle)
        ax.set_aspect('equal')
        ax.axis('off')
    except Exception:
        pass
    return fig

# 4. Main Application Logic
if check_password():
    st.title("⚙️ AI-Powered Mechanical Manufacturing Cost Estimator")
    st.write("Upload DXF files to process geometry, customize parameters, view previews, and calculate cost breakdown.")

    # Sidebar Shop Floor Parameters
    st.sidebar.header("Shop Floor Parameters")
    
    material_type = st.sidebar.selectbox("Select Material", ["Mild Steel (MS)", "Stainless Steel (SS)", "Aluminium"])
    
    if material_type == "Mild Steel (MS)":
        default_density, default_mat_rate = 7.85, 85.0
    elif material_type == "Stainless Steel (SS)":
        default_density, default_mat_rate = 8.00, 180.0
    else:
        default_density, default_mat_rate = 2.70, 240.0

    material_density = st.sidebar.number_input("Material Density (g/cm³)", value=default_density)
    raw_material_rate = st.sidebar.number_input("Material Rate (Rs/kg)", value=default_mat_rate)
    
    thickness = st.sidebar.number_input("Sheet Thickness (mm)", value=5.0, min_value=0.5, max_value=100.0, step=0.5)
    laser_cutting_rate = st.sidebar.number_input("Laser Cutting Rate (Rs/meter)", value=20.0)
    
    bending_cost_rate = st.sidebar.number_input("Bending Cost (Rs/bend)", value=10.0)
    hole_drilling_rate = st.sidebar.number_input("Hole Drilling Cost (Rs/hole)", value=5.0)

    # File Uploader
    uploaded_files = st.file_uploader("Upload DXF Files", type=["dxf"], accept_multiple_files=True)

    if uploaded_files:
        results = []
        total_project_cost = 0.0

        st.subheader("🔍 DXF Visual Previews")
        cols = st.columns(min(len(uploaded_files), 3))

        for idx, uploaded_file in enumerate(uploaded_files):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                col_idx = idx % 3
                with cols[col_idx]:
                    st.text(uploaded_file.name[:25])
                    fig = plot_dxf_file(tmp_path)
                    st.pyplot(fig)
                    plt.close(fig) # Clear memory

                doc = ezdxf.readfile(tmp_path)
                msp = doc.modelspace()

                total_cut_length = 0.0
                circle_count = 0
                min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

                for e in msp:
                    if e.dxftype() == 'LINE':
                        p1, p2 = e.dxf.start, e.dxf.end
                        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
                        total_cut_length += length
                        min_x, max_x = min(min_x, p1[0], p2[0]), max(max_x, p1[0], p2[0])
                        min_y, max_y = min(min_y, p1[1], p2[1]), max(max_y, p1[1], p2[1])
                    elif e.dxftype() == 'LWPOLYLINE':
                        points = list(e.get_points(format='xy'))
                        for i in range(len(points) - 1):
                            p1, p2 = points[i], points[i+1]
                            length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
                            total_cut_length += length
                            min_x, max_x = min(min_x, p1[0], p2[0]), max(max_x, p1[0], p2[0])
                            min_y, max_y = min(min_y, p1[1], p2[1]), max(max_y, p1[1], p2[1])
                        if e.closed and len(points) > 2:
                            p1, p2 = points[-1], points[0]
                            length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
                            total_cut_length += length
                    elif e.dxftype() == 'CIRCLE':
                        circle_count += 1
                        r = e.dxf.radius
                        total_cut_length += 2 * 3.14159 * r
                        cx, cy = e.dxf.center[0], e.dxf.center[1]
                        min_x, max_x = min(min_x, cx-r), max(max_x, cx+r)
                        min_y, max_y = min(min_y, cy-r), max(max_y, cy+r)

                width = max(0.0, max_x - min_x) if min_x != float('inf') else 0.0
                height = max(0.0, max_y - min_y) if min_y != float('inf') else 0.0
                
                volume_cm3 = (width * height * thickness) / 1000.0
                weight_kg = (volume_cm3 * material_density) / 1000.0

                mat_cost = weight_kg * raw_material_rate
                cut_cost = (total_cut_length / 1000.0) * laser_cutting_rate
                bend_cost = 2.0 * bending_cost_rate 
                drill_cost = circle_count * hole_drilling_rate

                part_cost = mat_cost + cut_cost + bend_cost + drill_cost
                total_project_cost += part_cost

                results.append({
                    "File Name": uploaded_file.name,
                    "Material": material_type,
                    "Thick (mm)": thickness,
                    "Blank Size (mm)": f"{width:.1f} x {height:.1f}",
                    "Weight (kg)": weight_kg,
                    "Cut Length (mm)": total_cut_length,
                    "Mat. Cost (Rs.)": mat_cost,
                    "Cut Cost (Rs.)": cut_cost,
                    "Total Cost (Rs.)": part_cost
                })
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if results:
            st.markdown("---")
            df_results = pd.DataFrame(results)
            st.subheader("Calculation Summary & Cost Breakdown")
            st.dataframe(df_results)

            st.success(f"**Total Estimated Project Cost: Rs. {total_project_cost:,.2f}**")

            st.markdown("---")
            if st.button("📄 Generate PDF Quotation"):
                pdf_file_path = create_pdf_quotation(df_results, total_project_cost)
                with open(pdf_file_path, "rb") as f:
                    st.download_button(
                        label="📥 Click Here to Download PDF File",
                        data=f,
                        file_name="Manufacturing_Quotation.pdf",
                        mime="application/pdf"
                    )
