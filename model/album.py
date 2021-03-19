from typing import Optional, List
from pydantic import BaseModel, Field


class createAlbumModel(BaseModel):
    id: str = Field(
        min_length=4, max_length=4
    )  # ในการที่เราจะ insert เราควจจะล็อคตั้งแต่ตอนนี้ ฟิลด์คือห้ามน้อยกว่า 4 และห้ามมากกว่า 4
    name_of_album: str
    details_of_album: List[str]  # รายละเอียดอัลบั้ม
    size: str
    weight: str
    track_lists: List[str]  # ลิสต์เพลงในอัลบั้ม
    price: float


# ถ้าไม่เป็น Optional มันไม่ได้บังคับให้ตัว body ต้องใส่ทุกอันเพราะไม่ได้ต้องการจะ update และใช้ฟิลด์ทุกอัน


class updateAlbumModel(BaseModel):
    name_of_album: Optional[str]
    details_of_album: Optional[List[str]]
    size: Optional[str]
    weight: Optional[str]
    track_lists: Optional[List[str]]
    price: Optional[float]
