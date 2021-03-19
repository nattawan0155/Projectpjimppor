import pymongo

from model.album import createAlbumModel, updateAlbumModel


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

    def create(self, album: createAlbumModel):
        album_dict = album.dict(
            exclude_unset=True
        )  # .dict คือการแปลงค่า album ให้เป็น dict

        insert_dict = {
            **album_dict,
            "_id": album_dict["id"],
        }  # แบบสั้นๆ แล้วได้ address ใหม่
        # ถ้าแบบยาวๆแล้วได้ address เดิม โค้ดคือ
        # album_dict["_id"] = album_dict["id"]
        # insert_dict = album_dict

        inserted_result = self.connection.insert_one(insert_dict)
        album_id = str(inserted_result.inserted_id)

        return album_id

    def update(self, album_id, update_album: updateAlbumModel):
        updated_result = self.connection.update_one(
            {"id": album_id}, {"$set": update_album.dict(exclude_unset=True)}
        )
        return [album_id, updated_result.modified_count]

    def delete(self, album_id):
        deleted_result = self.connection.delete_one({"id": album_id})
        return [album_id, deleted_result.deleted_count]