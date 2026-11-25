"""Streamlit web app for the Farm Advisor."""
from __future__ import annotations

import pandas as pd
import streamlit as st

from farm_advisor import get_advice, parse_station_csv

st.set_page_config(page_title="Farm Advisor", page_icon="🌱", layout="centered")

LOCATIONS = {
    "Yaoundé (Centre)": (3.87, 11.52), "Douala (Littoral)": (4.05, 9.77),
    "Bafoussam (West)": (5.48, 10.42), "Bamenda (North-West)": (5.96, 10.15),
    "Buea (South-West)": (4.16, 9.24), "Bertoua (East)": (4.58, 13.68),
    "Ebolowa (South)": (2.91, 11.15), "Ngaoundéré (Adamawa)": (7.32, 13.58),
    "Garoua (North)": (9.30, 13.39), "Maroua (Far North)": (10.59, 14.32),
    "Other (enter coordinates)": None,
}

# All app copy lives here so adding or correcting a translation is straightforward.
TEXT = {
    "English": {
        "title":"🌱 Farm Advisor", "intro":"Should you plant now, and what? Based on live rainfall and temperature data for your area.",
        "language":"Language", "where":"Where is your farm?", "other":"Other (enter coordinates)",
        "latitude":"Latitude", "longitude":"Longitude", "tip":"Tip: in Google Maps, right-click your farm to copy its coordinates.",
        "station":"I have my own weather station", "upload":"Upload the last 30 days as CSV (columns: date, rain_mm, tmax, tmin)",
        "loading":"Reading the latest weather data…", "error":"Could not get weather data right now. Please try again later.",
        "rain10":"Rain, last 10 days", "rain7":"Rain, next 7 days", "dry":"Dry days ahead (max)",
        "chart":"Daily rainfall (mm)", "observed":"Observed", "forecast":"Forecast", "crops":"Best crops for this season",
        "none":"No rain-fed crop is suitable right now. Plant only with irrigation.", "avoid":"Avoid for now:", "all":"All weather indicators",
        "weather":"Weather data: Open-Meteo. Advice is a guide only; combine it with local knowledge and your agricultural extension officer.",
        "decision":{"PLANT NOW":"PLANT NOW", "WAIT":"WAIT", "PREPARE":"PREPARE", "DO NOT PLANT (rain-fed)":"DO NOT PLANT (rain-fed)"},
        "reason":{"PLANT NOW":"The rains have started and no long dry spell is forecast. You can plant now.", "WAIT":"Weather conditions are risky. Wait until the heavy rain or dry spell has passed.", "PREPARE":"Rain is expected soon. Prepare your land and seed; sow once the soil is moist.", "DO NOT PLANT (rain-fed)":"There is too little rain. Plant only if you can irrigate."},
        "indicators":{"rain_last_30_days_mm":"rain last 30 days mm", "rain_last_10_days_mm":"rain last 10 days mm", "rain_next_7_days_mm":"rain next 7 days mm", "rain_next_16_days_mm":"rain next 16 days mm", "water_balance_30_days_mm":"water balance 30 days mm", "longest_dry_spell_next_14_days":"longest dry spell next 14 days", "heaviest_3_day_rain_forecast_mm":"heaviest 3-day rain forecast mm", "soil_moisture_3_9cm":"soil moisture 3–9 cm", "mean_temp_next_16_days_c":"mean temperature next 16 days °C"},
    },
    "Français": {
        "title":"🌱 Conseiller agricole", "intro":"Faut-il planter maintenant, et quelle culture choisir ? Conseils basés sur les précipitations et températures récentes de votre région.",
        "language":"Langue", "where":"Où se trouve votre ferme ?", "other":"Autre (saisir les coordonnées)", "latitude":"Latitude", "longitude":"Longitude",
        "tip":"Astuce : faites un clic droit sur votre ferme dans Google Maps pour copier ses coordonnées.", "station":"J’ai ma propre station météo", "upload":"Importez les 30 derniers jours au format CSV (colonnes : date, rain_mm, tmax, tmin)",
        "loading":"Récupération des dernières données météo…", "error":"Données météo indisponibles. Veuillez réessayer plus tard.", "rain10":"Pluie, 10 derniers jours", "rain7":"Pluie, 7 prochains jours", "dry":"Jours secs à venir (maximum)",
        "chart":"Précipitations quotidiennes (mm)", "observed":"Observées", "forecast":"Prévisions", "crops":"Meilleures cultures pour cette saison", "none":"Aucune culture pluviale ne convient actuellement. Plantez uniquement avec irrigation.", "avoid":"À éviter pour le moment :", "all":"Tous les indicateurs météo",
        "weather":"Données météo : Open-Meteo. Ces conseils sont indicatifs ; tenez compte des connaissances locales et des recommandations de votre agent agricole.",
        "decision":{"PLANT NOW":"PLANTER MAINTENANT", "WAIT":"ATTENDRE", "PREPARE":"SE PRÉPARER", "DO NOT PLANT (rain-fed)":"NE PAS PLANTER (sans irrigation)"},
        "reason":{"PLANT NOW":"Les pluies ont commencé et aucune longue période sèche n’est prévue. Vous pouvez planter.", "WAIT":"Les conditions météo présentent un risque. Attendez la fin des fortes pluies ou de la période sèche.", "PREPARE":"De la pluie est bientôt prévue. Préparez le terrain et les semences ; plantez quand le sol sera humide.", "DO NOT PLANT (rain-fed)":"Il y a trop peu de pluie. Plantez uniquement si vous pouvez irriguer."},
        "indicators":{"rain_last_30_days_mm":"pluie des 30 derniers jours mm", "rain_last_10_days_mm":"pluie des 10 derniers jours mm", "rain_next_7_days_mm":"pluie des 7 prochains jours mm", "rain_next_16_days_mm":"pluie des 16 prochains jours mm", "water_balance_30_days_mm":"bilan hydrique sur 30 jours mm", "longest_dry_spell_next_14_days":"plus longue période sèche sur 14 jours", "heaviest_3_day_rain_forecast_mm":"pluie maximale prévue sur 3 jours mm", "soil_moisture_3_9cm":"humidité du sol à 3–9 cm", "mean_temp_next_16_days_c":"température moyenne sur 16 jours °C"},
    },
    "Pidgin": {
        "title":"🌱 Farm Advisor", "intro":"You for plant now? And which crop go do well? We dey use current rain and temperature data for your area.",
        "language":"Language", "where":"Where your farm dey?", "other":"Other (put coordinates)", "latitude":"Latitude", "longitude":"Longitude",
        "tip":"Tip: right-click your farm for Google Maps make you copy the coordinates.", "station":"I get my own weather station", "upload":"Upload the last 30 days as CSV (columns: date, rain_mm, tmax, tmin)",
        "loading":"We dey check the latest weather…", "error":"We no fit get weather data now. Abeg try again later.", "rain10":"Rain for last 10 days", "rain7":"Rain for next 7 days", "dry":"Longest dry days wey dey come",
        "chart":"Rain each day (mm)", "observed":"Rain wey don fall", "forecast":"Rain wey dem predict", "crops":"Crops wey fit this season well", "none":"No crop fit grow well with only rain now. Plant only if you fit water am.", "avoid":"Avoid for now:", "all":"All weather information",
        "weather":"Weather data: Open-Meteo. This advice na guide; join am with wetin local farmers and your farm extension officer know.",
        "decision":{"PLANT NOW":"PLANT NOW", "WAIT":"WAIT SMALL", "PREPARE":"PREPARE", "DO NOT PLANT (rain-fed)":"NO PLANT (without irrigation)"},
        "reason":{"PLANT NOW":"Rain don start, and no long dry time dey forecast. You fit plant now.", "WAIT":"The weather fit cause problem. Wait make heavy rain or dry time pass first.", "PREPARE":"Rain go come soon. Prepare your land and seed; plant when soil don wet well.", "DO NOT PLANT (rain-fed)":"Rain no plenty. Plant only if you fit irrigate.",},
        "indicators":{"rain_last_30_days_mm":"rain for last 30 days mm", "rain_last_10_days_mm":"rain for last 10 days mm", "rain_next_7_days_mm":"rain for next 7 days mm", "rain_next_16_days_mm":"rain for next 16 days mm", "water_balance_30_days_mm":"water balance for 30 days mm", "longest_dry_spell_next_14_days":"longest dry time for next 14 days", "heaviest_3_day_rain_forecast_mm":"heaviest rain wey dem predict for 3 days mm", "soil_moisture_3_9cm":"soil water for 3–9 cm", "mean_temp_next_16_days_c":"average temperature for next 16 days °C"},
    },
}

@st.cache_data(ttl=3600, show_spinner=False)
def cached_advice(lat: float, lon: float, station_text: str | None):
    station = parse_station_csv(station_text) if station_text else None
    return get_advice(lat, lon, station)

lang = st.radio("Language / Langue", list(TEXT), horizontal=True, key="language")
t = TEXT[lang]
st.title(t["title"])
st.caption(t["intro"])

location_names = list(LOCATIONS)
other_name = t["other"]
location_names[-1] = other_name
choice = st.selectbox(t["where"], location_names)
if choice == other_name:
    c1, c2 = st.columns(2)
    lat = c1.number_input(t["latitude"], -90.0, 90.0, 3.87, format="%.4f")
    lon = c2.number_input(t["longitude"], -180.0, 180.0, 11.52, format="%.4f")
    st.caption(t["tip"])
else:
    lat, lon = LOCATIONS[choice]

with st.expander(t["station"]):
    upload = st.file_uploader(t["upload"], type="csv")
station_text = upload.getvalue().decode("utf-8") if upload else None

try:
    with st.spinner(t["loading"]):
        advice, past, future = cached_advice(lat, lon, station_text)
except Exception as exc:
    st.error(f"{t['error']}\n\n{exc}")
    st.stop()

decision = t["decision"].get(advice.decision, advice.decision)
show = {"PLANT NOW": st.success, "PREPARE": st.info, "WAIT": st.warning}.get(advice.decision, st.error)
show(f"### {decision}\n{t['reason'].get(advice.decision, '')}")

ind = advice.indicators
m1, m2, m3 = st.columns(3)
m1.metric(t["rain10"], f"{ind['rain_last_10_days_mm']:.0f} mm")
m2.metric(t["rain7"], f"{ind['rain_next_7_days_mm']:.0f} mm")
m3.metric(t["dry"], ind["longest_dry_spell_next_14_days"])

rain = pd.DataFrame({"date": past.dates + future.dates,
                     t["observed"]: past.rain + [None] * len(future.rain),
                     t["forecast"]: [None] * len(past.rain) + future.rain}).set_index("date")
st.subheader(t["chart"])
st.bar_chart(rain, color=["#2f7d4f", "#7fb3d5"])

st.subheader(t["crops"])
good = [r for r in advice.ranking if r["score"] > 0]
if not good:
    st.write(t["none"])
for r in good[:6]:
    st.markdown(f"**{r['crop']}** — {r['score']}/100 · {r['cycle_days']} days")
    st.progress(r["score"] / 100)

avoid = [r["crop"] for r in advice.ranking if r["score"] < 20]
if avoid:
    st.markdown(f"**{t['avoid']}** " + ", ".join(avoid))

with st.expander(t["all"]):
    st.table(pd.DataFrame({"value": [str(v) for v in ind.values()]},
                          index=[t["indicators"].get(k, k.replace("_", " ")) for k in ind]))

st.caption(t["weather"])
