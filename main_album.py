import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb_al import MongoDB
from config.development_al import config
from model.album import (
    createAlbumModel,
    updateAlbumModel,
)  # อิมพอร์ตมาจาก Model->album

mongo_config = config["mongo_config"]
mongo_db = MongoDB(
    mongo_config["host"],
    mongo_config["port"],
    mongo_config["user"],
    mongo_config["password"],
    mongo_config["auth_db"],
    mongo_config["db"],
    mongo_config["collection"],
)
mongo_db._connect()  # เอามาจาก def _connect ใน mongodb.py

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#               C     R       U          D
# http method [post, get, [put, patch], delete] patch กับ put คือการ update เหมือนกัน แต่ put จะ update ทั้ง document ทั้งหมดเลย แต่ถ้าเป็น patch เราสามารถเปลี่ยนแค่บางตัวได้ เช่น เปลี่ยนแค่อายุ
# ตระกูลตัว P -> post put patch ต้องส่งไปเป็น body แต่ของอันอื่นอาจจะส่งเป็น param หรือเป็น query ก็ได้


@app.get("/")
def index():
    return JSONResponse(
        content={"message": "อยากทำให้ได้แต่ทำไม่ได้... มุแง้งง ;-;"}, status_code=200
    )


@app.get("/albums/")  # หา album ทั้งหมด
def get_albums(
    sort_by: Optional[
        str
    ] = None,  # ความหมายของ optional คือ ถ้ามันไม่เป็นสตริงมนควรจะเป็น none ถ้ามันไม่มีค่าก็ให้รีเทิร์นเป็น none หรือเป็นค่า defult
    order: Optional[str] = Query(
        None, min_length=4, max_length=4  # Query คือการกำหนดค่า
    ),  # เป็นการนับค่า str อย่างน้อยต้องมีสามและมากสุดคือมีสี่ตัวเท่านั้น ถ้ามากกว่าสี่จะเออเร่อทันที
):

    try:
        result = mongo_db.find(sort_by, order)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.get("/albums/{album_id}")  # หา student ตาม ID
def get_albums_by_id(album_id: str = Path(None, min_length=4, max_length=4)):
    try:
        result = mongo_db.find_one(album_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="Album Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/albums")  # การโพสต์ก็คือการ create หรือการสร้าง
def create_albums(
    album: createAlbumModel,
):  # อยากสร้าง create_albums (createAlbumModel) มาจากการอิมพอร์ตข้างบน (from)
    try:
        album_id = mongo_db.create(album)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "album_id": album_id,
            },
        },
        status_code=201,
    )


@app.patch(
    "/albums/{album_id}"
)  # patch album คืออยากเปลี่ยนหรือ update album_id แค่บางบั้มเท่านั้น
def update_albums(
    update_album: updateAlbumModel,
    album_id: str = Path(None, min_length=4, max_length=4),
):
    print("album", update_album)
    try:
        updated_album_id, modified_count = mongo_db.update(
            album_id, update_album
        )  # จำนวนการแก้ไขข้อมูล
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  # server error

    if (
        modified_count == 0
    ):  # ค่าที่ไม่ได้ถูก update อาจจะเพราะ album_id ผิด หรือว่าฟิลด์ที่เราเอาเข้าไปมันผิด
        raise HTTPException(
            status_code=404,
            detail=f"Album Id: {updated_album_id} is not update want fields",  # client ผิดพลาดเอง
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "album_id": updated_album_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/albums/{album_id}")
def delete_album_by_id(album_id: str = Path(None, min_length=4, max_length=4)):
    try:
        deleted_album_id, deleted_count = mongo_db.delete(album_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Album Id: {deleted_album_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "album_id": deleted_album_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main_album:app", host="127.0.0.1", port=3001, reload=True)