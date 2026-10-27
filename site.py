import os
import qrcode
from flask import Flask, render_template_string, request, send_from_directory

app = Flask(__name__)

# Dosyaların kaydedileceği klasör
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Listeler
uploaded_files_list = []
uploaded_links_list = []

# 1. TAHTA EKRANI (Sol: QR, Orta: Dosyalar, Sağ: Linkler)
@app.route('/')
def index():
    global uploaded_files_list, uploaded_links_list
    current_url = request.host_url.rstrip('/') + '/upload'
    
    # QR kodu üret
    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(current_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    img.save("static_qr.png")

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <title>Akıllı Tahta Dosya & Link Paylaşımı</title>
        <meta http-equiv="refresh" content="3">
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .main-container { display: flex; background: white; width: 1250px; max-width: 100%; border-radius: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); overflow: hidden; }
            .pane { padding: 30px; display: flex; flex-direction: column; justify-content: flex-start; }
            .left-pane { flex: 0.9; background: #ffffff; text-align: center; border-right: 1px solid #eee; align-items: center; justify-content: center; }
            .left-pane h1 { font-size: 20px; color: #333; margin-bottom: 8px; }
            .left-pane p { color: #666; font-size: 14px; margin-bottom: 15px; }
            img.qr { width: 220px; height: 220px; border: 4px solid #f0f0f0; border-radius: 12px; }
            .middle-pane, .right-pane { flex: 1.1; background: #fafbfc; }
            .middle-pane { border-right: 1px solid #eee; }
            h2 { font-size: 18px; color: #333; margin-top: 0; margin-bottom: 15px; border-bottom: 2px solid #eaeaea; padding-bottom: 8px; }
            .list-container { flex-grow: 1; max-height: 380px; overflow-y: auto; padding-right: 5px; }
            .item-card { background: white; padding: 10px 14px; margin-bottom: 10px; border-radius: 8px; border: 1px solid #e1e4e8; display: flex; justify-content: space-between; align-items: center; box-shadow: 0 2px 5px rgba(0,0,0,0.02); }
            .item-text { font-size: 13px; color: #333; font-weight: 500; word-break: break-all; max-width: 200px; }
            .btn-action { background: #28a745; color: white; padding: 6px 12px; text-decoration: none; border-radius: 6px; font-size: 12px; font-weight: 600; transition: background 0.2s; white-space: nowrap; }
            .btn-action:hover { background: #218838; }
            .btn-link { background: #007bff; }
            .btn-link:hover { background: #0056b3; }
            .empty-text { color: #999; font-style: italic; text-align: center; margin-top: 40px; font-size: 13px; }
        </style>
    </head>
    <body>
        <div class="main-container">
            <div class="pane left-pane">
                <h1>Tahtaya Gönder</h1>
                <p>Kameranla okut, dosya veya link at!</p>
                <img src="/qr" class="qr">
            </div>
            <div class="pane middle-pane">
                <h2>Dosyalar</h2>
                <div class="list-container">
                    {% if files %}
                        {% for f in files %}
                            <div class="item-card">
                                <span class="item-text" title="{{ f }}">{{ f }}</span>
                                <a href="/uploads/{{ f }}" target="_blank" class="btn-action">Aç / İndir</a>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p class="empty-text">Henüz dosya yok.</p>
                    {% endif %}
                </div>
            </div>
            <div class="pane right-pane">
                <h2>Linkler (URL)</h2>
                <div class="list-container">
                    {% if links %}
                        {% for l in links %}
                            <div class="item-card">
                                <span class="item-text" title="{{ l }}">{{ l }}</span>
                                <a href="{{ l }}" target="_blank" class="btn-action btn-link">Git</a>
                            </div>
                        {% endfor %}
                    {% else %}
                        <p class="empty-text">Henüz link yok.</p>
                    {% endif %}
                </div>
            </div>
        </div>
    </body>
    </html>
    ''', files=uploaded_files_list, links=uploaded_links_list)

@app.route('/qr')
def qrcode_image():
    return send_from_directory('.', 'static_qr.png')

# 2. TELEFON EKRANI (Dosya ve Link Paneli - v2 Güncel)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    global uploaded_files_list, uploaded_links_list
    
    if request.method == 'POST':
        action_type = request.form.get('action_type')
        
        if action_type == 'file':
            if 'file' in request.files:
                file = request.files['file']
                if file.filename != '':
                    filename = file.filename
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    file.save(filepath)
                    if filename not in uploaded_files_list:
                        uploaded_files_list.insert(0, filename)
                        
        elif action_type == 'link':
            link_url = request.form.get('link_url')
            if link_url:
                if not link_url.startswith(('http://', 'https://')):
                    link_url = 'https://' + link_url
                if link_url not in uploaded_links_list:
                    uploaded_links_list.insert(0, link_url)
                    
        return '''
        <script>
            alert("Başarıyla tahtaya gönderildi!");
            window.location.href = "/upload";
        </script>
        '''

    return render_template_string('''
    <!DOCTYPE html>
    <html lang="tr">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Akıllı Tahta Gönderim Paneli v2</title>
        <style>
            * { box-sizing: border-box; }
            body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background: #f4f7f6; margin: 0; padding: 20px; display: flex; justify-content: center; align-items: center; min-height: 100vh; }
            .mobile-container { display: flex; flex-direction: column; gap: 20px; width: 100%; max-width: 420px; }
            .box { background: white; padding: 25px 20px; border-radius: 16px; box-shadow: 0 6px 15px rgba(0,0,0,0.06); text-align: center; }
            h2 { color: #333; font-size: 18px; margin-bottom: 8px; }
            p { color: #666; font-size: 13px; margin-bottom: 15px; }
            input[type="file"], input[type="text"] { width: 100%; padding: 10px; border: 1px solid #ccc; border-radius: 8px; background: #fafafa; font-size: 14px; margin-bottom: 12px; }
            input[type="file"] { border: 2px dashed #ccc; }
            button { background: #007bff; color: white; border: none; padding: 12px; font-size: 15px; font-weight: 600; border-radius: 8px; width: 100%; cursor: pointer; transition: background 0.2s; }
            button:hover { background: #0056b3; }
            .btn-file { background: #28a745; }
            .btn-file:hover { background: #218838; }
        </style>
    </head>
    <body>
        <div class="mobile-container">
            <!-- 1. Dosya Gönderme Kutusu -->
            <div class="box">
                <h2>📁 Dosya Gönder</h2>
                <p>Fotoğraf, video veya PDF seç.</p>
                <form method="post" enctype="multipart/form-data">
                    <input type="hidden" name="action_type" value="file">
                    <input type="file" name="file" required>
                    <button type="submit" class="btn-file">Dosyayı Gönder</button>
                </form>
            </div>

            <!-- 2. Link Gönderme Kutusu -->
            <div class="box" style="border: 2px solid #007bff;">
                <h2>🔗 Link (URL) Gönder</h2>
                <p>İnternet adresi veya YouTube linki yapıştır.</p>
                <form method="post">
                    <input type="hidden" name="action_type" value="link">
                    <input type="text" name
