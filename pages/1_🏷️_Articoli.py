import streamlit as st
import sqlite3
import pandas as pd
from datetime import date

# Impostazioni delle pagina
st.set_page_config(
    page_title="App Rosso - Richieste", 
    page_icon="🏷️", 
    layout="wide")

# Connessione al database SQLite
conn = sqlite3.connect('offerte.db')

def load_category():
    query = "SELECT Categoria FROM Categorie"
    df = pd.read_sql_query(query, conn)
    return df

# Inserisci i dati degli articoli nel database
def insert_data(conn, data):
    query = '''
    INSERT INTO articoli (Descrizione, Categoria, Marca, Ean, Pcs_crt, Crt_plt, Data_creazione, Data_modifica)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    '''
    conn.execute(query, data)
    conn.commit()

# Carica i nome degli articoli nella casella di selezione
def load_data():
    query = "SELECT Id_art, Descrizione FROM articoli"
    df = pd.read_sql_query(query, conn)
    return df['Descrizione'].tolist(), df['Id_art'].tolist()

# Carica tutti i dati degli articoli nel form
def load_article_details(conn, article_id):
    query = "SELECT * FROM articoli WHERE Id_art = ?"
    df = pd.read_sql_query(query, conn, params=(article_id,))
    return df.iloc[0] if not df.empty else None

# Modifica i dati di un articolo esistente nel database
def update_data(conn, data, article_id):
    query = '''
    UPDATE articoli
    SET Descrizione = ?, Categoria = ?, Marca = ?, Ean = ?, Pcs_crt = ?, Crt_plt = ?, Data_modifica = ? 
    WHERE Id_art = ?
    '''
    conn.execute(query, (*data, article_id))
    conn.commit()

# Elimina un articolo dal database
def delete_data(article_id):
    query = 'DELETE FROM articoli WHERE Id_art = ?'
    conn.execute(query, (article_id,))
    conn.commit()


def main():
    st.title('Articoli')
    Categorie = load_category()

    tab1, tab2, tab3 = st.tabs(["Crea", "Modifica", "Elimina"])
    with tab1:
        st.write("Inserisci un nuovo articolo")

        with st.form(key="frm_Crea", clear_on_submit=True):
            Cr_Dsc = st.text_input("Descrizione", key="Cr_dsc")
            Cr_Ctg = st.selectbox("Categoria", Categorie, key="Cr_ctg")
            Cr_Mrc = st.text_input("Marca", key="Cr_Mrc")
            Cr_Ean = st.text_input("EAN", key="Cr_Ean")
            Cr_Pcs = st.number_input("PZ / CRT", key="Cr_Pcs", min_value=0, step=1)
            Cr_Crt = st.number_input("CRT / PLT", key="Cr_Crt", min_value=0, step=1)
            Cr_DataCreazione = date.today()
            Cr_DataModifica = date.today()
            Cr_Submit = st.form_submit_button("Inserisci articolo")

        # Se premi il pulsante "Submit", inserisci i dati nel database
        if Cr_Submit:
            if len(Cr_Dsc) < 3:
                st.warning("Attenzione! Descrizione non valida.")
            else:
                data = (Cr_Dsc, Cr_Ctg, Cr_Mrc, Cr_Ean, Cr_Pcs, Cr_Crt, Cr_DataCreazione, Cr_DataModifica)
                insert_data(conn, data)
                st.success('Articolo inserito con successo!')

       

    with tab2:
        st.write("Modifica un articolo esistente")
        descrizioni, id_articoli = load_data()
        art = st.selectbox("Seleziona:", descrizioni, key="Md_selezione")

        selected_id = id_articoli[descrizioni.index(art)]
        article_details = load_article_details(conn, selected_id)

        with st.form(key="frm_Modifica", clear_on_submit=True):
            st.text_input("ID dell'articolo", value=selected_id, key="md_selected_id", disabled=True)
            if article_details['Descrizione'] is not None:
                Md_Dsc = st.text_input("Descrizione", value=article_details['Descrizione'], key="Md_dsc")
            else:
                Md_Dsc = st.text_input("Descrizione", key="Md_dsc")
            if article_details['Categoria'] is not None:
                Md_Ctg = st.selectbox("Categoria", Categorie, index=int(Categorie[Categorie['Categoria']==article_details['Categoria']].index.values), key="Md_ctg")
            else:
                Md_Ctg = st.selectbox("Categoria", Categorie, key="Md_ctg")
            if article_details['Marca'] is not None:
                Md_Mrc = st.text_input("Marca", value=article_details['Marca'], key="Md_Mrc")
            else:
                Md_Mrc = st.text_input("Marca", key="Md_Mrc")
            if article_details['Ean'] is not None:
                Md_Ean = st.text_input("EAN", value=article_details['Ean'], key="Md_Ean")
            else:
                Md_Ean = st.text_input("EAN", key="Md_Ean")
            if article_details['Pcs_Crt'] is not None:
                Md_Pcs = st.number_input("PZ / CRT", value=int(article_details['Pcs_Crt']), key="Md_Pcs", min_value=0, step=1)
            else:
                Md_Pcs = st.number_input("PZ / CRT", key="Md_Pcs", min_value=0, step=1)
            if article_details['Crt_Plt'] is not None:
                Md_Crt = st.number_input("CRT / PLT", value=int(article_details['Crt_Plt']), key="Md_Crt", min_value=0, step=1)
            else:
                Md_Crt = st.number_input("CRT / PLT", key="Md_Crt", min_value=0, step=1)
            Md_DataModifica = date.today()
            if selected_id == 0:
                Update_Submit = st.form_submit_button("Aggiorna articolo", disabled=True)
            else:
                Update_Submit = st.form_submit_button("Aggiorna articolo", disabled=False)

        if Update_Submit:
            if len(Md_Dsc) < 3:
                st.warning("Attenzione! Descrizione non valida.")
            else:
                data = (Md_Dsc, Md_Ctg, Md_Mrc, Md_Ean, Md_Pcs, Md_Crt, Md_DataModifica)
                update_data(conn, data, selected_id)
                st.success(f'Articolo con ID {selected_id} aggiornato con successo!')


    with tab3:
            st.write("Elimina un articolo")
            descrizioni, id_articoli = load_data()
            art = st.selectbox("Seleziona:", descrizioni)
            with st.form(key="frm_Elimina", clear_on_submit=True):
                selected_id = id_articoli[descrizioni.index(art)]
                st.text_input("ID dell'articolo", value=selected_id, key="clr_selected_id", disabled=True)
                if selected_id == 0:
                    Delete_Submit = st.form_submit_button("Elimina articolo", disabled=True)
                else:
                    Delete_Submit = st.form_submit_button("Elimina articolo", disabled=False)
            if Delete_Submit:
                delete_data(selected_id)
                st.success(f'Articolo con ID {selected_id} eliminato con successo!')


if __name__ == '__main__':
    main()