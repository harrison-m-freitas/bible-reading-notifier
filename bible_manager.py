import os
import re
import json
from typing import Dict, List, Union

# Bible Dir
BOOK_ABBREVIATIONS = {
    "Gênesis": "Gn",
    "Êxodo": "Ex",
    "Levítico": "Lv",
    "Números": "Nm",
    "Deuteronômio": "Dt",
    "Josué": "Js",
    "Juízes": "Jz",
    "Rute": "Rt",
    "I Samuel": "1Sm",
    "II Samuel": "2Sm",
    "I Reis": "1Rs",
    "II Reis": "2Rs",
    "I Crônicas": "1Cr",
    "II Crônicas": "2Cr",
    "Esdras": "Ed",
    "Neemias": "Ne",
    "Ester": "Et",
    "Jó": "Jó",
    "Salmos": "Sl",
    "Provérbios": "Pv",
    "Eclesiastes": "Ec",
    "Cantares": "Ct",
    "Isaías": "Is",
    "Jeremias": "Jr",
    "Lamentações": "Lm",
    "Ezequiel": "Ez",
    "Daniel": "Dn",
    "Oseias": "Os",
    "Joel": "Jl",
    "Amós": "Am",
    "Obadias": "Ob",
    "Jonas": "Jn",
    "Miquéias": "Mq",
    "Naum": "Na",
    "Habacuque": "Hc",
    "Sofonias": "Sf",
    "Ageu": "Ag",
    "Zacarias": "Zc",
    "Malaquias": "Ml",
    "Mateus": "Mt",
    "Marcos": "Mc",
    "Lucas": "Lc",
    "João": "Jo",
    "Atos": "At",
    "Romanos": "Rm",
    "I Coríntios": "1Co",
    "II Coríntios": "2Co",
    "Gálatas": "Gl",
    "Efésios": "Ef",
    "Filipenses": "Fp",
    "Colossenses": "Cl",
    "I Tessalonicenses": "1Ts",
    "II Tessalonicenses": "2Ts",
    "I Timóteo": "1Tm",
    "II Timóteo": "2Tm",
    "Tito": "Tt",
    "Filemom": "Fm",
    "Hebreus": "Hb",
    "Tiago": "Tg",
    "I Pedro": "1Pe",
    "II Pedro": "2Pe",
    "I João": "1Jo",
    "II João": "2Jo",
    "III João": "3Jo",
    "Judas": "Jd",
    "Apocalipse": "Ap"
}


class BibleManager:
    def __init__(self) -> None:
        self.bible_dir: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "bible")
        )
        self.old_testament: str = os.path.abspath(
            os.path.join(self.bible_dir, "Antigo Testamento")
        )
        self.new_testament: str = os.path.abspath(
            os.path.join(self.bible_dir, "Novo Testamento")
        )
        self.last_chapter: str = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "config", "last_chapter.json")
        )
        
        self.bible_books: Dict[str, Dict[str, Union[str, int, Dict[str, str]]]] = {
            **self.load_books(self.old_testament),
            **self.load_books(self.new_testament)
        }
        
    def chapters_list_filter(self, list_chapters: List[str], dir_path: str) -> Dict[str, str]:
        """
        Filtra e retorna os capítulos de um livro.
        
        :param list_chapters: Lista de Capítulos.
        :param dir_path: Caminho do diretório dos capítulos.
        :return: Dicionário com capítulos e seus caminhos
        """
        chapter_pattern = re.compile(r"^(\S+)\s(\d+).txt$")
        chapters = {}
        
        for chapter in list_chapters:
            match = chapter_pattern.match(chapter)
            
            if match:
                chapter_num = match.group(2)
                chapter_path = os.path.join(dir_path, chapter)
                chapters[chapter_num] = chapter_path
        return chapters

    def load_books(self, testament_book: str) ->  Dict[str, Dict[str, Union[str, int, Dict[str, str]]]]:
        """
        Carrega os livros de um testamento.
        
        :param testament_book: Caminho do diretório do testamento.
        :return: Dicionário de livros com seus capítulos e informações.
        """
        books = {}
        
        for book in os.listdir(testament_book):
            book_path = os.path.join(testament_book, book)
            if os.path.isdir(book_path):
                chapters = self.chapters_list_filter(
                    sorted(os.listdir(book_path)),
                    book_path
                )
                book_pattern = re.compile(r"^\d+\s(.+)$")
                match = book_pattern.match(book)
                if match:
                    book = match.group(1)
                
                book_abbrev = BOOK_ABBREVIATIONS.get(book, book)
                books[book_abbrev] = {
                    "chapters": chapters,
                    "book": book,
                    "num_chapters": len(chapters)
                }
        return books
    
    def get_next_book(self, current_book: str) -> Union[str, None]:
        """
        Obtém o próximo livro na sequência da Bíblia.
        
        :param current_book: Livro atual.
        :return: Próximo livro ou None se não houver mais livros.
        """
        books = list(self.bible_books.keys())
        current_index = books.index(current_book)
        if current_index + 1 < len(books):
            return books[current_index + 1]
        return None
    
    def save_current_state(self, book: str, chapter: int, finished: bool) -> None:
        """
        Salva o estado atual da leitura.
        
        :param book: Livro atual.
        :param chapter: Capítulo atual.
        :pram finished: Indica se a leitura foi concluída.
        """
        with open(self.last_chapter, "w", encoding="UTF-8") as file:
            json.dump(
                {"last_book": book, "last_chapter": chapter, "finished": finished},
                file,
                ensure_ascii=False
            )
        
    def daily_read_chapter(self, was_sent: bool = False) -> List[Dict[str, Union[str, List[int]]]]:
        """
        Obtém a leitura diária dos capítulos da Bíblia.
        
        :param was_sent: Indica se a mensagem foi enviada.
        :return: Lista de dicionários com os livros e capítulos a serem lidos.
        """
        
        read_chapters = []
        
        if os.path.exists(self.last_chapter):
            with open(self.last_chapter, 'r', encoding="UTF-8") as file:
                last_data = json.load(file)
                
                book: str = last_data.get("last_book", None)
                chapter: int = last_data.get("last_chapter", None)
                finished: bool = last_data.get("finished", False)
        else:
            book = "Gn"
            chapter = 0
            finished = False
            
        if book and chapter is not None:
            bible_book = self.bible_books.get(book, None)
            
            if bible_book is None:
                raise ValueError("Livro não encontrado na Bíblia")
            
            nums_chapter = 4 # Numero de capítulos por dia
            daily_range = []
            
            while nums_chapter > 0:
                remaining_chapters = bible_book["num_chapters"] - chapter
                if remaining_chapters >= nums_chapter:
                    daily_range = list(range(chapter + 1, chapter + nums_chapter + 1))
                    if daily_range:
                        read_chapters.append({"book": book, "chapters": daily_range})
                        
                    chapter += nums_chapter
                    nums_chapter = 0
                else:
                    daily_range = list(range(chapter + 1, bible_book["num_chapters"] + 1))
                    if daily_range:
                        read_chapters.append({"book": book, "chapters": daily_range})
                    
                    nums_chapter -= remaining_chapters
                    chapter = 0
                    book = self.get_next_book(book)
                    if book is None:
                        finished = True
                        break
                    bible_book = self.bible_books[book]
                    
            if was_sent:
                self.save_current_state(book, chapter, finished)
            
            return read_chapters
        return read_chapters


if __name__ == "__main__":
    bible_manager = BibleManager()
    read_ch = bible_manager.daily_read_chapter()
    print(f"Proxima leitura: {read_ch}")