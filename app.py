import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo con il nome ufficiale ALFREDO
st.set_page_config(
    page_title="ALFREDO", page_icon="📊", layout="wide"
)

# Applica uno sfondo grigio neutro fisso e professionale a tutta l'applicazione
st.markdown(
    "<style>.stApp { background-color: #f5f5f5; }</style>",
    unsafe_allow_html=True,
)

# --- DIZIONARIO DEI SINONIMI PER L'ACCOGLIENZA DI ALTRI EXCEL ---
mappa_sinonimi = {
    "Emittente": ["emittente", "canale", "tv", "broadcaster", "network", "channel"],
    "Giornata": ["giornata", "turno", "round", "week", "matchday"],
    "Partita": ["partita", "match", "evento", "game", "incontro"],
    "Brand": ["brand", "marchio", "azienda", "sponsor", "company"],
    "Data": ["data", "giorno", "date"],
    "Detections_MxM_Id": [
        "detections_mxm_id",
        "id_rilevazione",
        "detection_id",
        "id",
        "mxm_id",
    ],
    "Minuto": ["minuto", "minute", "time_min"],
    "Placement": ["placement", "posizionamento", "posizione", "location"],
    "tipo": ["tipo", "type", "formato", "format"],
    "sec_to_time(dmm.durata)": [
        "sec_to_time(dmm.durata)",
        "durata",
        "duration",
        "tempo",
        "durata_secondi",
    ],
    "Area Totale": ["area totale", "totale area", "total area", "area_tot"],
    "Area Media Per Sec": ["area media per sec", "area media", "average area"],
    "% Schermo Media Per Sec": [
        "% schermo media per sec",
        "percentuale schermo",
        "% schermo",
        "screen_%",
    ],
    "Audience_AMR": ["audience_amr", "audience", "amr", "ascolti", "share_amr"],
}


# --- FUNZIONE DI NORMALIZZAZIONE AUTOMATICA DELLE COLONNE ---
def normalizza_colonne(dataframe):
    colonne_presenti = dataframe.columns.tolist()
    nuovo_mapping = {}

    for col_ufficiale, sinonimi in mappa_sinonimi.items():
        for col_presente in colonne_presenti:
            if str(col_presente).strip().lower() in [
                s.lower() for s in sinonimi
            ]:
                nuovo_mapping[col_presente] = col_ufficiale
                break

    return dataframe.rename(columns=nuovo_mapping)


# --- INTERFACCIA PRINCIPALE ---
st.title("ALFREDO")
st.markdown(
    "Carica il file Excel o CSV per analizzare la correttezza dei dati di monitoraggio."
)

campi_obbligatori = list(mappa_sinonimi.keys())

file_caricato = st.file_uploader(
    "📂 Trascina qui il file Excel (.xlsx) o CSV", type=["xlsx", "xls", "csv"]
)

if file_caricato is not None:
    try:
        if file_caricato.name.endswith(".csv"):
            df_grezzo = pd.read_csv(file_caricato)
        else:
            df_grezzo = pd.read_excel(file_caricato)

        st.toast(f"File '{file_caricato.name}' caricato!", icon="📊")

        # NORMALIZZAZIONE DELLE DIDASCALIE
        df = normalizza_colonne(df_grezzo)

        # --- LOGICA ALLARME DOPPIONE CONTIGUO ---
        colonne_presenti = df.columns.tolist()
        colonne_controllo = [
            c for c in campi_obbligatori if c in colonne_presenti and c != "Emittente"
        ]

        if len(colonne_controllo) > 3:
            doppione_precedente = df.duplicated(subset=colonne_controllo, keep=False)
        else:
            doppione_precedente = pd.Series([False] * len(df))

        campi_chiave_vuoti = [
            c for c in ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"] if c in colonne_presenti
        ]
        righe_con_vuoti = (
            df[campi_chiave_vuoti].isnull().any(axis=1)
            if campi_chiave_vuoti
            else pd.Series([False] * len(df))
        )
        righe_con_errori = righe_con_vuoti | doppione_precedente

        tab_verifica, tab_esplora, tab_metriche = st.tabs(
            ["🔍 Esito della Verifica", "👀 Esplora la Tabella", "📈 Numeri Chiave"]
        )

        # --- TAB 1: ESITO DELLA VERIFICA ---
        with tab_verifica:
            st.subheader("Rapporto di Controllo Qualità")

            colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]

            if colonne_mancanti:
                st.error(
                    "❌ ERRORE CRITICO: La struttura del file non è riconosciuta!"
                )
                st.write(
                    "Mancano colonne compatibili con le seguenti didascalie richieste:"
                )
                for c in colonne_mancanti:
                    st.markdown(f"- **{c}**")
                st.stop()
            else:
                st.success(
                    "✅ **Struttura Campi:** Traduzione completata! Tutte le 14 didascalie sono state associate correttamente."
                )

            totale_vuoti = df[campi_chiave_vuoti].isnull().sum().sum()
            if totale_vuoti > 0:
                st.warning(
                    f"⚠️ **Celle Vuote Rilevate:** Trovate righe non compilate."
                )
            else:
                st.success(
                    "✅ **Completezza Dati:** Superata. Nessuna cella vuota nei campi chiave."
                )

            num_doppioni = doppione_precedente.sum()
            if num_doppioni > 0:
                st.error(
                    f"🚨 **ALLARME RIGHE DUPLICATE:** Trovati **{num_doppioni}** meri doppioni specchio contigui!"
                )
            else:
                st.success(
                    "✅ **Univocità Rilevazioni:** Superata. Nessuna riga presenta doppioni contigui."
                )

        # --- TAB 2: ESPLORA E ESPORTA ---
        with tab_esplora:
            st.subheader("Visualizzazione Filtri e Dati Completi")

            col1, col2, col3 = st.columns(3)
            with col1:
                lista_emittenti = ["Tutte"] + sorted(
                    df["Emittente"].dropna().unique().tolist()
                )
                scelta_emittente = st.selectbox(
                    "Filtra per Canale TV", lista_emittenti
                )
            with col2:
                lista_brand = ["Tutti"] + sorted(df["Brand"].dropna().unique().tolist())
                scelta_brand = st.selectbox("Filtra per Marchio", lista_brand)
            with col3:
                scelta_errore = st.selectbox(
                    "Filtra per stato errore",
                    [
                        "Mostra tutti i dati",
                        "Solo righe con ERRORI (Vuoti o Doppioni Contigui)",
                        "Solo righe CORRETTE",
                    ],
                )

            df_filtrato = df.copy()
            if scelta_emittente != "Tutte":
                df_filtrato = df_filtrato[df_filtrato["Emittente"] == scelta_emittente]
            if scelta_brand != "Tutti":
                df_filtrato = df_filtrato[df_filtrato["Brand"] == scelta_brand]

            if scelta_errore == "Solo righe con ERRORI (Vuoti o Doppioni Contigui)":
                df_filtrato = df_filtrato[righe_con_errori]
            elif scelta_errore == "Solo righe CORRETTE":
                df_filtrato = df_filtrato[~righe_con_errori]

            st.write(f"Righe visualizzate: {len(df_filtrato)} su {len(df)}")
            st.dataframe(df_filtrato, use_container_width=True)

            # --- TASTO DOWNLOAD EXCEL PULITO ---
            st.markdown("---")
            st.subheader("📥 Esporta Report Corretto")
            df_pulito_da_scaricare = df[~righe_con_errori]

            towrite = io.BytesIO()
            with pd.ExcelWriter(towrite, engine="openpyxl") as writer:
                df_pulito_da_scaricare.to_excel(
                    writer, index=False, sheet_name="Dati_Puliti"
                )
            towrite.seek(0)

            st.download_button(
                label="🚀 Scarica il File Excel ripulito da tutti gli errori",
                data=towrite,
                file_name=f"Alfredo_Report_Cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )

        # --- TAB 3: NUMERI CHIAVE ---
        with tab_metriche:
            st.subheader("Panoramica Rapida dell'Assegno")
            tot_rilevazioni = len(df)
            brand_unici = df["Brand"].nunique()

            m1, m2 = st.columns(2)
            m1.metric("Totale Rilevazioni (Righe)", f"{tot_rilevazioni:,}")
            m2.metric("Marchi Monitorati", brand_unici)

    except Exception as e:
        st.error(f"Errore imprevisto durante la lettura della maschera: {e}")


