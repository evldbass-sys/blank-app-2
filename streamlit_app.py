import streamlit as st
import requests
import json
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

# ====== FIREBASE SETTINGS ======
PROJECT_ID = "volt-a-value" 
FIRESTORE_URL = f"https://firestore.googleapis.com/v1/projects/{PROJECT_ID}/databases/(default)/documents"

# TRVALE OTEVŘENÝ BOČNÍ PANEL PRO SNADNÉ TESTOVÁNÍ VŠECH ROZHRANÍ
st.set_page_config(page_title="Volt and value - Lieferdienst Steyr", layout="wide", initial_sidebar_state="expanded")

# Čistý CSS design: schování log, patiček a úprava tlačítek pro gastro standardy
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        .stButton>button {
            border-radius: 8px;
            font-weight: bold;
        }
        .stRadio>div {
            flex-direction: row;
        }
    </style>
""", unsafe_allow_html=True)

# ====== DATABASE FUNCTIONS ======
def naechste_bestellnummer_holen():
    try:
        url = f"{FIRESTORE_URL}/objednavky"
        res = requests.get(url)
        max_nr = 0
        if res.status_code == 200 and "documents" in res.json():
            for d in res.json()["documents"]:
                f = d.get("fields", {})
                if "cislo_objednavky" in f:
                    try:
                        nr = int(f["cislo_objednavky"]["stringValue"])
                        if nr > max_nr:
                            max_nr = nr
                    except:
                        pass
        naechste = max_nr + 1
        if naechste > 9999:
            naechste = 1
        return naechste
    except:
        return 1

def bestellung_speichern(daten):
    url = f"{FIRESTORE_URL}/objednavky"
    daten["cislo_objednavky"] = str(naechste_bestellnummer_holen())
    payload = {"fields": {k: {"stringValue": str(v)} for k, v in daten.items()}}
    requests.post(url, json=payload)

def bestellungen_laden():
    url = f"{FIRESTORE_URL}/objednavky"
    res = requests.get(url)
    if res.status_code == 200 and "documents" in res.json():
        return res.json()["documents"]
    return []

def bestellstatus_aktualisieren(doc_name, neuer_status, fahrer_name="", lieferdetails="", zubereitungszeit="10"):
    url = f"https://firestore.googleapis.com/v1/{doc_name}?updateMask.fieldPaths=stav&updateMask.fieldPaths=kuryr&updateMask.fieldPaths=adresa&updateMask.fieldPaths=cas_pripravy"
    payload = {
        "fields": {
            "stav": {"stringValue": neuer_status},
            "kuryr": {"stringValue": fahrer_name},
            "adresa": {"stringValue": lieferdetails},
            "cas_pripravy": {"stringValue": str(zubereitungszeit)}
        }
    }
    requests.patch(url, json=payload)

def alle_bestellungen_loeschen():
    docs = bestellungen_laden()
    for d in docs:
        requests.delete(f"https://firestore.googleapis.com/v1/{d['name']}")

# ====== INITIALIZACE PAMĚTI V SESSION STATE ======
if "kunden_korb_liste" not in st.session_state: st.session_state.kunden_korb_liste = []
if "rest_korb_liste" not in st.session_state: st.session_state.rest_korb_liste = []
if "gewaehltes_rest_kunde" not in st.session_state: st.session_state.gewaehltes_rest_kunde = None
if "gewaehltes_rest_kassa" not in st.session_state: st.session_state.gewaehltes_rest_kassa = "Smash Brothers"
if "aktiver_korb_rest" not in st.session_state: st.session_state.aktiver_korb_rest = None

# ====== MULTI-RESTAURANT & SUPERMARKET STRUCTURE ======
url_burger = "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=500&auto=format&fit=crop&q=60"
url_chicken = "https://images.unsplash.com/photo-1626082927389-6cd097cdc6ec?w=500&auto=format&fit=crop&q=60"
url_wrap = "https://images.unsplash.com/photo-1626700051175-6518c4793f4f?w=500&auto=format&fit=crop&q=60"
url_kebab = "https://images.unsplash.com/photo-1628258475456-0224b1e4225a?w=500&auto=format&fit=crop&q=60"
url_pizza = "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=500&auto=format&fit=crop&q=60"
url_schnitzel = "https://images.unsplash.com/photo-1599921841143-819065a55cc6?w=500&auto=format&fit=crop&q=60"

url_wasser = "https://images.unsplash.com/photo-1608889174637-3c44f6326f60?w=500&auto=format&fit=crop&q=60"
url_milch = "https://images.unsplash.com/photo-1550583724-b2692b85b150?w=500&auto=format&fit=crop&q=60"
url_brot = "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=500&auto=format&fit=crop&q=60"
url_energy = "https://images.unsplash.com/photo-1622543953495-a17ebd37933f?w=500&auto=format&fit=crop&q=60"
url_bier = "https://images.unsplash.com/photo-1608270586620-248524c67de9?w=500&auto=format&fit=crop&q=60"

restaurants_menue = {
    "Smash Brothers": {
        "Cheese Burger": {"preis": 9.00, "icon": "🍔", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Chili Cheese Burger": {"preis": 10.00, "icon": "🌶️", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Double Trouble Burger": {"preis": 12.90, "icon": "🔥", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Oklahoma Double Burger": {"preis": 12.90, "icon": "🧅", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Double Beast Burger": {"preis": 12.90, "icon": "👹", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Smash 'n' Egg": {"preis": 12.50, "icon": "🍳", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "OG SMASH": {"preis": 10.00, "icon": "👑", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Classic Chicken Burger": {"preis": 10.00, "icon": "🍗", "kat": "Smash Burger", "extras": True, "bild": url_chicken},
        "Spicy Chicken Burger": {"preis": 10.00, "icon": "💥", "kat": "Smash Burger", "extras": True, "bild": url_chicken},
        "Green Dream Burger": {"preis": 10.00, "icon": "🌱", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Vegan Leaf Burger": {"preis": 10.00, "icon": "🍃", "kat": "Smash Burger", "extras": True, "bild": url_burger},
        "Chicken Wrap": {"preis": 9.90, "icon": "🌯", "kat": "Wraps", "extras": False, "bild": url_wrap},
        "Beef Wrap": {"preis": 9.90, "icon": "🥩", "kat": "Wraps", "extras": False, "bild": url_wrap},
        "Green Wrap": {"preis": 9.90, "icon": "🥗", "kat": "Wraps", "extras": False, "bild": url_wrap}
    },
    "King Food": {
        "Kebab Oriental": {"preis": 6.50, "icon": "🥙", "kat": "Kebab", "extras": False, "bild": url_kebab},
        "Kebab Spezial": {"preis": 7.20, "icon": "🌯", "kat": "Kebab", "extras": False, "bild": url_wrap},
        "Pizza Margherita": {"preis": 8.50, "icon": "🍕", "kat": "Pizza", "extras": False, "bild": url_pizza},
        "Pizza Salami": {"preis": 9.50, "icon": "🍕", "kat": "Pizza", "extras": False, "bild": url_pizza},
        "Pizza Cardinale": {"preis": 9.90, "icon": "🍕", "kat": "Pizza", "extras": False, "bild": url_pizza},
        "Pizza Tonno": {"preis": 10.20, "icon": "🍕", "kat": "Pizza", "extras": False, "bild": url_pizza},
        "Pizza Quattro Formaggi": {"preis": 10.90, "icon": "🍕", "kat": "Pizza", "extras": False, "bild": url_pizza},
        "Wiener Schnitzel (vom Schwein)": {"preis": 11.50, "icon": "🥩", "kat": "Schnitzel", "extras": False, "bild": url_schnitzel}
    },
    "Billa": {
        "Clever Minerální voda (6x1.5L)": {"preis": 3.90, "icon": "💧", "kat": "Getränke", "extras": False, "bild": url_wasser},
        "Red Bull Energy Drink 250ml": {"preis": 2.20, "icon": "⚡", "kat": "Getränke", "extras": False, "bild": url_energy},
        "Gösser Märzen Pivo (6-pack)": {"preis": 6.90, "icon": "🍺", "kat": "Alkohol", "extras": False, "bild": url_bier},
        "Toastbrot 500g": {"preis": 1.90, "icon": "🍞", "kat": "Lebensmittel", "extras": False, "bild": url_brot}
    },
    "Penny": {
        "Penny Trvanlivé mléko 1L": {"preis": 1.45, "icon": "🥛", "kat": "Lebensmittel", "extras": False, "bild": url_milch},
        "Monster Energy Green 500ml": {"preis": 2.50, "icon": "💥", "kat": "Getränke", "extras": False, "bild": url_energy},
        "Wieselburger Bier (6-pack)": {"preis": 6.50, "icon": "🍺", "kat": "Alkohol", "extras": False, "bild": url_bier}
    },
    "Hofer": {
        "Zurück zum Ursprung Bio-Milch 1L": {"preis": 1.85, "icon": "🥛", "kat": "Lebensmittel", "extras": False, "bild": url_milch},
        "Žitný chléb krájený 500g": {"preis": 2.40, "icon": "🍞", "kat": "Lebensmittel", "extras": False, "bild": url_brot},
        "Flying Power Energy 250ml": {"preis": 0.90, "icon": "⚡", "kat": "Getränke", "extras": False, "bild": url_energy}
    }
}

extra_options = {
    "Extra Fleisch (+3.00 €)": 3.00,
    "Extra Gurken (+0.50 €)": 0.50,
    "Ketchup (+0.50 €)": 0.50,
    "Mayo (+0.50 €)": 0.50
}

def rendering_menue_grid(aktive_rest, session_key):
    aktuelle_speisekarte = restaurants_menue[aktive_rest]
    kategorien = list(set(info["kat"] for info in aktuelle_speisekarte.values()))
    
    for kat in sorted(kategorien):
        st.markdown(f"#### 📦 {kat}")
        items = [item for item in aktuelle_speisekarte.items() if item[1]["kat"] == kat]
        for i in range(0, len(items), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(items):
                    artikel, info = items[i + j]
                    with cols[j]:
                        with st.container(border=True):
                            if "bild" in info:
                                st.image(info["bild"], width="stretch")
                                
                            st.markdown(f"**{info['icon']} {artikel}**")
                            st.markdown(f"Cena: **{info['preis']:.2f} €**")
                            
                            selected_extras = []
                            extra_cost = 0.0
                            if info.get("extras", False):
                                with st.expander("✨ Zutaten / Extras"):
                                    for ex_name, ex_preis in extra_options.items():
                                        if st.checkbox(ex_name, key=f"{session_key}_{aktive_rest}_{artikel}_{ex_name}"):
                                            selected_extras.append(ex_name.split(" (")[0])
                                            extra_cost += ex_preis
                            
                            st.write("")
                            if st.button("➕ Hinzufügen", key=f"{session_key}_{aktive_rest}_btn_{artikel}", width="stretch"):
                                název_polozky = artikel
                                if selected_extras:
                                    název_polozky += f" ({', '.join(selected_extras)})"
                                
                                final_preis = info["preis"] + extra_cost
                                st.session_state[f"{session_key}_liste"].append({"name": název_polozky, "preis": final_preis})
                                st.success("Hinzugefügt!")
                                time.sleep(0.1)
                                st.rerun()

# ====== ROZCESTNÍK NAVIGACE V BOČNÍM PANELU ======
st.sidebar.title("🎛️ Administrace systému")
rolle = st.sidebar.radio("Zvolte sekci rozhraní:", [
    "🏠 1. Kunden-Ansicht (E-Shop)", 
    "🏬 2. Kassa / Pokladna",
    "👨‍🍳 3. Küche Monitor", 
    "🚗 4. Fahrer-Ansicht (Mobil & Finanzen)"
])

# ====== 1. KUNDEN-ANSICHT (ZÁKAZNICKÝ E-SHOP) ======
if rolle == "🏠 1. Kunden-Ansicht (E-Shop)":
    st.title("🍔 Volt and value - Lieferdienst Steyr")
    st.markdown("##### Expresní rozvoz z nejlepších restaurací a supermarketů ve městě")
    st.write("")
    
    st.markdown("### 🏪 Zvolte obchod nebo restauraci:")
    
    c_res = st.columns(5)
    names_buttons = ["Smash Brothers", "King Food", "Billa", "Penny", "Hofer"]
    icons_buttons = ["🍔 Smash Brothers", "🥙 King Food", "🛍️ Billa", "🛍️ Penny", "🛍️ Hofer"]
    
    for idx, r_name in enumerate(names_buttons):
        with c_res[idx]:
            is_active = st.session_state.gewaehltes_rest_kunde == r_name
            if st.button(icons_buttons[idx], key=f"cust_btn_{r_name}", width="stretch", type="primary" if is_active else "secondary"):
                if st.session_state.kunden_korb_liste and st.session_state.aktiver_korb_rest != r_name:
                    st.session_state.wunsch_rest = r_name
                else:
                    st.session_state.gewaehltes_rest_kunde = r_name
                    st.rerun()
            
    st.write("---")
    
    if "wunsch_rest" in st.session_state and st.session_state.wunsch_rest is not None:
        with st.container(border=True):
            st.error(f"🛑 Pozor! Máte v košíku položky z: **{st.session_state.aktiver_korb_rest}**.")
            st.write("Není možné míchat jídla a nákupy z různých míst v jedné objednávce kvůli logistice kurýrů.")
            c_clear1, c_clear2 = st.columns(2)
            if c_clear1.button("🗑️ Vymazat košík a přejít jinam", type="primary", width="stretch"):
                st.session_state.kunden_korb_liste = []
                st.session_state.aktiver_korb_rest = None
                st.session_state.gewaehltes_rest_kunde = st.session_state.wunsch_rest
                st.session_state.wunsch_rest = None
                st.rerun()
            if c_clear2.button("❌ Zrušit změnu", width="stretch"):
                st.session_state.wunsch_rest = None
                st.rerun()
                
    if st.session_state.gewaehltes_rest_kunde is None:
        st.info("Pro zobrazení nabídky si prosím nahoře kliknutím vyberte restauraci nebo supermarket.")
    else:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.subheader(f"📋 Nabídka: {st.session_state.gewaehltes_rest_kunde}")
            l_vorher = len(st.session_state.kunden_korb_liste)
            rendering_menue_grid(st.session_state.gewaehltes_rest_kunde, "kunden_korb")
            if len(st.session_state.kunden_korb_liste) > l_vorher:
                st.session_state.aktiver_korb_rest = st.session_state.gewaehltes_rest_kunde

        with col2:
            st.subheader("🛒 Váš nákupní košík")
            gesamtsumme = 0.0
            artikel_strings = []
            
            if not st.session_state.kunden_korb_liste:
                st.info("Košík je prázdný. Přidejte položky z nabídky vlevo.")
            else:
                st.caption(f"Odesíláte objednávku z: {st.session_state.aktiver_korb_rest}")
                for idx, item in enumerate(st.session_state.kunden_korb_liste):
                    st.text(f"• {item['name']} = {item['preis']:.2f} €")
                    gesamtsumme += item["preis"]
                    artikel_strings.append(item["name"])
                    
                if st.button("🧹 Vyčistit košík", key="clear_kunden", width="stretch"):
                    st.session_state.kunden_korb_liste = []
                    st.session_state.aktiver_korb_rest = None
                    st.rerun()
                    
            st.write("---")
            
            if st.session_state.aktiver_korb_rest in ["Billa", "Penny", "Hofer"]:
                liefergebuehr = 4.90 if st.session_state.kunden_korb_liste else 0.0
            else:
                liefergebuehr = 3.90 if st.session_state.kunden_korb_liste else 0.0
                
            endbetrag = gesamtsumme + liefergebuehr
            
            st.text(f"Mezisoučet položky: {gesamtsumme:.2f} €")
            st.text(f"Doprava (Liefergebühr): {liefergebuehr:.2f} €")
            st.markdown(f"### **Celková cena: {endbetrag:.2f} €**")
            
            st.write("---")
            st.markdown("#### 📍 Údaje pro doručení")
            k_name = st.text_input("Jméno a příjmení", "Max Mustermann")
            k_telefon = st.text_input("Telefonní číslo", "+43 ")
            k_adresse = st.text_input("Adresa doručení v Steyru", "Hauptstraße 12, Steyr")
            k_zahlung = st.selectbox("Způsob platby", ["💳 Online platební karta (Stripe)", "💵 Hotovost při převzetí"])
            k_trinkgeld = st.number_input("Trinkgeld pro řidiče (€)", min_value=0.0, max_value=20.0, value=0.0, step=0.5)
            
            if st.session_state.kunden_korb_liste:
                if st.button("🚀 ZÁVAZNĚ OBJEDNAT A ZAPLATIT", type="primary", width="stretch"):
                    if not k_name or not k_adresse or len(k_telefon) < 8:
                        st.error("Prosím vyplňte kompletní údaje pro kurýra včetně správného telefonu!")
                    else:
                        if k_zahlung == "💳 Online platební karta (Stripe)":
                            with st.spinner("Zabezpečená autorizace karty na platební bráně Stripe..."):
                                time.sleep(1.5)
                            st.success(f"💳 Platba {endbetrag:.2f} € byla úspěšně zpracována!")
                            
                        neue_bestellung = {
                            "restaurant": st.session_state.aktiver_korb_rest,
                            "obsah": ", ".join(artikel_strings),
                            "cena": f"{gesamtsumme:.2f}",
                            "platba": "Platba kartou (Stripe)" if k_zahlung == "💳 Online platební karta (Stripe)" else "Barzahlung",
                            "adresa": f"{k_adresse} | Kunde: {k_name} | Tel: {k_telefon}",
                            "stav": "Wartet auf Bestätigung durch Kassa",
                            "kuryr": "Petr (Auto)",
                            "cas": datetime.now().strftime("%H:%M:%S"),
                            "dysko": f"{k_trinkgeld:.2f}",
                            "cas_pripravy": "10"
                        }
                        bestellung_speichern(neue_bestellung)
                        st.session_state.kunden_korb_liste = []
                        st.session_state.aktiver_korb_rest = None
                        st.balloons()
                        st.success("🎉 Objednávka byla úspěšně odeslána do systému!")
                        time.sleep(1.5)
                        st.rerun()

# ====== 2. KASSA / POKLADNA ======
elif rolle == "🏬 2. Kassa / Pokladna":
    st_autorefresh(interval=5 * 1000, key="kassa_autorefresh")
    st.header("🏬 Kassa & Správa objednávek")
    
    docs = bestellungen_laden()
    if "zeit_online" not in st.session_state: st.session_state.zeit_online = {}
    if "zeit_manuell" not in st.session_state: st.session_state.zeit_manuell = 10

    st.subheader("🔔 Nové online objednávky ke schválení")
    online_gefunden = False
    for d in docs:
        f = d["fields"]
        status = f["stav"]["stringValue"]
        doc_name = d["name"]
        nr_obj = f.get("cislo_objednavky", {}).get("stringValue", "0")
        r_von = f.get("restaurant", {}).get("stringValue", "Smash Brothers")
        
        if status == "Wartet auf Bestätigung durch Kassa":
            online_gefunden = True
            if doc_name not in st.session_state.zeit_online: st.session_state.zeit_online[doc_name] = 10
                
            with st.container(border=True):
                col_o1, col_o2, col_o3 = st.columns([2, 1, 1])
                with col_o1:
                    st.markdown(f"### 📦 OBJEDNÁVKA #{int(nr_obj):04d} ({r_von})")
                    st.markdown(f"**Obsah:** {f['obsah']['stringValue']} ({f['cena']['stringValue']} €)")
                    st.text(f"📍 {f['adresa']['stringValue']} | Čas: {f['cas']['stringValue']}")
                with col_o2:
                    st.markdown(f"⏱️ **Čas přípravy:** `{st.session_state.zeit_online[doc_name]} Min`")
                    zc1, zc2 = st.columns(2)
                    if zc1.button("➕ 5 Min", key=f"p5_on_{doc_name}"): 
                        st.session_state.zeit_online[doc_name] += 5
                        st.rerun()
                    if zc2.button("➖ 5 Min", key=f"m5_on_{doc_name}"):
                        if st.session_state.zeit_online[doc_name] > 5: 
                            st.session_state.zeit_online[doc_name] -= 5
                            st.rerun()
                with col_o3:
                    if st.button("✔️ Schválit do kuchyně", key=f"prij_online_{doc_name}", type="primary", width="stretch"):
                        bestellstatus_aktualisieren(doc_name, "In Zubereitung (Küche)", "Petr (Auto)", f["adresa"]["stringValue"], st.session_state.zeit_online[doc_name])
                        st.rerun()
                        
    if not online_gefunden: st.info("Žádné nové online objednávky nečekají.")
        
    st.write("---")
    st.subheader("✍️ Manuální zadání (Telefon / Pult)")
    st.session_state.gewaehltes_rest_kassa = st.selectbox("Vyberte provozovnu:", ["Smash Brothers", "King Food", "Billa", "Penny", "Hofer"])
    
    col_kassa_1, col_kassa_2 = st.columns([2, 1])
    with col_kassa_1:
        rendering_menue_grid(st.session_state.gewaehltes_rest_kassa, "rest_korb")
                    
    with col_kassa_2:
        r_summe = 0.0
        r_artikel_strings = []
        if not st.session_state.rest_korb_liste:
            st.info("Pultový lístek je prázdný.")
        else:
            for item in st.session_state.rest_korb_liste:
                st.text(f"• {item['name']} = {item['preis']:.2f} €")
                r_summe += item["preis"]
                r_artikel_strings.append(item["name"])
                
            if st.button("🧹 Vymazat lístek", key="clear_rest", width="stretch"):
                st.session_state.rest_korb_liste = []
                st.rerun()
                
        st.write("---")
        st.metric("Celkem za zboží", f"{r_summe:.2f} €")
        r_name = st.text_input("Jméno zákazníka", "Zákazník na telefonu", key="r_name")
        r_tel = st.text_input("Telefon", "+43 ", key="r_tel")
        r_adresse = st.text_input("Adresa", "Ennser Straße 5, Steyr", key="r_adr")
        r_zahlung = st.selectbox("Platba", ["Barzahlung", "Online-Karte"], key="r_zahl")
        
        st.markdown(f"⏱️ **Čas doručení/přípravy:** `{st.session_state.zeit_manuell} Min`")
        mc1, mc2 = st.columns(2)
        if mc1.button("➕ 5 Min", key="p5_man"): 
            st.session_state.zeit_manuell += 5
            st.rerun()
        if mc2.button("➖ 5 Min", key="m5_man"):
            if st.session_state.zeit_manuell > 5: 
                st.session_state.zeit_manuell -= 5
                st.rerun()
                
        if st.button("📥 ODESLAT ROVNOU DO KUCHYNĚ / KURÝROVI", type="primary", width="stretch"):
            if not r_artikel_strings:
                st.error("Prázdný nákup!")
            else:
                neue_bestellung = {
                    "restaurant": st.session_state.gewaehltes_rest_kassa,
                    "obsah": ", ".join(r_artikel_strings),
                    "cena": f"{r_summe:.2f}",
                    "platba": r_zahlung,
                    "adresa": f"{r_adresse} | Kunde: {r_name} | Tel: {r_tel}",
                    "stav": "In Zubereitung (Küche)",
                    "kuryr": "Petr (Auto)",
                    "cas": datetime.now().strftime("%H:%M:%S"),
                    "dysko": "0.00",
                    "cas_pripravy": str(st.session_state.zeit_manuell)
                }
                bestellung_speichern(neue_bestellung)
                st.session_state.rest_korb_liste = []
                st.session_state.zeit_manuell = 10
                st.success("Odesláno na přípravu!")
                st.rerun()

    st.write("---")
    if st.button("🗑️ Resetovat a smazat celou databázi historie"): 
        alle_bestellungen_loeschen()
        st.rerun()

# ====== 3. KÜCHE MONITOR ======
elif rolle == "👨‍🍳 3. Küche Monitor":
    st_autorefresh(interval=5 * 1000, key="kueche_autorefresh")
    st.header("👨‍🍳 Monitor v kuchyni a expedici (Küche Monitor)")
    
    docs = bestellungen_laden()
    offene_kueche = False
    cols_kueche = st.columns(3)
    k_idx = 0
    
    for d in docs:
        f = d["fields"]
        status = f["stav"]["stringValue"]
        doc_name = d["name"]
        nr_obj = f.get("cislo_objednavky", {}).get("stringValue", "0")
        r_von = f.get("restaurant", {}).get("stringValue", "Smash Brothers")
        
        try:
            label_bon = f"BON #{int(nr_obj):04d}"
        except:
            label_bon = f"BON #{nr_obj}"
        
        if status == "In Zubereitung (Küche)":
            offene_kueche = True
            with cols_kueche[k_idx % 3]:
                with st.container(border=True):
                    st.markdown(
                        f'<div style="background-color: #ffffff; border: 2px solid #333333; padding: 15px; border-radius: 4px; font-family: monospace; color: #000000 !important;">'
                        f'<h3 style="text-align: center; color: #e91e63 !important; margin: 0;">{label_bon}</h3>'
                        f'<p style="text-align: center; color: #333333 !important; font-weight: bold; margin: 2px 0;">{r_von}</p>'
                        f'<p style="text-align: center; color: #555555 !important; margin: 5px 0;">Čas: {f["cas"]["stringValue"]}</p>'
                        f'<hr style="border-top: 1px dashed #333333;">',
                        unsafe_allow_html=True
                    )
                    
                    items_list = f['obsah']['stringValue'].split(", ")
                    for item in items_list:
                        st.markdown(f"<p style='color: #000000 !important; font-size: 16px; font-weight: bold; margin: 4px 0;'>• {item}</p>", unsafe_allow_html=True)
                    
                    st.markdown(
                        f'<hr style="border-top: 1px dashed #333333;">'
                        f'<p style="color: #000000 !important; margin: 0;"><b>Typ:</b> {f["platba"]["stringValue"]}</p>'
                        f'</div>',
                        unsafe_allow_html=True
                    )
                    st.write("")
                    
                    if st.button(f"✅ READY / EXPEDICE ({label_bon})", key=f"hotovo_kuch_{doc_name}", type="primary", width="stretch"):
                        c_prip = f.get("cas_pripravy", {}).get("stringValue", "10")
                        bestellstatus_aktualisieren(doc_name, "Ready for Pick-up", "Petr (Auto)", f["adresa"]["stringValue"], c_prip)
                        st.success(f"{label_bon} HOTOVO!")
                        time.sleep(0.2)
                        st.rerun()
            k_idx += 1
            
    if not offene_kueche:
        st.info("Všechny zakázky jsou hotové. V kuchyni je čisto! ✨")

# ====== 4. FAHRER-ANSICHT ======
elif rolle == "🚗 4. Fahrer-Ansicht (Mobil & Finanzen)":
    st_autorefresh(interval=5 * 1000, key="fahrer_autorefresh")
    st.header("Kurier-App (Rozvoz Volt and value)")
    fahrer_name = "Petr (Auto)"
    
    if "bargeld_eur" not in st.session_state:
        st.session_state.bargeld_eur = 0.0
        st.session_state.provision_eur = 0.0
        st.session_state.trinkgeld_eur = 0.0

    st.subheader("📊 Přehled mých financí na směně")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Moje provize", f"{st.session_state.provision_eur:.2f} €")
    with c2: st.metric("Vybrané spropitné (dýška)", f"{st.session_state.trinkgeld_eur:.2f} €")
    with c3: st.metric("Hotovost u sebe (Limit 200€)", f"{st.session_state.bargeld_eur:.2f} / 200.00 €")
    st.write("---")
    
    if st.session_state.bargeld_eur >= 200.0:
        st.error("🛑 STOP! DOSÁHL JSI LIMITU 200 € V HOTOVOSTI.")
        st.warning("⚠️ Z bezpečnostních důvodů musíš okamžitě jet odevzdat hotovost na centrálu Volt and value.")
        if st.button("💰 Hotovost složena na centrále Volt and value", type="primary", width="stretch"):
            st.session_state.bargeld_eur = 0.0
            st.success("Peníze bezpečně složeny, můžeš pokračovat v jízdách!")
            time.sleep(1)
            st.rerun()
    else:
        st.subheader("Aktuální zakázky v mé pipeline")
        docs = bestellungen_laden()
        aktive_auftraege = []
        for d in docs:
            try:
                if d["fields"]["kuryr"]["stringValue"] == fahrer_name and d["fields"]["stav"]["stringValue"] in ["In Zubereitung (Küche)", "Ready for Pick-up", "Auf dem Weg zum Kunden"]:
                    aktive_auftraege.append(d)
            except:
                pass
        
        if not aktive_auftraege:
            st.info("Zatím žádná aktivní práce. Čekej na schválení na pokladně...")
        else:
            for d in aktive_auftraege:
                f = d["fields"]
                status = f["stav"]["stringValue"]
                doc_name = d["name"]
                dysko_val = f.get("dysko", {}).get("stringValue", "0.00")
                minuten_pripravy = f.get("cas_pripravy", {}).get("stringValue", "10")
                nr_obj = f.get("cislo_objednavky", {}).get("stringValue", "0")
                r_von = f.get("restaurant", {}).get("stringValue", "Smash Brothers")
                
                try:
                    txt_nr = f"BON #{int(nr_obj):04d}"
                except:
                    txt_nr = f"BON #{nr_obj}"
                
                if status == "Ready for Pick-up":
                    st.success(f"🚨 KUCHYŇ NEBO OBCHOD MÁ HOTOVO! {txt_nr} ({r_von}) čeká na baru na vyzvednutí!")
                elif status == "Auf dem Weg zum Kunden":
                    st.info(f"🚚 VEZETE OBJEDNÁVKU ZÁKAZNÍKOVI ({txt_nr})")
                else:
                    st.warning(f"⏳ JÍDLO SE PŘIPRAVUJE / NÁKUP SE CHYSTÁ ({txt_nr} - {r_von})")

                with st.container(border=True):
                    st.markdown(f"**📍 Místo vyzvednutí:** `{r_von}`")
                    st.write(f"🍱 **Položky:** {f['obsah']['stringValue']}")
                    st.write(f"💶 **Inkasovat od zákazníka:** {f['cena']['stringValue']} € ({f['platba']['stringValue']})")
                    st.write(f"💰 **Dýško v aplikaci:** {dysko_val} €")
                    
                    if status == "In Zubereitung (Küche)":
                        st.write(f"⏱️ Připraveno bude za cca {minuten_pripravy} minut.")
                    elif status == "Ready for Pick-up":
                        st.write("Věci jsou sbalené na pultu / baru.")
                        if st.button("👍 Potvrdit převzetí na baru / prodejně", key=f"pick_{doc_name}", type="primary", width="stretch"):
                            bestellstatus_aktualisieren(doc_name, "Auf dem Weg zum Kunden", fahrer_name, f["adresa"]["stringValue"], minuten_pripravy)
                            st.rerun()
                    elif status == "Auf dem Weg zum Kunden":
                        st.write(f"➡️ **Adresa klienta:** `{f['adresa']['stringValue']}`")
                        if st.button("✅ Doručeno & Inkasováno", key=f"deliver_{doc_name}", type="primary", width="stretch"):
                            st.session_state.provision_eur += 6.50
                            st.session_state.trinkgeld_eur += float(dysko_val)
                            if f["platba"]["stringValue"] == "Barzahlung":
                                st.session_state.bargeld_eur += float(f["cena"]["stringValue"])
                            bestellstatus_aktualisieren(doc_name, "Geliefert", fahrer_name, f["adresa"]["stringValue"], minuten_pripravy)
                            st.success("Zakázka úspěšně uzavřena!")
                            time.sleep(0.4)
                            st.rerun()
