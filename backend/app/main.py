from pathlib import Path

from fastapi import FastAPI, Depends, HTTPException
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.database import Base, engine, SessionLocal
from app.models import Album, Track
from app.scanner import scan_music

app = FastAPI(title="Music App Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)


@app.on_event("startup")
def startup():
    db = SessionLocal()
    try:
        scan_music(db)
    finally:
        db.close()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
def health():
    return {"status": "healthy"}


@app.get("/albums")
def albums_only(db: Session = Depends(get_db)):
    albums = db.query(Album).all()

    return [
        {"id": album.id, "name": album.title}
        for album in albums
    ]


@app.get("/albums-with-tracks")
def albums_with_tracks(db: Session = Depends(get_db)):

    albums = db.query(Album).all()

    response = []

    for album in albums:

        tracks = [
            {
                "track_id": track.id,
                "name": track.title,
                "duration": track.duration
            }
            for track in album.tracks
        ]

        cover_url = (
            f"/artwork/{tracks[0]['track_id']}"
            if tracks and album.cover
            else "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17"
        )

        response.append({
            "id": album.id,
            "name": album.title,
            "cover": cover_url,
            "tracks": tracks
        })

    return response


@app.get("/stream/{track_id}")
def stream(track_id: int, db: Session = Depends(get_db)):

    track = db.query(Track).filter(
        Track.id == track_id
    ).first()

    if not track:
        raise HTTPException(
            status_code=404,
            detail="Track not found"
        )

    file_path = Path(track.filename)

    if not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Audio file not found"
        )

    return FileResponse(
        path=file_path,
        media_type="audio/mpeg",
        filename=file_path.name
    )


@app.get("/artwork/{track_id}")
def artwork(track_id: int, db: Session = Depends(get_db)):

    track = db.query(Track).filter(
        Track.id == track_id
    ).first()

    if not track:
        raise HTTPException(
            status_code=404,
            detail="Track not found"
        )

    album = db.query(Album).filter(
        Album.id == track.album_id
    ).first()

    if not album or not album.cover:
        return RedirectResponse(
            "https://images.unsplash.com/photo-1614613535308-eb5fbd3d2c17"
        )

    cover_path = Path(album.cover)

    if not cover_path.is_file():
        raise HTTPException(
            status_code=404,
            detail="Artwork not found"
        )

    media_types = {
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".png": "image/png",
        ".webp": "image/webp"
    }

    return FileResponse(
        cover_path,
        media_type=media_types.get(
            cover_path.suffix.lower(),
            "application/octet-stream"
        )
    )
