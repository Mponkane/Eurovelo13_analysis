
import streamlit as st


st.set_page_config(page_title="Eurovelo 13 analyysi", 
                   page_icon="🌍", 
                   layout="wide", 
                   initial_sidebar_state="auto")

# info
st.markdown("""
 <div style="display: flex; align-items: center;">
   <h2 style="margin: 0;">Eurovelo 13 -reitin paikkatietoanalyysi</h2>
   <img style="margin-left: auto;" src="https://raw.githubusercontent.com/Mponkane/Eurovelo13_analysis/main/streamlit/data/welcome_cyclist.png" width="150" height="150">
 </div>
            
Erilaisten pyörämatkailureittien varrelle sijoittuvat palvelut sekä virkistyskohteet ovat keskeisessä roolissa
tuottamassa positiivista ja turvallista pyörämatkailukokemusta. Erityisesti harvaan asuttujen seutujen läpi kulkevat pitkänmatkan pyöräilyreitit voivat sisältää pitkiäkin reittiosuuksia, missä palveluita ei ole lainkaan saatavilla. 
Toisaalta ongelmana on myös se, että tieto saatavilla olevista palveluista tai virkistyspaikoista ei myöskään ole aina helposti saatavilla, ajantasaista tai vertailtavassa muodossa. Täten pyöräreittien palvelutason laadun suunnittelua on vaikeaa systematisoida. 
Reittiosuuksia olisi siis hyvä saada vertailtavaan muotoon palveluiden ja virkistyskohteiden näkökulmasta, jotta voitaisiin paikantaa ne osuudet, mihin on syytä kohdistaa pyörämatkailun palvelutasoa nostattavia toimenpiteitä. 
Tällä hetkellä tietoa pyörämatkailureittien varrella olevista palveluista ja virkistyskohteista kerätään hyvin manuaalisesti. Koska yksittäisten palveluiden ja virkistysalueiden manuaalinen kartoittaminen on todella työlästä, on tarpeen tarkastella keinoja, miten olemassa
olevia paikkatietokantoja voitaisiin hyödyntää tehokkaammin osana pyörämatkailun suunnittelua ja miten tiedonhankintaa voitaisiin myös automatisoida.
<br><br>
Tämä verkkosovellus ja paikkatietoanalyysi on tuotettu osaksi harvaan asuttujen alueiden matkailuhanketta. Hankkeen on tarkoitus pilotoida erilaisia paikkatietomenetelmiä pyörämatkailun suunnitteluun. 
Verkkosovelluksella pystyt tarkastelemaan ja vertailemaan  Eurovelo 13 -reittisegmenttien palvelutasoa. 

                      
#### Verkkosovellus on jaettu neljään osaan:
<div style="margin-left: 20px;">
<b>1. Palvelutasotarkastelu</b>  
            <div style="margin-left: 40px;">Osiossa voit tarkastella Eurovelo 13 -reitin varrelle sijoittuvia palveluita, virkistyskohteita ja maisemallisia arvoja. Voit myös
            vertailla eri päiväsegmenttien palvelutasoa.</div></div><br>
<div style="margin-left: 20px;">
<b>2. Reittivaihtoehtojen vertailu:</b> 
            <div style="margin-left: 40px;">Osana harvaan asuttujen seutujen matkailuhanketta tarkasteltiin myös vaihtoehtoisia Eurovelo 13 reittilinjauksia palveluiden näkökulmasta.
            Tässä osiossa voit tarkastella tuotettua analyysiä.</b></div></div><br>
<div style="margin-left: 20px;">
<b>3. Painotettu matkailuindeksi:</b> 
            <div style="margin-left: 40px;">Painotetun matkailuindeksin avulla voidaan pisteyttää Eurovelo 13 -reitin päiväsegmenttejä
            asettamalla tärkeyden mukaan erilaisia painotuksia palveluille, virkistyskohteille tai maisema-arvoille. Esimerkiksi sen mukaan
            miten erilaiset pyörämatkailijat arvottaisivat niitä omalla matkallaan.</b></div></div><br>
<div style="margin-left: 20px;">
<b>4. Datalähteet:</b> 
            <div style="margin-left: 40px;">Viimeisestä osiosta löydät analyysissä käytetyt datalähteet. </b></div></div>

<br>
<h4 style="margin-left: -10px;">👈 Sivupalkista löydät tuotetun analyysin eri osa-alueet.</h4>


<br><br>
 <em>App made by Matti Pönkänen | FLOU ltd (2023). Licensed under CC-BY.</em>
 
 """, unsafe_allow_html=True)