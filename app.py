import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo (Solo ALFREDO)
st.set_page_config(
    page_title="ALFREDO 🤖", page_icon="📊", layout="wide"
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

sinonimi_generici = {
    "Emittente": ["emittente", "canale", "tv", "broadcaster", "sky"],
    "Giornata": ["giornata", "turno", "round", "gara"],
    "Partita": ["partita", "match", "evento", "incontro"],
    "Brand": ["brand", "marchio", "sponsor"],
    "Data": ["data", "giorno"],
    "Detections_MxM_Id": ["detections_mxm_id", "id_rilevazione", "detection_id"],
    "Minuto": ["minuto", "minute", "ora"],
    "Placement": ["placement", "posizionamento"],
    "tipo": ["tipo", "type"],
    "sec_to_time(dmm.durata)": ["sec_to_time(dmm.durata)", "durata", "tempo"],
    "Area Totale": ["area totale", "totale area"],
    "Area Media Per Sec": ["area media per sec", "area media"],
    "% Schermo Media Per Sec": ["% schermo media per sec", "percentuale schermo"],
    "Audience_AMR": ["audience_amr", "audience", "amr"]
}

# --- FUNZIONI DI SERVIZIO ---
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

# --- CALLBACK PER CAMBIARE STATO IN SICUREZZA ---
def imposta_sport(chiave_sport):
    st.session_state.sport_selezionato = chiave_sport

def resetta_sport():
    st.session_state.sport_selezionato = None

# --- GESTIONE DELLO STATO DELLA PAGINA ---
if "sport_selezionato" not in st.session_state:
    st.session_state.sport_selezionato = None

# Mappa dei pulsanti
dizionario_sport = {
    "🏀 Basket (Eurolega / LBA)": "🏀 Basket",
    "⚽ Calcio (Serie A / Estero)": "⚽ Calcio",
    "🏐 Pallavolo / Volley": "🏐 Volley",
    "🎾 Tennis": "🎾 Tennis",
    "🏎️ Motori (F1 / MotoGP)": "🏎️ Motori",
    "🏈 Football Americano": "🏈 Football",
    "🏉 Rugby": "🏉 Rugby",
    "🏓 Tennis da Tavolo": "🏓 Ping Pong",
    "🏸 Badminton": "🏸 Badminton",
    "🏒 Hockey": "🏒 Hockey",
    "🎯 Freccette": "🎯 Freccette",
    "🥊 Sport da Combattimento": "🥊 Combattimento"
}

# ==============================================================================
# MENU INIZIALE A BOTTONI
# ==============================================================================
if st.session_state.sport_selezionato is None:
    st.title("🤖 ALFREDO - Dashboard Principale")
    st.markdown("### Seleziona la palla o l'icona dello sport per avviare l'analisi del report:")
    st.write("")

    colonne = st.columns(4)
    for i, (chiave_sport, etichetta_bottone) in enumerate(dizionario_sport.items()):
        con_colonna = colonne[i % 4]
        with con_colonna:
            # L'uso di on_click evita il loop grafico e previene la pagina bianca
            st.button(
                etichetta_bottone, 
                use_container_width=True, 
                key=f"btn_{i}", 
                on_click=imposta_sport, 
                args=(chiave_sport,)
            )

# ==============================================================================
# PAGINE DI ANALISI
# ==============================================================================
else:
    sport_selezionato = st.session_state.sport_selezionato

    st.sidebar.title("🤖 ALFREDO")
    st.sidebar.button("⬅️ Torna al Menu Principale", on_click=resetta_sport)
    st.sidebar.markdown(f"**Sezione attiva:**\n{sport_selezionato}")

    # --------------------------------------------------------------------------
    # SEZIONE 1: BASKET (LOGICA SPECIALE RIGIDA)
    # --------------------------------------------------------------------------
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
                
                campi_obbligatori = list(sinonimi_basket.keys())
                colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]
                
                if colonne_mancanti:
                    st.error("❌ La struttura del file Basket non è corretta. Mancano:")
                    for c in colonne_mancanti: st.markdown(f"- **{c}**")
                    st.stop()
                    
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
