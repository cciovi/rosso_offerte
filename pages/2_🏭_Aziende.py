import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Aziende", 
    page_icon="🏭", 
    layout="wide")

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db')

def insert_data(conn, data):
    query = '''
    INSERT INTO aziende (Nome, Paese, Data_creazione, Data_modifica)
    VALUES (?, ?, ?, ?)
    '''
    conn.execute(query, data)
    conn.commit()

def load_country():
    query = "Select Nome_paese FROM paesi"
    df = pd.read_sql_query(query, conn)
    return df

def load_data():
    query = "SELECT Id_az, Nome FROM aziende"
    df = pd.read_sql_query(query, conn)
    return df['Nome'].tolist(), df['Id_az'].tolist()

def load_supplier_details(conn, supplier_id):
    query = "SELECT * FROM aziende WHERE Id_az = ?"
    df = pd.read_sql_query(query, conn, params=(supplier_id,))
    return df.iloc[0] if not df.empty else None

def update_data(conn, data, supplier_id):
    query = '''
    UPDATE aziende
    SET Nome = ?, Paese = ?, Data_modifica = ? 
    WHERE Id_az = ?
    '''
    conn.execute(query, (*data, supplier_id))
    conn.commit()


def delete_data(supplier_id):
    query = 'DELETE FROM aziende WHERE Id_az = ?'
    conn.execute(query, (supplier_id,))
    conn.commit()


def main():
    st.title('Aziende')
    nazioni = load_country()
    
    tab1, tab2, tab3 = st.tabs(["Crea", "Modifica", "Elimina"])
    with tab1:
        st.write("Inserisci una nuova azienda (cliente o fornitore)")

        with st.form(key="frm_Crea", clear_on_submit=True):
            Cr_Nom = st.text_input("Nome", key="Cr_nom")
            Cr_Pae = st.selectbox("Paese", nazioni, key="Cr_pae")
            Cr_Submit = st.form_submit_button("Inserisci azienda")
            Cr_DataCreazione = date.today()
            Cr_DataModifica = date.today()

        # Se premi il pulsante "Submit", inserisci i dati nel database
        if Cr_Submit:
            if len(Cr_Nom) < 3:
                st.warning("Attenzione! Nome azienda non valido.")
            else:
                data = (Cr_Nom, Cr_Pae, Cr_DataCreazione, Cr_DataModifica)
                insert_data(conn, data)
                st.success('Azienda inserita con successo!')


    with tab2:
        st.write("Modifica un'azienda esistente")
        nomi, id_azienda = load_data()
        forn = st.selectbox("Seleziona:", nomi, key="Md_selezione")

        selected_id = id_azienda[nomi.index(forn)]
        supplier_details = load_supplier_details(conn, selected_id)
        if supplier_details['Paese'] is not None:
            indice = int(nazioni[nazioni['Nome_paese']==supplier_details['Paese']].index.values)

        with st.form(key="frm_Modifica", clear_on_submit=True):
            st.text_input("ID dell'azienda", value=selected_id, key="md_selected_id", disabled=True)
            if supplier_details['Nome'] is not None:
                Md_Nom = st.text_input("Nome", value=supplier_details['Nome'], key="Md_nom")
            else:
                Md_Nom = st.text_input("Nome", key="Md_nom")
            if supplier_details['Paese'] is not None:
                Md_Pae = st.selectbox("Paese", nazioni, index=int(nazioni[nazioni['Nome_paese']==supplier_details['Paese']].index.values), key="Md_pae")
            else:
                Md_Pae = st.selectbox("Paese", nazioni, key="Md_pae")
            Md_DataModifica = date.today()
            if selected_id == 0:
                Update_Submit = st.form_submit_button("Aggiorna azienda", disabled=True)
            else:
                Update_Submit = st.form_submit_button("Aggiorna azienda", disabled=False)
                

        if Update_Submit:
            if len(Md_Nom) < 3:
                st.warning("Attenzione! Nome azienda non valido.")
            else:
                data = (Md_Nom, Md_Pae, Md_DataModifica)
                update_data(conn, data, selected_id)
                st.success(f'Azienda con ID {selected_id} aggiornata con successo!')


    with tab3:
            st.write("Elimina un'azienda")
            nomi, id_azienda = load_data()
            forn = st.selectbox("Seleziona:", nomi)
            with st.form(key="frm_Elimina", clear_on_submit=True):
                selected_id = id_azienda[nomi.index(forn)]
                st.text_input("ID dell'azienda", value=selected_id, key="clr_selected_id", disabled=True)
                if selected_id == 0:
                    Delete_Submit = st.form_submit_button("Elimina azienda", disabled=True)
                else:
                    Delete_Submit = st.form_submit_button("Elimina azienda", disabled=False)
            
            if Delete_Submit:
                delete_data(selected_id)
                st.success(f'Azienda con ID {selected_id} eliminato con successo!')


if __name__ == '__main__':
    main()