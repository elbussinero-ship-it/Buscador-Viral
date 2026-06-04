import streamlit as st
from googleapiclient.discovery import build

API_KEY = st.secrets["YOUTUBE_API_KEY"]

youtube = build(
    "youtube",
    "v3",
    developerKey=API_KEY
)

st.title("🔥 Buscador Viral YouTube")

tema = st.text_input(
    "Tema",
    placeholder="Ejemplo: ajo"
)

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
            video_ids.append(item["id"]["videoId"])

        videos_response = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids)
        ).execute()

        resultados = []

        for video in videos_response["items"]:

            titulo = video["snippet"]["title"]
            canal = video["snippet"]["channelTitle"]

            vistas = int(
                video["statistics"].get(
                    "viewCount",
                    0
                )
            )

            publicado = video["snippet"]["publishedAt"][:10]

            link = (
                "https://www.youtube.com/watch?v="
                + video["id"]
            )

            resultados.append({
                "titulo": titulo,
                "canal": canal,
                "vistas": vistas,
                "publicado": publicado,
                "link": link
            })

        resultados.sort(
            key=lambda x: x["vistas"],
            reverse=True
        )

        st.subheader("🏆 Videos más vistos")

        for r in resultados:

            st.markdown(f"### {r['titulo']}")
            st.write(f"Canal: {r['canal']}")
            st.write(f"👀 Vistas: {r['vistas']:,}")
            st.write(f"📅 Publicado: {r['publicado']}")
            st.write(r["link"])
            st.write("---")

    except Exception as e:

        st.error(str(e))
