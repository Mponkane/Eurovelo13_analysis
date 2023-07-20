import streamlit as st


st.set_page_config(page_title="Datalähteet", 
                   page_icon="💾", 
                   layout="wide", 
                   initial_sidebar_state="auto")

# info
st.markdown("""
### Analyysi on tuotettu seuraavien tietoaineistojen pohjalta:
<div style="margin-left: 20px;">
<b>Apteekit:</b>  
            <div style="margin-left: 40px;">Suomen Apteekkariliitto 2021 | https://www.apteekki.fi/apteekkihaku.html</div>
<b>Ruokakaupat:</b> 
            <div style="margin-left: 40px;">Ruokakauppojen verkkosivut | https://www.s-kaupat.fi/myymalat, https://www.k-ruoka.fi/k-citymarket?kaupat, https://www.lidl.fi/c/myymaelaet/s10021311,  https://www.m-ketju.fi/myymalat/</div>
<b>Huoltoasemat:</b> 
            <div style="margin-left: 40px;">OpenStreetMap</div>
<b>Kahvilat ja ravintolat:</b> 
            <div style="margin-left: 40px;">OpenStreetMap</div>
<b>Kulttuurikohteet:</b> 
            <div style="margin-left: 40px;">OpenStreetMap</div>
<b>Majoituskohteet:</b>
            <div style="margin-left: 40px;">OpenStreetmap</div>
<b>Muistomerkit:</b> 
            <div style="margin-left: 40px;">Maanmittauslaitoksen maastotietokanta | https://www.maanmittauslaitos.fi/kartat-ja-paikkatieto/asiantuntevalle-kayttajalle/tuotekuvaukset/maastotietokanta-0</div>
<b>Uimapaikat:</b> 
            <div style="margin-left: 40px;">Jyväskylän yliopisto | Lipas.fi</div>
<b>Laavu, Kota tai Kammi:</b> 
            <div style="margin-left: 40px;">Jyväskylän yliopisto | Lipas.fi</div>
<b>Kansallispuistot:</b>
            <div style="margin-left: 40px;">Jyväskylän yliopisto | Lipas.fi</div>
<b>Valtakunnallisesti arvokkaat maisema-alueet:</b>
            <div style="margin-left: 40px;">SYKE | https://www.syke.fi/fi-FI/Avoin_tieto/Paikkatietoaineistot</div>


</div>
 <br><br>
 <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC-BY.</em>
 
 """, unsafe_allow_html=True)