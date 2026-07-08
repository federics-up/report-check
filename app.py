import pandas as pd
import streamlit as st

# Configurazione della pagina per sfruttare tutto lo schermo (Layout largo)
st.set_page_config(
    page_title="Validatore Brand Eurolega", page_icon="📊", layout="wide"
)

st.title("📊 Validatore Dati Esposizione Brand")
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

        # --- LOGICA ALLARME DOPPIONE CONTIGUO ---
        colonne_controllo_doppione = [
            "Data",
            "Detections_MxM_Id",
            "Placement",
            "Minuto",
            "tipo",
            "sec_to_time(dmm.durata)",
            "Area Totale",
            "Area Media Per Sec",
            "% Schermo Media Per Sec",
        ]

        # Controlliamo se una riga è identica alla riga precedente o successiva solo per queste colonne specifiche
        doppione_precedente = df.duplicated(
            subset=colonne_controllo_doppione, keep=False
        )

        # Definiamo i criteri per i campi chiave vuoti
        campi_chiave_vuoti = ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]
        righe_con_vuoti = df[campi_chiave_vuoti].isnull().any(axis=1)

        # Unione degli errori reali (Celle vuote o errore di doppione contiguo specchio)
        righe_con_errori = righe_con_vuoti | doppione_precedente

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
                st.stop()
            else:
                st.success(
                    "✅ **Struttura Campi:** Superata. Tutti i 14 campi imprescindibili sono presenti."
                )

            # 2. Controllo Celle Vuote
            vuoti_per_colonna = {
                col: df[col].isnull().sum() for col in campi_chiave_vuoti
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

            # 3. Controllo Doppioni Contigui
            num_doppioni = doppione_precedente.sum()
            if num_doppioni > 0:
                st.error(
                    f"🚨 **ALLARME RIGHE DUPLICATE:** Trovati meri doppioni dei dati! Ci sono **{num_doppioni}** righe che hanno gli stessi identici valori di un'altra riga (stesso ID, Data, Minuto, Tipo, Durata e Area)."
                )
                st.info(
                    "Consiglio: Vai nella scheda 'Esplora la Tabella' e attiva il filtro degli ERRORI per isolarle e rimuoverle."
                )
            else:
                st.success(
                    "✅ **Univocità Rilevazioni:** Superata. Nessuna riga presenta doppioni specchio contigui."
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
                        "Solo righe con ERRORI (Vuoti o Doppioni Contigui)",
                        "Solo righe CORRETTE",
                    ],
                )

            # Applicazione dei filtri alla tabella mostrata
            df_filtrato = df.copy()

            if scelta_emittente != "Tutte":
                df_filtrato = df_filtrato[
                    df_filtrato["Emittente"] == scelta_emittente
                ]

            if scelta_brand != "Tutti":
                df_filtrato = df_filtrato[df_filtrato["Brand"] == scelta_brand]

            # Filtro Errori
            if (
                scelta_errore
                == "Solo righe con ERRORI (Vuoti o Doppioni Contigui)"
            ):
                df_filtrato = df_filtrato[righe_con_errori]
            elif scelta_errore == "Solo righe CORRETTE":
                df_filtrato = df_filtrato[~righe_con_errori]

            st.write(f"Righe visualizzate: {len(df_filtrato)} su {len(df)}")
            st.dataframe(df_filtrato, use_container_width=True)

        # --- TAB 3: NUMERI CHIAVE ---
        with tab_metriche:
            st.subheader("Panoramica Rapida dell'Assegno")

            tot_rilevazioni = len(df)
            brand_unici = df["Brand"].nunique()

            # Layout pulito a due colonne senza la voce delle partite
            m1, m2 = st.columns(2)
            m1.metric("Totale Rilevazioni (Righe)", f"{tot_rilevazioni:,}")
            m2.metric("Marchi Monitorati", brand_unici)

    except Exception as e:
        st.error(f"Errore imprevisto durante la lettura della maschera: {e}")
