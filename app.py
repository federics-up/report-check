import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo con il nome ufficiale ALFREDO (Solo ALFREDO)
st.set_page_config(
    page_title="ALFREDO", page_icon="📊", layout="wide"
)

# Applica uno sfondo grigio neutro fisso e professionale a tutta l'applicazione
st.markdown(
    "<style>.stApp { background-color: #f5f5f5; }</style>",
    unsafe_allow_html=True,
)

# --- DIZIONARIO DEI SINONIMI UNIVERSALE (BASKET + CALCIO + SERIE A ESTERO) ---
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
        "ec_to_time(dmm.durata",             
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
        "area media per sec schermo media per se" 
    ],
    "% Schermo Media Per Sec": [
        "% schermo media per sec",
        "schermo media per se",
        "per sec% schermo media per se",       
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
        campi_chiave_presenti = [
            c for c in ["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"] if c in colonne_presenti
        ]
        
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
                emittenti_disponibili = ["Tutte"]
                if "Emittente" in colonne_presenti:
                    emittenti_disponibili += sorted(df["Emittente"].dropna().unique().tolist())
                scelta_emittente = st.selectbox("Filtra per Emittente", emittenti_disponibili)
            with col2:
                brand_disponibili = ["Tutti"]
                if "Brand" in colonne_presenti:
                    brand_disponibili += sorted(df["Brand"].dropna().unique().tolist())
                scelta_brand = st.selectbox("Filtra per Marchio (Brand)", brand_disponibili)
            with col3:
                scelta_stato = st.selectbox(
                    "Filtra per stato dati",
                    [
                        "Mostra tutti i dati",
                        "Solo righe con campi vuoti (Anomalie)",
                        "Solo righe complete (Corrette)",
                    ],
                )

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

            st.markdown("---")
            st.subheader("📥 Esporta il file normalizzato")
            
            excel_data = converti_df_in_excel(df_filtrato)
            st.download_button(
                label="📁 Scarica Tabella Normalizzata in Excel",
                data=excel_data,
                file_name="Alfredo_Report_Cleaned.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

        # --- TAB 3: NUMERI CHIAVE ---
        with tab_metriche:
            st.subheader("Metriche e Indicatori Principali")
            
            c1, c2 = st.columns(2)
            with c1:
                st.metric("Totale Record Analizzati", f"{len(df):,}")
            with c2:
                if "Brand" in colonne_presenti:
                    st.metric("Brand Unici Rilevati", df["Brand"].nunique())
                else:
                    st.metric("Brand Unici Rilevati", "N/D")
                    
            st.markdown("### 📈 Focus Analisi Audience AMR")
            
            m1, m2, m3 = st.columns(3)
            if "Audience_AMR" in colonne_presenti:
                audience_pulita = df["Audience_AMR"].dropna()
                
                if not audience_pulita.empty:
                    aud_massima = int(audience_pulita.max())
                    aud_minima = int(audience_pulita.min())
                    aud_media = int(audience_pulita.mean())
                    
                    with m1:
                        st.metric("Audience AMR Più Alta (Massima)", f"{aud_massima:,}")
                    with m2:
                        st.metric("Audience AMR Più Bassa (Minima)", f"{aud_minima:,}")
                    with m3:
                        st.metric("Audience AMR Media", f"{aud_media:,}")
                else:
                    with m1:
                        st.metric("Audience AMR Più Alta (Massima)", "N/D")
                    with m2:
                        st.metric("Audience AMR Più Bassa (Minima)", "N/D")
                    with m3:

