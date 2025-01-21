from telethon import TelegramClient, events
import random
import json
import traceback
import asyncio
import os
from colorama import init, Fore
import shutil
import sys
import configparser
init(autoreset=True)


# Config loading 
config = configparser.ConfigParser()
config.read('config.ini', encoding='utf-8')

raw_instructions = config.get('SETTINGS', 'instructions')
instructions = raw_instructions.split("<::>")

try:os.mkdir("sessions")
except:pass

class StandardParams:
    app_id = 611335
    app_hash = "d524b414d21f4d37f08684c1df41ac9c"
    device = "ASUS TUF Dash F15"
    system_version = str(random.choice(["Deepin 15.11"]))
    app_version = "5.9 arm64 Snap"
    lang_code = "en"
    system_lang_code = "en"
    lang_pack = "tdesktop"


msg_timer = 2
voice_timer = 2

class Forwarder:
    def __init__(self, session_path: str, json_path: str = None):
        self.session_path = session_path
        self.json_path = json_path
        self.client = None

    def load_json(self):
        if self.json_path is not None:
            with open(self.json_path, encoding='utf-8') as f:
                data = json.load(f)
            return data
        else:
            data = {
                'app_id': StandardParams.app_id,
                'app_hash': StandardParams.app_hash,
                'device': StandardParams.device,
                'system_version': StandardParams.system_version,
                'app_version': StandardParams.app_version,
                'lang_code': StandardParams.lang_code,
                'system_lang_code': StandardParams.system_lang_code,
                'lang_pack': StandardParams.lang_pack
            }
            return data

    async def response(self, event: events.NewMessage.Event):
        if self.client is not None:
            print(Fore.YELLOW + "[?] Сессия " + self.session_path + " получила сообщение и начала отвечать!")
            try:
                
                for i in instructions:
                    if i == "":
                        continue
                    if "\\n" in i:
                        i = i.replace("\\n", "\n")
                    if not i.startswith("-voice="):
                        async with self.client.action(event.chat_id, 'typing'):
                            await asyncio.sleep(msg_timer)
                            await self.client.send_message(event.chat_id, i)
                    else:
                        async with self.client.action(event.chat_id, 'record-audio'):
                            file = i.split("=")[1]
                            await asyncio.sleep(voice_timer)
                            
                            await self.client.send_file(event.chat_id, file=file)
            except Exception as ex:
                print("Error sending file:", ex)
                traceback.print_exc()
        else:
            print("Bot is not running")

    async def start_forward(self):
        data = self.load_json()
        try:
            tg = TelegramClient(
                self.session_path,
                api_id=data['app_id'],
                api_hash=data['app_hash'],
                device_model=data['device'],
                system_version=data['system_version'],
                app_version=data['app_version'],
                lang_code=data['lang_code'],
                system_lang_code=data['system_lang_code']
            )

            await tg.start()
            if await tg.is_user_authorized():
                self.client = tg

                print(Fore.GREEN + "[+] Сессия " + self.session_path + " запущена!")

                @tg.on(events.NewMessage)
                async def handle_new_message(event):
                    try:
                        # Log incoming message

                        # Respond to the message
                        await self.response(event)

                    except Exception as e:
                        print(f"Error handling message: {e}")
                        traceback.print_exc()

                # Keep the client running until disconnected
                await tg.run_until_disconnected()

            else:
                print(Fore.RED + f"[DEAD] Сессия {self.session_path} мертвая!")

        except Exception as ex:
            traceback.print_exc()

def chat_clear():
    if sys.platform == "win32":
        os.system("cls")
    else:
        os.system("clear")

async def main():
    global instructions  # Объявляем, что будем изменять глобальную переменную instructions
    while True:
        menu = input(Fore.CYAN + "\n\n\nПриветствую! \n\n1. - Начать работу с сессиями\n2. - Кол-во текущих сессий\n3. - Текущая настройка\n4. - Настроить очередность\n5. - Очистить текущие настройки \n-> ")
        if menu == "1":
            chat_clear()
            try:
                sessions = []
                tasks = []
                
                sessions_dir = "sessions"  # Ensure this is the correct path to your sessions directory
                if not os.path.isdir(sessions_dir):
                    print(f"The directory '{sessions_dir}' does not exist.")
                    return

                for i in os.listdir(sessions_dir):
                    if not i.endswith(".session"):
                        continue
                    sessions.append(os.path.join(sessions_dir, i))  # Include the directory path

                if not sessions:
                    print("No session files found.")
                    return

                for session in sessions:
                    json_path = session.replace(".session", ".json")
                    if os.path.exists(json_path):
                        tasks.append(asyncio.create_task(Forwarder(session, json_path).start_forward()))
                    else:
                        tasks.append(asyncio.create_task(Forwarder(session, None).start_forward()))
                
                if tasks:
                    await asyncio.gather(*tasks)
                else:
                    print("No tasks to run.")
            except Exception as ex:
                traceback.print_exc()

        elif menu == "2":
            chat_clear()
            sessions = []
            for i in os.listdir("sessions"):
                if not i.endswith(".session"):
                    continue
                sessions.append(os.path.join("sessions", i))
            print("Общее кол-во аккаунтов: " + str(len(sessions)))
        elif menu == "3":
            chat_clear()
            instructions_string = ""
            for i in instructions:
                if not i.startswith("-voice="):
                    instructions_string += Fore.LIGHTCYAN_EX + f"\n({msg_timer} сек.)\n{i}"
                else: 
                    instructions_string += f"\n({voice_timer} сек.){Fore.LIGHTGREEN_EX}\n(голосовое сообщение)"
            print(f"Текущие настройки:\n\nЗадержка сообщений: {msg_timer}\nЗадержка голосовых сообщений: {voice_timer}\nПорядок: \n\n{instructions_string}\n\n")

        elif menu == "4":
            chat_clear()
            print("Настройте порядок\nДля обычного сообщения введите его текстом, а для голосового, введите его так: \n-voice={voice_file.ogg}\nНапример: \n-voice=my_recording.ogg\n\\n - Перенос строки\nДля выхода введите /stop\n")
            while True:
                now = input("Введите новый пункт.\n-> ")
                if now.strip() == "/stop":
                    break
                if now.strip(): 
                    instructions.append(now.strip())
                    print("Действие добавлено!")

            try:
                raw_instructions_updated = "<::>".join(instructions)
                config.set('SETTINGS', 'instructions', raw_instructions_updated)
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    config.write(configfile)
                print(Fore.GREEN + "Настройки успешно сохранены в config.ini!")
            except Exception as e:
                print(Fore.RED + f"Ошибка при сохранении настроек: {e}")
                traceback.print_exc()

        elif menu == "5":
            chat_clear()
            try:
                raw_instructions_updated = ""
                config.set('SETTINGS', 'instructions', raw_instructions_updated)
                with open('config.ini', 'w', encoding='utf-8') as configfile:
                    config.write(configfile)
                instructions = []
                print(Fore.GREEN + "Настройки успешно очищены!")
            except Exception as e:
                print(Fore.RED + f"Ошибка при очистке настройок: {e}")
                traceback.print_exc()
        else:
            print(Fore.RED + "Неверный выбор. Пожалуйста, попробуйте снова.")

        

if __name__ == "__main__":
    asyncio.run(main())
