import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo (Solo ALFREDO)
st.set_page_config(
    page_title="ALFREDO", page_icon="📊", layout="wide"
)

# --- DIZIONARI DEI SINONIMI SPECIFICI ---
sinonimi_basket = {
    "Emittente": ["emittente", "canale", "tv"],
    "Giornata": ["giornata", "turno"],
    "Partita": ["partita", "match"],
    "Brand": ["brand", "marchio"],
    "Data": ["data", "giorno"],
    "Detections_MxM_Id": ["detections_mxm_id", "id_rilevazione", "id"],
    "Minuto": ["minuto", "minute"],
    "Placement": ["placement", "posizionamento"],
    "tipo": ["tipo", "type"],
    "sec_to_time(dmm.durata)": ["sec_to_time(dmm.durata)", "durata"],
    "Area Totale": ["area totale", "totale area"],
    "Area Media Per Sec": ["area media per sec", "area media"],
    "% Schermo Media Per Sec": ["% schermo media per sec", "percentuale schermo"],
    "Audience_AMR": ["audience_amr", "audience"]
}

sinonimi_calcio = {
    "Emittente": ["emittente", "canale", "tv", "broadcaster", "dazn"],
    "Giornata": ["giornata", "turno", "round"],
    "Partita": ["partita", "match", "evento"],
    "Brand": ["brand", "marchio", "sponsor"],
    "Data": ["data", "giorno"],
    "Detections_MxM_Id": ["detections_mxm_id", "detections_mxm_idminuto", "id_rilevazione", "detection_id"],
    "Minuto": ["minuto", "minute", "ora"],
    "Placement": ["placement", "posizionamento"],
    "tipo": ["tipo", "type"],
    "sec_to_time(dmm.durata)": ["sec_to_time(dmm.durata)", "ec_to_time(dmm.durata", "durata", "tempo"],
    "Area Totale": ["area totale", "totale area", "area totale area media per sec"],
    "Area Media Per Sec": ["area media per sec", "area media", "area media per sec schermo media per se"],
    "% Schermo Media Per Sec": ["% schermo media per sec", "schermo media per se", "per sec% schermo media per se"],
    "Audience_AMR": ["audience_amr", "audience_am", "audience", "amr"]
}

# --- FUNZIONE DI NORMALIZZAZIONE ---
def normalizza_colonne(dataframe, mappa_sinonimi):
    colonne_presenti = dataframe.columns.tolist()
    nuovo_mapping = {}
    for col_ufficiale, sinonimi in mappa_sinonimi.items():
        for col_presente in colonne_presenti:
            nome_col_pulito = str(col_presente).strip().lower()
            if any(s.lower() in nome_col_pulito for s in sinonimi):
                nuovo_mapping[col_presente] = col_ufficiale
                break
    return dataframe.rename(columns=nuovo_mapping)

def converti_df_in_excel(df_da_convertire):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df_da_convertire.to_excel(writer, index=False, sheet_name='Dati_Normalizzati')
    return output.getvalue()

# ==============================================================================
# BARRA LATERALE - SELEZIONE DELLO SPORT (LE DUE PAGINE SEPARATE)
# ==============================================================================
st.sidebar.title("🎮 ALFREDO MENU")
st.sidebar.markdown("Seleziona lo sport del report da analizzare per attivare la logica corretta.")
sport_selezionato = st.sidebar.radio(
    "Scegli la sezione:",
    ["🏀 Basket (Eurolega / LBA)", "⚽ Calcio (Serie A / Estero)"]
)

# ==============================================================================
# SEZIONE 1: BASKET (LOGICA ORIGINALE RIPARTENDO DA QUI)
# ==============================================================================
if sport_selezionato == "🏀 Basket (Eurolega / LBA)":
    st.title("ALFREDO - Sezione Basket 🏀")
    st.markdown("Carica i file di monitoraggio dell'Eurolega o della LBA. È attiva la verifica rigida dei duplicati specchio.")
    
    file_caricato = st.file_uploader("📂 Trascina qui il file Excel o CSV del Basket", type=["xlsx", "xls", "csv"], key="basket_file")
    
    if file_caricato is not None:
        try:
            df_grezzo = pd.read_csv(file_caricato) if file_caricato.name.endswith(".csv") else pd.read_excel(file_caricato)
            st.toast("File Basket caricato!", icon="🏀")
            
            df = normalizza_colonne(df_grezzo, sinonimi_basket)
            colonne_presenti = df.columns.tolist()
            
            # Controllo colonne obbligatorie basket
            campi_obbligatori = list(sinonimi_basket.keys())
            colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]
            
            if colonne_mancanti:
                st.error("❌ La struttura del file Basket non è corretta. Mancano:")
                for c in colonne_mancanti: st.markdown(f"- **{c}**")
                st.stop()
                
            # LOGICA CONTROLLO DOPPIONI BASKET (Quella corretta e verificata)
            colonne_controllo_doppione = ["Data", "Detections_MxM_Id", "Placement", "Minuto", "tipo", "sec_to_time(dmm.durata)", "Area Totale", "Area Media Per Sec", "% Schermo Media Per Sec"]
            colonne_effettive = [c for c in colonne_controllo_doppione if c in colonne_presenti]
            
            doppione_basket = df.duplicated(subset=colonne_effettive, keep=False)
            righe_con_vuoti = df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().any(axis=1)
            righe_con_errori = righe_con_vuoti | doppione_basket
            
            tab_ver, tab_esp, tab_met = st.tabs(["🔍 Verifica", "👀 Esplora", "📈 Metriche"])
            
            with tab_ver:
                st.subheader("Rapporto Qualità Basket")
                st.success("✅ Struttura campi verificata con successo.")
                
                if df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().sum().sum() > 0:
                    st.warning("⚠️ Rilevate celle vuote nei campi chiave.")
                else:
                    st.success("✅ Nessun valore mancante nei campi chiave.")
                    
                num_doppioni = doppione_basket.sum()
                if num_doppioni > 0:
                    st.error(f"🚨 **ALLARME RIGHE DUPLICATE (BASKET):** Trovati **{num_doppioni}** meri doppioni specchio contigui!")
                else:
                    st.success("✅ **Univocità Rilevazioni:** Superata. Nessun doppione specchio contiguo.")
                    
            with tab_esp:
                col1, col2, col3 = st.columns(3)
                with col1: scelta_emi = st.selectbox("Filtra Emittente", ["Tutte"] + sorted(df["Emittente"].dropna().unique().tolist()))
                with col2: scelta_brd = st.selectbox("Filtra Marchio", ["Tutti"] + sorted(df["Brand"].dropna().unique().tolist()))
                with col3: scelta_err = st.selectbox("Filtra Errori", ["Mostra tutti", "Solo ERRORI (Vuoti o Doppioni)", "Solo CORRETTE"])
                
                df_fil = df.copy()
                if scelta_emi != "Tutte": df_fil = df_fil[df_fil["Emittente"] == scelta_emi]
                if scelta_brd != "Tutti": df_fil = df_fil[df_fil["Brand"] == scelta_brd]
                if scelta_err == "Solo ERRORI (Vuoti o Doppioni)": df_fil = df_fil[righe_con_errori]
                elif scelta_err == "Solo CORRETTE": df_fil = df_fil[~righe_con_errori]
                
                st.dataframe(df_fil, use_container_width=True)
                st.markdown("---")
                excel_data = converti_df_in_excel(df_fil)
                st.download_button(label="📁 Scarica Report Basket Normalizzato", data=excel_data, file_name="Alfredo_Basket_Cleaned.xlsx")
                
            with tab_met:
                st.subheader("Indicatori Basket")
                st.metric("Totale Record Analizzati", f"{len(df):,}")
                st.metric("Brand Rilevati", df["Brand"].nunique())
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Basket: {e}")

# ==============================================================================
# SEZIONE 2: CALCIO (NUOVA PAGINA DEDICATA E ISOLATA)
# ==============================================================================
else:
    st.title("ALFREDO - Sezione Calcio ⚽")
    st.markdown("Carica i file di monitoraggio del Calcio. È attiva la verifica con i sinonimi dedicati alla Serie A e campionati esteri.")
    
    file_caricato_calcio = st.file_uploader("📂 Trascina qui il file Excel o CSV del Calcio", type=["xlsx", "xls", "csv"], key="calcio_file")
    
    if file_caricato_calcio is not None:
        try:
            df_grezzo = pd.read_csv(file_caricato_calcio) if file_caricato_calcio.name.endswith(".csv") else pd.read_excel(file_caricato_calcio)
            st.toast("File Calcio caricato!", icon="⚽")
            
            df = normalizza_colonne(df_grezzo, sinonimi_calcio)
            colonne_presenti = df.columns.tolist()
            
            # Controllo colonne obbligatorie calcio
            campi_obbligatori = list(sinonimi_calcio.keys())
            colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]
            
            if colonne_mancanti:
                st.error("❌ La struttura del file Calcio non è corretta. Mancano:")
                for c in colonne_mancanti: st.markdown(f"- **{c}**")
                st.stop()
                
            # Logica controllo doppioni e vuoti per il Calcio
            colonne_controllo_doppione = ["Data", "Detections_MxM_Id", "Placement", "Minuto", "tipo", "sec_to_time(dmm.durata)", "Area Totale", "Area Media Per Sec", "% Schermo Media Per Sec"]
            colonne_effettive = [c for c in colonne_controllo_doppione if c in colonne_presenti]
            
            doppione_calcio = df.duplicated(subset=colonne_effettive, keep=False)
            righe_con_vuoti = df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().any(axis=1)
            righe_con_errori = righe_con_vuoti | doppione_calcio
            
            # Interfaccia a Tab per il Calcio
            tab_ver, tab_esp, tab_met = st.tabs(["🔍 Verifica", "👀 Esplora", "📈 Metriche"])



