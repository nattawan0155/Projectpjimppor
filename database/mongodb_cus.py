import pymongo

from model.customer import createCustomerModel, updateCustomerModel


class MongoDB:
    def __init__(
        self, host, port, user, password, auth_db, db, collection
    ):  # เป็นการบอกว่ารับอะไรเข้ามาบ้าง ก็คือรับในวงเล็บเข้ามา
        # self ในไพธอนก็เหมือนกับ this ในจาวา คือการเรียกใช้
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.auth_db = auth_db
        self.db = db
        self.collection = collection
        self.connection = None

    def _connect(self):
        client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
            authSource=self.auth_db,
            authMechanism="SCRAM-SHA-1",
        )
        db = client[self.db]
        self.connection = db[self.collection]

    def find(self, sort_by, order):
        mongo_results = self.connection.find({})
        if sort_by is not None and order is not None:
            mongo_results.sort(sort_by, self._get_sort_by(order))

        return list(mongo_results)

    def _get_sort_by(self, sort: str) -> int:
        return pymongo.DESCENDING if sort == "desc" else pymongo.ASCENDING

    def find_one(self, id):
        return self.connection.find_one({"_id": id})

    def create(self, customer: createCustomerModel):
        customer_dict = customer.dict(
            exclude_unset=True
        )  # .dict คือการแปลงค่า customer ให้เป็น dict

        insert_dict = {
            **customer_dict,
            "_id": customer_dict["id"],
        }  # แบบสั้นๆ แล้วได้ address ใหม่
        # ถ้าแบบยาวๆแล้วได้ address เดิม โค้ดคือ
        # customer_dict["_id"] = customer_dict["id"]
        # insert_dict = customer_dict

        inserted_result = self.connection.insert_one(insert_dict)
        customer_id = str(inserted_result.inserted_id)

        return customer_id

    def update(self, customer_id, update_customer: updateCustomerModel):
        updated_result = self.connection.update_one(
            {"id": customer_id}, {"$set": update_customer.dict(exclude_unset=True)}
        )
        return [customer_id, updated_result.modified_count]

    def delete(self, customer_id):
        deleted_result = self.connection.delete_one({"id": customer_id})
        return [customer_id, deleted_result.deleted_count]