import webview
import json

# Python 端 API，負責接收元素資訊
class Api:
    def show_element_info(self, info):
        print('--- 你點選的元素資訊 ---')
        print(json.dumps(info, ensure_ascii=False, indent=2))
        props = [f"{k}: {v}" if not isinstance(v, dict) else f"{k}: {json.dumps(v, ensure_ascii=False)}"
                for k, v in info.items()]
        msg = "\\n".join(props).replace("`", "'")
        msg = msg.replace("'", "\\'")
        js = f"alert('元素資訊：\\n{msg}')"
        webview.windows[0].evaluate_js(js)

    def load_url(self, url):
        if not url.startswith('http'):
            url = 'https://' + url
        webview.windows[0].load_url(url)

# JS：選取模式與按鈕
element_picker_js = """
function enableElementPicker() {
    document.body.style.cursor = 'crosshair';
    document.addEventListener('click', function handler(e) {
        e.preventDefault();
        e.stopPropagation();
        document.body.style.cursor = '';
        let elem = e.target;
        let attrs = {};
        for (let attr of elem.attributes) {
            attrs[attr.name] = attr.value;
        }
        let info = {
            tag: elem.tagName,
            id: elem.id,
            class: elem.className,
            href: elem.href || '',
            src: elem.src || '',
            name: elem.name || '',
            value: elem.value || '',
            text: elem.innerText || '',
            outerHTML: elem.outerHTML,
            attributes: attrs
        };
        window.pywebview.api.show_element_info(info);
        document.removeEventListener('click', handler, true);
    }, true);
}

// 注入按鈕與選取模式
if (!document.getElementById('element-picker-btn')) {
    let btn = document.createElement('button');
    btn.innerText = '啟用元素讀取';
    btn.id = 'element-picker-btn';
    btn.style.position = 'fixed';
    btn.style.top = '10px';
    btn.style.right = '10px';
    btn.style.zIndex = 9999;
    btn.style.padding = '10px 20px';
    btn.style.background = '#1976d2';
    btn.style.color = 'white';
    btn.style.border = 'none';
    btn.style.borderRadius = '5px';
    btn.style.cursor = 'pointer';
    btn.onclick = enableElementPicker;
    document.body.appendChild(btn);
}
"""

def on_loaded(window):
    # 每次頁面載入都注入選取按鈕與功能
    window.evaluate_js(element_picker_js)

if __name__ == '__main__':
    # 首頁 HTML：網址輸入框與載入按鈕
    html = """
    <div style="padding:20px;">
        <input id="url-input" type="text" placeholder="輸入網址（如 youtube.com ）" style="width:300px;font-size:16px;">
        <button onclick="window.pywebview.api.load_url(document.getElementById('url-input').value)"
            style="font-size:16px;padding:4px 16px;">載入</button>
        <div style="margin-top:20px;">
            <span>可直接輸入 YouTube、PTT、FB、動態網頁等網址，進入網頁後點右上角「啟用元素讀取」即可點選元素取得所有屬性。</span>
        </div>
    </div>
    """
    # gui='cef' 或 gui='qt'，確保 YouTube、動態網頁兼容性
    window = webview.create_window('互動式爬蟲輔助工具', html=html, js_api=Api())
    webview.start(on_loaded, window)
