import streamlit as st
from googleapiclient.discovery import build
from collections import Counter
import re

from conceptos import CONCEPTOS
from nichos import NICHOS

API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

PALABRAS_PROHIBIDAS = [
    "official video","video oficial","official music video",
    "lyrics","lyric","letra","remix","audio oficial",
    "audio","trailer","tráiler","vevo"
]

CANALES_PROHIBIDOS = ["vevo","records","music"]

st.title("🧠 Radar de Tendencias Virales")

nicho = st.selectbox(
    "Selecciona un nicho",
    list(NICHOS.keys())
)

tema_libre = st.text_input(
    "O escribe cualquier tema",
    placeholder="Ejemplo: magnesio, narcisista, menopausia..."
)

if st.button("🚀 Analizar"):

    try:

        consultas = [tema_libre] if tema_libre.strip() else NICHOS[nicho]

        resultados = []

        for consulta in consultas:

            search_response = youtube.search().list(
                q=consulta,
                part="snippet",
                maxResults=15,
                type="video"
            ).execute()

            video_ids = [
                item["id"]["videoId"]
                for item in search_response["items"]
            ]

            if not video_ids:
                continue

            videos_response = youtube.videos().list(
                part="statistics,snippet",
                id=",".join(video_ids)
            ).execute()

            for video in videos_response["items"]:

                titulo_lower = video["snippet"]["title"].lower()
                canal_lower = video["snippet"]["channelTitle"].lower()

                if any(x in titulo_lower for x in PALABRAS_PROHIBIDAS):
                    continue

                if any(x in canal_lower for x in CANALES_PROHIBIDOS):
                    continue

                resultados.append({
                    "titulo": video["snippet"]["title"],
                    "canal": video["snippet"]["channelTitle"],
                    "vistas": int(video["statistics"].get("viewCount", 0)),
                    "publicado": video["snippet"]["publishedAt"][:10],
                    "link": "https://www.youtube.com/watch?v=" + video["id"]
                })

        resultados.sort(key=lambda x: x["vistas"], reverse=True)

        radar = Counter()
        vistas_radar = {}

        for r in resultados:

            titulo = re.sub(r"[^\w\s]", "", r["titulo"].lower())

            for concepto, palabras in CONCEPTOS.items():

                for palabra in palabras:

                    if palabra.lower() in titulo:

                        radar[concepto] += 1
                        vistas_radar.setdefault(concepto, 0)
                        vistas_radar[concepto] += r["vistas"]

        todos_los_titulos = " ".join([r["titulo"] for r in resultados]).lower()
        todos_los_titulos = re.sub(r"[^\w\s]", "", todos_los_titulos)

        palabras = todos_los_titulos.split()

        stopwords = {
            "de","la","el","en","y","a","que","los","las","un","una",
            "por","para","con","del","al","como","más","mas","esto",
            "esta","este","estas","estos","porque","sobre","desde",
            "hasta","entre","cuando","donde","cómo","qué","video",
            "viral","shorts"
        }

        palabras_filtradas = [
            p for p in palabras
            if p not in stopwords and len(p) > 3
        ]

        conteo_palabras = Counter(palabras_filtradas)

        st.subheader("🔥 Palabras Más Repetidas")

        for palabra, cantidad in conteo_palabras.most_common(15):
            st.write(f"🔥 {palabra} ({cantidad})")

        bigramas = []

        for i in range(len(palabras_filtradas) - 1):
            bigramas.append(
                palabras_filtradas[i] + " " + palabras_filtradas[i + 1]
            )

        conteo_bigramas = Counter(bigramas)

        st.subheader("🧠 Temas Emergentes")

        for frase, cantidad in conteo_bigramas.most_common(10):
            st.write(f"🚀 {frase} ({cantidad})")

        st.subheader("💡 Ideas Detectadas Automáticamente")

        for frase, cantidad in conteo_bigramas.most_common(5):
            st.write(f"• Lo que nadie te cuenta sobre {frase}")
            st.write(f"• El error más común relacionado con {frase}")

        st.subheader("🔥 Oportunidades Detectadas")

        for concepto, cantidad in radar.most_common():
            vistas = vistas_radar.get(concepto, 0)
            puntaje = cantidad * 10 + min(vistas // 100000, 100)

            st.markdown(
                f"""
### {concepto}

📊 Apariciones: {cantidad}

👀 Vistas acumuladas: {vistas:,}

🚀 Puntaje Viral: {puntaje}
"""
            )

        st.subheader("🏆 Videos Más Relevantes")

        for r in resultados[:30]:
            st.markdown(f"### {r['titulo']}")
            st.write(f"Canal: {r['canal']}")
            st.write(f"👀 Vistas: {r['vistas']:,}")
            st.write(f"📅 Publicado: {r['publicado']}")
            st.write(r["link"])
            st.write("---")

    except Exception as e:
        st.error(str(e))
