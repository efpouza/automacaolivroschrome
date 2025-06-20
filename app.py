import streamlit as st
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time

# Função para raspar os dados com requests + BeautifulSoup
def raspar_livros(progress_bar, status_text, porcentagem_texto):
    base_url = 'https://books.toscrape.com/catalogue/page-{}.html'
    books = []
    current_page = 1

    while True:
        url = base_url.format(current_page)
        response = requests.get(url)
        if response.status_code != 200:
            break  # Parar se a página não existir

        soup = BeautifulSoup(response.text, 'html.parser')
        book_elements = soup.select('article.product_pod')

        if not book_elements:
            break  # Fim das páginas

        for book in book_elements:
            title = book.h3.a['title']
            price = book.select_one('.price_color').text
            availability = book.select_one('.availability').get_text(strip=True)
            rating_class = book.select_one('.star-rating')['class'][-1]

            books.append([title, price, availability, rating_class])

        progresso = min((current_page / 50), 1.0)
        progresso_percentual = int(progresso * 100)
        progress_bar.progress(progresso)
        status_text.markdown(f"<div style='text-align: center;'>📖 Coletando página {current_page}...</div>", unsafe_allow_html=True)
        porcentagem_texto.markdown(f"<div style='text-align: center;'>Progresso: <strong>{progresso_percentual}%</strong></div>", unsafe_allow_html=True)

        current_page += 1
        time.sleep(0.3)  # Pausa para evitar sobrecarga no servidor

    df = pd.DataFrame(books, columns=["Título", "Preço", "Disponibilidade", "Avaliação"])
    df.to_csv("livros.csv", index=False, encoding="utf-8")
    return df

# --- Interface Streamlit ---
st.set_page_config(page_title="📚 Raspador de Livros", layout="wide")

# Título centralizado
st.markdown("<h1 style='text-align: center;'>📚 Coleta Livros - Loja Virtual</h1>", unsafe_allow_html=True)
st.markdown("---")

# Área fixa para barra de progresso e status
status_text = st.empty()
progress_bar = st.progress(0)
porcentagem_texto = st.empty()

# Exibir mensagem inicial
status_text.markdown("<div style='text-align: center;'>⏳ Aguardando ação do usuário...</div>", unsafe_allow_html=True)
porcentagem_texto.markdown("<div style='text-align: center;'>Progresso: <strong>0%</strong></div>", unsafe_allow_html=True)

# Espaço antes dos botões
st.markdown("###")

# Layout dos botões
col1, col2 = st.columns([1, 1])

with col1:
    iniciar = st.button("🔍 Iniciar Coleta", use_container_width=True)

with col2:
    limpar = st.button("🧹 Limpar", use_container_width=True)

st.markdown("---")

# Processamento
if iniciar:
    with st.spinner("Coletando dados..."):
        df_resultado = raspar_livros(progress_bar, status_text, porcentagem_texto)
        status_text.markdown(f"<div style='text-align: center;'>✅ Coleta finalizada com {len(df_resultado)} livros.</div>", unsafe_allow_html=True)
        porcentagem_texto.markdown("<div style='text-align: center;'>Progresso: <strong>100%</strong></div>", unsafe_allow_html=True)
        progress_bar.progress(1.0)
        st.dataframe(df_resultado, use_container_width=True)
        st.download_button("⬇️ Baixar CSV", df_resultado.to_csv(index=False), file_name="livros.csv", mime="text/csv")

# Limpeza (reinicializa o app)
if limpar:
    st.rerun()
