import streamlit as st
import time
import json
import requests

url = "https://api.gameofthronesquotes.xyz/v1/random/10"

def getData():
    print("getting json")
    resp = requests.get(url)
    global quotes
    quotes = resp.json()

def CreateWindow():
    global window 
    window = st.empty()

def showQuote(quote):
    QuoteToShow = quote["sentence"]
    Author =  quote["character"]['name']
    window.empty()
    with window.container():
        HTML_Quote = f'<p style="color:Blue; font-size: 20px;">\"{QuoteToShow}\"</p>'
        st.markdown(HTML_Quote, unsafe_allow_html=True)
        st.write(Author)

def Loop():
    for quote in quotes:
        showQuote(quote)
        time.sleep(5)

if __name__ == '__main__':
    getData()
    CreateWindow()
    Loop()