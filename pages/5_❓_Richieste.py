import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Richieste", 
    page_icon="❓", 
    layout="wide",)

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db') 

def load_art():
    query = "SELECT Id_art, Descrizione FROM articoli"
    df = pd.read_sql_query(query, conn)
    return df['Descrizione'].tolist(), df['Id_art'].tolist()

def load_az():
    query = "SELECT Id_az, Nome FROM aziende"
    df = pd.read_sql_query(query, conn)
    return df['Nome'].tolist(), df['Id_az'].tolist()

def load_requests():
    query = ''' 
        SELECT
            aziende.Nome AS Nome_Cliente,
            articoli.Descrizione AS Descrizione_Articolo,
            richieste.Quantita,
            richieste.Target,
            richieste.Destinazione,
            richieste.Note
        FROM
            richieste
        JOIN
            aziende ON richieste.Cliente = aziende.Id_az 
        JOIN
            articoli ON richieste.Articolo = articoli.Id_art 
        ORDER BY richieste.Id_ric DESC;
    '''  
    df_raw = pd.read_sql_query(query, conn) # Qui i campi vuoti sono "None"
    df = df_raw.fillna("")  # Qui i campi vuoti sono ""
    return df

def insert_request(conn, data):
    query = '''
    INSERT INTO richieste (Cliente, Articolo, Quantita, Target, Destinazione, Note, Data_creazione, Data_modifica)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn.execute(query, data)
    conn.commit()

def main():
    st.title('Richieste')
    
    tab1, tab2, tab3 = st.tabs(["Nuova", "Modifica", "Elimina"])

    with tab1:
        articoli, id_art = load_art()
        art = st.selectbox("Seleziona l'articolo", articoli, key="Sel_art")
        Id_Articolo = id_art[articoli.index(art)]

        aziende, id_az = load_az()
        az = st.selectbox("Seleziona il cliente", aziende, key="Sel_cli")
        Id_Cliente = id_az[aziende.index(az)]
        
        with st.form(key="frm_CreaRich", clear_on_submit=True):
                CrRic_Cli = Id_Cliente
                CrRic_Art = Id_Articolo
                CrRic_Qta = st.text_input("Quantità", key="CrRic_qta")
                CrRic_Dest = st.text_input("Destinazione", key="CrRic_dest")
                CrRic_Target = st.number_input("Prezzo target", key="CrRic_Target")
                CrRic_Note = st.text_area ("Note", key="CrRic_Note")
                CrRic_DataCreazione = date.today()
                CrRic_DataModifica = date.today()
                CrRic_Submit = st.form_submit_button("Inserisci richiesta")


            # Se premi il pulsante "Submit", inserisci i dati nel database
        if CrRic_Submit:
            data = (CrRic_Cli, CrRic_Art, CrRic_Qta, CrRic_Target, CrRic_Dest, CrRic_Note, CrRic_DataCreazione, CrRic_DataModifica)
            insert_request(conn, data)
            st.success('Richiesta inserita con successo!')

        req = load_requests()
        st.dataframe(req, use_container_width=True,  hide_index=True)
    

if __name__ == '__main__':
    main()