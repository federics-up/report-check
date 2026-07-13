import io
import pandas as pd
import streamlit as st

# Configurazione della pagina largo (Solo ALFREDO)
st.set_page_config(
    page_title="ALFREDO🤖", page_icon="📊", layout="wide"
)

# --- MIGLIORIE GRAFICHE (NON MODIFICANO LA LOGICA DEI CONTROLLI) ---
st.markdown("""
<style>
    .block-container {
        padding-top: 1.8rem;
        padding-bottom: 3rem;
        max-width: 1450px;
    }

    .alfredo-hero {
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 20px;
        padding: 24px 28px;
        margin: 4px 0 22px 0;
        border: 1px solid rgba(128, 128, 128, 0.22);
        border-radius: 18px;
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(235,242,250,0.80));
        box-shadow: 0 8px 24px rgba(15, 23, 42, 0.07);
    }

    .alfredo-hero h1 {
        margin: 0;
        font-size: 2.15rem;
        line-height: 1.1;
    }

    .alfredo-hero p {
        margin: 8px 0 0 0;
        opacity: 0.72;
        font-size: 1rem;
    }

    .alfredo-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        white-space: nowrap;
        padding: 10px 16px;
        border-radius: 999px;
        font-weight: 750;
        letter-spacing: 0.02em;
        border: 1px solid rgba(128, 128, 128, 0.20);
    }

    .badge-basket { background: rgba(255, 149, 0, 0.14); }
    .badge-calcio { background: rgba(52, 199, 89, 0.14); }
    .badge-invernali { background: rgba(10, 132, 255, 0.14); }

    .upload-card {
        padding: 16px 20px;
        margin: 6px 0 12px 0;
        border-radius: 14px;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-left: 5px solid #2f80ed;
        background: rgba(247, 250, 255, 0.72);
    }

    .upload-card h3 { margin: 0; font-size: 1.05rem; }
    .upload-card p { margin: 5px 0 0 0; opacity: 0.70; }

    div[data-testid="stMetric"] {
        padding: 17px 18px;
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 14px;
        background: rgba(255,255,255,0.65);
        box-shadow: 0 5px 16px rgba(15, 23, 42, 0.05);
    }

    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(128, 128, 128, 0.20);
        border-radius: 12px;
        overflow: hidden;
    }

    section[data-testid="stSidebar"] {
        border-right: 1px solid rgba(128, 128, 128, 0.18);
    }

    .sidebar-footer {
        margin-top: 28px;
        padding-top: 14px;
        border-top: 1px solid rgba(128,128,128,0.20);
        font-size: 0.82rem;
        opacity: 0.66;
    }

    @media (max-width: 800px) {
        .alfredo-hero { align-items: flex-start; flex-direction: column; }
    }
</style>
""", unsafe_allow_html=True)

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

# --- DIZIONARIO DEI SINONIMI SPORT INVERNALI ---
sinonimi_sport_invernali = {
    "Emittente": ["emittente", "canale", "tv", "broadcaster", "dazn"],
    "Giornata": ["giornata", "turno", "round", "specialita", "specialità", "disciplina"],
    "Partita": ["partita", "match", "evento", "gara"],
    "Brand": ["brand", "marchio", "sponsor"],
    "Data": ["data", "giorno"],
    "Detections_MxM_Id": ["detections_mxm_id", "detections_mxm_idminuto", "id_rilevazione", "detection_id"],
    "Minuto": ["minuto", "minute", "ora"],
    "Placement": ["placement", "posizionamento"],
    "sec_to_time(dmm.durata)": ["sec_to_time(dmm.durata)", "ec_to_time(dmm.durata", "durata", "tempo"],
    "Area_Totale": ["area_totale", "area totale", "totale area"],
    "Area_Media_x_Sec": ["area_media_x_sec", "area media x sec", "area media per sec", "area media"],
    "Percentuale_Schermo_Med": ["percentuale_schermo_med", "percentuale schermo med", "% schermo media per sec", "percentuale schermo"],
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


# --- COMPONENTI GRAFICI RIUTILIZZABILI ---
def mostra_intestazione(sport, emoji, descrizione, classe_badge):
    st.markdown(
        f"""
        <div class="alfredo-hero">
            <div>
                <h1>ALFREDO 🤖</h1>
                <p>{descrizione}</p>
            </div>
            <div class="alfredo-badge {classe_badge}">{emoji} {sport.upper()}</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def mostra_area_caricamento(titolo):
    st.markdown(
        f"""
        <div class="upload-card">
            <h3>📂 {titolo}</h3>
            <p>Formati supportati: Excel XLSX, XLS e CSV</p>
        </div>
        """,
        unsafe_allow_html=True
    )


def mostra_riepilogo(df, righe_con_errori, doppioni):
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Record analizzati", f"{len(df):,}")
    col2.metric("Brand rilevati", df["Brand"].nunique())
    col3.metric("Righe con errori", int(righe_con_errori.sum()))
    col4.metric("Duplicati", int(doppioni.sum()))

    if int(righe_con_errori.sum()) == 0:
        st.success("✅ FILE APPROVATO — Nessun errore rilevato")
    else:
        st.error(
            f"❌ FILE DA CONTROLLARE — "
            f"{int(righe_con_errori.sum())} righe presentano problemi"
        )


def mostra_dataframe_evidenziato(df_visualizzato, righe_vuote, righe_duplicate):
    righe_vuote_filtrate = righe_vuote.reindex(df_visualizzato.index, fill_value=False)
    righe_duplicate_filtrate = righe_duplicate.reindex(df_visualizzato.index, fill_value=False)

    def evidenzia_riga(riga):
        if bool(righe_duplicate_filtrate.loc[riga.name]):
            return ["background-color: rgba(255, 99, 71, 0.22)"] * len(riga)
        if bool(righe_vuote_filtrate.loc[riga.name]):
            return ["background-color: rgba(255, 193, 7, 0.22)"] * len(riga)
        return [""] * len(riga)

    st.caption("Legenda: rosso = riga duplicata · giallo = campo chiave vuoto")
    st.dataframe(
        df_visualizzato.style.apply(evidenzia_riga, axis=1),
        use_container_width=True,
        height=520
    )

# ==============================================================================
# BARRA LATERALE - SELEZIONE DELLO SPORT (LE DUE PAGINE SEPARATE)
# ==============================================================================
st.sidebar.title("🎮 ALFREDO MENU")
st.sidebar.caption("Report Quality Control")
st.sidebar.markdown("Seleziona lo sport del report da analizzare per attivare la logica corretta.")
sport_selezionato = st.sidebar.radio(
    "Scegli la sezione:",
    ["🏀 Basket (Eurolega / LBA)", "⚽ Calcio (Serie A / Estero)", "⛷️ Sport Invernali"]
)

st.sidebar.markdown(
    '<div class="sidebar-footer">ALFREDO · Versione grafica 1.1</div>',
    unsafe_allow_html=True
)

# ==============================================================================
# SEZIONE 1: BASKET (LOGICA ORIGINALE RIPARTENDO DA QUI)
# ==============================================================================
if sport_selezionato == "🏀 Basket (Eurolega / LBA)":
    st.title("ALFREDO - Sezione Basket 🏀")
    st.markdown("Carica i file di monitoraggio dell'Eurolega o della LBA. È attiva la verifica rigida dei duplicati specchio.")
    mostra_intestazione("Basket", "🏀", "Controllo qualità dei report di monitoraggio", "badge-basket")
    mostra_area_caricamento("Carica il report Basket")
    
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

            mostra_riepilogo(df, righe_con_errori, doppione_basket)
            
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
                
                mostra_dataframe_evidenziato(df_fil, righe_con_vuoti, doppione_basket)
                st.markdown("---")
                excel_data = converti_df_in_excel(df_fil)
                st.download_button(label="📁 Scarica Report Basket Normalizzato", data=excel_data, file_name="Alfredo_Basket_Cleaned.xlsx", use_container_width=True, type="primary")
                
            with tab_met:
                st.subheader("Indicatori Basket")
                st.metric("Totale Record Analizzati", f"{len(df):,}")
                st.metric("Brand Rilevati", df["Brand"].nunique())
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Basket: {e}")

# ==============================================================================
# SEZIONE 2: CALCIO (NUOVA PAGINA DEDICATA E ISOLATA)
# ==============================================================================
elif sport_selezionato == "⚽ Calcio (Serie A / Estero)":
    st.title("ALFREDO - Sezione Calcio ⚽")
    st.markdown("Carica i file di monitoraggio del Calcio. È attiva la verifica con i sinonimi dedicati alla Serie A e campionati esteri.")
    mostra_intestazione("Calcio", "⚽", "Controllo qualità dei report di monitoraggio", "badge-calcio")
    mostra_area_caricamento("Carica il report Calcio")
    
    file_caricato_calcio = st.file_uploader("📂 Trascina qui il file Excel o CSV del Calcio", type=["xlsx", "xls", "csv"], key="calcio_file")
    
    if file_caricato_calcio is not None:
        try:
            # Lettura del file in base all'estensione
            df_grezzo = pd.read_csv(file_caricato_calcio) if file_caricato_calcio.name.endswith(".csv") else pd.read_excel(file_caricato_calcio)
            st.toast("File Calcio caricato!", icon="⚽")
            
            # Normalizzazione colonne con sinonimi specifici del calcio
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

            mostra_riepilogo(df, righe_con_errori, doppione_calcio)
            
            # Interfaccia a Tab per il Calcio
            tab_ver, tab_esp, tab_met = st.tabs(["🔍 Verifica", "👀 Esplora", "📈 Metriche"])
            
            with tab_ver:
                st.subheader("Rapporto Qualità Calcio")
                st.success("✅ Struttura campi verificata con successo.")
                
                if df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().sum().sum() > 0:
                    st.warning("⚠️ Rilevate celle vuote nei campi chiave del Calcio.")
                else:
                    st.success("✅ Nessun valore mancante nei campi chiave.")
                    
                num_doppioni = doppione_calcio.sum()
                if num_doppioni > 0:
                    st.error(f"🚨 **ALLARME RIGHE DUPLICATE (CALCIO):** Trovati **{num_doppioni}** doppioni rilevati!")
                else:
                    st.success("✅ **Univocità Rilevazioni:** Superata. Nessun duplicato trovato.")
                    
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
                
                mostra_dataframe_evidenziato(df_fil, righe_con_vuoti, doppione_calcio)
                st.markdown("---")
                excel_data = converti_df_in_excel(df_fil)
                st.download_button(label="📁 Scarica Report Calcio Normalizzato", data=excel_data, file_name="Alfredo_Calcio_Cleaned.xlsx", use_container_width=True, type="primary")
                
            with tab_met:
                st.subheader("Indicatori Calcio")
                st.metric("Totale Record Analizzati", f"{len(df):,}")
                st.metric("Brand Rilevati", df["Brand"].nunique())
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Calcio: {e}")

# ==============================================================================
# SEZIONE 3: SPORT INVERNALI (NUOVA PAGINA DEDICATA E ISOLATA)
# ==============================================================================
else:
    st.title("ALFREDO - Sezione Sport Invernali ⛷️")
    st.markdown("Carica i file di monitoraggio degli Sport Invernali. È attiva la verifica con i campi del file di riferimento.")
    mostra_intestazione("Sport Invernali", "⛷️", "Controllo qualità dei report di monitoraggio", "badge-invernali")
    mostra_area_caricamento("Carica il report Sport Invernali")
    
    file_caricato_invernali = st.file_uploader("📂 Trascina qui il file Excel o CSV degli Sport Invernali", type=["xlsx", "xls", "csv"], key="invernali_file")
    
    if file_caricato_invernali is not None:
        try:
            # Lettura del file in base all'estensione
            df_grezzo = pd.read_csv(file_caricato_invernali) if file_caricato_invernali.name.endswith(".csv") else pd.read_excel(file_caricato_invernali)
            st.toast("File Sport Invernali caricato!", icon="⛷️")
            
            # Normalizzazione colonne con sinonimi specifici degli sport invernali
            df = normalizza_colonne(df_grezzo, sinonimi_sport_invernali)
            colonne_presenti = df.columns.tolist()
            
            # Controllo colonne obbligatorie sport invernali
            campi_obbligatori = list(sinonimi_sport_invernali.keys())
            colonne_mancanti = [c for c in campi_obbligatori if c not in colonne_presenti]
            
            if colonne_mancanti:
                st.error("❌ La struttura del file Sport Invernali non è corretta. Mancano:")
                for c in colonne_mancanti: st.markdown(f"- **{c}**")
                st.stop()
                
            # Logica controllo doppioni e vuoti per gli Sport Invernali
            colonne_controllo_doppione = ["Data", "Detections_MxM_Id", "Placement", "Minuto", "sec_to_time(dmm.durata)", "Area_Totale", "Area_Media_x_Sec", "Percentuale_Schermo_Med"]
            colonne_effettive = [c for c in colonne_controllo_doppione if c in colonne_presenti]
            
            doppione_invernali = df.duplicated(subset=colonne_effettive, keep=False)
            righe_con_vuoti = df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().any(axis=1)
            righe_con_errori = righe_con_vuoti | doppione_invernali

            mostra_riepilogo(df, righe_con_errori, doppione_invernali)
            
            # Interfaccia a Tab per gli Sport Invernali
            tab_ver, tab_esp, tab_met = st.tabs(["🔍 Verifica", "👀 Esplora", "📈 Metriche"])
            
            with tab_ver:
                st.subheader("Rapporto Qualità Sport Invernali")
                st.success("✅ Struttura campi verificata con successo.")
                
                if df[["Emittente", "Brand", "Detections_MxM_Id", "Audience_AMR"]].isnull().sum().sum() > 0:
                    st.warning("⚠️ Rilevate celle vuote nei campi chiave degli Sport Invernali.")
                else:
                    st.success("✅ Nessun valore mancante nei campi chiave.")
                    
                num_doppioni = doppione_invernali.sum()
                if num_doppioni > 0:
                    st.error(f"🚨 **ALLARME RIGHE DUPLICATE (SPORT INVERNALI):** Trovati **{num_doppioni}** doppioni rilevati!")
                else:
                    st.success("✅ **Univocità Rilevazioni:** Superata. Nessun duplicato trovato.")
                    
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
                
                mostra_dataframe_evidenziato(df_fil, righe_con_vuoti, doppione_invernali)
                st.markdown("---")
                excel_data = converti_df_in_excel(df_fil)
                st.download_button(label="📁 Scarica Report Sport Invernali Normalizzato", data=excel_data, file_name="Alfredo_Sport_Invernali_Cleaned.xlsx", use_container_width=True, type="primary")
                
            with tab_met:
                st.subheader("Indicatori Sport Invernali")
                st.metric("Totale Record Analizzati", f"{len(df):,}")
                st.metric("Brand Rilevati", df["Brand"].nunique())
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Sport Invernali: {e}")
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Sport Invernali: {e}")
