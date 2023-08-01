import streamlit as st


st.set_page_config(page_title="Datalähteet", 
                   page_icon="💾", 
                   layout="wide", 
                   initial_sidebar_state="auto")

st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Analyysissä käytetyt tietoaineistot</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
 </div>   
<div style="margin-left: 20px;">
<b>Apteekit:</b>  
            <div style="margin-left: 40px;">Suomen Apteekkariliitto 2021 | https://www.apteekki.fi/apteekkihaku.html</div>
<b>Ruokakaupat:</b> 
            <div style="margin-left: 40px;">Ruokakauppojen verkkosivut | https://www.s-kaupat.fi/myymalat, https://www.k-ruoka.fi/k-citymarket?kaupat, https://www.lidl.fi/c/myymaelaet/s10021311,  https://www.m-ketju.fi/myymalat/</div>
<b>Huoltoasemat:</b> 
            <div style="margin-left: 40px;">OpenStreetMap Contributors</div>
<b>Kahvilat ja ravintolat:</b> 
            <div style="margin-left: 40px;">OpenStreetMap Contributors</div>
<b>Kulttuurikohteet:</b> 
            <div style="margin-left: 40px;">OpenStreetMap Contributors</div>
<b>Majoituskohteet:</b>
            <div style="margin-left: 40px;">OpenStreetmap Contributors</div>
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
<b>Pyörämatkailijatunnuksen alla olevat palvelut:</b>
            <div style="margin-left: 40px;">Pyörämatkailukeskus</div>


</div>
 <br><br>
 <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC0-1.0.</em>
 
 """, unsafe_allow_html=True)