"""
Test script för att verifiera datainläsning från P&L och KPI-filer
"""
import pandas as pd

# Test 1: Läs P&L Actual för 601
print("=== TEST 1: P&L Actual för 601 (Frölunda Torg Rehab) ===")
try:
    df_actual = pd.read_excel(r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\601\P&L Actual.xlsx')
    print(f"Shape: {df_actual.shape}")

    # Hitta 3053 Rehab-raden
    rehab_row = df_actual[df_actual['Unnamed: 3'].astype(str).str.contains('3053.*Rehab', case=False, na=False)]
    if not rehab_row.empty:
        print("\nHittade 3053 Rehab-rad:")
        # Visa kolumner Selected Period (202601), Selected Period.1 (202602), Selected Period.2 (202603)
        # Kontrollera vilken kolumn som är 202601
        header_row = df_actual.iloc[0]
        print(f"\nHeader row (first 20 cols): {header_row[:20].tolist()}")

        # Hitta kolumnen för 202601, 202602, 202603
        period_cols = [col for col in df_actual.columns if 'Selected Period' in col]
        print(f"\nPeriod columns: {period_cols[:5]}")

        # Läs värdena
        for i, col in enumerate(period_cols[:3]):
            month_val = header_row[col]
            rehab_val = rehab_row.iloc[0][col]
            print(f"{col}: Month={month_val}, Rehab value={rehab_val}")
    else:
        print("Ingen 3053 Rehab-rad hittades!")

except Exception as e:
    print(f"Fel: {e}")

# Test 2: Läs KPI-data
print("\n\n=== TEST 2: KPI-data (Rehab Poäng och TeamBesök) ===")
try:
    kpi_path = r'C:\Users\ezzat.rajab.AD\claude-workspace\VGR Alla enheter\KPIer Storg-GBG.xlsx'
    df = pd.read_excel(kpi_path, sheet_name='Data', header=None)

    # Rehab Poäng header (rad 292)
    print("\n--- Rehab Poäng (rad 292-294) ---")
    for row_idx in range(292, 295):
        row_data = df.iloc[row_idx, :20].tolist()
        print(f"Row {row_idx}: {row_data}")

    # TeamBesök header (rad 304-306)
    print("\n--- TeamBesök (rad 304-306) ---")
    for row_idx in range(304, 307):
        row_data = df.iloc[row_idx, :20].tolist()
        print(f"Row {row_idx}: {row_data}")

    # Extrahera data för Jan-Feb 2026
    print("\n--- Extraherade data för 2026 ---")
    header_row = df.iloc[292, :].tolist()
    print(f"Header: {header_row[:20]}")

    # Hitta kolumner för 202601 och 202602
    col_mapping = {}
    for i, val in enumerate(header_row):
        if pd.notna(val) and str(val).replace('.0', '').isdigit():
            month_num = int(val)
            if month_num >= 202601:
                col_mapping[month_num] = i

    print(f"\nKolumnmapping för 2026: {col_mapping}")

    # Frölunda Torg Rehab Poäng (från VC 102, rad 293)
    frolunda_vc_poang = df.iloc[293, :].tolist()
    print(f"\nFrölunda Torg VC (102) Rehab Poäng:")
    print(f"  Enhet: {frolunda_vc_poang[0]} ({frolunda_vc_poang[1]})")
    print(f"  Jan 2026 (col {col_mapping.get(202601)}): {frolunda_vc_poang[col_mapping.get(202601)] if col_mapping.get(202601) else 'N/A'}")
    print(f"  Feb 2026 (col {col_mapping.get(202602)}): {frolunda_vc_poang[col_mapping.get(202602)] if col_mapping.get(202602) else 'N/A'}")

    # Frölunda Torg Rehab TeamBesök (601, rad 305)
    frolunda_rehab_teambesok = df.iloc[305, :].tolist()
    print(f"\nFrölunda Torg Rehab (601) TeamBesök:")
    print(f"  Enhet: {frolunda_rehab_teambesok[0]} ({frolunda_rehab_teambesok[1]})")
    print(f"  Jan 2026 (col {col_mapping.get(202601)}): {frolunda_rehab_teambesok[col_mapping.get(202601)] if col_mapping.get(202601) else 'N/A'}")
    print(f"  Feb 2026 (col {col_mapping.get(202602)}): {frolunda_rehab_teambesok[col_mapping.get(202602)] if col_mapping.get(202602) else 'N/A'}")

except Exception as e:
    print(f"Fel: {e}")

print("\n\n=== TESTNING KLAR ===")
