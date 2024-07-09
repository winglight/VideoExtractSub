import tkinter as tk
from tkinter import ttk, messagebox
import requests
import sqlite3
import markdown2
import webbrowser
from tkhtmlview import HTMLLabel
import json
from dotenv import load_dotenv
import os

load_dotenv()

LANGFLOW_API_KEY = os.getenv('LANGFLOW_API_KEY')

class DictionaryApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Dictionary App")
        self.master.geometry("600x500")

        self.create_widgets()
        self.create_database()

    def create_widgets(self):
        # 搜索框和按钮
        self.search_frame = ttk.Frame(self.master)
        self.search_frame.pack(pady=10)

        self.search_entry = ttk.Entry(self.search_frame, width=40)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_button = ttk.Button(self.search_frame, text="Search", command=self.search_word)
        self.search_button.pack(side=tk.LEFT)

        # 结果显示区域
        self.result_frame = ttk.Frame(self.master)
        self.result_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.result_display = HTMLLabel(self.result_frame, html="")
        self.result_display.pack(fill=tk.BOTH, expand=True)

        # 历史记录列表
        self.history_frame = ttk.Frame(self.master)
        self.history_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.history_tree = ttk.Treeview(self.history_frame, columns=("word", "count"), show="headings")
        self.history_tree.heading("word", text="Word")
        self.history_tree.heading("count", text="Search Count")
        self.history_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scrollbar = ttk.Scrollbar(self.history_frame, orient=tk.VERTICAL, command=self.history_tree.yview)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_tree.configure(yscrollcommand=self.scrollbar.set)

        # 删除按钮
        self.delete_button = ttk.Button(self.master, text="Delete Selected", command=self.delete_selected)
        self.delete_button.pack(pady=5)

    def create_database(self):
        self.conn = sqlite3.connect("dictionary_history.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS history
            (word TEXT PRIMARY KEY, count INTEGER)
        """)
        self.conn.commit()

    def search_word(self):
        word = self.search_entry.get().strip()
        if not word:
            messagebox.showwarning("Warning", "Please enter a word to search.")
            return

        # 调用新的API
        api_url = "https://ai.zhnbhl.cn/api/v1/run/eb76f1d6-85d3-43c9-9c4d-a027833ccedd?stream=false"
        headers = {
            'Content-Type': 'application/json',
            'x-api-key': LANGFLOW_API_KEY  # 请替换为您的实际API密钥
        }
        payload = {
            "input_value": f"Define the word: {word}",
            "output_type": "chat",
            "input_type": "chat",
            "tweaks": {
                "GroqModel-snATY": {},
                "ChatInput-rBilA": {},
                "ChatOutput-ZT9GJ": {},
                "Prompt-GDHj8": {}
            }
        }

        try:
            response = requests.post(api_url, headers=headers, data=json.dumps(payload))
            response.raise_for_status()  # 抛出异常如果请求失败
            data = response.json()
            
            # 假设API返回的是一个包含定义的字符串
            definition = data.get('output', 'No definition found.')
            
            # 将返回的定义转换为简单的Markdown格式
            formatted_definition = f"# {word}\n\n{definition}"
            
            html_content = markdown2.markdown(formatted_definition)
            self.result_display.set_html(html_content)
            self.update_history(word)
        except requests.RequestException as e:
            self.result_display.set_html(f"<p>Error occurred while fetching the definition: {str(e)}</p>")

    def format_definition(self, data):
        word = data['word']
        phonetic = data.get('phonetic', '')
        meanings = data['meanings']

        definition = f"# {word}\n\n"
        if phonetic:
            definition += f"*{phonetic}*\n\n"

        for meaning in meanings:
            part_of_speech = meaning['partOfSpeech']
            definition += f"## {part_of_speech}\n\n"

            for idx, definition_item in enumerate(meaning['definitions'], 1):
                definition += f"{idx}. {definition_item['definition']}\n"
                if 'example' in definition_item:
                    definition += f"   - Example: *{definition_item['example']}*\n"
                definition += "\n"

        return definition

    def update_history(self, word):
        self.cursor.execute("INSERT OR REPLACE INTO history VALUES (?, COALESCE((SELECT count FROM history WHERE word = ?) + 1, 1))", (word, word))
        self.conn.commit()
        self.update_history_display()

    def update_history_display(self):
        self.history_tree.delete(*self.history_tree.get_children())
        self.cursor.execute("SELECT word, count FROM history ORDER BY count DESC")
        for row in self.cursor.fetchall():
            self.history_tree.insert("", "end", values=row)

    def delete_selected(self):
        selected_items = self.history_tree.selection()
        if not selected_items:
            messagebox.showwarning("Warning", "Please select an item to delete.")
            return

        for item in selected_items:
            word = self.history_tree.item(item)['values'][0]
            self.cursor.execute("DELETE FROM history WHERE word = ?", (word,))

        self.conn.commit()
        self.update_history_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = DictionaryApp(root)
    root.mainloop()