import streamlit as st
from googleapiclient.discovery import build
from collections import Counter
import re

# ==================================
# CONFIGURACION
# ==================================

 API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

# ==================================
# INTERFAZ
# ==================================

st.title("🔥 Buscador Viral YouTube")

tema = st.text_input(
    "Tema",
    placeholder="Ejemplo: banderas rojas"
)

# ==================================
# BUSQUEDA
# ==================================

if st.button("Buscar contenido viral"):

    try:

        search_response = youtube.search().list(
            q=tema,
            part="snippet",
            maxResults=25,
            type="video"
        ).execute()

        video_ids = []

        for item in search_response["items"]:
            video_ids.append(
                item["id"]["videoId"]
            )

        videos_response = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids)
        ).execute()

        resultados = []

        for video in videos_response["items"]:

            titulo = video["snippet"]["title"]

            canal = video["snippet"][
                "channelTitle"
            ]

            vistas = int(
                video["statistics"].get(
                    "viewCount",
                    0
                )
            )

            publicado = (
                video["snippet"][
                    "publishedAt"
                ][:10]
            )

            link = (
                "https://www.youtube.com/watch?v="
                + video["id"]
            )

            resultados.append(
                {
                    "titulo": titulo,
                    "canal": canal,
                    "vistas": vistas,
                    "publicado": publicado,
                    "link": link
                }
            )

        resultados.sort(
            key=lambda x: x["vistas"],
            reverse=True
        )

        # ==================================
        # RADAR DE OPORTUNIDADES V2 + V3
        # ==================================

        stopwords = {
            "de", "la", "el", "en",
            "y", "a", "que",
            "los", "las", "un",
            "una", "por", "para",
            "con", "del", "al",
            "es", "como", "cómo",
            "qué", "porque",
            "este", "esta",
            "estos", "estas",
            "desde", "hasta",
            "sobre", "entre",
            "más", "menos",
            "todo", "todos",
            "todas",
            "video", "videos",
            "oficial",
            "completo",
            "directo",
            "edicion",
            "edición"
        }

        frases = Counter()
        vistas_frases = {}

        for r in resultados:

            titulo = r["titulo"].lower()

            titulo = re.sub(
                r"[^\w\s]",
                "",
                titulo
            )

            palabras = [
                p
                for p in titulo.split()
                if p not in stopwords
                and len(p) > 3
            ]

            for i in range(
                len(palabras) - 1
            ):

                frase = (
                    palabras[i]
                    + " "
                    + palabras[i + 1]
                )

                frases[frase] += 1

                vistas_frases.setdefault(
                    frase,
                    0
                )

                vistas_frases[frase] += (
                    r["vistas"]
                )

        st.subheader(
            "🧠 Radar de oportunidades virales"
        )

        top_frases = (
            frases.most_common(15)
        )

        for frase, apariciones in top_frases:

            vistas = vistas_frases.get(
                frase,
                0
            )

            puntaje = (
                apariciones * 10
                + min(
                    vistas // 100000,
                    100
                )
            )

            st.markdown(
                f"""
### 🔥 {frase}

📊 Apariciones: {apariciones}

👀 Vistas acumuladas: {vistas:,}

🚀 Puntaje viral: {puntaje}
"""
            )

        st.write("---")

        # ==================================
        # VIDEOS
        # ==================================

        st.subheader(
            "🏆 Videos más vistos"
        )

        for r in resultados:

            st.markdown(
                f"### {r['titulo']}"
            )

            st.write(
                f"Canal: {r['canal']}"
            )

            st.write(
                f"👀 Vistas: {r['vistas']:,}"
            )

            st.write(
                f"📅 Publicado: {r['publicado']}"
            )

            st.write(
                r["link"]
            )

            st.write("---")

    except Exception as e:

        st.error(str(e))
