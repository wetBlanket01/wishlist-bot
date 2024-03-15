import sqlite3


class DataBase:
    def __init__(self, db_file):
        self.connect = sqlite3.connect(db_file)
        self.cursor = self.connect.cursor()

    async def add_user(self, user_id, user_name):
        with self.connect:
            return self.cursor.execute("""INSERT INTO users (user_id, user_name) VALUES (?, ?)""",
                                       (user_id, user_name if user_name is not None else '?guest',))

    async def add_gift(self, gift_name, description, category, image, link, for_who):
        with self.connect:
            return self.cursor.execute(
                """INSERT INTO stock (gift_name, description, category, image, link, for_who) VALUES (?, ?, ?, ?, ?, ?)""",
                (gift_name, description, category, image, link, for_who))

    async def get_categories(self, for_who):
        with self.connect:
            return self.cursor.execute("""SELECT category FROM stock WHERE for_who=(?)""", (for_who,)).fetchall()

    async def get_gifts(self, category):
        with self.connect:
            return self.cursor.execute("""SELECT gift_name FROM stock WHERE category=(?)""",
                                       (category,)).fetchall()

    async def get_gift(self, gift_name):
        with self.connect:
            return self.cursor.execute("""SELECT description, image FROM stock WHERE gift_name=(?)""",
                                       (gift_name,)).fetchall()

    # async def get_users_without_gift(self):
    #     with self.connect:
    #         return self.cursor.execute("""SELECT user_id FROM users WHERE gift_name IS NULL""").fetchall()

    async def delete_gift(self, gift_name):
        with self.connect:
            return self.cursor.execute(
                """DELETE FROM stock WHERE gift_name=(?)""",
                (gift_name,))

    async def add_gift_to_user(self, for_who, gift_name, user_id):
        with self.connect:
            return self.cursor.execute(
                f"""UPDATE users SET {for_who}=(?) WHERE user_id=(?)""",
                (gift_name, user_id,))

    async def get_link(self, gift_name):
        with self.connect:
            return self.cursor.execute("""SELECT link FROM stock WHERE gift_name=(?)""",
                                       (gift_name,)).fetchone()

    async def get_users_table(self):
        with self.connect:
            return self.cursor.execute("""SELECT * FROM users""").fetchall()

    async def is_gift_chosen_by_user(self, user_id, for_who):
        with self.connect:
            return self.cursor.execute(f"""SELECT {for_who} FROM users WHERE user_id=(?)""", (user_id,)).fetchone()

    async def remove_gift(self, for_who, user_id):
        with self.connect:
            return self.cursor.execute(f"""UPDATE users SET {for_who}=(?) WHERE user_id=(?)""",
                                       (None, user_id,)).fetchone()
