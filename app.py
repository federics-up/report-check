# ==============================================================================
# SEZIONE 2: CALCIO (NUOVA PAGINA DEDICATA E ISOLATA)
# ==============================================================================
else:
    st.title("ALFREDO - Sezione Calcio ⚽")
    st.markdown("Carica i file di monitoraggio del Calcio. È attiva la verifica con i sinonimi dedicati alla Serie A e campionati esteri.")
    
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
                
                st.dataframe(df_fil, use_container_width=True)
                st.markdown("---")
                excel_data = converti_df_in_excel(df_fil)
                st.download_button(label="📁 Scarica Report Calcio Normalizzato", data=excel_data, file_name="Alfredo_Calcio_Cleaned.xlsx")
                
            with tab_met:
                st.subheader("Indicatori Calcio")
                st.metric("Totale Record Analizzati", f"{len(df):,}")
                st.metric("Brand Rilevati", df["Brand"].nunique())
                
        except Exception as e:
            st.error(f"❌ Errore elaborazione Calcio: {e}")
