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

        # --- LOGICA CORRETTA PER VERIFICA ALTERNANZA LOGO/TEXT ---
        # Ordiniamo i dati per ID e per tipo per garantire la sequenzialità temporale
        df_ordinato = df.sort_values(by=["Detections_MxM_Id", "tipo"]).reset_index(
            drop=True
        )

        # Creiamo una serie che ci dice se l'elemento successivo ha lo stesso 'tipo' (es: logo dopo logo)
        # e se appartiene allo stesso ID o a ID immediatamente contigui
        tipo_uguale_successivo = df_ordinato["tipo"] == df_ordinato["tipo"].shift(-1)
        id_vicino = (
            df_ordinato["Detections_MxM_Id"].shift(-1)
            - df_ordinato["Detections_MxM_Id"]
        ) <= 1

        # L'allarme si attiva solo se due tipi uguali sono contigui/nello stesso ID
        df_ordinato["Allarme_Mancata_Alternanza"] = tipo_uguale_successivo & id_vicino

        # Riportiamo l'allarme sul DataFrame originale usando l'indice o mappando
        # Per sicurezza verifichiamo gli ID che hanno fallito il test di alternanza
        id_con_errore_alternanza = df_ordinato[
            df_ordinato["Allarme_Mancata_Alternanza"] == True
        ]["Detections_MxM_Id"].unique()

        # Definiamo le righe con errori reali
        campi_chiave = ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]
        righe_con_vuoti = df[campi_chiave].isnull().any(axis=1)
        righe_errore_alternanza = df["Detections_MxM_Id"].isin(
            id_con_errore_alternanza
        )

        # Unione degli errori reali (Celle vuote o errore di alternanza logo/text)
        righe_con_errori = righe_con_vuoti | righe_errore_alternanza

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

            # 3. Controllo Alternanza e Allarme Logo/Text (Nuova Logica)
            num_errori_alternanza = len(id_con_errore_alternanza)
            if num_errori_alternanza > 0:
                st.error(
                    f"🚨 **ALLARME ALTERNANZA:** Trovate anomalie nella sequenza! Ci sono **{num_errori_alternanza}** ID in cui 'logo' e 'text' non si alternano correttamente (es. duplicati consecutivi dello stesso tipo)."
                )
                st.info(
                    "Consiglio: Usa la scheda 'Esplora la Tabella' e filtra per ERRORI per vedere gli ID bloccati."
                )
            else:
                st.success(
                    "✅ **Alternanza Logo/Text:** Superata. La presenza contemporanea di logo e testo rispetta l'alternanza corretta."
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
                        "Solo righe con ERRORI (Vuoti o Mancata Alternanza)",
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

            # Filtro Errori Ottimizzato
            if scelta_errore == "Solo righe con ERRORI (Vuoti o Mancata Alternanza)":
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
            partite_totali = df["Partita"].nunique()

            m1, m2, m3 = st.columns(3)
            m1.metric("Totale Rilevazioni (Righe)", f"{tot_rilevazioni:,}")
            m2.metric("Marchi Monitorati", brand_unici)
            m3.metric("Partite in Archivio", partite_totali)

    except Exception as e:
        st.error(f"Errore imprevisto durante la lettura della maschera: {e}")
