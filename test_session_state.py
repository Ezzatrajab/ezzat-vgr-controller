"""
Test för att se vad som händer med session_state
"""

# Simulera ENHETER_DATA
ENHETER_DATA = {
    '601': {
        'månader': {
            '2026-03': {
                'intakter_totalt': {'actual': 810000, 'budget': 870000}
            }
        }
    }
}

print("Initial ENHETER_DATA:")
print(f"  601, Mars: {ENHETER_DATA['601']['månader']['2026-03']['intakter_totalt']['actual']:,} kr")

# Simulera uppdatering
def uppdatera_data():
    ENHETER_DATA['601']['månader']['2026-03']['intakter_totalt'] = {
        'actual': 76134,
        'budget': 660183
    }

uppdatera_data()

print("\nEfter uppdatering:")
print(f"  601, Mars: {ENHETER_DATA['601']['månader']['2026-03']['intakter_totalt']['actual']:,} kr")

# Men om scriptet laddas om...
print("\n--- SCRIPT RELOADS (simulerar Streamlit refresh) ---")

# ENHETER_DATA återställs till original
ENHETER_DATA = {
    '601': {
        'månader': {
            '2026-03': {
                'intakter_totalt': {'actual': 810000, 'budget': 870000}
            }
        }
    }
}

print("\nEfter reload:")
print(f"  601, Mars: {ENHETER_DATA['601']['månader']['2026-03']['intakter_totalt']['actual']:,} kr")
print("\n❌ PROBLEMET: Varje gång Streamlit kör scriptet återställs ENHETER_DATA!")
