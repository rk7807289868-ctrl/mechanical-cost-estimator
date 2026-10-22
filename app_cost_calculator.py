from fpdf import FPDF
import tempfile

# 1. PDF Generation Function
def create_pdf_quotation(summary_df, total_cost):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "Mechanical Manufacturing Cost Quotation", 0, 1, "C")
    pdf.ln(10)
    
    # Summary Details
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, f"Total Estimated Project Cost: Rs. {total_cost:,.2f}", 0, 1, "L")
    pdf.ln(5)
    
    # Table Header
    pdf.set_font("Arial", "B", 10)
    pdf.cell(60, 10, "File Name", 1)
    pdf.cell(35, 10, "Weight (kg)", 1)
    pdf.cell(45, 10, "Cut Length (mm)", 1)
    pdf.cell(45, 10, "Cost (Rs.)", 1)
    pdf.ln()
    
    # Table Rows
    pdf.set_font("Arial", "", 10)
    for _, row in summary_df.iterrows():
        pdf.cell(60, 10, str(row.get('File Name', 'Part')), 1)
        pdf.cell(35, 10, f"{row.get('Weight (kg)', 0):.2f}", 1)
        pdf.cell(45, 10, f"{row.get('Cut Length (mm)', 0):.2f}", 1)
        pdf.cell(45, 10, f"{row.get('Total Cost', 0):.2f}", 1)
        pdf.ln()
        
    # Save to a temporary file
    temp_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp_pdf.name)
    return temp_pdf.name

# 2. Streamlit Download Button (Apne results display ke baad ise rakhein)
if 'df_results' in locals() or 'df_results' in globals(): # Jab calculation ho chuki ho
    if st.button("📄 Generate & Download PDF Quotation"):
        pdf_file_path = create_pdf_quotation(df_results, total_cost)
        with open(pdf_file_path, "rb") as f:
            st.download_button(
                label="📥 Click here to download PDF file",
                data=f,
                file_name="Manufacturing_Quotation.pdf",
                mime="application/pdf"
            )
