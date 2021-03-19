import uvicorn
from fastapi import FastAPI, Path, Query, HTTPException
from starlette.responses import JSONResponse
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from database.mongodb_cus import MongoDB
from config.development_cus import config
from model.customer import (
    createCustomerModel,
    updateCustomerModel,
)  # อิมพอร์ตมาจาก Model->customer

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
    return JSONResponse(content={"message": "อันนี้ก็เศร้าพอกัน..."}, status_code=200)


@app.get("/customers/")  # หา customer ทั้งหมด
def get_customers(
    sort_by: Optional[
        str
    ] = None,  # ความหมายของ optional คือ ถ้ามันไม่เป็นสตริงมนควรจะเป็น none ถ้ามันไม่มีค่าก็ให้รีเทิร์นเป็น none หรือเป็นค่า defult
    order: Optional[str] = Query(
        None, min_length=6, max_length=6  # Query คือการกำหนดค่า
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


@app.get("/customers/{customer_id}")  # หา customer ตาม ID
def get_customers_by_id(customer_id: str = Path(None, min_length=6, max_length=6)):
    try:
        result = mongo_db.find_one(customer_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if result is None:
        raise HTTPException(status_code=404, detail="Customer Id not found !!")

    return JSONResponse(
        content={"status": "OK", "data": result},
        status_code=200,
    )


@app.post("/customers")  # การโพสต์ก็คือการ create หรือการสร้าง
def create_customers(
    customer: createCustomerModel,
):  # อยากสร้าง create_customers (createCustomerModel) มาจากการอิมพอร์ตข้างบน (from)
    try:
        customer_id = mongo_db.create(customer)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "customer_id": customer_id,
            },
        },
        status_code=201,
    )


@app.patch(
    "/customers/{customer_id}"
)  # patch customer คืออยากเปลี่ยนหรือ update customer_id แค่บางคนเท่านั้น
def update_customers(
    update_customer: updateCustomerModel,
    customer_id: str = Path(None, min_length=6, max_length=6),
):
    print("customer", update_customer)
    try:
        updated_customer_id, modified_count = mongo_db.update(
            customer_id, update_customer
        )  # จำนวนการแก้ไขข้อมูล
    except:
        raise HTTPException(
            status_code=500, detail="Something went wrong !!"
        )  # server error

    if (
        modified_count == 0
    ):  # ค่าที่ไม่ได้ถูก update อาจจะเพราะ customer_id ผิด หรือว่าฟิลด์ที่เราเอาเข้าไปมันผิด
        raise HTTPException(
            status_code=404,
            detail=f"Customer Id: {updated_customer_id} is not update want fields",  # client ผิดพลาดเอง
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "customer_id": updated_customer_id,
                "modified_count": modified_count,
            },
        },
        status_code=200,
    )


@app.delete("/customers/{customer_id}")
def delete_customer_by_id(customer_id: str = Path(None, min_length=6, max_length=6)):
    try:
        deleted_customer_id, deleted_count = mongo_db.delete(customer_id)
    except:
        raise HTTPException(status_code=500, detail="Something went wrong !!")

    if deleted_count == 0:
        raise HTTPException(
            status_code=404, detail=f"Customer Id: {deleted_customer_id} is not Delete"
        )

    return JSONResponse(
        content={
            "status": "ok",
            "data": {
                "customer_id": deleted_customer_id,
                "deleted_count": deleted_count,
            },
        },
        status_code=200,
    )


if __name__ == "__main__":
    uvicorn.run("main_cus:app", host="127.0.0.1", port=3001, reload=True)
