import pandas as pd
import streamlit as st

st.title("Validatore Dati Esposizione Brand")
st.write("Carica il tuo file Excel o CSV per avviare il controllo automatico.")

# Elenco dei campi imprescindibili richiesti
campi_obbligatori = [
    "Emittente",
    "Giornata",
    "Partita",
    "Brand",
    "Data",
    "Detections_MxM_Id",
    "Minuto",
    "Placement",
    "tipo",
    "sec_to_time(dmm.durata)",
    "Area Totale",
    "Area Media Per Sec",
    "% Schermo Media Per Sec",
    "Audience_AMR",
]

# Bottone di caricamento file sul web
file_caricato = st.file_uploader(
    "Scegli un file", type=["xlsx", "xls", "csv"]
)

if file_caricato is not None:
    try:
        if file_caricato.name.endswith(".csv"):
            df = pd.read_csv(file_caricato)
        else:
            df = pd.read_excel(file_caricato)

        st.success(f"File '{file_caricato.name}' caricato con successo!")

        # 1. Verifica Struttura Colonne
        colonne_presenti = df.columns.tolist()
        colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]

        st.subheader("1. Verifica Struttura Colonne")
        if colonne_mancanti:
            st.error(
                "❌ ERRORE CRITICO! Mancano le seguenti colonne imprescindibili:"
            )
            for c in colonne_mancanti:
                st.write(f"- {c}")
        else:
            st.success("✅ Ottimo. Tutti i campi richiesti sono presenti.")

            # Se la struttura è corretta, procediamo con gli altri controlli
            # 2. Controllo Celle Vuote
            st.subheader("2. Verifica Celle Vuote")
            campi_chiave = ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]
            vuoti_trovati = False
            for col in campi_chiave:
                num_vuoti = df[col].isnull().sum()
                if num_vuoti > 0:
                    st.warning(
                        f"⚠️ Attenzione: '{col}' presenta {num_vuoti} righe vuote."
                    )
                    vuoti_trovati = True
            if not vuoti_trovati:
                st.success(
                    "✅ Nessun valore mancante rilevato nei campi chiave."
                )

            # 3. Controllo Duplicati
            st.subheader("3. Verifica Coerenza ID Rilevazione")
            id_duplicati = df["Detections_MxM_Id"].duplicated().sum()
            if id_duplicati > 0:
                st.warning(
                    f"⚠️ Attenzione: Rilevati {id_duplicati} codici 'Detections_MxM_Id' ripetuti."
                )
            else:
                st.success("✅ Coerenza ID verificata. Ogni rilevazione è univoca.")

    except Exception as e:
        st.error(f"Errore durante l'analisi del file: {e}")
