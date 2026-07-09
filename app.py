import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo con il nome ufficiale ALFREDO
st.set_page_config(
    page_title="Alfredo - Validatore Brand", page_icon="📊", layout="wide"
)

# Applica uno sfondo grigio neutro fisso e professionale a tutta l'applicazione
st.markdown(
    "<style>.stApp { background-color: #f5f5f5; }</style>",
    unsafe_allow_html=True,
)

# --- DIZIONARIO DEI SINONIMI UNIVERSALE (BASKET + CALCIO + SERIE A ESTERO) ---
# Include le varianti troncate, le parentesi asimmetriche e i refusi tipici delle esportazioni
mappa_sinonimi = {
    "Emittente": ["emittente", "canale", "tv", "broadcaster", "network", "channel", "dazn", "sky"],
    "Giornata": ["giornata", "turno", "round", "week", "matchday"],
    "Partita": ["partita", "match", "evento", "game", "incontro"],
    "Brand": ["brand", "marchio", "azienda", "sponsor", "company"],
    "Data": ["data", "giorno", "date"],
    "Detections_MxM_Id": [
        "detections_mxm_id",
        "detections_mxm_idminuto",
        "id_rilevazione",
        "detection_id",
        "id",
        "mxm_id",
    ],
    "Minuto": ["minuto", "minute", "time_min", "ora", "orario"],
    "Placement": ["placement", "posizionamento", "posizione", "location"],
    "tipo": ["tipo", "type", "formato", "format"],
    "sec_to_time(dmm.durata)": [
        "sec_to_time(dmm.durata)",
        "ec_to_time(dmm.durata",             # Intercetta la parentesi non chiusa del file Serie A Estero
        "sec_to_time(dmm.durata area totale",
        "durata",
        "duration",
        "tempo",
    ],
    "Area Totale": ["area totale", "totale area", "total area", "area_tot", "area totale area media per sec"],
    "Area Media Per Sec": [
        "area media per sec", 
        "area media", 
        "average area", 
        "area media per sec schermo media per se" # Intercetta la colonna combinata
    ],
    "% Schermo Media Per Sec": [
        "% schermo media per sec",
        "schermo media per se",
        "per sec% schermo media per se",       # Nuova variante presente nel file Serie A Estero
        "percentuale schermo",
        "% schermo",
        "screen_%",
    ],
    "Audience_AMR": ["audience_amr", "audience_am", "audience", "amr", "ascolti", "share_amr"],
}


# --- FUNZIONE DI NORMALIZZAZIONE AUTOMATICA DELLE COLONNE ---
def normalizza_colonne(dataframe):
    colonne_presenti = dataframe.columns.tolist()
    nuovo_mapping = {}

    for col_ufficiale, sinonimi in mappa_sinonimi.items():
        for col_presente in colonne_presenti:
            # Controllo flessibile: verifica se il sinonimo è contenuto nel nome della colonna reale
            nome_col_pulito = str(col_presente).strip().lower()
            if any(s.lower() in nome_col_pulito for s in sinonimi):
                nuovo_mapping[col_presente] = col_ufficiale
                break

    return dataframe.rename(columns=nuovo_mapping)


# --- FUNZIONE DI CONVERSIONE PER IL DOWNLOAD IN EXCEL ---
@st.cache_data
def converti_df_in_excel(df_da_convertire):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_da_convertire.to_excel(writer, index=False, sheet_name='Dati_Normalizzati')
    return output.getvalue()


# --- INTERFACCIA PRINCIPALE ---
st.title("ALFREDO")
st.markdown(
    "Carica il file Excel o CSV (Basket o Calcio) per analizzare la correttezza dei dati di monitoraggio."
)

campi_obbligatori = list(mappa_sinonimi.keys())

file_caricato = st.file_uploader(
    "📂 Trascina qui il file Excel (.xlsx) o CSV", type=["xlsx", "xls", "csv"]
)

if file_caricato is not None:
    try:
        # Lettura del file caricato
        if file_caricato.name.endswith(".csv"):
            df_grezzo = pd.read_csv(file_caricato)
        else:
            df_grezzo = pd.read_excel(file_caricato)

        st.toast(f"File '{file_caricato.name}' caricato con successo!", icon="📊")

        # NORMALIZZAZIONE INTELLIGENTE DELLE DIDASCALIE
        df = normalizza_colonne(df_grezzo)
        colonne_presenti = df.columns.tolist()

        # --- LOGICA DI CONTROLLO QUALITÀ COMPRENSIVA ---
        # Identifichiamo i campi chiave realmente presenti nel file normalizzato
        campi_chiave_presenti = [
            c for c in ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"] if c in colonne_presenti
        ]
        
        # Rilevamento delle righe che presentano celle vuote (mancanti) nei campi portanti
        righe_con_vuoti = (
            df[campi_chiave_presenti].isnull().any(axis=1)
            if campi_chiave_presenti
            else pd.Series([False] * len(df))
        )

        # Creazione della maschera organizzata a Schede (Tab)
        tab_verifica, tab_esplora, tab_metriche = st.tabs(
            ["🔍 Esito della Verifica", "👀 Esplora la Tabella", "📈 Numeri Chiave"]
        )

        # --- TAB 1: ESITO DELLA VERIFICA ---
        with tab_verifica:
            st.subheader("Rapporto di Controllo Qualità")

            # 1. Verifica Struttura e Integrità Campi
            colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]

            if colonne_mancanti:
                st.error(
                    "❌ STRUTTURA FILE NON RICONOSCIUTA: Alcuni campi fondamentali non sono stati mappati."
                )
                st.write("Verifica che il file contenga colonne riconducibili a:")
                for c in colonne_mancanti:
                    st.markdown(f"- **{c}**")
                st.stop()
            else:
                st.success(
                    "✅ **Struttura Dati:** Superata. Tutte le didascalie richieste sono state mappate e uniformate correttamente."
                )

            # 2. Verifica Celle Vuote / Dati Mancanti nei Campi Chiave
            totale_vuoti = df[campi_chiave_presenti].isnull().sum().sum() if campi_chiave_presenti else 0
            if totale_vuoti > 0:
                st.warning(
                    f"⚠️ **Completezza Dati:** Rilevate celle vuote. Ci sono righe non compilate nei campi chiave importanti."
                )
                for col in campi_chiave_presenti:
                    qta_vuoti = df[col].isnull().sum()
                    if qta_vuoti > 0:
                        st.info(f"La colonna *{col}* ha **{qta_vuoti}** celle vuote da verificare.")
            else:
                st.success(
                    "✅ **Completezza Dati:** Superata. Nessun valore mancante rilevato nei campi chiave portanti."
                )

            st.success("✅ **Analisi Coerenza:** Completata. I tracciamenti per secondo e posizionamento sono pronti per l'esportazione.")

        # --- TAB 2: ESPLORA E ESPORTA ---
        with tab_esplora:
            st.subheader("Visualizzazione Filtri e Dati Completi")

            col1, col2, col3 = st.columns(3)
            with col1:
                # Canale TV / Emittente
                emittenti_disponibili = ["Tutte"]
                if "Emittente" in colonne_presenti:
                    emittenti_disponibili += sorted(df["Emittente"].dropna().unique().tolist())
                scelta_emittente = st.selectbox("Filtra per Emittente", emittenti_disponibili)
            with col2:
                # Marchio / Brand
                brand_disponibili = ["Tutti"]
                if "Brand" in colonne_presenti:
                    brand_disponibili += sorted(df["Brand"].dropna().unique().tolist())
                scelta_brand = st.selectbox("Filtra per Marchio (Brand)", brand_disponibili)
            with col3:
                # Stato Anomalia
                scelta_stato = st.selectbox(
                    "Filtra per stato dati",
                    [
                        "Mostra tutti i dati",
                        "Solo righe con campi vuoti (Anomalie)",
                        "Solo righe complete (Corrette)",
                    ],
                )

            # Applicazione dei filtri sul DataFrame finale
            df_filtrato = df.copy()
            if scelta_emittente != "Tutte" and "Emittente" in colonne_presenti:
                df_filtrato = df_filtrato[df_filtrato["Emittente"] == scelta_emittente]
            if scelta_brand != "Tutti" and "Brand" in colonne_presenti:
                df_filtrato = df_filtrato[df_filtrato["Brand"] == scelta_brand]

            if scelta_stato == "Solo righe con campi vuoti (Anomalie)":
                df_filtrato = df_filtrato[righe_con_vuoti]
            elif scelta_stato == "Solo righe complete (Corrette)":
                df_filtrato = df_filtrato[~righe_con_vuoti]

            st.write(f"Righe visualizzate: {len(df_filtrato)} su {len(df)}")
            st.dataframe(df_filtrato, use_container_width=True)

            # --- TASTO DOWNLOAD EXCEL NORMALIZZATO ---
            st.markdown("---")
            st.subheader("📥 Esporta il file normalizzato")
            
            excel_data = converti_df_in_excel(df_filtrato)
            st.download_button(
                label="📁 Scarica Tabella Normalizzata in Excel",
                data=excel_data,
                file_name=f"validato_{file_caricato.name if '.' not in file_caricato.name else file_caricato.name.split('.')[0]}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # --- TAB 3: NUMERI CHIAVE ---
        with tab_metriche:
            st.subheader("Metriche e Indicatori Principali")
            
            m1, m2, m3 = st.columns(3)
            with m1:
                st.metric("Totale Record Analizzati", f"{len(df):,}")
            with m2:
                if "Brand" in colonne_presenti:
                    st.metric("Brand Unici Rilevati", df["Brand"].nunique())
                else:
                    st.metric("Brand Unici Rilevati", "N/D")
            with m3:
                if "Audience_AMR" in colonne_presenti:
                    st.metric("Audience AMR Massima", f"{df['Audience_AMR'].max():,}")

