"""
SQL Data Loader - Hämtar CAUSE-data från DMFinance
Skapad: 2026-09-17 av Citus
Ersätter Excel-filer med live SQL-queries till DMFinance

FUNKTIONALITET:
- Ansluter till MEDTAN-SQL-001\INST02,50002
- Hämtar Actual, Budget, Forecast från AI schema
- Mappar KST till enhetsnamn
- Returnerar samma format som data_loader_functions.py
"""

import pandas as pd
import pyodbc
from datetime import datetime
import streamlit as st

# SQL Server connection settings
SQL_SERVER = 'MEDTAN-SQL-001\\INST02,50002'
SQL_DATABASE = 'DMFinance'

@st.cache_data(ttl=3600)  # Cache i 1 timme
def get_sql_connection():
    """
    Skapar SQL Server-anslutning med Windows Authentication
    """
    try:
        conn_str = f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={SQL_SERVER};DATABASE={SQL_DATABASE};Trusted_Connection=yes;'
        conn = pyodbc.connect(conn_str, timeout=10)
        return conn
    except Exception as e:
        st.error(f"Kunde inte ansluta till DMFinance: {e}")
        return None

@st.cache_data(ttl=3600)
def load_kst_mapping():
    """
    Laddar mappning mellan KST-nummer och enhetsnamn från INFO.xlsx
    Fallback om INFO.xlsx inte finns
    """
    try:
        import os
        script_dir = os.path.dirname(os.path.abspath(__file__))
        info_path = os.path.join(script_dir, 'INFO.xlsx')

        if os.path.exists(info_path):
            df = pd.read_excel(info_path, sheet_name='Org')
            kst_map = dict(zip(df['KST'].astype(str), df['Enhet']))
            return kst_map
        else:
            # Fallback mapping om INFO.xlsx saknas
            return {
                '201': 'Frölunda Torg',
                '202': 'Grimmered',
                '203': 'Majorna',
                '204': 'Landala',
                '205': 'Pedagogen Park',
                '260': 'Kviberg',
                '261': 'Olskroken',
                '262': 'City VC',
                '263': 'City Spec',
                '264': 'Husaren',
                '265': 'Karlastaden',
                '266': 'Avenyn-Lorensberg',
                '5001': 'Frölunda Torg Rehab',
                '5020': 'Grimmered Rehab',
                '5021': 'Majorna Rehab',
                '5022': 'Pedagogen Park Rehab',
                '5061': 'Olskroken Rehab',
                '5062': 'Avenyn Rehab',
                '5063': 'Karlastaden Rehab',
                '5065': 'Åby Rehab',
                '5201': 'Torpa',
                '5203': 'Stavre',
                '8001': 'Holding',
            }
    except Exception as e:
        st.warning(f"Kunde inte ladda KST-mapping: {e}")
        return {}

@st.cache_data(ttl=3600)
def load_finance_data_from_sql(year=2026, kst_list=None):
    """
    Hämtar finansiell data från DMFinance för specificerade KST

    Parameters:
    - year: År att hämta data för (default 2026)
    - kst_list: Lista med KST-nummer att hämta (None = alla Medtanken)

    Returns:
    - DataFrame med kolumner: KST, Enhet, Year, Month, Scenario, AccountNumber, AccountName, SEK
    """
    conn = get_sql_connection()
    if conn is None:
        return pd.DataFrame()

    try:
        # SQL query
        kst_filter = ""
        if kst_list and len(kst_list) > 0:
            kst_str = "','".join([str(k) for k in kst_list])
            kst_filter = f"AND cc.CostCenterNumber IN ('{kst_str}')"

        query = f"""
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
        ORDER BY
            Year DESC,
            Month DESC,
            cc.CostCenterNumber
        """

        df = pd.read_sql(query, conn)
        conn.close()

        # Lägg till enhetsnamn
        kst_map = load_kst_mapping()
        df['Enhet'] = df['KST'].astype(str).map(kst_map)

        # Fyll i okända enheter med KST-nummer
        df['Enhet'] = df['Enhet'].fillna('KST ' + df['KST'].astype(str))

        return df

    except Exception as e:
        st.error(f"Fel vid hämtning från SQL: {e}")
        if conn:
            conn.close()
        return pd.DataFrame()

def get_current_month_data(kst, scenario='Actual', year=None, month=None):
    """
    Hämtar data för specifik KST, scenario, år och månad
    Kompatibel med data_loader_functions format

    Returns:
    - Dictionary med financial metrics
    """
    if year is None:
        year = datetime.now().year
    if month is None:
        month = datetime.now().month

    df = load_finance_data_from_sql(year=year, kst_list=[kst])

    if df.empty:
        return {
            'intakter': 0,
            'kostnader': 0,
            'resultat': 0,
            'personal_kostnad': 0
        }

    # Filtrera på scenario, år och månad
    filtered = df[
        (df['KST'].astype(str) == str(kst)) &
        (df['Scenario'] == scenario) &
        (df['Year'] == year) &
        (df['Month'] == month)
    ]

    if filtered.empty:
        return {
            'intakter': 0,
            'kostnader': 0,
            'resultat': 0,
            'personal_kostnad': 0
        }

    # Beräkna metrics baserat på kontonummer
    # Intäkter = konton 3000-3999
    intakter = filtered[
        (filtered['AccountNumber'].astype(str) >= '3000') &
        (filtered['AccountNumber'].astype(str) < '4000')
    ]['SEK'].sum()

    # Kostnader = konton 4000-7999
    kostnader = abs(filtered[
        (filtered['AccountNumber'].astype(str) >= '4000') &
        (filtered['AccountNumber'].astype(str) < '8000')
    ]['SEK'].sum())

    # Personalkostnader = konton 7000-7999
    personal_kostnad = abs(filtered[
        (filtered['AccountNumber'].astype(str) >= '7000') &
        (filtered['AccountNumber'].astype(str) < '8000')
    ]['SEK'].sum())

    resultat = intakter - kostnader

    return {
        'intakter': intakter,
        'kostnader': kostnader,
        'resultat': resultat,
        'personal_kostnad': personal_kostnad
    }

def test_sql_connection():
    """
    Testar SQL-anslutning och visar tillgänglig data
    """
    st.write("### SQL Connection Test")

    conn = get_sql_connection()
    if conn:
        st.success("✅ Anslutning till DMFinance OK!")

        # Hämta sample data
        df = load_finance_data_from_sql(year=2026)

        if not df.empty:
            st.write(f"**Antal rader hämtade:** {len(df)}")
            st.write(f"**Unika KST:** {df['KST'].nunique()}")
            st.write(f"**Scenarios:** {df['Scenario'].unique()}")
            st.write("**Sample data:**")
            st.dataframe(df.head(10))
        else:
            st.warning("Ingen data hittades")
    else:
        st.error("❌ Kunde inte ansluta till DMFinance")

if __name__ == "__main__":
    # Test mode
    import streamlit as st
    st.title("SQL Data Loader - Test")
    test_sql_connection()
