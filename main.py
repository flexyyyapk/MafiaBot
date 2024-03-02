from aiogram import Bot, Dispatcher, types, executor
from db import DataBase, gameMafia
import asyncio
import random
from datetime import datetime

bot = Bot("Tokem")
dp = Dispatcher(bot)

db = DataBase("mafia.db")
gm = gameMafia("mafia.db", bot)

@dp.message_handler(commands=["start"])
async def start(message: types.Message):
   await db.check_db(message)
   
   if message.text[7:]:
      
      check_game = db.cur.execute("SELECT users FROM game_room WHERE room_id = ?", (message.text.split("/start ")[1],)).fetchone()[0]
      
      if not str(message.from_user.id) in check_game:
         splited = message.text.split("/start ")[1]
         
         users = db.cur.execute("SELECT users FROM game_room WHERE room_id = ?", (splited,)).fetchone()
         
         db.cur.execute("UPDATE user_data SET room = ? WHERE user_id = ?", (f"game {splited}", message.from_user.id))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET users = ? WHERE room_id = ?", (f"{users[0]},{message.from_user.id}", splited))
         db.conn.commit()
         
         await message.answer("Вы успешно присоеденились")
      else:
         await message.answer("Вы и так играете")
   else:
      await message.answer("Hi")

@dp.message_handler(commands=["start_game"])
async def start_game(message: types.Message):
   await db.check_db(message)
   
   if not str(message.from_user.id) in gm.game_data:
      
      game_id = 0
      
      while True:
         try:
            db.cur.execute("INSERT INTO game_room (room_id, users, room_room, mafia, doctor, komisar, villager, dead, time) VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?)", (game_id, message.from_user.id, "None", "None", "None", "None", "None", "None", "0 день"))
            db.conn.commit()
            break
         except Exception as e:
            game_id += 1
         
      users = db.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (game_id,)).fetchone()
         
      userses = db.cur.execute("SELECT users FROM game_room WHERE room_id = ?", (game_id,)).fetchone()
      
      print(game_id)
      print(users)
      
      db.cur.execute("UPDATE user_data SET room = ? WHERE user_id = ?", (f"game {game_id}", message.from_user.id))
      db.conn.commit()
      
      markup = types.InlineKeyboardMarkup()
      markup.add(types.InlineKeyboardButton("Присоедениться", url=f"https://t.me/constructor_robot_bot?start={game_id}"))
         
      isale = ",".join([db.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (first_name_user,)).fetchone()[0] for first_name_user in userses[0].split(",")])
      
      msg = await message.answer(f"<b>Игра создана!</b>\n\nЗашли: {isale}\n{len(userses[0].split(','))} игрок(ов)", reply_markup=markup)
         
      await bot.pin_chat_message(message.chat.id, msg.message_id)
      
      db.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("waitUsers", game_id))
      db.conn.commit()
      
      while True:
         userses = db.cur.execute("SELECT users FROM game_room WHERE room_id = ?", (game_id,)).fetchone()
         try:
            isale = ",".join([db.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (first_name_user,)).fetchone()[0] for first_name_user in userses[0].split(",")])
            
            await bot.edit_message_text(chat_id=message.chat.id, text=f"<b>Игра создана!</b>\n\nЗашли: {isale}\n{len(userses[0].split(','))} игрок(ов)", message_id=msg.message_id, reply_markup=markup)
         except Exception as e:
            pass
            
         await asyncio.sleep(5)
            
         if len(userses[0].split(',')) > 3:
            
            asyncio.create_task(gm.selection(game_id, message))
            
            break
   else:
      await message.answer("Вы и так уже играете")

@dp.message_handler(content_types=["text"])
async def text(message: types.Message):
   id = message.from_user.id
   
   await db.check_db(message)
   
   if db.cur.execute("SELECT room FROM user_data WHERE user_id = ?", (id,)).fetchone()[0].startswith("game "):
      
      online_game_id = db.cur.execute("SELECT room FROM user_data WHERE user_id = ?", (id,)).fetchone()[0].split()
      
      game = db.cur.execute("SELECT users, dead FROM game_room WHERE room_id = ?", (online_game_id[1],)).fetchone()
      
      print(online_game_id)
      print(game)
      
      if str(id) in game[1].split(",") and online_game_id[2] == "dead":
         for user in game[0].split(","):
            if str(id) not in str(user):
               await bot.send_message(user, f"Кто то из жителей видел как <a href='https://t.me/{message.from_user.username}'>{message.from_user.first_name}</a> кричал:\n{message.text}")
               
               db.cur.execute("UPDATE user_data SET room = ? WHERE user_id = ?", (f"{online_game_id[:2]} deach", id))
               return db.conn.commit()
      
      try:
         if str(id) not in game[1].split(",") and online_game_id[2] != "deach":
            for user in game[0].split(","):
               if str(id) not in str(user):
                  await bot.send_message(user, f"<a href='https://t.me/{message.from_user.username}'>{message.from_user.first_name}</a>:\n{message.text}", parse_mode="html", disable_web_page_preview=True)
         else:
            for death in game[1].split(","):
               if str(id) not in death:
                  await bot.send_message(user, f"💀 <a href='https://t.me/{message.from_user.username}'>{message.from_user.first_name}</a>:\n{message.text}", parse_mode="html", disable_web_page_preview=True)
      except:
         pass

@dp.callback_query_handler(lambda call: call.data.startswith("kill "))
async def kill(call: types.CallbackQuery):
   await call.message.delete()
   
   splited = call.data.split()
   
   kill = db.cur.execute("SELECT * FROM game_room WHERE room_id = ?", (splited[3],)).fetchone()
   
   print(f"{splited} test")
   
   if str(splited[1]) in kill[3].split(","):
      if kill[7] == "None":
         db.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (call.from_user.id, splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (f"{kill[7]},{call.from_user.id}", splited[3]))
         db.conn.commit()
      
      print("test")
      
      mafia = ""
      doctor = ""
      komisar = ""
      villager = ""
      
      for user in kill[3].split(","):
         try:
            if mafia:
               mafia += f",{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            else:
               mafia += f"{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
         except:
            pass
      
      for user in kill[4].split(","):
         try:
            if doctor:
               doctor += f",{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            else:
               doctor += f"{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
         except:
            pass
      
      for user in kill[5].split(","):
         try:
            if komisar:
               komisar += f",{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            else:
               komisar += f"{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
         except:
            pass
      
      for user in kill[6].split(","):
         try:
            if villager:
               villager += f",{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
            else:
               villager += f"{db.cur.execute('SELECT first_name FROM user_data WHERE user_id = ?', (user,)).fetchone()[0]}"
         except:
            pass
      
      news = ["Местный врач объяснил, что подозреваемый страдал психическим расстройством, и местные жители сообщали, что по ночам слышали, как он кричал о чем-то, связанном с призраками. Возможно, эти 'призраки'' стали причиной суицида подозреваемого. Местная полиция уже занимается этим вопросом.", "Местная полиция обнаружила в особняке мафии множество загадочных следов, которых оказалось не менее десятка. Продолжая расследование, следователи наткнулись на группировку, насчитывающую около двадцати убийц. Однако, к моменту обнаружения, было уже слишком поздно: мафиозные члены, между зубами у которых оказалась пелена, раздавили ее, высвободив яд, который быстро распространился по их телам. Инцидент произошел настолько молниеносно, что полиция не смогла даже начать допрос: вероятно, убийцы услышали шаги и, опасаясь быть раскрытыми, действовали моментально. Местная полиция уже проводит расследование данного инцидента."]
      
      for user in kill[1].split(","):
         await bot.send_message(user, f"<b>Мафия суециднулся</b>\n\n{random.choice(news)}\n\n👨‍🌾<b>МИРНЫЕ ПОБЕДИЛИ</b>\n\n🧛‍♂️Мафия-{mafia}\n👨‍⚕️Доктор-{doctor}\n👮‍♂️Шэриф-{komisar}\n👨‍🌾Жители-{villager}")
      
      db.cur.execute(f"DELETE FROM game_room WHERE room_id LIKE {splited[3]}")
      db.conn.commit()
   else:
      if kill[7] == "None":
         db.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (splited[1], splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (f"{kill[7]},{splited[1]}", splited[3]))
         db.conn.commit()
      
      await bot.send_message(splited[1], "Вас убили")
      
      gamesid = db.cur.execute("SELECT room FROM user_data WHERE user_id = ?", (splited[1],)).fetchone()[0]
      
      db.cur.execute("UPDATE user_data SET room = ? WHERE user_id = ?", (f"{gamesid.split()[:2]} dead", splited[1]))
      db.conn.commit()
      
      db.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("waitActionsKomisar", splited[3]))
      db.conn.commit()

@dp.callback_query_handler(lambda call: call.data.startswith("check "))
async def check(message: types.Message):
   await call.message.delete()
   
   splited = call.data.split()
   
   user = db.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (splited[1],)).fetchone()
   
   role_name = db.cur.execute("SELECT mafia, doctor, komisar, villager, history_role_for_komisar, is_check FROM game_room WHERE room_id = ?", (splited[3],)).fetchone()
   
   name = db.cur.execute("SELECT first_name FROM user_data WHERE user_id = ?", (splited[1],)).fetchone()
   
   if str(splited[1]) in role_name[0]:
      if role_name[4] == "None":
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{name[0]}-мафия", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{splited[1]}", splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{role_name[4]},{name[0]}-мафия", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{role_name[5]},{splited[1]}", splited[3]))
         db.conn.commit()
      
      await call.message.answer(f"{name[0]}-мафия")
         
   elif str(splited[1]) in role_name[1]:
      if role_name[4] == "None":
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{name[0]}-доктор", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{splited[1]}", splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{role_name[4]},{name[0]}-доктор", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{role_name[5]},{splited[1]}", splited[3]))
         db.conn.commit()
      
      await call.message.answer(f"{name[0]}-доктор")
         
   elif str(splited[1]) in role_name[2]:
      if role_name[4] == "None":
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{name[0]}-шэриф", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{splited[1]}", splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{role_name[4]},{name[0]}-шэриф", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{role_name[5]},{splited[1]}", splited[3]))
         db.conn.commit()
      
      await call.message.answer(f"{name[0]}-шэриф")
         
   elif str(splited[1]) in role_name[3]:
      if role_name[4] == "None":
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{name[0]}-житель", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{splited[1]}", splited[3]))
         db.conn.commit()
      else:
         db.cur.execute("UPDATE game_room SET history_role_for_komisar = ? WHERE room_id = ?", (f"{role_name[4]},{name[0]}-житель", splited[3]))
         db.conn.commit()
         
         db.cur.execute("UPDATE game_room SET is_check = ? WHERE room_id = ?", (f"{role_name[5]},{splited[1]}", splited[3]))
         db.conn.commit()
      
      await call.message.answer(f"{name[0]}-житель")
   
   db.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("waitActionsDoctor", splited[3]))
   db.conn.commit()

@dp.callback_query_handler(lambda call: call.data.startswith("cure "))
async def cure(call: types.CallbackQuery):
   await call.message.delete()
   
   splited = call.data.split()
   
   cure = db.cur.execute("SELECT dead FROM game_room WHERE room_id = ?", (splited[3],)).fetchone()[0]
   
   if splited[1] in cure:
      dead = cure.split(",")
      
      dead.remove(splited[1])
      
      db.cur.execute("UPDATE game_room SET dead = ? WHERE room_id = ?", (",".join(dead), splited[3]))
      db.conn.commit()
      
      await call.message.answer("Вы успешно вылечили пациента")
   else:
      await call.message.answer("Пациент был здоров")
   
   db.cur.execute("UPDATE game_room SET room_room = ? WHERE room_id = ?", ("EndNight", splited[3]))
   db.conn.commit()

@dp.callback_query_handler(lambda call: call.data.startswith("vote "))
async def vote(call: types.CallbackQuery):
   await call.message.delete()
   
   splited = call.data.split()
   
   vote = db.cur.execute("SELECT vote, who_voted FROM game_room WHERE room_id = ?", (splited[3],)).fetchone()
   
   if str(call.from_user.id) not in vote[0]:
      if vote[1] == "None":
         db.cur.execute("UPDATE game_room SET who_voted = ? WHERE room_id = ?", (call.from_user.id, splited[3]))
      else:
         db.cur.execute("UPDATE game_room SET who_voted = ? WHERE room_id = ?", (f"{vote[1]},{call.from_user.id}", splited[3]))
      
      db.conn.commit()
      
      output = ""
      for voted_user in vote[0].split(","):
         if splited[1] in voted_user:
            quantity_vote = int(voted_user.split("-")[1]) + 1
            result = f"{voted_user.split('-')[0]}-{quantity_vote}"
            
            if not output:
               output += result
            else:
               output += f",{result}"
      
      db.cur.execute("UPDATE game_room SET vote = ? WHERE room_id = ?", (output, splited[3]))
      db.conn.commit()
      
      await call.answer("Вы успешно проголосовали")

if "__main__" == __name__:
   
   loop = asyncio.get_event_loop()
   
   executor.start_polling(dp)
   
   loop.run_forever()
