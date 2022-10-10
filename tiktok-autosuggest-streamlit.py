import streamlit as st
st.set_page_config(
    page_title="TikTok Search Autosuggest API Parser",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)
import requests
import json
from stqdm import stqdm
from user_agent2 import (generate_user_agent)
import pandas as pd

st.title("TikTok Search Autosuggest API Parser")
st.subheader("Extract keyword ideas from TikTok autosuggest API.")
st.write("This was made in less than an hour, just for fun and educational purposes. The script will run through a series of loops in order to get some extra keywords, as the suggestions are limited to only 7 per keyword.")
st.write("You can also generated keyword ideas by adding alphabet letters to your seed search term.")
st.write("You need to enter the search term, the country, and the language code in ISO-3166 and ISO-639 respectively. For example US for USA and EN for English.")
st.write("")

with st.form(key='columns_in_form_2'):
    seedkwd = st.text_input('Seed Keyword')
    region = st.selectbox(
        'Country',
        ('US', 'ES', 'FR', 'DE', 'IT', 'UK', 'RU', 'BR', 'AR', 'PT', 'CA', 'NL', 'MX'))
    language = st.selectbox(
        'Language',
        ('en', 'es', 'fr', 'de', 'it', 'ru', 'pt', 'pl'))
    submitted = st.form_submit_button('Start')

if submitted:
    def getkwds(seed_keyword, reg, lang):
      ua = generate_user_agent(navigator="chrome")
      header = {'User-Agent': str(ua)}
      getterms_url = "https://www.tiktok.com/api/search/general/preview/?app_language=" + lang + "&keyword=" + seed_keyword + "&region=" + reg
      response = requests.get(getterms_url, headers=header)
      return response

    srclist = []
    kwdlist = []
    
    for h in stqdm(getkwds(seedkwd, region, language).json()['sug_list'], desc='Extracting keywords'):
        srclist.append(seedkwd)
        kwdlist.append(h['content'])
        for i in getkwds(h['content'], region, language).json()['sug_list']:
          srclist.append(h['content'])
          kwdlist.append(i['content'])
          for j in getkwds(i['content'], region, language).json()['sug_list']:
            srclist.append(i['content'])
            kwdlist.append(j['content'])
            for k in getkwds(j['content'], region, language).json()['sug_list']:
              srclist.append(j['content'])
              kwdlist.append(k['content'])

    df = pd.DataFrame(None)
    df['seed_keyword'] = srclist
    df['related_searches'] = kwdlist

    df = df.explode('related_searches').reset_index(drop=True)
    print("Removing duplicates...")
    df = df.drop_duplicates().reset_index(drop=True)
    st.write(len(df), "keywords found, printing results...")

    # add download button
    def convert_df(df):  # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return df.to_csv().encode('utf-8')

    csv = convert_df(df)

    st.download_button(
        label = "📥 Download keyword ideas!",
        data = csv,
        file_name = 'tiktok_related_searches.csv',
        mime = 'text/csv', )
