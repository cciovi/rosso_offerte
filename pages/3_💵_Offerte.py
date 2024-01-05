import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta, datetime

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Offerte", 
    page_icon="💵", 
    layout="wide")

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db') 

def insert_offer(conn, data):
    query = '''
    INSERT INTO offerte (Articolo, Fornitore, Disponibilita, Moq, Lead_time, Incoterms, Pagamento, Prezzo, BBD, Data_ins, Data_val, Data_modifica)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
    query = f"SELECT * FROM offerte WHERE Articolo = {art} AND Fornitore = {az} ORDER BY Id_off DESC"
    df = pd.read_sql_query(query, conn)
    return df

# Carica tutti i dati dell'offerta selezionata nel form (se sono presenti più offerte)
def load_offert_details(conn, offer_id):
    query = "SELECT * FROM offerte WHERE Id_off = ?"
    df = pd.read_sql_query(query, conn, params=(offer_id,))
    return df.iloc[0] if not df.empty else None

# Modifica i dati di un'offerta esistente nel database
def update_data(conn, data, off_id):
    query = '''
    UPDATE offerte
    SET Disponibilita = ?, Moq = ?, Lead_time = ?, Incoterms = ?, Pagamento = ?, Prezzo = ?, BBD = ?, Data_val = ?, Data_modifica = ?
    WHERE Id_off = ?
    '''
    conn.execute(query, (*data, off_id))
    conn.commit()

def main():
    st.title('Offerte')
    
    tab1, tab2, tab3 = st.tabs(["Crea", "Modifica", "Elimina"])
    
    
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
            CrOff_art = Id_Articolo
            CrOff_for = Id_Azienda
            CrOff_Disp = st.text_input("Disponibilità", key="CrOff_Disp")
            CrOff_Moq = st.text_input("MOQ", key="CrOff_Moq")
            CrOff_Lead = st.text_input("Lead Time", key="CrOff_Lead")
            CrOff_Inco = st.text_input("Incoterms", key="Cr_Inco")
            CrOff_Pay = st.text_input("Termini di pagamento", key="CrOff_Pay")
            CrOff_Price = st.number_input("Prezzo", key="CrOff_Price", step=None)
            CrOff_Bbd = st.text_input("BBD", key="CrOff_Bbd")
            CrOff_Ins = st.date_input("Data inserimento", key="CrOff_Ins", value="today", format="DD/MM/YYYY")
            CrOff_Val = st.date_input("Data di validità", key="CrOff_Val", value=data_validita_dft, format="DD/MM/YYYY")
            CrOff_DataModifica = date.today()
            CrOff_Submit = st.form_submit_button("Inserisci offerta")
        
        # Se premi il pulsante "Submit", inserisci i dati nel database
        if CrOff_Submit:
            if CrOff_Price == 0:
                st.warning("Attenzione! Il prezzo non può essere 0. Offerta non inserita.")
            else:
                data = (CrOff_art, CrOff_for, CrOff_Disp, CrOff_Moq, CrOff_Lead, CrOff_Inco, CrOff_Pay, CrOff_Price, CrOff_Bbd, CrOff_Ins, CrOff_Val, CrOff_DataModifica)
                insert_offer(conn, data)
                st.success('Offerta inserita con successo!')
    
    with tab2:
        st.write("Modifica un'offerta")
        articoli, id_art = load_art()
        art = st.selectbox("Seleziona l'articolo", articoli, key="Md_Sel_art")
        Id_Articolo = id_art[articoli.index(art)]

        aziende, id_az = load_az()
        az = st.selectbox("Seleziona il fornitore", aziende, key="Md_Sel_az")
        Id_Azienda = id_az[aziende.index(az)]
        
        if art != " " and az != " ":
            tabella = load_off(Id_Articolo, Id_Azienda)
            
            if len(tabella) > 1:
                st.markdown('#')
                st.write("Sono presenti più offerte che corrispondono ai criteri di ricerca")
                st.dataframe(tabella, use_container_width=True,  hide_index=True)
                st.markdown('#')
                SelectedId = st.selectbox("Seleziona ID offerta da modificare", tabella['Id_off'])
                st.markdown('#')
                with st.form(key="frm_MdOff", clear_on_submit=True):
                    
                    offert_details = load_offert_details(conn, SelectedId)

                    if offert_details['Disponibilita'] is not None:
                        MdOff_Disp = st.text_input("Disponibilità", value=offert_details['Disponibilita'], key="MdOff_Disp")
                    else:
                        MdOff_Disp = st.text_input("Disponibilità", key="MdOff_Disp")

                    if offert_details['Moq'] is not None:
                        MdOff_Moq = st.text_input("MOQ", value=offert_details['Moq'] , key="MdOff_Moq")
                    else:
                        MdOff_Moq = st.text_input("MOQ", key="MdOff_Moq")

                    if offert_details['Lead_time'] is not None:
                        MdOff_Lead = st.text_input("Lead Time", value=offert_details['Lead_time'] , key="MdOff_Lead")
                    else:
                        MdOff_Lead = st.text_input("Lead Time", key="MdOff_Lead")

                    if offert_details['Incoterms'] is not None:
                        MdOff_Inco = st.text_input("Incoterms", value=offert_details['Incoterms'], key="MdOff_Inco")
                    else:
                        offert_details = st.text_input("Incoterms", key="MdOff_Inco")

                    if offert_details['Pagamento'] is not None:
                        MdOff_Pay = st.text_input("Termini di pagamento", value=offert_details['Pagamento'], key="MdOff_Pay")
                    else:
                        MdOff_Pay = st.text_input("Termini di pagamento", key="MdOff_Pay")

                    if offert_details['Prezzo'] is not None:
                        MdOff_Price = st.number_input("Prezzo", value=offert_details['Prezzo'], key="MdOff_Price", step=None)
                    else:
                        MdOff_Price = st.number_input("Prezzo", key="MdOff_Price", step=None)

                    if offert_details['BBD'] is not None:
                        MdOff_Bbd = st.text_input("BBD", value=offert_details['BBD'], key="MdOff_Bbd")
                    else:
                        MdOff_Bbd = st.text_input("BBD", key="MdOff_Bbd")

                    validita = datetime.strptime(offert_details['Data_val'], '%Y-%m-%d')
                    MdOff_Val = st.date_input("Data di validità", value=validita, key="MdOff_Val", format="DD/MM/YYYY")

                    Md_DataModifica = date.today()

                    MdOff_Submit = st.form_submit_button("Aggiorna offerta")

                    if MdOff_Submit:
                        data = (MdOff_Disp, MdOff_Moq, MdOff_Lead, MdOff_Inco, MdOff_Pay, MdOff_Price, MdOff_Bbd, MdOff_Val, Md_DataModifica)
                        update_data(conn, data, SelectedId)
                        st.success(f'Offerta con ID {SelectedId} aggiornata con successo!')

            elif len(tabella) == 1:
                with st.form(key="frm_MdOff", clear_on_submit=True):
                    MdOff_ID = tabella['Id_off'].iloc[0]

                    if tabella['Disponibilita'].iloc[0] is not None:
                        MdOff_Disp = st.text_input("Disponibilità", value=tabella['Disponibilita'].iloc[0], key="MdOff_Disp")
                    else:
                        MdOff_Disp = st.text_input("Disponibilità", key="MdOff_Disp")

                    if tabella['Moq'].iloc[0] is not None:
                        MdOff_Moq = st.text_input("MOQ", value=tabella['Moq'].iloc[0] , key="MdOff_Moq")
                    else:
                        MdOff_Moq = st.text_input("MOQ", key="MdOff_Moq")

                    if tabella['Lead_time'].iloc[0] is not None:
                        MdOff_Lead = st.text_input("Lead Time", value=tabella['Lead_time'].iloc[0] , key="MdOff_Lead")
                    else:
                        MdOff_Lead = st.text_input("Lead Time", key="MdOff_Lead")

                    if tabella['Incoterms'].iloc[0] is not None:
                        MdOff_Inco = st.text_input("Incoterms", value=tabella['Incoterms'].iloc[0], key="MdOff_Inco")
                    else:
                        MdOff_Inco = st.text_input("Incoterms", key="MdOff_Inco")

                    if tabella['Pagamento'].iloc[0] is not None:
                        MdOff_Pay = st.text_input("Termini di pagamento", value=tabella['Pagamento'].iloc[0], key="MdOff_Pay")
                    else:
                        MdOff_Pay = st.text_input("Termini di pagamento", key="MdOff_Pay")

                    if tabella['Prezzo'].iloc[0] is not None:
                        MdOff_Price = st.number_input("Prezzo", value=tabella['Prezzo'].iloc[0], key="MdOff_Price", step=None)
                    else:
                        MdOff_Price = st.number_input("Prezzo", key="MdOff_Price", step=None)

                    if tabella['BBD'].iloc[0] is not None:
                        MdOff_Bbd = st.text_input("BBD", value=tabella['BBD'].iloc[0], key="MdOff_Bbd")
                    else:
                        MdOff_Bbd = st.text_input("BBD", key="MdOff_Bbd")

                    validita = datetime.strptime(tabella['Data_val'].iloc[0], '%Y-%m-%d')
                    MdOff_Val = st.date_input("Data di validità", value=validita, key="MdOff_Val", format="DD/MM/YYYY")

                    Md_DataModifica = date.today()

                    MdOff_Submit = st.form_submit_button("Aggiorna offerta")

                    if MdOff_Submit:
                        data = (str(MdOff_Disp), str(MdOff_Moq), str(MdOff_Lead), str(MdOff_Inco), str(MdOff_Pay), MdOff_Price, str(MdOff_Bbd), MdOff_Val, Md_DataModifica)
                        update_data(conn, data, int(MdOff_ID))
                        st.success(f'Offerta con ID {MdOff_ID} aggiornata con successo!')

                             
            else:
                st.warning("Nessuna offerta disponibile")

    with tab3:
        st.write("Elimina un'offerta esistente")
        articoli, id_art = load_art()
        art = st.selectbox("Seleziona l'articolo", articoli, key="Cn_Sel_art")
        Id_Articolo = id_art[articoli.index(art)]

        aziende, id_az = load_az()
        az = st.selectbox("Seleziona il fornitore", aziende, key="Cn_Sel_az")
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

