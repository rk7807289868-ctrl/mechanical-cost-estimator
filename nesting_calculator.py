# nesting_calculator.py - Sheet Metal Nesting & Utilization Estimator
import math

def calculate_sheet_utilization(sheet_length, sheet_width, part_length, part_width, clearance=5.0):
    """
    Calculates how many parts can fit in a standard sheet and overall material utilization %.
    clearance: Cutting gap / edge margin between parts (mm)
    """
    # Effective sheet area with margin considerations
    effective_length = sheet_length - (2 * clearance)
    effective_width = sheet_width - (2 * clearance)
    
    # Check normal orientation (Length along Sheet Length)
    parts_along_length_1 = effective_length // (part_length + clearance)
    parts_along_width_1 = effective_width // (part_width + clearance)
    total_parts_orientation_1 = int(parts_along_length_1 * parts_along_width_1)
    
    # Check rotated orientation (Part rotated by 90 degrees)
    parts_along_length_2 = effective_length // (part_width + clearance)
    parts_along_width_2 = effective_width // (part_length + clearance)
    total_parts_orientation_2 = int(parts_along_length_2 * parts_along_width_2)
    
    # Maximize total parts fit
    max_parts = max(total_parts_orientation_1, total_parts_orientation_2)
    
    # Areas calculation
    sheet_area = sheet_length * sheet_width
    part_area = part_length * part_width
    utilized_area = max_parts * part_area
    
    utilization_percentage = (utilized_area / sheet_area) * 100.0
    scrap_percentage = 100.0 - utilization_percentage
    
    print(f"\n----------------------------------------")
    print(f" Sheet Metal Nesting & Utilization Report")
    print(f"----------------------------------------")
    print(f" Standard Sheet Size : {sheet_length} mm x {sheet_width} mm")
    print(f" Part Dimensions     : {part_length} mm x {part_width} mm")
    print(f" Edge Clearance      : {clearance} mm")
    print(f"----------------------------------------")
    print(f" Max Parts per Sheet : {max_parts}")
    print(f" Sheet Utilization   : {utilization_percentage:.2f}%")
    print(f" Scrap / Wastage     : {scrap_percentage:.2f}%")
    print(f"----------------------------------------")
    
    return max_parts, utilization_percentage

if __name__ == "__main__":
    # Example: 2500x1250mm sheet par ek 300x200mm ka part nest karna
    S_LEN, S_WID = 2500.0, 1250.0
    P_LEN, P_WID = 300.0, 200.0
    
    calculate_sheet_utilization(S_LEN, S_WID, P_LEN, P_WID, clearance=5.0)