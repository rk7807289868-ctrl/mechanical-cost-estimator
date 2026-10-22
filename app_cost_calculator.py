import streamlit as st
import pandas as pd
import ezdxf
import tempfile
import os
from fpdf import FPDF

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

# 2. PDF Generator Function
def create_pdf_quotation(summary_df, total_cost):
    pdf = FPDF()
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
    pdf.set_font("Arial", "B", 10)
    pdf.cell(50, 10, "File Name", 1)
    pdf.cell(35, 10, "Weight (kg)", 1)
    pdf.cell(45, 10, "Cut Length (mm)", 1)
    pdf.cell(45, 10, "Cost (Rs.)", 1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", "", 10)
    for _, row in summary_df.iterrows():
        file_nm = str(row.get('File Name', 'Part'))[:20]
        pdf.cell(50, 10, file_nm, 1)
        pdf.cell(35, 10, f"{row.get('Weight (kg)', 0):.2f}", 1)
        pdf.cell(45, 10, f"{row.get('Cut Length (mm)', 0):.2f}", 1)
        pdf.cell(45, 10, f"{row.get('Total Cost', 0):.2f}", 1)
        pdf.ln()
        
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# 3. Main Application Logic
if check_password():
    st.title("⚙️ AI-Powered Mechanical Manufacturing Cost Estimator")
    st.write("Upload DXF files to process geometry and calculate cost breakdown.")

    # Sidebar Shop Floor Rates
    st.sidebar.header("Shop Floor Parameters")
    material_density = st.sidebar.number_input("Material Density (g/cm³)", value=7.85) # Steel
    raw_material_rate = st.sidebar.number_input("Material Rate (Rs/kg)", value=90.0)
    laser_cutting_rate = st.sidebar.number_input("Cutting Rate (Rs/meter)", value=15.0)

    # File Uploader
    uploaded_files = st.file_uploader("Upload DXF Files", type=["dxf"], accept_multiple_files=True)

    if uploaded_files:
        results = []
        total_project_cost = 0.0

        for uploaded_file in uploaded_files:
            # Save temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            try:
                doc = ezdxf.readfile(tmp_path)
                msp = doc.modelspace()

                # Basic Geometry Extraction
                total_cut_length = 0.0
                min_x, min_y, max_x, max_y = float('inf'), float('inf'), float('-inf'), float('-inf')

                for e in msp:
                    if e.dxftype() == 'LINE':
                        p1, p2 = e.dxf.start, e.dxf.end
                        length = ((p2[0]-p1[0])**2 + (p2[1]-p1[1])**2)**0.5
                        total_cut_length += length
                        min_x, max_x = min(min_x, p1[0], p2[0]), max(max_x, p1[0], p2[0])
                        min_y, max_y = min(min_y, p1[1], p2[1]), max(max_y, p1[1], p2[1])
                    elif e.dxftype() == 'CIRCLE':
                        r = e.dxf.radius
                        total_cut_length += 2 * 3.14159 * r
                        cx, cy = e.dxf.center[0], e.dxf.center[1]
                        min_x, max_x = min(min_x, cx-r), max(max_x, cx+r)
                        min_y, max_y = min(min_y, cy-r), max(max_y, cy+r)

                # Bounding Box Blank Calculation (assuming 5mm thickness default)
                width = max(0.0, max_x - min_x) if min_x != float('inf') else 0.0
                height = max(0.0, max_y - min_y) if min_y != float('inf') else 0.0
                thickness = 5.0 # mm
                
                volume_cm3 = (width * height * thickness) / 1000.0
                weight_kg = (volume_cm3 * material_density) / 1000.0

                # Costs
                mat_cost = weight_kg * raw_material_rate
                cut_cost = (total_cut_length / 1000.0) * laser_cutting_rate
                part_cost = mat_cost + cut_cost
                total_project_cost += part_cost

                results.append({
                    "File Name": uploaded_file.name,
                    "Blank Size (mm)": f"{width:.1f} x {height:.1f}",
                    "Weight (kg)": weight_kg,
                    "Cut Length (mm)": total_cut_length,
                    "Total Cost": part_cost
                })
            except Exception as e:
                st.error(f"Error reading {uploaded_file.name}: {e}")
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)

        if results:
            df_results = pd.DataFrame(results)
            st.subheader("Calculation Summary")
            st.dataframe(df_results)

            st.success(f"**Total Estimated Project Cost: Rs. {total_project_cost:,.2f}**")

            # PDF Download Button
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
