from pathlib import Path

from mutagen.mp3 import MP3
from sqlalchemy.orm import Session

from app.models import Album, Track
from app.settings import MUSIC_DIR


def scan_music(db: Session):

    MUSIC_DIR.mkdir(parents=True, exist_ok=True)

    for album_folder in MUSIC_DIR.iterdir():

        if not album_folder.is_dir():
            continue

        album = db.query(Album).filter(
            Album.folder == str(album_folder)
        ).first()

        if not album:
            album = Album(
                title=album_folder.name,
                folder=str(album_folder),
                cover=find_cover(album_folder)
            )

            db.add(album)
            db.flush()

        for file in sorted(album_folder.iterdir()):

            if file.suffix.lower() == ".mp3":

                existing_track = db.query(Track).filter(
                    Track.filename == str(file)
                ).first()

                if not existing_track:

                    try:
                        audio = MP3(file)

                        track = Track(
                            title=file.stem,
                            filename=str(file),
                            duration=int(audio.info.length),
                            album_id=album.id
                        )

                        db.add(track)

                    except Exception as e:
                        print(f"Skipping {file}: {e}")

    db.commit()


def find_cover(folder):

    for file in folder.iterdir():

        if file.suffix.lower() in [
            ".jpg", ".jpeg", ".png", ".webp"
        ]:
            return str(file)

    return None
