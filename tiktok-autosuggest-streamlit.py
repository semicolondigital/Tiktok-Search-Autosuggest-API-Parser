import streamlit as st
st.set_page_config(
    page_title="TikTok Search Autosuggest API Parser - SEO",
    page_icon="chart_with_upwards_trend",
    layout="wide",
)
import requests
import json
from stqdm import stqdm
from user_agent2 import (generate_user_agent)
import pandas as pd
import string

st.title("TikTok Search Autosuggest API Parser")
tab1, tab2, tab3 = st.tabs(["♪ TikTok Search Autosuggest Parser", "ℹ️ Notes", "📈 TikTok SEO"])

tab1.subheader("Extract keyword ideas from TikTok.")
tab1.write("This was made in less than an hour, just for fun and educational purposes. The script will run through a series of loops in order to get some extra keywords, as the suggestions are limited to only 7 per keyword. You can also generated keyword ideas by adding alphabet letters to your seed search term.")
tab1.write("Author: [Martin Aberastegue](https://twitter.com/xyborg)")

tab2.subheader("Some notes and known issues.")
tab2.write("Country and Language codes are in ISO-3166 and ISO-639 format respectively. For example US for USA and EN for English.")
tab2.write("For some short-tail generic keywords, TikTok seems to suggest very broad results when using their API, something that doesn't happen if you use the app.")

tab3.subheader("Useful links for your journey to TikTok SEO")
tab3.write("Rise at Seven: [The ultimate guide to TikTok SEO](https://riseatseven.com/blog/the-ultimate-guide-to-tiktok-seo/)")
tab3.write("NoGood: [TikTok SEO Strategies: How to Rank for TikTok Search Results](https://nogood.io/2022/08/19/tiktok-seo/)")
tab3.write("Tuff: [TikTok SEO What is it and how to rank](https://tuffgrowth.com/tiktok-seo-what-is-it-and-how-to-rank/)")

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
    @st.cache(suppress_st_warning=True, show_spinner=False)
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
            if i['content'] not in kwdlist :
                srclist.append(h['content'])
                kwdlist.append(i['content'])
            for j in getkwds(i['content'], region, language).json()['sug_list']:
                if j['content'] not in kwdlist :
                    srclist.append(i['content'])
                    kwdlist.append(j['content'])
                for k in getkwds(j['content'], region, language).json()['sug_list']:
                    if k['content'] not in kwdlist :
                        srclist.append(j['content'])
                        kwdlist.append(k['content'])

    d = dict.fromkeys(string.ascii_lowercase, 0)
    for abc in stqdm(d, desc='Extracting alphabetic related keywords'):
      kwdseed = seedkwd + " " + abc
      for iabc in getkwds(kwdseed, region, language).json()['sug_list']:
        if iabc['content'] not in kwdlist:
          srclist.append(kwdseed)
          kwdlist.append(iabc['content'])

    dfalpha = pd.DataFrame(None)
    dfalpha['seed_keyword'] = srclist
    dfalpha['related_searches'] = kwdlist

    dfalpha = dfalpha.explode('related_searches').reset_index(drop=True)
    dfalpha = dfalpha.drop_duplicates().reset_index(drop=True)

    st.subheader(str(len(dfalpha)) + " keywords found, printing results...")
    st.dataframe(dfalpha, width=None, height=500, use_container_width=True)
    
    # add download button
    def convert_df(dfalpha):  # IMPORTANT: Cache the conversion to prevent computation on every rerun
        return dfalpha.to_csv().encode('utf-8')

    csvalpha = convert_df(dfalpha)

    st.download_button(
        label = "📥 Download TikTok Keyword Ideas!",
        data = csvalpha,
        file_name = 'tiktok_keywords_ideas.csv',
        mime = 'text/csv', )
