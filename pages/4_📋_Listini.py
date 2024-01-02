import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta
import time

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Listini", 
    page_icon="📋", 
    layout="wide")

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db')


def load_data():
    query = "SELECT Nome FROM aziende"
    df = pd.read_sql_query(query, conn)
    return df

def cerca_listini(stringa):
    query = "SELECT Fornitore, Articolo, Prezzo, Codice, EAN, Moq, Lead_time, Incoterms, Pagamento, Data_validita, Data_ins FROM listini WHERE Articolo LIKE ?"
    pattern = f"%{stringa}%"
    df = pd.read_sql_query(query, conn, params=(pattern,))
    return df

def clean_db(data_limite):
    try:
        query = "DELETE FROM listini WHERE DATE(Data_ins) < DATE(?)"
        conn.execute(query, (data_limite,))
        conn.commit()
        return True
    except Exception as e:
        print(f"Errore durante l'eliminazione dei record: {str(e)}")
        return False

    

def main():
    st.title('Listini')

    st.subheader('Carica listino')

    
    st.download_button('Download template csv', data="Articolo;Prezzo;Codice;EAN;Moq;Lead_time;Incoterms;Pagamento;Data_validita", file_name='import_template.csv', mime='text/csv')
    
    aziende = load_data()
    fornitore = st.selectbox('Selziona il fornitore', aziende, key="selection")
    if fornitore != " ":
        uploaded_file = st.file_uploader('Seleziona un file', type='csv')
    
        if uploaded_file:
            df = pd.read_csv(uploaded_file, delimiter=";")
            if df.columns.values.tolist() == ['Articolo', 'Prezzo', 'Codice', 'EAN', 'Moq', 'Lead_time', 'Incoterms', 'Pagamento', 'Data_validita']:
                df.insert(0, 'Fornitore', fornitore)
                df['Data_ins'] = date.today()

                st.dataframe(df, hide_index=True)
                upload = st.button("Upload")

                if upload:
                    df.to_sql('listini', conn, if_exists='append')
                    st.success("Listino caricato!")
                    time.sleep(2)
            else:
                st.warning("Attenzione! Template non valido.")

    st.divider()

    st.subheader('Cerca nei listini')
    
    stringa = st.text_input('Cerca per nome articolo')

    if stringa:
        tabella = cerca_listini(stringa)
        st.dataframe(tabella, hide_index=True, use_container_width=True)


    st.divider()

    st.subheader('Pulisci il database')
    data_max = date.today()-timedelta(days=30)
    data_limite = st.date_input('Elimina record precedenti a:', value=data_max, max_value= data_max, format='DD/MM/YYYY')
    clean = st.button('Clean up')

    if clean:
        esito = clean_db(data_limite)
        if esito:
            st.success(f"Eliminazione dei record precedenti a {data_limite} riuscita!")
        else:
            st.warning("Si è verificato un errore durante l'eliminazione dei record.")



if __name__ == '__main__':
    main()