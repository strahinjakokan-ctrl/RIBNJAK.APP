import os
import json
from datetime import datetime, date
import streamlit as st
from fpdf import FPDF

st.set_page_config(page_title="Evidencija hrane za ribu", page_icon="🌾", layout="wide")

# --- RJEČNIK PREVODA (LATINICA / ĆIRILICA) ---
PREVODI = {
    # Opšte i Meni
    "NASLOV_APP": {"Latinica": "🌾 EVIDENCIJA HRANE ZA RIBU", "Ćirilica": "🌾 ЕВИДЕНЦИЈА ХРАНЕ ЗА РИБУ"},
    "IZABERITE_OPCIJU": {"Latinica": "Izaberite opciju za nastavak:", "Ćirilica": "Изаберите опцију за наставак:"},
    "MENI_NABAVKA": {"Latinica": "🛒 NABAVKA", "Ćirilica": "🛒 НАБАВКА"},
    "MENI_UTROSAK": {"Latinica": "📉 UTROŠAK / PRODAJA", "Ćirilica": "📉 УТРОШАК / ПРОДАЈА"},
    "MENI_STANJE": {"Latinica": "📦 STANJE", "Ćirilica": "📦 СТАЊЕ"},
    "MENI_IZVJESTAJ": {"Latinica": "📊 IZVJEŠTAJ", "Ćirilica": "📊 ИЗВЈЕШТАЈ"},
    "MENI_PODESAVANJA": {"Latinica": "⚙️ PODEŠAVANJA", "Ćirilica": "⚙️ ПОДЕШАВАЊА"},
    "DUGME_POCETNA": {"Latinica": "🏠 POČETNA", "Ćirilica": "🏠 ПОЧЕТНА"},

    # 1. Nabavka Hrane
    "NABAVKA_NASLOV": {"Latinica": "🛒 NABAVKA HRANE", "Ćirilica": "🛒 НАБАВКА ХРАНЕ"},
    "DATUM_UNOSA": {"Latinica": "🕒 Datum unosa:", "Ćirilica": "🕒 Датум уноса:"},
    "GRANULACIJA_LAB": {"Latinica": "Granulacija hrane (mm)", "Ćirilica": "Гранулација хране (мм)"},
    "KOLICINA_KG_LAB": {"Latinica": "Količina (kg)", "Ćirilica": "Количина (кг)"},
    "CIJENA_KG_LAB": {"Latinica": "Cijena po kg (KM)", "Ćirilica": "Цијена по кг (КМ)"},
    "NAPOMENA_NABAVKA": {"Latinica": "Napomena / dobavljač", "Ćirilica": "Напомена / добављач"},
    "UKUPNA_VRIJEDNOST": {"Latinica": "💰 Ukupna vrijednost:", "Ćirilica": "💰 Укупна вриједност:"},
    "DUGME_SACUVAJ_NABAVKU": {"Latinica": "Sačuvaj nabavku", "Ćirilica": "Сачувај набавку"},
    "USPJEH_NABAVKA": {"Latinica": "Uspješno evidentirano: Nabavka -", "Ćirilica": "Успјешно евидентирано: Набавка -"},

    # 2. Utrošak Hrane
    "UTROSAK_NASLOV": {"Latinica": "📉 UTROŠAK / PRODAJA", "Ćirilica": "📉 УТРОШАК / ПРОДАЈА"},
    "LOKACIJA_LAB": {"Latinica": "Izaberite lokaciju / namjenu", "Ćirilica": "Изаберите локацију / намјену"},
    "NAPOMENA_UTROSAK": {"Latinica": "Napomena (kupac / detalji)", "Ćirilica": "Напомена (купац / детаљи)"},
    "DUGME_SACUVAJ_UTROSAK": {"Latinica": "Sačuvaj utrošak", "Ćirilica": "Сачувај утрошак"},
    "USPJEH_UTROSAK": {"Latinica": "Uspješno evidentirano:", "Ćirilica": "Успјешно евидентирано:"},
    "GRESKA_NEDOSTAJE_STANJE": {"Latinica": "Greška: Nema dovoljno hrane ove granulacije na stanju!", "Ćirilica": "Грешка: Нема довољно хране ове гранулације на стању!"},

    # 3. Stanje Hrane
    "STANJE_NASLOV": {"Latinica": "📦 TRENUTNO STANJE HRANE", "Ćirilica": "📦 ТРЕНУТНО СТАЊЕ ХРАНЕ"},
    "STANJE_OPIS": {
        "Latinica": "Pregled raspoloživih količina hrane izračunat u realnom vremenu na osnovu svih nabavki i utrošaka.",
        "Ćirilica": "Преглед расположивих количина хране израчунат у реалном временом на основу свих набавки и утрошака."
    },
    "METRIKA_UKUPNO_KG": {"Latinica": "⚖️ Ukupne zalihe hrane", "Ćirilica": "⚖️ Укупне залихе хране"},
    "METRIKA_UKUPNO_KM": {"Latinica": "💰 Procijenjena vrijednost zaliha", "Ćirilica": "💰 Процијењена вриједност залиха"},
    "STANJE_PO_GRANULACIJAMA": {"Latinica": "📦 Stanje po granulacijama (u mm):", "Ćirilica": "📦 Стање по гранулацијама (у мм):"},
    "GRANULACIJA_NAZIV": {"Latinica": "Granulacija", "Ćirilica": "Гранулација"},
    "UPOZORENJE_NISKE_ZALIHE": {
        "Latinica": "⚠️ KRITIČNO NISKE ZALIHE (ispod zadate granice):",
        "Ćirilica": "⚠️ КРИТИЧНО НИСКЕ ЗАЛИХЕ (испод задате границе):"
    },

    # 4. Izvještaj
    "IZVJESTAJ_NASLOV": {"Latinica": "📊 IZVJEŠTAJ", "Ćirilica": "📊 ИЗВЈЕШТАЈ"},
    "FILTERI_NASLOV": {"Latinica": "🔍 Filteri za prikaz na ekranu", "Ćirilica": "🔍 Филтери за приказ на екрану"},
    "FILTERI_STAMPA": {"Latinica": "🖨️ Filteri za preuzimanje izvještaja (štampu)", "Ćirilica": "🖨️ Филтери за преузимање извјештаја (штампу)"},
    "DATUM_OD": {"Latinica": "Datum od:", "Ćirilica": "Датум од:"},
    "DATUM_DO": {"Latinica": "Datum do:", "Ćirilica": "Датум до:"},
    "FILTRIRAJ_JEZERO": {"Latinica": "Filtriraj po jezeru / lokaciji:", "Ćirilica": "Филтрирај по језеру / локацији:"},
    "NABAVKA_PERIOD": {"Latinica": "🛒 Nabavka u periodu", "Ćirilica": "🛒 Набавка у периоду"},
    "UKUPNO_KG_LAB": {"Latinica": "Ukupno kg:", "Ćirilica": "Укупно кг:"},
    "UKUPNO_KM_LAB": {"Latinica": "Ukupno KM:", "Ćirilica": "Укупно КМ:"},
    "UTROSAK_IZLAZ": {"Latinica": "📉 Utrošak / izlaz", "Ćirilica": "📉 Утрошак / излаз"},
    "UKUPNO_IZLAZ": {"Latinica": "Ukupno izlaz hrane:", "Ćirilica": "Укупно излаз хране:"},
    "NEMA_NABAVKI": {"Latinica": "Nema nabavki u izabranom periodu.", "Ćirilica": "Нема набавки у изабраном периоду."},
    "NEMA_UTROSKA": {"Latinica": "Nema unosa za izabrane filtere.", "Ćirilica": "Нема уноса за изабране филтере."},
    "PREUZMI_PDF": {"Latinica": "📄 Preuzimanje izvještaja", "Ćirilica": "📄 Преузимање извјештаја"},
    "DUGME_PDF": {"Latinica": "📄 Preuzmi PDF izvještaj", "Ćirilica": "📄 Преузми PDF извјештај"},
    "OTVORI_SVE": {"Latinica": "📂 Otvori sve", "Ćirilica": "📂 Отвори све"},
    "ZATVORI_SVE": {"Latinica": "📁 Zatvori sve", "Ćirilica": "📁 Затвори све"},
    "DUGME_EDIT": {"Latinica": "✏️ Izmijeni", "Ćirilica": "✏️ Измијени"},
    "DUGME_OBRISI": {"Latinica": "🗑️ Obriši", "Ćirilica": "🗑️ Обриши"},
    "IZMJENA_NABAVKE": {"Latinica": "✏️ **Izmjena unosa nabavke:**", "Ćirilica": "✏️ **Измјена уноса набавке:**"},
    "IZMJENA_UTROSKA": {"Latinica": "✏️ **Izmjena unosa utroška:**", "Ćirilica": "✏️ **Измјена уноса утрошка:**"},
    "LAB_GRANULACIJA_MM": {"Latinica": "Granulacija (mm):", "Ćirilica": "Гранулација (мм):"},
    "LAB_KOLICINA_KG": {"Latinica": "Količina (kg):", "Ćirilica": "Количина (кг):"},
    "LAB_CIJENA_KG": {"Latinica": "Cijena po kg (KM):", "Ćirilica": "Цијена по кг (КМ):"},
    "LAB_NAPOMENA": {"Latinica": "Napomena:", "Ćirilica": "Напомена:"},
    "LAB_JEZERO_LOKACIJA": {"Latinica": "Jezero / Lokacija:", "Ćirilica": "Језеро / Локација:"},
    "DUGME_SACUVAJ_IZMJENE": {"Latinica": "💾 Sačuvaj izmjene", "Ćirilica": "💾 Сачувај измјене"},
    "DUGME_OTKAZI": {"Latinica": "❌ Otkaži", "Ćirilica": "❌ Откажи"},
    "CIJENA_LAB_KRATKO": {"Latinica": "Cijena", "Ćirilica": "Цијена"},
    "LOKACIJA_KRATKO": {"Latinica": "Lokacija", "Ćirilica": "Локација"},

    # 5. Podešavanja
    "PODESAVANJA_NASLOV": {"Latinica": "⚙️ PODEŠAVANJA APLIKACIJE", "Ćirilica": "⚙️ ПОДЕШАВАЊА АПЛИКАЦИЈЕ"},
    "NAZIVI_JEZERA_POD": {"Latinica": "📍 Nazivi jezera / lokacija", "Ćirilica": "📍 Називи језера / локација"},
    "JEZERA_OPIS": {
        "Latinica": "Izmjena naziva čuva se odmah. Redoslijed možete mijenjati strelicama ⬆️⬇️ — isti redoslijed se koristi svugdje u padajućim menijima.",
        "Ćirilica": "Измјена назива чува се одмах. Редослијед можете мијењати стрелицама ⬆️⬇️ — исти редослијед се користи свугдје у падајућим менијима."
    },
    "NOVO_JEZERO_PLACEHOLDER": {"Latinica": "Novo jezero / prodaja...", "Ćirilica": "Ново језеро / продаја..."},
    "GRANULACIJE_POD": {"Latinica": "📏 Granulacije hrane (mm)", "Ćirilica": "📏 Гранулације хране (мм)"},
    "GRANULACIJE_OPIS": {
        "Latinica": "Možete kucati direktno ili koristiti dugmad − / + (korak 0.1 mm). Lista se automatski sortira.",
        "Ćirilica": "Можете куцати директно или користити дугмад − / + (корак 0.1 мм). Листа се аутоматски сортира."
    },
    "GRESKA_PRAZNO_NAZIV": {"Latinica": "Naziv ne može biti prazan.", "Ćirilica": "Назив не може бити празан."},
    "GRESKA_DUPLIKAT_NAZIV": {"Latinica": "⚠️ Taj naziv već postoji na listi.", "Ćirilica": "⚠️ Тај назив већ постоји на листи."},
    "GRESKA_DUPLIKAT_GRAN": {"Latinica": "⚠️ Ta granulacija već postoji na listi.", "Ćirilica": "⚠️ Та гранулација већ постоји на листи."},
    "GRESKA_MIN_STAVKI": {"Latinica": "⚠️ Mora ostati bar jedna stavka na listi.", "Ćirilica": "⚠️ Мора остати бар једна ставка на листи."},
    "LAB_NOVI_NAZIV": {"Latinica": "Novi naziv:", "Ćirilica": "Нови назив:"},
    "GORE": {"Latinica": "Gore", "Ćirilica": "Горе"},
    "DOLE": {"Latinica": "Dole", "Ćirilica": "Доле"},
    "UPOZORENJE_POD": {"Latinica": "⚠️ Upozorenje za zalihe", "Ćirilica": "⚠️ Упозорење за залихе"},
    "KRITICNA_GRANICA_LAB": {"Latinica": "Kritična granica zaliha po granulaciji (kg):", "Ćirilica": "Критична граница залиха по гранулацији (кг):"},
    "PISMO_POD": {"Latinica": "🔤 Pismo", "Ćirilica": "🔤 Писмо"},
    "PISMO_LAB": {"Latinica": "Izaberite pismo:", "Ćirilica": "Изаберите писмо:"},
    "DUGME_SACUVAJ_POD": {"Latinica": "💾 Sačuvaj podešavanja", "Ćirilica": "💾 Сачувај подешавања"},
    "USPJEH_POD": {"Latinica": "Podešavanja su uspješno sačuvana!", "Ćirilica": "Подешавања су успјешно сачувана!"},
    "BACKUP_NASLOV": {"Latinica": "💾 Sigurnosna kopija", "Ćirilica": "💾 Сигурносна копија"},
    "DUGME_BACKUP": {"Latinica": "📥 PREUZMI KOPIJU", "Ćirilica": "📥 ПРЕУЗМИ КОПИЈУ"},
    "RESTORE_NASLOV": {"Latinica": "📤 Vraćanje iz sigurnosne kopije", "Ćirilica": "📤 Враћање из сигурносне копије"},
    "RESTORE_LAB": {"Latinica": "Izaberite JSON fajl sigurnosne kopije:", "Ćirilica": "Изаберите JSON фајл сигурносне копије:"},
    "DUGME_RESTORE": {"Latinica": "📤 Učitaj kopiju", "Ćirilica": "📤 Учитај копију"},
    "USPJEH_RESTORE": {"Latinica": "Podaci su uspješno vraćeni iz kopije!", "Ćirilica": "Подаци су успјешно враћени из копије!"},
    "GRESKA_RESTORE": {"Latinica": "Greška: fajl nije validna sigurnosna kopija.", "Ćirilica": "Грешка: фајл није валидна сигурносна копија."},
    "RESET_NASLOV": {"Latinica": "🔄 Fabrička podešavanja", "Ćirilica": "🔄 Фабричка подешавања"},
    "DUGME_RESET": {"Latinica": "🔄 RESETUJ NA FABRIČKA", "Ćirilica": "🔄 РЕСЕТУЈ НА ФАБРИЧКА"},
    "USPJEH_RESET": {"Latinica": "Podešavanja su vraćena na fabričke vrijednosti!", "Ćirilica": "Подешавања су успјешно враћене!"},
    "COPYRIGHT": {
        "Latinica": "Aplikaciju razvio Kokan Strahinja © 2026",
        "Ćirilica": "Апликацију развио Кокан Страхиња © 2026"
    }
}

FAJL_PODACI = "podaci_ribnjak.json"
PODRAZUMEVANE_GRANULACIJE = ["1.5", "2.0", "3.0", "4.0", "5.0"]
PODRAZUMEVANA_JEZERA = ["JEZERO 1", "JEZERO 2", "JEZERO 3", "JEZERO 4", "PRODAJA"]


def ucitaj_podatke():
    podaci_struktura = {
        "nabavka_hrane": [],
        "utrosak_hrane": [],
        "podesavanja": {
            "pismo": "Latinica",
            "granulacije": PODRAZUMEVANE_GRANULACIJE,
            "jezera": PODRAZUMEVANA_JEZERA,
            "kriticno_kg": 20.0
        }
    }
    if os.path.exists(FAJL_PODACI):
        try:
            with open(FAJL_PODACI, "r", encoding="utf-8") as f:
                p = json.load(f)

                nabavke = p.get("nabavka_hrane", [])
                for n in nabavke:
                    if isinstance(n.get("Datum_obj"), str):
                        n["Datum_obj"] = datetime.strptime(n["Datum_obj"], "%Y-%m-%d").date()
                    n["Granulacija"] = str(n["Granulacija"]).replace(" mm", "").strip()
                podaci_struktura["nabavka_hrane"] = nabavke

                utrosci = p.get("utrosak_hrane", [])
                for u in utrosci:
                    if isinstance(u.get("Datum_obj"), str):
                        u["Datum_obj"] = datetime.strptime(u["Datum_obj"], "%Y-%m-%d").date()
                    u["Granulacija"] = str(u["Granulacija"]).replace(" mm", "").strip()
                    if "Jezero" in u:
                        u["Jezero"] = u["Jezero"].strip().upper()
                podaci_struktura["utrosak_hrane"] = utrosci

                if "podesavanja" in p:
                    podaci_struktura["podesavanja"].update(p["podesavanja"])
                    podaci_struktura["podesavanja"]["granulacije"] = [
                        str(g).replace(" mm", "").strip() for g in podaci_struktura["podesavanja"]["granulacije"]
                    ]
                    try:
                        podaci_struktura["podesavanja"]["granulacije"].sort(key=lambda x: float(x))
                    except (ValueError, TypeError):
                        pass
                    podaci_struktura["podesavanja"]["jezera"] = [
                        str(j).strip().upper() for j in podaci_struktura["podesavanja"]["jezera"]
                    ]
        except Exception:
            pass
    return podaci_struktura


def sacuvaj_podatke():
    nabavke_priprema = []
    for n in st.session_state.nabavka_hrane:
        n_copy = n.copy()
        if isinstance(n_copy["Datum_obj"], (date, datetime)):
            n_copy["Datum_obj"] = n_copy["Datum_obj"].strftime("%Y-%m-%d")
        nabavke_priprema.append(n_copy)

    utrosci_priprema = []
    for u in st.session_state.utrosak_hrane:
        u_copy = u.copy()
        if isinstance(u_copy["Datum_obj"], (date, datetime)):
            u_copy["Datum_obj"] = u_copy["Datum_obj"].strftime("%Y-%m-%d")
        utrosci_priprema.append(u_copy)

    podaci_za_snimanje = {
        "nabavka_hrane": nabavke_priprema,
        "utrosak_hrane": utrosci_priprema,
        "podesavanja": st.session_state.podesavanja
    }

    with open(FAJL_PODACI, "w", encoding="utf-8") as f:
        json.dump(podaci_za_snimanje, f, ensure_ascii=False, indent=4)


if "učitano" not in st.session_state:
    ucitano = ucitaj_podatke()
    st.session_state.nabavka_hrane = ucitano["nabavka_hrane"]
    st.session_state.utrosak_hrane = ucitano["utrosak_hrane"]
    st.session_state.podesavanja = ucitano["podesavanja"]
    st.session_state["učitano"] = True

if "stranica" not in st.session_state:
    st.session_state.stranica = "POCETNA"

if "edit_nabavka_idx" not in st.session_state:
    st.session_state.edit_nabavka_idx = None

if "edit_utrosak_idx" not in st.session_state:
    st.session_state.edit_utrosak_idx = None

if "expand_all" not in st.session_state:
    st.session_state.expand_all = True


def t(kljuc):
    pismo = st.session_state.podesavanja.get("pismo", "Latinica")
    if kljuc in PREVODI:
        return PREVODI[kljuc].get(pismo, PREVODI[kljuc]["Latinica"])
    return kljuc


def resetuj_unos_kljuceve(prefiks):
    kljucevi = [k for k in st.session_state.keys() if k.startswith(prefiks)]
    for k in kljucevi:
        del st.session_state[k]


def normalizuj_naziv(tekst):
    return str(tekst).strip().upper()


# --- UPRAVLJANJE LISTOM JEZERA / LOKACIJA ---
def izmijeni_jezero(idx):
    lista = st.session_state.podesavanja["jezera"]
    stari = lista[idx]
    novi = normalizuj_naziv(st.session_state[f"jezero_input_{idx}"])

    if not novi:
        st.session_state["_flash_warning"] = t("GRESKA_PRAZNO_NAZIV")
        st.session_state[f"jezero_input_{idx}"] = stari
        return False

    ostali = [j for i, j in enumerate(lista) if i != idx]
    if novi in ostali:
        st.session_state["_flash_warning"] = t("GRESKA_DUPLIKAT_NAZIV")
        st.session_state[f"jezero_input_{idx}"] = stari
        return False

    lista[idx] = novi
    st.session_state.podesavanja["jezera"] = lista
    sacuvaj_podatke()
    return True


def obrisi_jezero(idx):
    lista = st.session_state.podesavanja["jezera"]
    if len(lista) <= 1:
        st.session_state["_flash_warning"] = t("GRESKA_MIN_STAVKI")
        return
    lista.pop(idx)
    st.session_state.podesavanja["jezera"] = lista
    sacuvaj_podatke()
    resetuj_unos_kljuceve("jezero_input_")


def pomjeri_jezero_gore(idx):
    lista = st.session_state.podesavanja["jezera"]
    if idx > 0:
        lista[idx - 1], lista[idx] = lista[idx], lista[idx - 1]
        st.session_state.podesavanja["jezera"] = lista
        sacuvaj_podatke()
        resetuj_unos_kljuceve("jezero_input_")


def pomjeri_jezero_dole(idx):
    lista = st.session_state.podesavanja["jezera"]
    if idx < len(lista) - 1:
        lista[idx + 1], lista[idx] = lista[idx], lista[idx + 1]
        st.session_state.podesavanja["jezera"] = lista
        sacuvaj_podatke()
        resetuj_unos_kljuceve("jezero_input_")


def dodaj_jezero():
    novi = normalizuj_naziv(st.session_state.get("novo_jezero_input", ""))
    lista = st.session_state.podesavanja["jezera"]
    if not novi:
        return
    if novi in lista:
        st.session_state["_flash_warning"] = t("GRESKA_DUPLIKAT_NAZIV")
        return
    lista.append(novi)
    st.session_state.podesavanja["jezera"] = lista
    sacuvaj_podatke()
    st.session_state["novo_jezero_input"] = ""
    resetuj_unos_kljuceve("jezero_input_")


# --- UPRAVLJANJE LISTOM GRANULACIJA ---
def sortiraj_granulacije():
    st.session_state.podesavanja["granulacije"].sort(key=lambda x: float(x))


def izmijeni_granulaciju(idx):
    lista = st.session_state.podesavanja["granulacije"]
    stari = lista[idx]
    novi = f"{st.session_state[f'gran_input_{idx}']:.1f}"

    ostali = [g for i, g in enumerate(lista) if i != idx]
    if novi in ostali:
        st.session_state["_flash_warning"] = t("GRESKA_DUPLIKAT_GRAN")
        st.session_state[f"gran_input_{idx}"] = float(stari)
        return

    lista[idx] = novi
    sortiraj_granulacije()
    st.session_state.podesavanja["granulacije"] = lista
    sacuvaj_podatke()
    resetuj_unos_kljuceve("gran_input_")


def obrisi_granulaciju(idx):
    lista = st.session_state.podesavanja["granulacije"]
    if len(lista) <= 1:
        st.session_state["_flash_warning"] = t("GRESKA_MIN_STAVKI")
        return
    lista.pop(idx)
    st.session_state.podesavanja["granulacije"] = lista
    sacuvaj_podatke()
    resetuj_unos_kljuceve("gran_input_")


def dodaj_granulaciju():
    lista = st.session_state.podesavanja["granulacije"]
    novi = f"{st.session_state.get('nova_gran_input', 1.0):.1f}"
    if novi in lista:
        st.session_state["_flash_warning"] = t("GRESKA_DUPLIKAT_GRAN")
        return
    lista.append(novi)
    sortiraj_granulacije()
    st.session_state.podesavanja["granulacije"] = lista
    sacuvaj_podatke()
    resetuj_unos_kljuceve("gran_input_")


granulacije_lista = sorted(
    st.session_state.podesavanja.get("granulacije", PODRAZUMEVANE_GRANULACIJE),
    key=lambda x: float(x)
)
st.session_state.podesavanja["granulacije"] = granulacije_lista
jezera_i_prodaja_lista = st.session_state.podesavanja.get("jezera", PODRAZUMEVANA_JEZERA)
kriticna_granica = float(st.session_state.podesavanja.get("kriticno_kg", 20.0))

# --- UPRAVLJANJE PRIKAZOM NASLOVA I DUGMETA POČETNA ---
if st.session_state.stranica == "POCETNA":
    st.markdown(f"<h1 style='text-align: center; margin-bottom: 0px;'>{t('NASLOV_APP')}</h1>", unsafe_allow_html=True)
    st.markdown("---")
else:
    col_h_prazno, col_h_btn = st.columns([4, 1])
    with col_h_btn:
        if st.button(t("DUGME_POCETNA"), use_container_width=True):
            st.session_state.stranica = "POCETNA"
            st.rerun()
    st.markdown("---")

# --- KONTROLNA TABLA ---
if st.session_state.stranica == "POCETNA":
    st.markdown(f"<p style='text-align: center; color: #666; font-size: 13px; font-weight: 600; margin-bottom: 5px;'>{t('IZABERITE_OPCIJU')}</p>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)

    col_center = st.columns([1, 2, 1])[1]
    with col_center:
        if st.button(t("MENI_NABAVKA"), use_container_width=True):
            st.session_state.stranica = "NABAVKA"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("MENI_UTROSAK"), use_container_width=True):
            st.session_state.stranica = "UTROSAK"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("MENI_STANJE"), use_container_width=True):
            st.session_state.stranica = "STANJE"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("MENI_IZVJESTAJ"), use_container_width=True):
            st.session_state.stranica = "IZVJESTAJ"
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button(t("MENI_PODESAVANJA"), use_container_width=True):
            st.session_state.stranica = "PODESAVANJA"
            st.rerun()

    st.markdown("---")
    st.markdown(f"<p style='text-align: center; color: #777777; font-size: 13px;'>{t('COPYRIGHT')}</p>", unsafe_allow_html=True)

# --- 1. NABAVKA ---
elif st.session_state.stranica == "NABAVKA":
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 15px;'>{t('NABAVKA_NASLOV')}</h5>", unsafe_allow_html=True)
    trenutno = datetime.now()
    st.info(f"{t('DATUM_UNOSA')} **{trenutno.strftime('%d/%m/%Y %H:%M')}**")

    with st.form("forma_nabavka", clear_on_submit=True):
        granulacija = st.selectbox(t("GRANULACIJA_LAB"), [f"{g} mm" for g in granulacije_lista])
        gran_cista = granulacija.replace(" mm", "")

        kolicina_kg = st.number_input(t("KOLICINA_KG_LAB"), min_value=0.0, step=5.0, value=100.0)
        cijena_po_kg = st.number_input(t("CIJENA_KG_LAB"), min_value=0.0, step=0.1, value=1.50)
        napomena = st.text_input(t("NAPOMENA_NABAVKA"))

        ukupno_km = kolicina_kg * cijena_po_kg
        st.write(f"{t('UKUPNA_VRIJEDNOST')} **{ukupno_km:.2f} KM**")

        if st.form_submit_button(t("DUGME_SACUVAJ_NABAVKU")):
            st.session_state.nabavka_hrane.append({
                "Datum_obj": trenutno.date(),
                "Datum_vrijeme_str": trenutno.strftime("%d/%m/%Y %H:%M"),
                "Granulacija": gran_cista,
                "Količina (kg)": kolicina_kg,
                "Cijena/kg (KM)": cijena_po_kg,
                "Ukupno (KM)": ukupno_km,
                "Napomena": napomena
            })
            sacuvaj_podatke()
            st.success(f"{t('USPJEH_NABAVKA')} {gran_cista} mm ({kolicina_kg} kg - {ukupno_km:.2f} KM)")

# --- 2. UTROŠAK ---
elif st.session_state.stranica == "UTROSAK":
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 15px;'>{t('UTROSAK_NASLOV')}</h5>", unsafe_allow_html=True)
    trenutno = datetime.now()
    st.info(f"{t('DATUM_UNOSA')} **{trenutno.strftime('%d/%m/%Y %H:%M')}**")

    with st.form("forma_utrosak", clear_on_submit=True):
        jezero = st.selectbox(t("LOKACIJA_LAB"), jezera_i_prodaja_lista)
        granulacija = st.selectbox(t("GRANULACIJA_LAB"), [f"{g} mm" for g in granulacije_lista])
        gran_cista = granulacija.replace(" mm", "")

        kolicina_kg = st.number_input(t("KOLICINA_KG_LAB"), min_value=0.0, step=5.0, value=10.0)
        napomena = st.text_input(t("NAPOMENA_UTROSAK"))

        if st.form_submit_button(t("DUGME_SACUVAJ_UTROSAK")):
            trenutno_stanje = sum(n["Količina (kg)"] for n in st.session_state.nabavka_hrane if n["Granulacija"] == gran_cista) - \
                sum(u["Količina (kg)"] for u in st.session_state.utrosak_hrane if u["Granulacija"] == gran_cista)

            if kolicina_kg > trenutno_stanje:
                st.error(t("GRESKA_NEDOSTAJE_STANJE"))
            else:
                st.session_state.utrosak_hrane.append({
                    "Datum_obj": trenutno.date(),
                    "Datum_vrijeme_str": trenutno.strftime("%d/%m/%Y %H:%M"),
                    "Jezero": jezero,
                    "Granulacija": gran_cista,
                    "Količina (kg)": kolicina_kg,
                    "Napomena": napomena
                })
                sacuvaj_podatke()
                st.success(f"{t('USPJEH_UTROSAK')} {jezero} - {gran_cista} mm ({kolicina_kg} kg)")

# --- 3. STANJE ---
elif st.session_state.stranica == "STANJE":
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 12px; font-size: 1.25rem;'>{t('STANJE_NASLOV')}</h5>", unsafe_allow_html=True)
    st.write(t("STANJE_OPIS"))

    stanje = {g: 0.0 for g in granulacije_lista}
    prosjecna_cijena = {g: 0.0 for g in granulacije_lista}
    ukupno_nabavljeno_kg = {g: 0.0 for g in granulacije_lista}
    ukupno_nabavljeno_km = {g: 0.0 for g in granulacije_lista}

    for n in st.session_state.nabavka_hrane:
        g = n["Granulacija"]
        if g in stanje:
            stanje[g] += n["Količina (kg)"]
            ukupno_nabavljeno_kg[g] += n["Količina (kg)"]
            ukupno_nabavljeno_km[g] += n["Ukupno (KM)"]

    for u in st.session_state.utrosak_hrane:
        g = u["Granulacija"]
        if g in stanje:
            stanje[g] -= u["Količina (kg)"]

    for g in granulacije_lista:
        if ukupno_nabavljeno_kg[g] > 0:
            prosjecna_cijena[g] = ukupno_nabavljeno_km[g] / ukupno_nabavljeno_kg[g]

    uk_stanje_kg = sum(stanje.values())
    uk_vrijednost_km = sum(stanje[g] * prosjecna_cijena[g] for g in granulacije_lista if stanje[g] > 0)

    col_s1, col_s2 = st.columns(2)
    with col_s1:
        st.metric(t("METRIKA_UKUPNO_KG"), f"{uk_stanje_kg:.1f} kg")
    with col_s2:
        st.metric(t("METRIKA_UKUPNO_KM"), f"{uk_vrijednost_km:.2f} KM")

    st.markdown("---")
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 15px; font-size: 1.25rem;'>{t('STANJE_PO_GRANULACIJAMA')}</h5>", unsafe_allow_html=True)

    cols = st.columns(2)
    kriticne_granulacije = []

    for i, g in enumerate(granulacije_lista):
        col = cols[i % 2]
        kg = stanje[g]
        with col:
            st.metric(label=f"{t('GRANULACIJA_NAZIV')} {g} mm", value=f"{kg:.1f} kg")
            if kg < kriticna_granica:
                kriticne_granulacije.append(f"• **{g} mm** (Trenutno: **{kg:.1f} kg** / Prag: {kriticna_granica:.0f} kg)")

    if kriticne_granulacije:
        st.markdown("---")
        poruka_upozorenja = f"##### {t('UPOZORENJE_NISKE_ZALIHE')}\n\n" + "\n".join(kriticne_granulacije)
        st.error(poruka_upozorenja)

# --- 4. IZVJEŠTAJ ---
elif st.session_state.stranica == "IZVJESTAJ":
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 15px;'>{t('IZVJESTAJ_NASLOV')}</h5>", unsafe_allow_html=True)

    st.markdown(f"##### {t('FILTERI_NASLOV')}")
    danas = date.today()
    pocetni_datum = date(danas.year, danas.month, 1)

    datum_od_ekran = st.date_input(t("DATUM_OD"), value=pocetni_datum, format="DD/MM/YYYY", key="d_od_e")
    datum_do_ekran = st.date_input(t("DATUM_DO"), value=danas, format="DD/MM/YYYY", key="d_do_e")

    opcije_filtera = ["⭐ SVE / UKUPNO"] + jezera_i_prodaja_lista
    izabrana_opcija_ekran = st.selectbox(t("FILTRIRAJ_JEZERO"), opcije_filtera, key="f_jez_e")

    filtrirane_nabavke_ekran = [
        (idx, n) for idx, n in enumerate(st.session_state.nabavka_hrane)
        if datum_od_ekran <= n["Datum_obj"] <= datum_do_ekran and n["Granulacija"] in granulacije_lista
    ]

    if izabrana_opcija_ekran == "⭐ SVE / UKUPNO":
        filtrirani_utrosci_ekran = [
            (idx, u) for idx, u in enumerate(st.session_state.utrosak_hrane)
            if datum_od_ekran <= u["Datum_obj"] <= datum_do_ekran and u["Granulacija"] in granulacije_lista
        ]
    else:
        filtrirani_utrosci_ekran = [
            (idx, u) for idx, u in enumerate(st.session_state.utrosak_hrane)
            if datum_od_ekran <= u["Datum_obj"] <= datum_do_ekran and u["Jezero"] == izabrana_opcija_ekran and u["Granulacija"] in granulacije_lista
        ]

    st.markdown("---")

    if "expand_nabavka" not in st.session_state:
        st.session_state.expand_nabavka = False
    if "expand_utrosak" not in st.session_state:
        st.session_state.expand_utrosak = False

    st.markdown(f"##### {t('NABAVKA_PERIOD')}")
    uk_nabavljeno_kg = sum(n["Količina (kg)"] for _, n in filtrirane_nabavke_ekran)
    uk_nabavljeno_km = sum(n["Ukupno (KM)"] for _, n in filtrirane_nabavke_ekran)
    st.write(f"**{t('UKUPNO_KG_LAB')}** {uk_nabavljeno_kg:.1f} kg | **{t('UKUPNO_KM_LAB')}** {uk_nabavljeno_km:.2f} KM")

    b_otvori_n, b_zatvori_n = st.columns(2)
    with b_otvori_n:
        if st.button(t("OTVORI_SVE"), key="btn_otvori_n", use_container_width=True):
            st.session_state.expand_nabavka = True
            st.rerun()
    with b_zatvori_n:
        if st.button(t("ZATVORI_SVE"), key="btn_zatvori_n", use_container_width=True):
            st.session_state.expand_nabavka = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if filtrirane_nabavke_ekran:
        for redni_br, (orig_idx, n) in enumerate(reversed(filtrirane_nabavke_ekran), 1):
            with st.expander(f"**{redni_br}. [{n['Datum_vrijeme_str']}] {n['Granulacija']} mm** - {n['Količina (kg)']} kg ({n['Ukupno (KM)']} KM)", expanded=st.session_state.expand_nabavka):
                st.write(f"• {t('CIJENA_LAB_KRATKO')}: {n['Cijena/kg (KM)']} KM/kg | {t('UKUPNO_KM_LAB')} {n['Ukupno (KM)']} KM")
                if n['Napomena']:
                    st.write(f"• {t('LAB_NAPOMENA')} {n['Napomena']}")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(t("DUGME_EDIT"), key=f"edit_n_{orig_idx}", use_container_width=True):
                        st.session_state.edit_nabavka_idx = orig_idx
                        st.session_state.edit_utrosak_idx = None
                        st.rerun()
                with c_btn2:
                    if st.button(t("DUGME_OBRISI"), key=f"del_n_{orig_idx}", use_container_width=True):
                        st.session_state.nabavka_hrane.pop(orig_idx)
                        sacuvaj_podatke()
                        st.rerun()

            if st.session_state.edit_nabavka_idx == orig_idx:
                st.info(t("IZMJENA_NABAVKE"))
                with st.form(key=f"form_edit_n_{orig_idx}"):
                    e_gran = st.selectbox(t("LAB_GRANULACIJA_MM"), [f"{g} mm" for g in granulacije_lista], index=granulacije_lista.index(n['Granulacija']) if n['Granulacija'] in granulacije_lista else 0)
                    e_kg = st.number_input(t("LAB_KOLICINA_KG"), min_value=0.0, value=float(n['Količina (kg)']), step=5.0)
                    e_cijena = st.number_input(t("LAB_CIJENA_KG"), min_value=0.0, value=float(n['Cijena/kg (KM)']), step=0.1)
                    e_nap = st.text_input(t("LAB_NAPOMENA"), value=n['Napomena'])

                    col_sub1, col_sub2 = st.columns(2)
                    if col_sub1.form_submit_button(t("DUGME_SACUVAJ_IZMJENE"), use_container_width=True):
                        g_cista = e_gran.replace(" mm", "")
                        st.session_state.nabavka_hrane[orig_idx]['Granulacija'] = g_cista
                        st.session_state.nabavka_hrane[orig_idx]['Količina (kg)'] = e_kg
                        st.session_state.nabavka_hrane[orig_idx]['Cijena/kg (KM)'] = e_cijena
                        st.session_state.nabavka_hrane[orig_idx]['Ukupno (KM)'] = e_kg * e_cijena
                        st.session_state.nabavka_hrane[orig_idx]['Napomena'] = e_nap
                        sacuvaj_podatke()
                        st.session_state.edit_nabavka_idx = None
                        st.rerun()
                    if col_sub2.form_submit_button(t("DUGME_OTKAZI"), use_container_width=True):
                        st.session_state.edit_nabavka_idx = None
                        st.rerun()
    else:
        st.info(t("NEMA_NABAVKI"))

    st.markdown("---")
    st.markdown(f"##### {t('UTROSAK_IZLAZ')} ({izabrana_opcija_ekran})")
    uk_utroseno_kg = sum(u["Količina (kg)"] for _, u in filtrirani_utrosci_ekran)
    st.write(f"**{t('UKUPNO_IZLAZ')}** {uk_utroseno_kg:.1f} kg")

    b_otvori_u, b_zatvori_u = st.columns(2)
    with b_otvori_u:
        if st.button(t("OTVORI_SVE"), key="btn_otvori_u", use_container_width=True):
            st.session_state.expand_utrosak = True
            st.rerun()
    with b_zatvori_u:
        if st.button(t("ZATVORI_SVE"), key="btn_zatvori_u", use_container_width=True):
            st.session_state.expand_utrosak = False
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if filtrirani_utrosci_ekran:
        for redni_br, (orig_idx, u) in enumerate(reversed(filtrirani_utrosci_ekran), 1):
            with st.expander(f"**{redni_br}. [{u['Datum_vrijeme_str']}] {u['Jezero']}** - {u['Granulacija']} mm ({u['Količina (kg)']} kg)", expanded=st.session_state.expand_utrosak):
                st.write(f"• {t('LOKACIJA_KRATKO')}: {u['Jezero']} | {t('GRANULACIJA_NAZIV')}: {u['Granulacija']} mm | {t('KOLICINA_KG_LAB')}: {u['Količina (kg)']} kg")
                if u['Napomena']:
                    st.write(f"• {t('LAB_NAPOMENA')} {u['Napomena']}")
                c_btn1, c_btn2 = st.columns(2)
                with c_btn1:
                    if st.button(t("DUGME_EDIT"), key=f"edit_u_{orig_idx}", use_container_width=True):
                        st.session_state.edit_utrosak_idx = orig_idx
                        st.session_state.edit_nabavka_idx = None
                        st.rerun()
                with c_btn2:
                    if st.button(t("DUGME_OBRISI"), key=f"del_u_{orig_idx}", use_container_width=True):
                        st.session_state.utrosak_hrane.pop(orig_idx)
                        sacuvaj_podatke()
                        st.rerun()

            if st.session_state.edit_utrosak_idx == orig_idx:
                st.info(t("IZMJENA_UTROSKA"))
                with st.form(key=f"form_edit_u_{orig_idx}"):
                    e_j = st.selectbox(t("LAB_JEZERO_LOKACIJA"), jezera_i_prodaja_lista, index=jezera_i_prodaja_lista.index(u['Jezero']) if u['Jezero'] in jezera_i_prodaja_lista else 0)
                    e_gran = st.selectbox(t("LAB_GRANULACIJA_MM"), [f"{g} mm" for g in granulacije_lista], index=granulacije_lista.index(u['Granulacija']) if u['Granulacija'] in granulacije_lista else 0)
                    e_kg = st.number_input(t("LAB_KOLICINA_KG"), min_value=0.0, value=float(u['Količina (kg)']), step=5.0)
                    e_nap = st.text_input(t("LAB_NAPOMENA"), value=u['Napomena'])

                    col_sub1, col_sub2 = st.columns(2)
                    if col_sub1.form_submit_button(t("DUGME_SACUVAJ_IZMJENE"), use_container_width=True):
                        g_cista = e_gran.replace(" mm", "")
                        st.session_state.utrosak_hrane[orig_idx]['Jezero'] = e_j
                        st.session_state.utrosak_hrane[orig_idx]['Granulacija'] = g_cista
                        st.session_state.utrosak_hrane[orig_idx]['Količina (kg)'] = e_kg
                        st.session_state.utrosak_hrane[orig_idx]['Napomena'] = e_nap
                        sacuvaj_podatke()
                        st.session_state.edit_utrosak_idx = None
                        st.rerun()
                    if col_sub2.form_submit_button(t("DUGME_OTKAZI"), use_container_width=True):
                        st.session_state.edit_utrosak_idx = None
                        st.rerun()
    else:
        st.info(t("NEMA_UTROSKA"))

    st.markdown("---")
    st.markdown(f"##### {t('FILTERI_STAMPA')}")

    datum_od_stampa = st.date_input(t("DATUM_OD"), value=pocetni_datum, format="DD/MM/YYYY", key="d_od_s")
    datum_do_stampa = st.date_input(t("DATUM_DO"), value=danas, format="DD/MM/YYYY", key="d_do_s")
    izabrana_opcija_stampa = st.selectbox(t("FILTRIRAJ_JEZERO"), opcije_filtera, key="f_jez_s")

    filtrirane_nabavke_stampa = [
        (idx, n) for idx, n in enumerate(st.session_state.nabavka_hrane)
        if datum_od_stampa <= n["Datum_obj"] <= datum_do_stampa and n["Granulacija"] in granulacije_lista
    ]

    if izabrana_opcija_stampa == "⭐ SVE / UKUPNO":
        filtrirani_utrosci_stampa = [
            (idx, u) for idx, u in enumerate(st.session_state.utrosak_hrane)
            if datum_od_stampa <= u["Datum_obj"] <= datum_do_stampa and u["Granulacija"] in granulacije_lista
        ]
    else:
        filtrirani_utrosci_stampa = [
            (idx, u) for idx, u in enumerate(st.session_state.utrosak_hrane)
            if datum_od_stampa <= u["Datum_obj"] <= datum_do_stampa and u["Jezero"] == izabrana_opcija_stampa and u["Granulacija"] in granulacije_lista
        ]

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"##### {t('PREUZMI_PDF')}")

    def cisti_tekst(tekst):
        """Konvertuje specifične i ćirilične karaktere u standardne latinične radi sigurne podrške u PDF-u bez vanjskih fontova"""
        if not tekst:
            return ""
        mapa = {
            'Č': 'C', 'Ć': 'C', 'Đ': 'Dj', 'Š': 'S', 'Ž': 'Z',
            'č': 'c', 'ć': 'c', 'đ': 'dj', 'š': 's', 'ž': 'z',
            'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Ђ': 'Dj', 'Е': 'E', 'Ж': 'Z', 'З': 'Z', 'И': 'I', 'Ј': 'J', 'К': 'K', 'Л': 'L', 'Љ': 'Lj', 'М': 'M', 'Н': 'N', 'Њ': 'Nj', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'Ћ': 'C', 'У': 'U', 'Ф': 'F', 'Х': 'H', 'Ц': 'C', 'Ч': 'C', 'Џ': 'Dz', 'Ш': 'S',
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'ђ': 'dj', 'е': 'e', 'ж': 'z', 'з': 'z', 'и': 'i', 'ј': 'j', 'к': 'k', 'л': 'l', 'љ': 'lj', 'м': 'm', 'н': 'n', 'њ': 'nj', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'ћ': 'c', 'у': 'u', 'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'c', 'џ': 'dz', 'ш': 's'
        }
        return "".join([mapa.get(c, c) for c in str(tekst)])

    def napravi_pdf_izvjestaj_fpdf(nabavke_par, utrosci_par, d_od, d_do, opcija_naziv):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Courier", size=10)

        naslov = cisti_tekst("IZVJEŠTAJ O NABAVCI I UTROŠKU HRANE")
        period_str = cisti_tekst(f"Period: {d_od.strftime('%d/%m/%Y')} - {d_do.strftime('%d/%m/%Y')}")
        filter_str = cisti_tekst(f"Filter: {opcija_naziv.replace('⭐ ', '')}")

        pdf.set_font("Courier", style="B", size=13)
        pdf.cell(0, 8, naslov, ln=True, align="C")
        pdf.set_font("Courier", size=10)
        pdf.cell(0, 5, period_str, ln=True, align="C")
        pdf.cell(0, 5, filter_str, ln=True, align="C")
        pdf.ln(3)
        pdf.cell(0, 0, "-" * 65, ln=True)
        pdf.ln(5)

        # 1. NABAVKA
        pdf.set_font("Courier", style="B", size=11)
        pdf.cell(0, 6, cisti_tekst("1. NABAVKA HRANE"), ln=True)
        pdf.set_font("Courier", size=9)

        sum_nabavka_gran = {g: 0.0 for g in granulacije_lista}
        sum_nabavka_km = {g: 0.0 for g in granulacije_lista}

        if nabavke_par:
            for _, n in nabavke_par:
                g = n['Granulacija']
                if g in sum_nabavka_gran:
                    sum_nabavka_gran[g] += n['Količina (kg)']
                    sum_nabavka_km[g] += n['Ukupno (KM)']
                nap = cisti_tekst(n['Napomena'])
                txt = f"[{n['Datum_vrijeme_str']}] {g} mm | {n['Količina (kg)']} kg | Cijena: {n['Cijena/kg (KM)']} KM/kg | Ukupno: {n['Ukupno (KM)']} KM"
                pdf.cell(0, 4, cisti_tekst(txt), ln=True)
                if nap:
                    pdf.cell(0, 4, f"    Napomena: {nap}", ln=True)

            pdf.ln(2)
            pdf.set_font("Courier", style="B", size=9)
            pdf.cell(0, 5, cisti_tekst("UKUPNO NABAVKA PO GRANULACIJAMA:"), ln=True)
            pdf.set_font("Courier", size=9)
            for g in granulacije_lista:
                if sum_nabavka_gran[g] > 0:
                    pdf.cell(0, 4, cisti_tekst(f"  * {g} mm: {sum_nabavka_gran[g]:.1f} kg ({sum_nabavka_km[g]:.2f} KM)"), ln=True)

            uk_sve_n_kg = sum(sum_nabavka_gran.values())
            uk_sve_n_km = sum(sum_nabavka_km.values())
            pdf.set_font("Courier", style="B", size=9)
            pdf.cell(0, 5, cisti_tekst(f"UKUPNO SVE NABAVLJENO: {uk_sve_n_kg:.1f} kg | {uk_sve_n_km:.2f} KM"), ln=True)
        else:
            pdf.cell(0, 4, cisti_tekst("Nema unosa u izabranom periodu."), ln=True)

        pdf.ln(4)
        pdf.cell(0, 0, "-" * 65, ln=True)
        pdf.ln(4)

        # 2. UTROŠAK
        pdf.set_font("Courier", style="B", size=11)
        pdf.cell(0, 6, cisti_tekst("2. UTROŠAK / PRODAJA HRANE"), ln=True)
        pdf.set_font("Courier", size=9)

        sum_utrosak_gran = {g: 0.0 for g in granulacije_lista}

        if utrosci_par:
            for _, u in utrosci_par:
                g = u['Granulacija']
                if g in sum_utrosak_gran:
                    sum_utrosak_gran[g] += u['Količina (kg)']
                lok = cisti_tekst(u['Jezero'])
                nap = cisti_tekst(u['Napomena'])
                txt = f"[{u['Datum_vrijeme_str']}] {lok} | {g} mm | {u['Količina (kg)']} kg"
                pdf.cell(0, 4, cisti_tekst(txt), ln=True)
                if nap:
                    pdf.cell(0, 4, f"    Napomena: {nap}", ln=True)

            pdf.ln(2)
            pdf.set_font("Courier", style="B", size=9)
            pdf.cell(0, 5, cisti_tekst("UKUPNO UTROŠAK PO GRANULACIJAMA:"), ln=True)
            pdf.set_font("Courier", size=9)
            for g in granulacije_lista:
                if sum_utrosak_gran[g] > 0:
                    pdf.cell(0, 4, cisti_tekst(f"  * {g} mm: {sum_utrosak_gran[g]:.1f} kg"), ln=True)

            uk_sve_u_kg = sum(sum_utrosak_gran.values())
            pdf.set_font("Courier", style="B", size=9)
            pdf.cell(0, 5, cisti_tekst(f"UKUPNO SVE UTROŠENO: {uk_sve_u_kg:.1f} kg"), ln=True)
        else:
            pdf.cell(0, 4, cisti_tekst("Nema unosa u izabranom periodu."), ln=True)

        # Pravilan izvoz u bajtove za fpdf2
        pdf_str = pdf.output(dest="S")
        if isinstance(pdf_str, str):
            return pdf_str.encode("latin-1")
        return bytes(pdf_str)

    pdf_podaci = napravi_pdf_izvjestaj_fpdf(
        filtrirane_nabavke_stampa,
        filtrirani_utrosci_stampa,
        datum_od_stampa,
        datum_do_stampa,
        izabrana_opcija_stampa
    )

    st.download_button(
        label=t("DUGME_PDF"),
        data=pdf_podaci,
        file_name=f"izvjestaj_ribnjak_{datum_od_stampa.strftime('%Y%m%d')}_{datum_do_stampa.strftime('%Y%m%d')}.pdf",
        mime="application/pdf",
        use_container_width=True
    )

# --- 5. PODEŠAVANJA ---
elif st.session_state.stranica == "PODESAVANJA":
    st.markdown(f"<h5 style='text-align: center; margin-bottom: 15px;'>{t('PODESAVANJA_NASLOV')}</h5>", unsafe_allow_html=True)

    if st.session_state.get("_flash_success"):
        st.success(st.session_state["_flash_success"])
        del st.session_state["_flash_success"]

    if st.session_state.get("_flash_warning"):
        st.warning(st.session_state["_flash_warning"])
        del st.session_state["_flash_warning"]

    st.markdown(f"**{t('NAZIVI_JEZERA_POD')}**")
    st.caption(t("JEZERA_OPIS"))

    if "edit_jezero_idx" not in st.session_state:
        st.session_state.edit_jezero_idx = None

    jezera_trenutna = st.session_state.podesavanja["jezera"]
    ukupno_jezera = len(jezera_trenutna)

    for idx, naziv_jezera in enumerate(jezera_trenutna):
        c_naziv, c_edit = st.columns([5, 1])
        with c_naziv:
            st.write(naziv_jezera)
        with c_edit:
            if st.button("✏️", key=f"jezero_edit_btn_{idx}", use_container_width=True):
                st.session_state.edit_jezero_idx = None if st.session_state.edit_jezero_idx == idx else idx
                st.rerun()

        if st.session_state.edit_jezero_idx == idx:
            with st.container(border=True):
                st.text_input(
                    t("LAB_NOVI_NAZIV"),
                    value=naziv_jezera,
                    key=f"jezero_input_{idx}"
                )
                if st.button(t("DUGME_SACUVAJ_IZMJENE"), key=f"jezero_save_{idx}", use_container_width=True):
                    if izmijeni_jezero(idx):
                        st.session_state.edit_jezero_idx = None
                    st.rerun()

                c_up, c_down = st.columns(2)
                with c_up:
                    if st.button("⬆️ " + t("GORE"), key=f"jezero_up_{idx}", use_container_width=True, disabled=(idx == 0)):
                        pomjeri_jezero_gore(idx)
                        st.rerun()
                with c_down:
                    if st.button("⬇️ " + t("DOLE"), key=f"jezero_down_{idx}", use_container_width=True, disabled=(idx == ukupno_jezera - 1)):
                        pomjeri_jezero_dole(idx)
                        st.rerun()

                if st.button(t("DUGME_OBRISI"), key=f"jezero_del_{idx}", use_container_width=True):
                    obrisi_jezero(idx)
                    st.session_state.edit_jezero_idx = None
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1n, c2n = st.columns([5, 1])
    with c1n:
        st.text_input(
            "novo_jezero",
            key="novo_jezero_input",
            placeholder=t("NOVO_JEZERO_PLACEHOLDER"),
            label_visibility="collapsed"
        )
    with c2n:
        if st.button("➕", key="dodaj_jezero_btn", use_container_width=True):
            dodaj_jezero()
            st.rerun()

    st.markdown("---")

    st.markdown(f"**{t('GRANULACIJE_POD')}**")
    st.caption(t("GRANULACIJE_OPIS"))

    for idx in range(len(st.session_state.podesavanja["granulacije"])):
        trenutna_vrijednost = float(st.session_state.podesavanja["granulacije"][idx])
        c1, c2 = st.columns([5, 1])
        with c1:
            st.number_input(
                f"gran_{idx}",
                min_value=0.1,
                max_value=50.0,
                value=trenutna_vrijednost,
                step=0.1,
                format="%.1f",
                key=f"gran_input_{idx}",
                label_visibility="collapsed",
                on_change=izmijeni_granulaciju,
                args=(idx,)
            )
        with c2:
            if st.button("🗑️", key=f"gran_del_{idx}", use_container_width=True):
                obrisi_granulaciju(idx)
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    c1g, c2g = st.columns([5, 1])
    with c1g:
        st.number_input(
            "nova_granulacija",
            min_value=0.1,
            max_value=50.0,
            value=1.0,
            step=0.1,
            format="%.1f",
            key="nova_gran_input",
            label_visibility="collapsed"
        )
    with c2g:
        if st.button("➕", key="dodaj_gran_btn", use_container_width=True):
            dodaj_granulaciju()
            st.rerun()

    st.markdown("---")

    with st.form("forma_podesavanja_ostalo"):
        st.markdown(f"**{t('UPOZORENJE_POD')}**")
        nova_kriticna_granica = st.number_input(
            t("KRITICNA_GRANICA_LAB"),
            min_value=0.0,
            step=5.0,
            value=float(st.session_state.podesavanja.get("kriticno_kg", 20.0))
        )

        st.markdown(f"**{t('PISMO_POD')}**")
        trenutno_pismo = st.session_state.podesavanja.get("pismo", "Latinica")
        izabrano_pismo = st.radio(t("PISMO_LAB"), ["Latinica", "Ćirilica"], index=0 if trenutno_pismo == "Latinica" else 1)

        st.markdown("<br>", unsafe_allow_html=True)

        if st.form_submit_button(t("DUGME_SACUVAJ_POD"), use_container_width=True):
            st.session_state.podesavanja["kriticno_kg"] = float(nova_kriticna_granica)
            st.session_state.podesavanja["pismo"] = izabrano_pismo

            sacuvaj_podatke()
            st.success(t("USPJEH_POD"))
            st.rerun()

    st.markdown("---")
    st.markdown(f"##### {t('BACKUP_NASLOV')}")
    if os.path.exists(FAJL_PODACI):
        with open(FAJL_PODACI, "r", encoding="utf-8") as f:
            json_sadrzaj = f.read()
        st.download_button(
            label=t("DUGME_BACKUP"),
            data=json_sadrzaj,
            file_name=f"backup_ribnjak_{date.today().strftime('%Y%m%d')}.json",
            mime="application/json",
            use_container_width=True
        )

    st.markdown("---")
    st.markdown(f"##### {t('RESTORE_NASLOV')}")
    ucitani_fajl = st.file_uploader(t("RESTORE_LAB"), type=["json"], key="restore_uploader")
    if ucitani_fajl is not None:
        if st.button(t("DUGME_RESTORE"), use_container_width=True):
            try:
                sadrzaj = json.loads(ucitani_fajl.getvalue().decode("utf-8"))
                if "nabavka_hrane" in sadrzaj and "utrosak_hrane" in sadrzaj:
                    with open(FAJL_PODACI, "w", encoding="utf-8") as f:
                        json.dump(sadrzaj, f, ensure_ascii=False, indent=4)
                    ucitano = ucitaj_podatke()
                    st.session_state.nabavka_hrane = ucitano["nabavka_hrane"]
                    st.session_state.utrosak_hrane = ucitano["utrosak_hrane"]
                    st.session_state.podesavanja = ucitano["podesavanja"]
                    st.success(t("USPJEH_RESTORE"))
                    st.rerun()
                else:
                    st.error(t("GRESKA_RESTORE"))
            except Exception:
                st.error(t("GRESKA_RESTORE"))

    st.markdown("---")
    st.markdown(f"##### {t('RESET_NASLOV')}")

    if "potvrda_reseta" not in st.session_state:
        st.session_state.potvrda_reseta = False
    if "prikazi_poruku_reset" not in st.session_state:
        st.session_state.prikazi_poruku_reset = False

    if not st.session_state.potvrda_reseta:
        if st.button(t("DUGME_RESET"), key="btn_reset_main", use_container_width=True):
            st.session_state.potvrda_reseta = True
            st.session_state.prikazi_poruku_reset = False
            st.rerun()
    else:
        with st.container(border=True):
            st.warning("⚠️ **Da li ste sigurni da želite vratiti podešavanja na fabrička?**\n\nOva akcija će poništiti sve vaše izmjene lokacija, granulacija i ostalih podešavanja.")
            col_da, col_ne = st.columns(2)
            with col_da:
                if st.button("✅ Da, siguran sam", key="btn_potvrdi_reset", use_container_width=True):
                    st.session_state.podesavanja = {
                        "pismo": "Latinica",
                        "granulacije": PODRAZUMEVANE_GRANULACIJE,
                        "jezera": PODRAZUMEVANA_JEZERA,
                        "kriticno_kg": 20.0
                    }
                    sacuvaj_podatke()
                    st.session_state.potvrda_reseta = False
                    st.session_state.prikazi_poruku_reset = True
                    st.rerun()

            with col_ne:
                if st.button("❌ Odustani", key="btn_otkazi_reset", use_container_width=True):
                    st.session_state.potvrda_reseta = False
                    st.session_state.prikazi_poruku_reset = False
                    st.rerun()

    if st.session_state.prikazi_poruku_reset:
        st.markdown("<br>", unsafe_allow_html=True)
        st.success("✅ Podešavanja su uspješno vraćena na fabrička!")