import tempfile
import ezdxf
import pandas as pd
import streamlit as st


# ==========================================
# 1. SECURITY / PASSWORD LOCK FEATURE
# ==========================================
def check_password():
  if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

  if not st.session_state["authenticated"]:
    st.title("🔒 Security Access Required")
    st.write(
        "Please enter the master password to access the Manufacturing Cost"
        " Estimator."
    )

    # Default Password: admin123
    password_input = st.text_input("Enter Password:", type="password")

    if st.button("Unlock App"):
      if password_input == "admin123":
        st.session_state["authenticated"] = True
        st.success("Access Granted! Loading App...")
        st.rerun()
      else:
        st.error("❌ Incorrect Password. Please try again.")
    return False
  return True


# Password check run karein
if check_password():

  # ==========================================
  # 2. STREAMLIT APP CONFIGURATION
  # ==========================================
  st.set_page_config(
      page_title="AI Mechanical Cost Estimator", page_icon="⚙️", layout="wide"
  )

  st.title("⚙️ AI-Powered Mechanical Manufacturing Cost Estimator")
  st.write(
      "Upload **multiple DXF 2D Drawings** to extract geometry & generate"
      " automated batch costing quotes."
  )

  # ==========================================
  # 3. SIDEBAR: SHOP FLOOR RATES & SETTINGS
  # ==========================================
  st.sidebar.header("🛠️ Shop Floor Rates & Settings")

  material = st.sidebar.selectbox(
      "Select Material Grade",
      [
          "MS (Mild Steel)",
          "SS 304 (Stainless Steel)",
          "SS 316",
          "Aluminium 6061",
      ],
  )

  # Material Densities (g/cm3)
  density_dict = {
      "MS (Mild Steel)": 7.85,
      "SS 304 (Stainless Steel)": 7.93,
      "SS 316": 8.00,
      "Aluminium 6061": 2.70,
  }
  density = density_dict[material]

  # Material Rates per kg
  material_rate_dict = {
      "MS (Mild Steel)": 65.0,
      "SS 304 (Stainless Steel)": 220.0,
      "SS 316": 310.0,
      "Aluminium 6061": 280.0,
  }
  rm_rate_per_kg = st.sidebar.number_input(
      "Raw Material Rate (₹/kg)",
      value=float(material_rate_dict[material]),
      step=5.0,
  )

  thickness = st.sidebar.number_input(
      "Sheet / Plate Thickness (mm)", min_value=0.5, value=5.0, step=0.5
  )
  cutting_rate_per_m = st.sidebar.number_input(
      "Laser Cutting Rate (₹/meter)", value=12.0, step=1.0
  )
  hole_machining_rate = st.sidebar.number_input(
      "Hole Machining Charge (₹/feature)", value=20.0, step=2.0
  )
  setup_charge = st.sidebar.number_input(
      "Fixed Setup Charges (₹)", value=150.0, step=25.0
  )

  # ==========================================
  # 4. MULTIPLE DXF FILE UPLOADER
  # ==========================================
  st.markdown("---")
  uploaded_files = st.file_uploader(
      "Drag & Drop your DXF Drawings here (Multiple Files Supported)",
      type=["dxf"],
      accept_multiple_files=True,
  )

  # ==========================================
  # 5. DXF PARSING & CALCULATION LOGIC
  # ==========================================
  if uploaded_files:
    summary_data = []
    total_batch_cost = 0.0

    st.success(f"Successfully Loaded {len(uploaded_files)} Drawing(s)!")

    for file in uploaded_files:
      try:
        # Save uploaded file temporarily to disk to prevent readstream errors
        with tempfile.NamedTemporaryFile(delete=False, suffix=".dxf") as tmp:
          tmp.write(file.getvalue())
          tmp_path = tmp.name

        # Read DXF file safely
        doc = ezdxf.readfile(tmp_path)
        msp = doc.modelspace()

        # Calculate Bounding Box (Blank Size)
        min_x, min_y, max_x, max_y = float("inf"), float("inf"), 0, 0
        total_length = 0.0
        hole_count = 0

        for e in msp:
          if e.dxftype() == "LINE":
            start, end = e.dxf.start, e.dxf.end
            total_length += (
                (end.x - start.x) ** 2 + (end.y - start.y) ** 2
            ) ** 0.5
            min_x, max_x = (
                min(min_x, start.x, end.x),
                max(max_x, start.x, end.x),
            )
            min_y, max_y = (
                min(min_y, start.y, end.y),
                max(max_y, start.y, end.y),
            )

          elif e.dxftype() == "CIRCLE":
            r = e.dxf.radius
            center = e.dxf.center
            total_length += 2 * 3.14159 * r
            hole_count += 1
            min_x, max_x = (
                min(min_x, center.x - r),
                max(max_x, center.x + r),
            )
            min_y, max_y = (
                min(min_y, center.y - r),
                max(max_y, center.y + r),
            )

          elif e.dxftype() == "LWPOLYLINE":
            points = e.get_points()
            for p in points:
              min_x, max_x = min(min_x, p[0]), max(max_x, p[0])
              min_y, max_y = min(min_y, p[1]), max(max_y, p[1])

        # Dimension Calculations
        blank_len = round(max(0, max_x - min_x), 1)
        blank_wid = round(max(0, max_y - min_y), 1)

        # Weight Calculation (kg) = (L * W * T * Density) / 1,000,000
        weight_kg = round(
            (blank_len * blank_wid * thickness * density) / 1000000.0, 3
        )
        cut_len_m = round(total_length / 1000.0, 2)

        # Cost Calculations
        rm_cost = round(weight_kg * rm_rate_per_kg, 2)
        cutting_cost = round(cut_len_m * cutting_rate_per_m, 2)
        machining_cost = round(hole_count * hole_machining_rate, 2)
        total_part_cost = round(
            rm_cost + cutting_cost + machining_cost + setup_charge, 2
        )

        total_batch_cost += total_part_cost

        # Append data to summary
        summary_data.append({
            "File Name": file.name,
            "Blank Size (mm)": f"{blank_len} x {blank_wid}",
            "Weight (kg)": weight_kg,
            "Cut Length (m)": cut_len_m,
            "Holes": hole_count,
            "RM Cost (₹)": rm_cost,
            "Cutting Cost (₹)": cutting_cost,
            "Machining (₹)": machining_cost,
            "Total Cost (₹)": total_part_cost,
        })

      except Exception as err:
        st.error(f"Error processing {file.name}: {err}")

    # ==========================================
    # 6. DISPLAY RESULTS & TABLES
    # ==========================================
    if summary_data:
      df = pd.DataFrame(summary_data)

      st.subheader("📊 Batch Costing Summary Table")
      st.dataframe(df, use_container_width=True)

      st.markdown("---")
      col1, col2 = st.columns(2)
      with col1:
        st.metric(label="Total Parts Processed", value=f"{len(summary_data)}")
      with col2:
        st.metric(
            label="Grand Total Batch Quote (₹)", value=f"₹ {total_batch_cost:.2f}"
        )