from typing import Optional, List
from pydantic import BaseModel, Field


class createCustomerModel(BaseModel):
    id: str = Field(
        min_length=6, max_length=6
    )  # ในการที่เราจะ insert เราควจจะล็อคตั้งแต่ตอนนี้ ฟิลด์คือห้ามน้อยกว่า 6 และห้ามมากกว่า 6
    first_name: str
    last_name: str
    email: str
    desired_product_details: str  # รายละเอียดสินค้าที่ต้องการ
    shipment_of_goods: str  # ตัวเลือกการจัดส่งสินค้า
    address: str
    telephone_number: str = Field(min_length=10, max_length=10)
    payment_amount: float  # จำนวนเงินที่ชำระ


# ถ้าไม่เป็น Optional มันไม่ได้บังคับให้ตัว body ต้องใส่ทุกอันเพราะไม่ได้ต้องการจะ update และใช้ฟิลด์ทุกอัน


class updateCustomerModel(BaseModel):
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    desired_product_details: Optional[str]
    shipment_of_goods: Optional[str]
    address: Optional[str]
    payment_amount: Optional[float]
