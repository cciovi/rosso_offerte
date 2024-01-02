import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Offerte", 
    page_icon="💵", 
    layout="wide")

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db') 

def insert_offer(conn, data):
    query = '''
    INSERT INTO offerte (Articolo, Fornitore, Moq, Lead_time, Incoterms, Pagamento, Prezzo, Data_ins, Data_val)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn.execute(query, data)
    conn.commit()

def delete_offer(id):
    query = 'DELETE FROM offerte WHERE Id_off = ?'
    conn.execute(query, (id,))
    conn.commit()

def load_art():
    query = "SELECT Id_art, Descrizione FROM articoli"
    df = pd.read_sql_query(query, conn)
    return df['Descrizione'].tolist(), df['Id_art'].tolist()

def load_az():
    query = "SELECT Id_az, Nome FROM aziende"
    df = pd.read_sql_query(query, conn)
    return df['Nome'].tolist(), df['Id_az'].tolist()

def load_off(art, az):
    query = f"SELECT * FROM offerte WHERE Articolo = {art} AND Fornitore = {az}"
    df = pd.read_sql_query(query, conn)
    return df


def main():
    st.title('Offerte')
    
    tab1, tab2, = st.tabs(["Crea", "Elimina"])
    
    
    with tab1:
        st.write("Inserisci una nuova offerta")
        
        data_validita_dft = date.today() + timedelta(days=30)

        articoli, id_art = load_art()
        art = st.selectbox("Seleziona l'articolo", articoli, key="Sel_art")
        Id_Articolo = id_art[articoli.index(art)]
    

        aziende, id_az = load_az()
        az = st.selectbox("Seleziona il fornitore", aziende, key="Sel_az")
        Id_Azienda = id_az[aziende.index(az)]

        with st.form(key="frm_CreaOff", clear_on_submit=True):
            CrOff_art = st.text_input("Articolo", key="CrOff_art", value=Id_Articolo, disabled=True)
            CrOff_for = st.text_input("Fornitore", key="CrOff_for", value=Id_Azienda, disabled=True)
            CrOff_Moq = st.text_input("MOQ", key="CrOff_Moq")
            CrOff_Lead = st.text_input("Lead Time", key="CrOff_Lead")
            CrOff_Inco = st.text_input("Incoterms", key="Cr_Inco")
            CrOff_Pay = st.text_input("Termini di pagamento", key="CrOff_Pay")
            CrOff_Price = st.number_input("Prezzo", key="CrOff_Price", step=None)
            CrOff_Ins = st.date_input("Data inserimento", key="CrOff_Ins", value="today", format="DD/MM/YYYY")
            CrOff_Val = st.date_input("Data di validità", key="CrOff_Val", value=data_validita_dft, format="DD/MM/YYYY")
            CrOff_Submit = st.form_submit_button("Inserisci offerta")
        
        # Se premi il pulsante "Submit", inserisci i dati nel database
        if CrOff_Submit:
            if CrOff_Price == 0:
                st.warning("Attenzione! Il prezzo non può essere 0. Offerta non inserita.")
            else:
                data = (CrOff_art, CrOff_for, CrOff_Moq, CrOff_Lead, CrOff_Inco, CrOff_Pay, CrOff_Price, CrOff_Ins, CrOff_Val)
                insert_offer(conn, data)
                st.success('Offerta inserita con successo!')

    with tab2:
        st.write("Elimina un'offerta esistente")
        articoli, id_art = load_art()
        art = st.selectbox("Seleziona l'articolo", articoli, key="Md_Sel_art")
        Id_Articolo = id_art[articoli.index(art)]

        aziende, id_az = load_az()
        az = st.selectbox("Seleziona il fornitore", aziende, key="Md_Sel_az")
        Id_Azienda = id_az[aziende.index(az)]

        tabella = load_off(Id_Articolo, Id_Azienda)
        st.dataframe(tabella, use_container_width=True,  hide_index=True)

        with st.form(key="frm_CancOff", clear_on_submit=True):
            if art == " " or az == " ":
                CncOff = st.selectbox("ID", tabella['Id_off'], disabled=True)
                CncOff_Submit = st.form_submit_button("Elimina offerta", disabled=True)
            else:
                CncOff = st.selectbox("ID", tabella['Id_off'], disabled=False)
                if CncOff == None:
                    CncOff_Submit = st.form_submit_button("Elimina offerta", disabled=True)
                else:
                    CncOff_Submit = st.form_submit_button("Elimina offerta", disabled=False)

        if CncOff_Submit:
            delete_offer(CncOff)
            st.success('Offerta eliminata con successo!')



if __name__ == '__main__':
    main()

