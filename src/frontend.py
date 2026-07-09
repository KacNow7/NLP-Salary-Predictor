import streamlit as st
import requests

st.set_page_config(page_title="Salary Predictor", page_icon="💰")

st.title("💸 IT Salary Predictor")
st.write("Wpisz stanowisko i technologie, aby oszacować rynkowe wynagrodzenie.")

title_input = st.text_input("Stanowisko (np. Mid Python Developer):")
tech_input = st.text_input("Technologie (oddzielone spacją, np. python django sql):")

if st.button("Wyceń stanowisko"):
    if title_input and tech_input:
        # Wysyłanie zapytania POST do naszego FastAPI
        payload = {"title": title_input, "technologies": tech_input}
        try:
            response = requests.post("http://api:8000/predict", json=payload)
            if response.status_code == 200:
                result = response.json()
                st.success(f"Szacowane wynagrodzenie: {result['predicted_salary_pln']} PLN")
            else:
                st.error("Błąd serwera API.")
        except requests.exceptions.ConnectionError:
            st.error("Nie można połączyć się z API. Upewnij się, że FastAPI działa.")
    else:
        st.warning("Proszę wypełnić oba pola.")