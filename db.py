import asyncio
import sqlite3
import random
from aiogram import Bot, types

class DataBase:
   def __init__(self, db):
      self.conn = sqlite3.connect(db)
      self.cur = self.conn.cursor()
      
      self.cur.execute("""CREATE TABLE IF NOT EXISTS user_data(
      first_name TEXT,
      last_name TEXT,
      user_name TEXT,
      user_id INTEGER PRIMARY KEY,
      room TEXT DEFAULT 'None'
      )""")
      
      self.cur.execute("""CREATE TABLE IF NOT EXISTS game_room(
      room_id INTEGER PRIMARY KEY,
      users TEXT,
      room_room TEXT,
      mafia TEXT,
      doctor TEXT,
      komisar TEXT,
      villager TEXT,
      dead TEXT DEFAULT 'None',
      time TEXT DEFAULT 'None',
      history_role_for_komisar TEXT DEFAULT 'None',
      is_check TEXT DEFAUT 'None',
      history_night TEXT DEFAULT 'None',
      history_all TEXT DEFAULT 'None',
      vote TEXT DEFAULT 'None',
      who_voted TEXT DEFAULT 'None'
      )""")
      
      # index 14 всего 
      
      #self.cur.execute("DELETE FROM game_room")
      
      self.conn.commit()
   async def check_db(self, message):
      self.first_name = message.from_user.first_name
      self.last_name = message.from_user.last_name
      self.user_name = message.from_user.username
      self.id = message.from_user.id
      
      self.data = self.cur.execute("SELECT * FROM user_data WHERE user_id = ?", (self.id,)).fetchone()
      
      if not self.data:
         self.cur.execute("INSERT OR IGNORE INTO user_data (first_name, last_name, user_name, user_id) VALUES (?, ?, ?, ?)", (self.first_name, self.last_name, self.user_name, self.id))
         self.conn.commit()
      else:
         pass

class gameMafia:
   def __init__(self, db, bot):
      self.conn = sqlite3.connect(db)
      self.cur = self.conn.cursor()
      
      self.bot = bot
      
      self.game_data = self.cur.execute("SELECT * FROM game_room").fetchall()
   async def selection(self, room_id, message):
      self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
      
      markup = types.InlineKeyboardMarkup()
      markup.add(types.InlineKeyboardButton("Перейти в бота", url="https://t.me/constructor_robot_bot"))
      
      await message.answer("Все, кто участвует в этой игре, переходим ко мне в личку, там мы будем проводить игру в дальнейшем.", reply_markup=markup)
      
      for user in self.users[1].split(","):
         while True:
            self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
            
            self.role = random.randint(1, 4)
            
            if str(user) in self.users[3].split(",") or str(user) in self.users[4].split(",") or str(user) in self.users[5].split(",") or str(user) in self.users[6].split(","):
               break
            
            if self.role == 1:
               if self.users[3] == "None":
                  self.cur.execute("UPDATE game_room SET mafia = ? WHERE room_id = ?", (user, room_id))
                  self.conn.commit()
                  
                  await self.bot.send_message(user, "Вы <b>мафия</b>", parse_mode="html")
                  break
            if self.role == 2:
               if self.users[4] == "None":
                  self.cur.execute("UPDATE game_room SET doctor = ? WHERE room_id = ?", (user, room_id))
                  self.conn.commit()
                  
                  await self.bot.send_message(user, "Вы <b>доктор</b>", parse_mode="html")
                  break
            if self.role == 3:
               if self.users[5] == "None":
                  self.cur.execute("UPDATE game_room SET komisar = ? WHERE room_id = ?", (user, room_id))
                  self.conn.commit()
                  
                  await self.bot.send_message(user, "Вы <b>шэриф</b>", parse_mode="html")
                  break
            if self.role == 4:
               if self.users[6] == "None":
                  self.cur.execute("UPDATE game_room SET villager = ? WHERE room_id = ?", (user, room_id))
                  self.conn.commit()
                  
                  await self.bot.send_message(user, "Вы <b>житель</b>", parse_mode="html")
                  
                  break
               else:
                  self.cur.execute("UPDATE game_room SET villager = ? WHERE room_id = ?", (f"{self.users[6]},{user}", room_id))
                  self.conn.commit()
                  
                  await self.bot.send_message(user, "Вы <b>житель</b>", parse_mode="html")
                  
                  break
      print("selection done")
      asyncio.create_task(self.night(room_id, message))
   async def night(self, room_id, message):
      self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
      
      days = int(self.users[8][:-4]) + 1
      
      self.cur.execute("UPDATE game_room SET time = ? WHERE room_id = ?", (f"{days} день", room_id))
      
      self.cur.execute("UPDATE game_room SET who_voted = ? WHERE room_id = ?", ("None", room_id))
      
      self.output = ""
      for voted_user in self.users[13].split(","):
         self.null_voted = int(voted_user.split("-")[1]) - int(voted_user.split("-")[1])
         self.result = f"{voted_user.split('-')[0]}-{self.null_voted}"
         
         if self.output:
            self.output += f",{self.result}"
         else:
            self.output += result
      
      self.cur.execute("UPDATE game_room SET voted = ? WHERE room_id = ?")
      
      self.conn.commit()
      
      self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
      
      for user in self.users[1].split(","):
         await self.bot.send_message(user, f"Наступает {self.users[8]} ночи")
      
      for user in self.users[1].split(","):
         await self.bot.send_message(user, "просыпается мафия")
      
      self.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("waitActionsMafia", room_id))
      self.conn.commit()
      
      for user in self.users[3].split(","):
         markup = types.InlineKeyboardMarkup()
         for peoples in self.users[1].split(","):
            if peoples not in self.users[7].split(","):
               people = self.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (peoples,)).fetchone()
               
               markup.add(types.InlineKeyboardButton(f"{people[0]}", callback_data=f"kill {peoples} id {room_id}"))
         
         print(user)
         await self.bot.send_message(user, "Выберите жертву", reply_markup=markup)
      
      while True:
         await asyncio.sleep(1)
         try:
            self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
         except Exception as e:
            return print("closed")
         if str(self.users[5]) not in self.users[7]:
            if self.users[2] == "waitActionsKomisar":
               break
         else:
            break
      
      for user in self.users[1].split(","):
         await self.bot.send_message(user, "мафия уже выбрал жертву")
      
      print("test")
      
      for user in self.users[1].split(","):
         if str(self.users[5]) not in self.users[7].split(","):
            await self.bot.send_message(user, "просыпается шэриф")
      
      if str(self.users[5]) not in self.users[7].split(","):
         for user in self.users[5].split(","):
            await self.bot.send_message(user, f"Ваша история проверок:\n{self.users[9] if self.users[9] != 'None' else 'Пусто'}")
            
            markup = types.InlineKeyboardMarkup()
            for peoples in self.users[1].split(","):
               if str(peoples) not in self.users[5].split(","):
                  if str(peoples) not in self.users[10].split(","):
                     people = self.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (peoples,)).fetchone()
                     
                     markup.add(types.InlineKeyboardButton(f"{people[0]}", callback_data=f"check {peoples} id {room_id}"))
            await self.bot.send_message(user, "Выберите кого проверить", reply_markup=markup)
      
      while True:
         await asyncio.sleep(1)
         
         try:
            self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
         except Exception as e:
            return print("closed")
         if str(self.users[4]) not in self.users[7]:
            if self.users[2] == "waitActionsDoctor":
               break
         else:
            break
   
      for user in self.users[1].split(","):
         if str(self.users[5]) not in self.users[7].split(","):
            await self.bot.send_message(user, "шэриф уже выбрал кого проверить")
   
      for user in self.users[1].split(","):
         if str(self.users[4]) not in self.users[7].split(","):
            await self.bot.send_message(user, "просыпается доктор")
      
      for user in self.users[4].split(","):
         if str(user) not in self.users[7].split(","):
            
            markup = types.InlineKeyboardMarkup()
            for peoples in self.users[1].split(","):
               if str(peoples) not in self.users[4].split(","):
                  people = self.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (peoples,)).fetchone()
                     
                  markup.add(types.InlineKeyboardButton(f"{people[0]}", callback_data=f"cure {peoples} id {room_id}"))
            await self.bot.send_message(user, "Выберите кого вылечить", reply_markup=markup)
      
      while True:
         await asyncio.sleep(1)
         
         try:
            self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
         except Exception as e:
            return print("closed")
         if str(self.users[4]) not in self.users[7]:
            if self.users[2] == "EndNight":
               break
         else:
            break
      
      asyncio.create_task(self.day(room_id, message))
   async def day(self, room_id, message):
      self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
      
      for user in self.users[1].split(","):
         await self.bot.send_message(user, f"Наступает {self.users[8]} дня")
      
      self.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("waitVote", room_id))
      self.conn.commit()
      
      for user in self.users[1].split(","):
         markup = types.InlineKeyboardMarkup()
         
         if str(user) not in self.users[7].split(","):
            for people in self.users[1].split(","):
               self.peoples = self.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (people,)).fetchone()
               
               markup.add(f"{self.peoples[0]}", callback_data=f"vote {people} id {room_id}")
            
            await bot.send_message(user, "Проголосуйте за того, кого считаете подозрительным", reply_markup=markup)
      
      while True:
         await asyncio.sleep(1)
         
         try:
            self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
         except Exception as e:
            return print("closed")
         if len(self.users[14].split(",")) == len(self.users[1].split(",")):
            break
      
      self.max_vote = max([vote.split("-")[1] for vote in self.users[13].split(",")])
      
      self.quantity_user = 0
      self.leaving = ""
      
      for user in self.users[13].split(","):
         if user.split("-")[1] == self.max_vote:
            self.quantity_user += 1
            self.leaving = user.split("-")[0]
      
      if not self.quantity > 1:
         if self.users[7] == "None":
            self.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (f"{self.leaving}", room_id))
         else:
            self.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (f"{self.users[7]},{self.leaving}", room_id))
         self.conn.commit()
         
         self.who_leaving = self.cur.execute('SELECT first_name, user_name FROM user_data WHERE user_id = ?', (int(self.leaving),)).fetchone()
         
         self.who_leav_role = f"{'мафией' if self.leaving in self.users[3] else ''}{'доктором' if self.leaving in self.users[4] else ''}{'шэрифом' if self.leaving in self.users[5] else ''}{'жителем' if self.leaving in self.users[6] else ''}"
         
         for user in self.users[1].split(","):
            await bot.send_message(user, f"Игрок <a href='https://t.me/{self.who_leaving[1]}'>{self.who_leaving[0]}</a> выбыл, он был {self.who_leav_role}")
      else:
         for user in self.users[1].split(","):
            await bot.send_message(user, "Жители разделились во мнениях и решили не исключать никого из села.")
      
      # Дальше будет ключевая часть, где будет проверка, есть ли мафия в живых, или нет, или же, жив ли комисар и доктор.Если же все живи, то запустисть функцию ночи
      self.users = self.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (room_id,)).fetchone()
      
      if self.users[3] in self.users[7].split(","):
         self.mafia = ""
         self.doctor = ""
         self.komisar = ""
         self.villager = ""
         
         for user in self.users[3].split(","):
            try:
               if self.mafia:
                  self.mafia += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               else:
                  self.mafia += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            except:
               pass
         
         for user in self.users[4].split(","):
            try:
               if self.doctor:
                  self.doctor += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               else:
                  self.doctor += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            except:
               pass
         
         for user in self.users[5].split(","):
            try:
               if self.komisar:
                  self.komisar += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               else:
                  self.komisar += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            except:
               pass
         
         for user in self.users[6].split(","):
            try:
               if self.villager:
                  self.villager += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               else:
                  self.villager += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            except:
               pass
         
         for user in self.users[1].split(","):
            await bot.send_message(user, f"👨‍🌾<b>МИРНЫЕ ПОБЕДИЛИ</b>\n\n🧛‍♂️Мафия-{self.mafia}\n👨‍⚕️Доктор-{self.doctor}\n👮‍♂️Шэриф-{self.komisar}\n👨‍🌾Жители-{villager}")
         
         self.cur.execute(f"DELETE FROM game_room WHERE room_id LIKE {room_id}")
         return self.conn.commit()
      else:
         if self.users[4] in self.users[7].split(",") and self.users[5] in self.users[7]:
            self.mafia = ""
            self.doctor = ""
            self.komisar = ""
            self.villager = ""
            
            for user in self.users[3].split(","):
               try:
                  if self.mafia:
                     self.mafia += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
                  else:
                     self.mafia += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               except:
                  pass
            
            for user in self.users[4].split(","):
               try:
                  if self.doctor:
                     self.doctor += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
                  else:
                     self.doctor += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               except:
                  pass
            
            for user in self.users[5].split(","):
               try:
                  if self.komisar:
                     self.komisar += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
                  else:
                     self.komisar += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               except:
                  pass
            
            for user in self.users[6].split(","):
               try:
                  if self.villager:
                     self.villager += f",{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
                  else:
                     self.villager += f"{self.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
               except:
                  pass
            
            for user in self.users[1].split(","):
               await bot.send_message(user, f"👨‍🌾<b>МИРНЫЕ ПОБЕДИЛИ</b>\n\n🧛‍♂️Мафия-{self.mafia}\n👨‍⚕️Доктор-{self.doctor}\n👮‍♂️Шэриф-{self.komisar}\n👨‍🌾Жители-{villager}")
            
            self.cur.execute(f"DELETE FROM game_room WHERE room_id LIKE {room_id}")
            return self.conn.commit()
      asyncio.create_task(self.night(room_id, message))
