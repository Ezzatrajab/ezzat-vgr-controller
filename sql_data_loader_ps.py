"""
SQL Data Loader - PowerShell Version (Ingen pyodbc behövs!)
Skapad: 2026-09-17 av Citus

Använder PowerShell för SQL-anslutning istället för pyodbc
Perfekt för Streamlit Cloud där vi inte kan installera ODBC drivers
"""

import pandas as pd
import subprocess
import streamlit as st
from datetime import datetime
import os
import tempfile

SQL_SERVER = 'MEDTAN-SQL-001\\INST02,50002'
SQL_DATABASE = 'DMFinance'

@st.cache_data(ttl=3600)
def load_finance_data_ps(year=2026, kst_list=None):
    """
    Hämtar data från DMFinance via PowerShell
    Sparar till temp CSV och läser in
    """
    try:
        # Skapa PowerShell query
        kst_filter = ""
        if kst_list and len(kst_list) > 0:
            kst_str = "','".join([str(k) for k in kst_list])
            kst_filter = f"AND cc.CostCenterNumber IN ('{kst_str}')"

        # Temp fil för output
        temp_file = os.path.join(tempfile.gettempdir(), f'dmfinance_data_{year}.csv')

        ps_script = f"""
$server = '{SQL_SERVER}'
$database = '{SQL_DATABASE}'
$conn = New-Object System.Data.SqlClient.SqlConnection
$conn.ConnectionString = "Server=$server;Database=$database;Integrated Security=True;Connection Timeout=30"
$conn.Open()

$query = @"
SELECT
    cc.CostCenterNumber as KST,
    YEAR(f.DateKey) as Year,
    MONTH(f.DateKey) as Month,
    s.Scenario,
    a.AccountNumber,
    a.AccountName,
    SUM(f.SEK) as SEK
FROM AI.Fact_Finance f
INNER JOIN AI.DimCostCenter cc ON f.CostCenterKey = cc.CostCenterkey
INNER JOIN AI.Dim_Scenario s ON f.ScenarioKey = s.ScenarioKey
INNER JOIN AI.DimAccount a ON f.AccountKey = a.AccountKey
WHERE cc.CompanyName LIKE '%Medtanken%'
  AND cc.CostCenterNumber NOT IN ('-1', 'COVID', 'FAS4', 'FUSION VGR')
  AND YEAR(f.DateKey) >= {year}
  {kst_filter}
GROUP BY
    cc.CostCenterNumber,
    YEAR(f.DateKey),
    MONTH(f.DateKey),
    s.Scenario,
    a.AccountNumber,
    a.AccountName
ORDER BY Year DESC, Month DESC, cc.CostCenterNumber
"@

$cmd = $conn.CreateCommand()
$cmd.CommandText = $query
$adapter = New-Object System.Data.SqlClient.SqlDataAdapter($cmd)
$dataset = New-Object System.Data.DataSet
$adapter.Fill($dataset) | Out-Null
$dataset.Tables[0] | Export-Csv -Path '{temp_file}' -NoTypeInformation -Encoding UTF8
$conn.Close()
"""

        # Kör PowerShell
        result = subprocess.run(
            ['powershell', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=60
        )

        if result.returncode != 0:
            st.error(f"PowerShell error: {result.stderr}")
            return pd.DataFrame()

        # Läs CSV
        if os.path.exists(temp_file):
            df = pd.read_csv(temp_file)

            # Lägg till enhetsnamn
            kst_map = load_kst_mapping()
            df['Enhet'] = df['KST'].astype(str).map(kst_map)
            df['Enhet'] = df['Enhet'].fillna('KST ' + df['KST'].astype(str))

            # Cleanup
            try:
                os.remove(temp_file)
            except:
                pass

            return df
        else:
            st.error("Ingen data returnerades från SQL")
            return pd.DataFrame()

    except subprocess.TimeoutExpired:
        st.error("SQL query timeout (60s)")
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Fel vid SQL-hämtning: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=3600)
def load_kst_mapping():
    """
    Laddar KST-mapping från INFO.xlsx eller använder fallback
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        info_path = os.path.join(script_dir, 'INFO.xlsx')

        if os.path.exists(info_path):
            df = pd.read_excel(info_path, sheet_name='Org')
            return dict(zip(df['KST'].astype(str), df['Enhet']))
    except:
        pass

    # Fallback
    return {
        '201': 'Frölunda Torg', '202': 'Grimmered', '203': 'Majorna',
        '204': 'Landala', '205': 'Pedagogen Park', '260': 'Kviberg',
        '261': 'Olskroken', '262': 'City VC', '263': 'City Spec',
        '264': 'Husaren', '265': 'Karlastaden', '266': 'Avenyn-Lorensberg',
        '5001': 'Frölunda Torg Rehab', '5020': 'Grimmered Rehab',
        '5061': 'Olskroken Rehab', '5062': 'Avenyn Rehab',
        '5063': 'Karlastaden Rehab', '5201': 'Torpa',
    }

def get_enhet_data_sql(kst, year=2026, month=None):
    """
    Hämtar data för en specifik enhet
    Returnerar dict kompatibel med data_loader_functions
    """
    df = load_finance_data_ps(year=year, kst_list=[kst])

    if df.empty:
        return None

    if month:
        df = df[df['Month'] == month]

    # Gruppera per scenario
    result = {}
    for scenario in ['Actual', 'Budget', 'Forecast']:
        scenario_df = df[df['Scenario'] == scenario]

        if scenario_df.empty:
            result[scenario.lower()] = {
                'intakter': 0,
                'kostnader': 0,
                'resultat': 0,
                'personal_kostnad': 0
            }
        else:
            # Beräkna metrics
            intakter = scenario_df[
                (scenario_df['AccountNumber'].astype(str) >= '3000') &
                (scenario_df['AccountNumber'].astype(str) < '4000')
            ]['SEK'].sum()

            kostnader = abs(scenario_df[
                (scenario_df['AccountNumber'].astype(str) >= '4000') &
                (scenario_df['AccountNumber'].astype(str) < '8000')
            ]['SEK'].sum())

            personal = abs(scenario_df[
                (scenario_df['AccountNumber'].astype(str) >= '7000') &
                (scenario_df['AccountNumber'].astype(str) < '8000')
            ]['SEK'].sum())

            result[scenario.lower()] = {
                'intakter': intakter,
                'kostnader': kostnader,
                'resultat': intakter - kostnader,
                'personal_kostnad': personal
            }

    return result

if __name__ == "__main__":
    # Test
    st.title("SQL Data Loader - PowerShell Test")

    if st.button("Test SQL Connection"):
        with st.spinner("Hämtar data från DMFinance..."):
            df = load_finance_data_ps(year=2026)

            if not df.empty:
                st.success(f"✅ Hämtade {len(df)} rader!")
                st.write(f"**Unika KST:** {df['KST'].nunique()}")
                st.write(f"**Scenarios:** {', '.join(df['Scenario'].unique())}")
                st.dataframe(df.head(20))
            else:
                st.error("❌ Ingen data")
