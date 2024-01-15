import streamlit as st
import sqlite3
import pandas as pd
from datetime import date, datetime, timedelta

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

def load_offers_today():
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    query = '''
        SELECT 
            offerte.Id_off,
            offerte.Articolo AS ID_art,
            aziende.Nome AS Nome_Fornitore,
            articoli.Descrizione AS Nome_Articolo,
            offerte.Prezzo
        FROM
            offerte
        JOIN
            aziende ON offerte.Fornitore = aziende.Id_az
        JOIN
            articoli ON offerte.Articolo = articoli.Id_art
        WHERE
            offerte.Data_ins >= ?
    '''

    df_raw = pd.read_sql_query(query, conn, params=(yesterday,))
    df = df_raw.fillna("")
    return df


def load_offers(conn, article_id, filter_date=None):
    query = ''' 
        SELECT
            aziende.Nome AS Nome_Fornitore,
            offerte.Prezzo,
            offerte.Moq,
            offerte.Lead_time,
            offerte.Incoterms AS Exw_da,
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
    
    df_raw = pd.read_sql_query(query, conn, params=params)
    df = df_raw.fillna("")  # Qui i campi vuoti sono ""
    return df if not df.empty else None

def cerca_listini(stringa):
    query = "SELECT Fornitore, Articolo, Prezzo, Codice, EAN, Moq, Lead_time, Incoterms, Pagamento, Data_validita, Data_ins FROM listini WHERE Articolo LIKE ?"
    pattern = f"%{stringa}%"
    df = pd.read_sql_query(query, conn, params=(pattern,))
    return df


def main():
    st.image("./img/logo_RGB.png")
    st.markdown('#')

    st.subheader('Cerca offerte', anchor=False)
    
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
    

    st.divider()

    st.subheader('Cerca nei listini', anchor=False)
    
    stringa = st.text_input('Cerca per nome articolo')

    if stringa:
        tabella = cerca_listini(stringa)
        st.dataframe(tabella, hide_index=True, use_container_width=True)



    st.divider()


    st.subheader('Offerte attuali', anchor=False)
    df_offerte = load_offers_today()
    if len(df_offerte) > 0:
        Numero_offerte = []
        Massimo = []
        Minimo = []
        Media = []
        for offer in df_offerte["ID_art"]:
            off_art = load_offers(conn, offer)   
            Numero_offerte.append(len(off_art))   
            Massimo.append(round(off_art['Prezzo'].max(), 3))
            Minimo.append(round(off_art['Prezzo'].min(), 3))
            Media.append(round(off_art['Prezzo'].mean(), 3))

        df_offerte.insert(5, "N. off", Numero_offerte)
        df_offerte.insert(6, "Massimo", Massimo)
        df_offerte.insert(7, "Minimo", Minimo)
        df_offerte.insert(8, "Media", Media)

        
        df_offerte['Var_min'] = (df_offerte['Prezzo'] - df_offerte['Minimo']) / df_offerte['Minimo'] * 100

        df_offerte.drop(['Id_off', 'ID_art'], axis=1, inplace=True)

        df_offerte['Prezzo Eur'] = df_offerte['Prezzo'].apply(lambda x: '€ {:,.2f}'.format(x))
        df_offerte['Massimo Eur'] = df_offerte['Massimo'].apply(lambda x: '€ {:,.2f}'.format(x))
        df_offerte['Minimo Eur'] = df_offerte['Minimo'].apply(lambda x: '€ {:,.2f}'.format(x))
        df_offerte['Media Eur'] = df_offerte['Media'].apply(lambda x: '€ {:,.2f}'.format(x))

        df = df_offerte[['Nome_Fornitore', 'Nome_Articolo', 'Prezzo Eur', 'N. off', 'Massimo Eur', 'Minimo Eur', 'Media Eur', 'Var_min']]

        st.dataframe(df, use_container_width=True,  hide_index=True)


if __name__ == '__main__':
    main()
