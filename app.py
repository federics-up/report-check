import pandas as pd
import streamlit as st

# Configurazione della pagina per sfruttare tutto lo schermo (Layout largo)
st.set_page_config(
    page_title="Validatore Brand Eurolega", page_icon="📊", layout="wide"
)

st.title("ALFREDO")
st.markdown(
    "Carica il file Excel o CSV per analizzare la correttezza dei dati di monitoraggio."
)

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

# Maschera di caricamento principale in evidenza
file_caricato = st.file_uploader(
    "📂 Trascina qui il file Excel (.xlsx) o CSV", type=["xlsx", "xls", "csv"]
)

if file_caricato is not None:
    try:
        # Caricamento intelligente del file
        if file_caricato.name.endswith(".csv"):
            df = pd.read_csv(file_caricato)
        else:
            df = pd.read_excel(file_caricato)

        st.toast(f"File '{file_caricato.name}' caricato!", icon="✅")

        # Pre-calcolo degli errori per il filtro dinamico
        campi_chiave = ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]

        # Identifica le righe che hanno almeno una cella vuota nei campi chiave
        righe_con_vuoti = df[campi_chiave].isnull().any(axis=1)

        # Identifica le righe che hanno un ID duplicato
        righe_con_id_duplicato = df["Detections_MxM_Id"].duplicated(keep=False)

        # Unione di tutti i tipi di errore
        righe_con_errori = righe_con_vuoti | righe_con_id_duplicato

        # Creazione della maschera a Schede (Tab) per organizzare lo spazio
        tab_verifica, tab_esplora, tab_metriche = st.tabs(
            ["🔍 Esito della Verifica", "👀 Esplora la Tabella", "📈 Numeri Chiave"]
        )

        # --- TAB 1: ESITO DELLA VERIFICA ---
        with tab_verifica:
            st.subheader("Rapporto di Controllo Qualità")

            # 1. Verifica Struttura Colonne
            colonne_presenti = df.columns.tolist()
            colonne_mancanti = [
                c for c in campi_obbligatori if c not in colonne_presenti
            ]

            if colonne_mancanti:
                st.error(
                    "❌ ERRORE CRITICO: La struttura del file non è corretta!"
                )
                st.write(
                    "Mancano le seguenti colonne fondamentali nel tuo file:"
                )
                for c in colonne_mancanti:
                    st.markdown(f"- **{c}**")
                st.stop()  # Blocca l'esecuzione se mancano colonne
            else:
                st.success(
                    "✅ **Struttura Campi:** Superata. Tutti i 14 campi imprescindibili sono presenti."
                )

            # 2. Controllo Celle Vuote
            vuoti_per_colonna = {
                col: df[col].isnull().sum() for col in campi_chiave
            }
            totale_vuoti = sum(vuoti_per_colonna.values())

            if totale_vuoti > 0:
                st.warning(
                    f"⚠️ **Celle Vuote Rilevate:** Ci sono alcune righe non compilate nei campi chiave."
                )
                for col, qta in vuoti_per_colonna.items():
                    if qta > 0:
                        st.info(f"La colonna *{col}* ha **{qta}** righe vuote.")
            else:
                st.success(
                    "✅ **Completezza Dati:** Superata. Nessuna cella vuota nei campi chiave."
                )

            # 3. Controllo Duplicati dell'ID
            id_duplicati = df["Detections_MxM_Id"].duplicated().sum()
            if id_duplicati > 0:
                st.error(
                    f"❌ **Rilevazioni Duplicate:** Attenzione, ci sono **{id_duplicati}** ID di rilevazione inseriti più di una volta!"
                )
                st.info(
                    "Consiglio: Verifica se hai importato due volte lo stesso blocco di dati."
                )
            else:
                st.success(
                    "✅ **Univocità Rilevazioni:** Superata. Ogni ID di rilevazione (`Detections_MxM_Id`) è unico."
                )

        # --- TAB 2: ESPLORA LA TABELLA ---
        with tab_esplora:
            st.subheader("Visualizzazione Filtri e Dati Completi")
            st.write(
                "Usa questa sezione per cercare rapidamente informazioni all'interno del file appena caricato."
            )

            # Filtri dinamici nella maschera distribuiti su 3 colonne
            col1, col2, col3 = st.columns(3)
            with col1:
                lista_emittenti = ["Tutte"] + sorted(
                    df["Emittente"].dropna().unique().tolist()
                )
                scelta_emittente = st.selectbox(
                    "Filtra per Canale TV (Emittente)", lista_emittenti
                )
            with col2:
                lista_brand = ["Tutti"] + sorted(
                    df["Brand"].dropna().unique().tolist()
                )
                scelta_brand = st.selectbox(
                    "Filtra per Marchio (Brand)", lista_brand
                )
            with col3:
                scelta_errore = st.selectbox(
                    "Filtra per stato errore",
                    [
                        "Mostra tutti i dati",
                        "Solo righe con ERRORI (Vuoti o Duplicati)",
                        "Solo righe CORRETTE",
                    ],
                )

            # Applicazione dei filtri alla tabella mostrata
            df_filtrato = df.copy()

            # Filtro Emittente
            if scelta_emittente != "Tutte":
                df_filtrato = df_filtrato[
                    df_filtrato["Emittente"] == scelta_emittente
                ]

            # Filtro Brand
            if scelta_brand != "Tutti":
                df_filtrato = df_filtrato[df_filtrato["Brand"] == scelta_brand]

            # Filtro Errori (Logica Colonna 3)
            if scelta_errore == "Solo righe con ERRORI (Vuoti o Duplicati)":
                df_filtrato = df_filtrato[righe_con_errori]
            elif scelta_errore == "Solo righe CORRETTE":
                df_filtrato = df_filtrato[~righe_con_errori]

            st.write(f"Righe visualizzate: {len(df_filtrato)} su {len(df)}")
            st.dataframe(df_filtrato, use_container_width=True)

        # --- TAB 3: NUMERI CHIAVE ---
        with tab_metriche:
            st.subheader("Panoramica Rapida dell'Assegno")

            # Calcolo di metriche al volo per dare utilità alla maschera
            tot_rilevazioni = len(df)
            brand_unici = df["Brand"].nunique()
            partite_totali = df["Partita"].nunique()

            m1, m2, m3 = st.columns(3)
            m1.metric("Totale Rilevazioni (Righe)", f"{tot_rilevazioni:,}")
            m2.metric("Marchi Monitorati", brand_unici)
            m3.metric("Partite in Archivio", partite_totali)

    except Exception as e:
        st.error(f"Errore imprevisto durante la lettura della maschera: {e}")
