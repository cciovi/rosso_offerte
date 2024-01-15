import streamlit as st
import sqlite3
import pandas as pd
import time

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Backup DB", 
    page_icon="🤖", 
    layout="wide",)

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db')

def Export_table(table):
    if table == 'Articoli':
        query = "SELECT * FROM articoli"
    elif table == 'Aziende':
        query = "SELECT * FROM aziende"
    elif table == 'Offerte':
        query = " SELECT * FROM offerte"
    elif table == 'Listini':
        query = "SELECT * FROM listini"
    
    df_raw = pd.read_sql_query(query, conn)
    df = df_raw.fillna("")
    df.to_csv(index=False).encode('utf-8')
    df.replace(',', ';')
    return df


def main():
    st.subheader("Back up del database")
    st.write("Per eseguire il back up del database, premi il pulsante:")
    with open("offerte.db", "rb") as fp:
        btn = st.download_button(
        label="Download DB file",
        data=fp,
        file_name="offerte.db",
        mime="application/octet-stream"
    )

    st.markdown("#")
    st.markdown("#")

    st.subheader("Esporta tabelle DB")
    with st.form(key="Exp", clear_on_submit=True):
        table =st.selectbox("Seleziona la tabella da esportare", ['Articoli', 'Aziende', 'Offerte', 'Listini'] )
        Exp = st.form_submit_button('Esporta')
    
    if Exp:
        table
        df = Export_table(table)
        if len(df) > 0:
            st.dataframe(df, use_container_width=True)

    

if __name__ == '__main__':
    main()
