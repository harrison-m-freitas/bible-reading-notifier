import os
import json
import time
from datetime import datetime, timedelta
from threading import Timer
from typing import Dict, Union, List

from whatsapp_manager import WhatsAppManager
from whatsapp_manager import (CHROME_DRIVER, CHROME_PROFILE)
from bible_manager import BibleManager

class Controller:
    config_folder = os.path.abspath(
        os.path.join(os.path.dirname(__file__), "config")
    )
    contact_path = os.path.join(config_folder, "contact.json")
    last_sent_path = os.path.join(config_folder, "last_sent_date.json")
    
    def __init__(self) -> None:
        self.bible_manager = BibleManager()
        self.contacts = self.load_contacts()
    
    def load_contacts(self) -> Dict[str, Union[str, None]]:
        if os.path.exists(self.contact_path):
            with open(self.contact_path, "r", encoding="UTF-8") as file:
                file_contact = json.load(file)
                
                test_user: str = file_contact.get("test_user", "Bloco de Notas")
                support_user: str = file_contact.get("support_user", "Bloco de Notas")
                reading_group: Union[str, None] = file_contact.get("reading_group", None)
                
                contacts = {
                "test_user": test_user,
                "support_user": support_user,
                "reading_group": reading_group
                }
                
                return contacts
        else:
            contacts = {
                "test_user": "Bloco de Notas",
                "support_user": "Bloco de Notas",
                "reading_group": None
            }
            
            return contacts

    def was_sent_today(self) -> bool:
        if not os.path.exists(self.last_sent_path):
            return False

        today = datetime.today().date()

        with open(self.last_sent_path, 'r', encoding="UTF-8") as file:
            last_sent = json.load(file).get("date", None)

            if last_sent is None:
                return False

            last_sent_date = datetime.strptime(last_sent, "%Y/%m/%d").date()
            return last_sent_date == today
        
    def mark_as_sent_today(self) -> None:
        today_str = datetime.today().strftime('%Y/%m/%d')
        with open(self.last_sent_path, 'w', encoding="UTF-8") as file:
            json.dump({"date": today_str}, file, ensure_ascii=False)
    
    def send_daily_message(self) -> None:
        self.whatsapp_manager = WhatsAppManager(CHROME_PROFILE, CHROME_DRIVER)
        if not self.was_sent_today():
            try:
                self.whatsapp_manager.send_message(
                    self.contacts["support_user"], 
                    "Daily Bible reading message"
                )
                
                books_chapters = self.bible_manager.daily_read_chapter(was_sent=False)
                
                for pos, bk_chapters in enumerate(books_chapters):
                    if pos > 1:
                        print("Test - Most one book")
                    
                    bk: str = bk_chapters.get("book", None)
                    chapters: List[int] = bk_chapters.get("chapters", [])
                    if bk is not None:
                        book_data = self.bible_manager.bible_books.get(bk, None)
                        if book_data is not None:
                            for ch in chapters:
                                ch_str = f"{ch:02d}"
                                ch_path = book_data["chapters"][ch_str]
                                if os.path.exists(ch_path):
                                    with open(ch_path, "r", encoding="UTF-8") as file:
                                        text = file.read()
                                        self.whatsapp_manager.send_message(
                                            self.contacts["support_user"],
                                            text
                                        )
                                        
                # self.mark_as_sent_today() # Marca como enviado
                
                print("Daily message sent successfully.")
            except Exception as e:
                error_message = f"Error sending daily message: {str(e)}"
                print(error_message)
                self.whatsapp_manager.send_message(
                    self.contacts["support_user"],
                    error_message
                )
            finally:
                self.whatsapp_manager.close()

    def schedule_daily_task(self) -> None:
        now = datetime.now()
        if now.hour < 5:
            next_run_time = now.replace(hour=5, minute=0, second=0, microsecond=0)
        elif now.hour > 20:
            next_run_time = (now + timedelta(days=1)).replace(hour=5, minute=0, second=0, microsecond=0)
        else:
            next_run_time = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        
        delay = (next_run_time - now).total_seconds() 
        
        Timer(delay, self.run_daily_task).start()
        
    def run_daily_task(self) -> None:
        now = datetime.now()
        if 5 <= now.hour <= 20:
            self.send_daily_message()
        self.schedule_daily_task()
        
    def start_on_boot(self) -> None:
        startup_folder = os.path.join(
            os.getenv("APPDATA"), "Microsoft", "Windows",
            "Start Menu", "Programs", "Startup"
        )
        shortcut_path = os.path.join(startup_folder, "BibleReadingNotifier.Ink")
        
        if not os.path.exists(shortcut_path):
            target = os.path.abspath(__file__)
            os.system(f'shortcut /F:{shortcut_path} /A:C /T:{target}')

        

if __name__ == "__main__":
    controller = Controller()
    controller.send_daily_message()
    print(controller.contacts)
    print(controller.was_sent_today())