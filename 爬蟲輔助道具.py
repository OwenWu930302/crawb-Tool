import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import threading
import queue
import tkinter.filedialog as fd
from selenium_utils import find_by_keyword, advanced_search  

# 任務隊列
task_queue = queue.Queue()
result_queue = queue.Queue()

def crawler_task(url, keyword, headless, result_queue):
    result = find_by_keyword(url, keyword, headless)
    result_queue.put(result)

def worker(url, keyword, headless):
    while True:
        if not task_queue.empty():
            task_queue.get()
            crawler_task(url, keyword, headless, result_queue)
            task_queue.task_done()
        else:
            break

def start_crawling():
    url = url_var.get().strip()
    keyword = keyword_var.get().strip()
    try:
        thread_count = int(thread_var.get())
    except ValueError:
        messagebox.showerror("錯誤", "線程數必須為數字")
        return
    headless = headless_var.get()
    if not url or not keyword:
        messagebox.showerror("錯誤", "請輸入網址與文字")
        return

    # 清空結果
    result_text.delete('1.0', tk.END)
    # 填充任務隊列
    for _ in range(thread_count):
        task_queue.put(1)

    # 啟動線程
    threads = []
    for _ in range(thread_count):
        t = threading.Thread(target=worker, args=(url, keyword, headless))
        t.daemon = True
        t.start()
        threads.append(t)

    # 啟動結果監聽
    root.after(100, check_result)

def check_result():
    while not result_queue.empty():
        result = result_queue.get()
        result_text.insert(tk.END, result + '\n\n')
    if task_queue.unfinished_tasks > 0:
        root.after(100, check_result)
    else:
        # 自動匯出
        if export_var.get():
            export_to_txt()

def export_to_txt():
    content = result_text.get('1.0', tk.END).strip()
    if not content:
        messagebox.showinfo("提示", "沒有可匯出的內容")
        return
    file_path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        messagebox.showinfo("完成", f"已匯出到：{file_path}")

# 進階功能
def open_advanced():
    adv_win = tk.Toplevel(root)
    adv_win.title("進階元素搜尋")
    ttk.Label(adv_win, text="請貼上HTML片段或CSS/XPath選擇器:").pack(anchor='w', padx=10, pady=5)
    adv_input = tk.Text(adv_win, height=4, width=60)
    adv_input.pack(padx=10, pady=5)
    adv_result = scrolledtext.ScrolledText(adv_win, width=80, height=15)
    adv_result.pack(padx=10, pady=5)
    adv_result_queue = queue.Queue()

    def adv_worker(url, selector, headless):
        results = advanced_search(url, selector, headless)
        adv_result_queue.put(results)

    def run_advanced_search():
        url = url_var.get().strip()
        input_str = adv_input.get('1.0', tk.END).strip()
        headless = headless_var.get()
        try:
            adv_thread_count = int(thread_var.get())
        except ValueError:
            messagebox.showerror("錯誤", "線程數必須為數字")
            return
        if not url or not input_str:
            messagebox.showerror("錯誤", "請輸入網址與搜尋條件")
            return

        adv_result.delete('1.0', tk.END)
        threads = []
        for _ in range(adv_thread_count):
            t = threading.Thread(target=adv_worker, args=(url, input_str, headless))
            t.daemon = True
            t.start()
            threads.append(t)

        # 等待所有線程結束並收集結果
        def collect_results():
            if any([t.is_alive() for t in threads]):
                adv_win.after(100, collect_results)
            else:
                results = []
                while not adv_result_queue.empty():
                    results.extend(adv_result_queue.get())
                if results:
                    adv_result.insert(tk.END, '\n'.join(results))
                else:
                    adv_result.insert(tk.END, "未找到符合元素")
        collect_results()

    def adv_export_to_txt():
        content = adv_result.get('1.0', tk.END).strip()
        if not content:
            messagebox.showinfo("提示", "沒有可匯出的內容")
            return
        file_path = fd.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            messagebox.showinfo("完成", f"已匯出到：{file_path}")

    btn_frame = ttk.Frame(adv_win)
    btn_frame.pack(pady=5)
    ttk.Button(btn_frame, text="搜尋", command=run_advanced_search).pack(side='left', padx=5)
    ttk.Button(btn_frame, text="匯出TXT", command=adv_export_to_txt).pack(side='left', padx=5)

# Tkinter UI
root = tk.Tk()
root.title("動態爬蟲多線程工具")

frame = ttk.Frame(root, padding=10)
frame.pack(fill='x')

ttk.Label(frame, text="網址:").grid(row=0, column=0, sticky='w')
url_var = tk.StringVar()
ttk.Entry(frame, textvariable=url_var, width=50).grid(row=0, column=1, sticky='we', columnspan=3)

ttk.Label(frame, text="搜尋文字:").grid(row=1, column=0, sticky='w')
keyword_var = tk.StringVar()
ttk.Entry(frame, textvariable=keyword_var, width=30).grid(row=1, column=1, sticky='we')

ttk.Label(frame, text="線程數(0-20):").grid(row=2, column=0, sticky='w')
thread_var = tk.StringVar(value='5')
ttk.Combobox(frame, textvariable=thread_var, values=[str(i) for i in range(0, 21)], width=5).grid(row=2, column=1, sticky='w')

headless_var = tk.BooleanVar(value=True)
ttk.Checkbutton(frame, text="Headless(無頭瀏覽器)", variable=headless_var).grid(row=2, column=2, sticky='w')

export_var = tk.BooleanVar(value=False)
ttk.Checkbutton(frame, text="爬完自動匯出TXT", variable=export_var).grid(row=2, column=3, sticky='w')

ttk.Button(frame, text="開始爬取", command=start_crawling).grid(row=3, column=0, columnspan=4, pady=5)
ttk.Button(frame, text="手動匯出TXT", command=export_to_txt).grid(row=3, column=4, padx=5)
ttk.Button(frame, text="進階功能", command=open_advanced).grid(row=3, column=5, padx=5)

result_text = scrolledtext.ScrolledText(root, width=80, height=20)
result_text.pack(fill='both', expand=True, padx=10, pady=5)

root.mainloop()
