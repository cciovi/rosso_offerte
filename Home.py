import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, timedelta

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Home", 
    page_icon="🤖", 
    layout="wide",)

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db') 

def load_data():
    query = "SELECT Id_art, Descrizione FROM articoli"
    df = pd.read_sql_query(query, conn)
    return df['Descrizione'].tolist(), df['Id_art'].tolist()


def load_offers(conn, article_id, filter_date=None):
    query = ''' 
        SELECT
            aziende.Nome AS Nome_Fornitore,
            offerte.Prezzo,
            offerte.Moq,
            offerte.Lead_time,
            offerte.Incoterms,
            offerte.Pagamento,
            offerte.Data_ins,
            offerte.Data_val
        FROM
            offerte
        JOIN
            aziende ON offerte.Fornitore = aziende.Id_az
        WHERE
            offerte.Articolo = ? 
    '''
    
    if filter_date:
        query += ' AND offerte.Data_ins > ?'

    query += ' ORDER BY offerte.Id_off DESC'
    
    params = [article_id]
    if filter_date:
        params.append(filter_date)
    
    df = pd.read_sql_query(query, conn, params=params)
    return df if not df.empty else None

def load_requests():
    query = ''' 
        SELECT
            aziende.Nome AS Nome_Cliente,
            articoli.Descrizione AS Descrizione_Articolo,
            richieste.Destinazione,
            richieste.Quantita,
            richieste.Target AS "Traget Price",
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

def main():
    st.title('Cerca offerte')
    
    descrizioni, id_articoli = load_data()
    art = st.selectbox("Seleziona un articolo:", descrizioni, key="Selezione")
    data_selezionata = ""

    if art != " ":
        filtra_data = st.checkbox("Filtra per data")
        if filtra_data:
            data_selezionata = st.date_input("Filtra per data inserimento, da:", value=date.today() - timedelta(days=30), format="DD/MM/YYYY", max_value=date.today())
            data_selezionata = data_selezionata.strftime("%Y-%m-%d")  # Formatta la data nel formato corretto per SQLite
        else:
            data_selezionata = None
    
    selected_id = id_articoli[descrizioni.index(art)]
    offers = load_offers(conn, selected_id, filter_date=data_selezionata)

    
    if offers is not None:
        if len(offers) > 1:
            Massimo = offers['Prezzo'].max()
            Minimo = offers['Prezzo'].min()
            Media = round(offers['Prezzo'].mean(),3)
            Scostamento = round(((Massimo/Minimo)-1)*100, 1)
        
            coll1, coll2, coll3, coll4, coll5 = st.columns(5)
    
            with coll1:
                container1 = st.container(border=True)
                container1.metric("N. di offerte", value=len(offers))

            with coll2:
                container1 = st.container(border=True)
                container1.metric("Max", value="€ " + str(Massimo))
            
            with coll3:
                container2 = st.container(border=True)
                container2.metric("Min", value="€ " + str(Minimo))
            
            with coll4:
                container3 = st.container(border=True)
                container3.metric("Med", value="€ " + str(Media))

            with coll5:
                container4 = st.container(border=True)
                container4.metric("Scost. Max/Min", value=str(Scostamento) + "%")

        st.dataframe(offers, use_container_width=True,  hide_index=True)
    else:
        if selected_id != 0:
            st.warning("Nessuna offerta disponibile per l'articolo selezionato.")
    
    st.markdown('#')
    st.markdown('#')

    #st.subheader('Richieste in corso')
    #req = load_requests()
    #st.dataframe(req, use_container_width=True,  hide_index=True)

if __name__ == '__main__':
    main()
