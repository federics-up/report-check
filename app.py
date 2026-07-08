import pandas as pd
import streamlit as st

# Configurazione della pagina largo con il nuovo nome ufficiale ALFREDO
st.set_page_config(
    page_title="Alfredo - Validatore Brand", page_icon="🎮", layout="wide"
)


# --- FUNZIONE PER CAMBIARE LO SFONDO IN PIXEL ART IN BASE ALLO SPORT ---
def applica_sfondo_sport_pixel(dataframe):
    testo_partite = (
        " ".join(dataframe["Partita"].astype(str).dropna().unique()).lower()
    )

    parole_basket = [
        "bologna",
        "madrid",
        "monaco",
        "atene",
        "istanbul",
        "tel aviv",
        "milano",
        "kaunas",
        "belgrado",
        "barcelona",
        "valencia",
        "munich",
        "baskonia",
        "basket",
    ]
    parole_calcio = ["milan", "inter", "juventus", "roma", "lazio", "napoli", "fcalcio"]

    if any(parola in testo_partite for parola in parole_basket):
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #e65c00;
                background-image: radial-gradient(#ff9e43 20%, transparent 20%),
                                  radial-gradient(#ff9e43 20%, transparent 20%);
                background-size: 40px 40px;
                background-position: 0 0, 20px 20px;
            }
            .stApp::after {
                content: "🏀🕺\\A 🏃‍♂️💨";
                white-space: pre;
                font-size: 90px;
                position: fixed;
                bottom: 20px;
                right: 30px;
                opacity: 0.25;
                z-index: 0;
                font-family: monospace;
            }
            h1, p, label, .stMarkdown, .stTabs button {
                color: #ffffff !important;
                text-shadow: 2px 2px 0px #000000;
            }
            .stTabs button[aria-selected="true"] {
                color: #e65c00 !important;
                background-color: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("🏀 **Sport: PALLACANESTRO (8-BIT)**")

    elif any(parola in testo_partite for parola in parole_calcio):
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #1e532b;
                background-image: linear-gradient(45deg, #276b37 25%, transparent 25%, transparent 75%, #276b37 75%, #276b37),
                                  linear-gradient(45deg, #276b37 25%, transparent 25%, transparent 75%, #276b37 75%, #276b37);
                background-size: 60px 60px;
                background-position: 0 0, 30px 30px;
            }
            .stApp::after {
                content: "⚽🏃‍♂️\\A      🧱🧤";
                white-space: pre;
                font-size: 90px;
                position: fixed;
                bottom: 20px;
                right: 30px;
                opacity: 0.25;
                z-index: 0;
                font-family: monospace;
            }
            h1, p, label, .stMarkdown, .stTabs button {
                color: #ffffff !important;
                text-shadow: 2px 2px 0px #000000;
            }
            .stTabs button[aria-selected="true"] {
                color: #1e532b !important;
                background-color: white !important;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )
        st.sidebar.markdown("⚽ **Sport: CALCIO (8-BIT)**")

    else:
        st.markdown(
            """
            <style>
            .stApp {
                background-color: #f5f5f5;
            }
            </style>
            """,
            unsafe_allow_html=True,
        )


# --- INTERFACCIA GRAFICA ---
st.title("🕹️ Alfredo - Pixel Sports Edition")
st.markdown(
    "Carica il file Excel o CSV per analizzare la correttezza dei dati di monitoraggio."
)

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

file_caricato = st.file_uploader(
    "📂 Trascina qui il file Excel (.xlsx) o CSV", type=["xlsx", "xls", "csv"]
)

if file_caricato is not None:
    try:
        if file_caricato.name.endswith(".csv"):
            df = pd.read_csv(file_caricato)
        else:
            df = pd.read_excel(file_caricato)

        st.toast(f"File '{file_caricato.name}' caricato!", icon="🎮")

        # ATTIVAZIONE DELLO SFONDO DINAMICO PIXEL ART
        applica_sofndo_sport_pixel = applica_sfondo_sport_pixel(
            df
        )  # Correzione chiamata interna se necessario
        applica_sfondo_sport_pixel(df)

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
        doppione_precedente = df.duplicated(
            subset=colonne_controllo_doppione, keep=False
        )

        campi_chiave_vuoti = ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]
        righe_con_vuoti = df[campi_chiave_vuoti].isnull().any(axis=1)
        righe_con_errori = righe_con_vuoti | doppione_precedente

        tab_verifica, tab_esplora, tab_metriche = st.tabs(
            ["🔍 Esito della Verifica", "👀 Esplora la Tabella", "📈 Numeri Chiave"]
        )

        # --- TAB 1: ESITO DELLA VERIFICA ---
        with tab_verifica:
            st.subheader("Rapporto di Controllo Qualità")

            colonne_presenti = df.columns.tolist()
            colonne_mancanti = [
                c for c in campi_obbligatori if c not in colonne_presenti
            ]

            if colonne_mancanti:
                st.error(
                    "❌ ERRORE CRITICO: La struttura del file non è corretta!"
                )
                for c in colonne_mancanti:
                    st.markdown(f"- **{c}**")
                st.stop()
            else:
                st.success(
                    "✅ **Struttura Campi:** Superata. Tutti i 14 campi imprescindibili sono presenti."
                )

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

            num_doppioni = doppione_precedente.sum()
            if num_doppioni > 0:
                st.error(
                    f"🚨 **ALLARME RIGHE DUPLICATE:** Trovati meri doppioni dei dati! Ci sono **{num_doppioni}** righe specchio contigue."
                )
            else:
                st.success(
                    "✅ **Univocità Rilevazioni:** Superata. Nessuna riga presenta doppioni specchio contigui."
                )

        # --- TAB 2: ESPLORA LA TABELLA ---
        with tab_esplora:
            st.subheader("Visualizzazione Filtri e Dati Completi")

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

            df_filtrato = df.copy()
            if scelta_emittente != "Tutte":
                df_filtrato = df_filtrato[
                    df_filtrato["Emittente"] == scelta_emittente
                ]
            if scelta_brand != "Tutti":
                df_filtrato = df_filtrato[df_filtrato["Brand"] == scelta_brand]

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

            m1, m2 = st.columns(2)
            m1.metric("Totale Rilevazioni (Righe)", f"{tot_rilevazioni:,}")
            m2.metric("Marchi Monitorati", brand_unici)

    except Exception as e:
        st.error(f"Errore imprevisto durante la lettura della maschera: {e}")
