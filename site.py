import streamlit as st
import requests
import datetime
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Mert & Zübeyde Ders Takip", page_icon="📚", layout="centered")

# --- API BİLGİLERİ (SENİN GİRDİĞİN BİLGİLER) ---
BIN_ID = "691f3259d0ea881f40f4bd1b"
API_KEY = "$2a$10$ln7I9iGthRnAvR06HPE3g.USj5Li/vCQiH/XNKYpfjLb67jHguweW"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

# --- FONKSİYONLAR ---
def verileri_cek():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()['record']
        else:
            st.error("Veri çekilemedi. API Key veya Bin ID kontrol et.")
            return {}
    except:
        return {}

def verileri_gonder(veri):
    try:
        requests.put(URL, json=veri, headers=HEADERS)
        return True
    except:
        return False

# --- ARAYÜZ BAŞLIYOR ---
st.title("❤️ Çiftler İçin Ders Takip")
st.markdown("Bu site **Mert** tarafından Python ile kodlanmıştır.")

# Yan Menü (Kullanıcı Seçimi)
kullanici = st.sidebar.selectbox("Kim Giriş Yapıyor?", ["Seçiniz...", "Mert", "Zübeyde"])

if kullanici != "Seçiniz...":
    # Verileri İnternetten Çek
    with st.spinner('Veriler Buluttan İndiriliyor...'):
        ana_veri = verileri_cek()
    
    # Veri yapısı yoksa oluştur
    if "Mert" not in ana_veri: ana_veri["Mert"] = {}
    if "Zübeyde" not in ana_veri: ana_veri["Zübeyde"] = {}

    benim_verilerim = ana_veri[kullanici]
    
    # Tarih Bilgisi
    bugun = datetime.date.today()
    yil, hafta_no, _ = bugun.isocalendar()
    suanki_hafta = f"{yil}-{hafta_no}. Hafta"

    st.header(f"👋 Hoş geldin {kullanici}!")
    st.info(f"📅 Şu anki dönem: **{suanki_hafta}**")

    # --- SEKME SİSTEMİ ---
    tab1, tab2, tab3 = st.tabs(["✍️ Ders Ekle", "📊 Karnem", "👀 Diğerinin Durumu"])

    # --- SEKME 1: VERİ GİRİŞİ ---
    with tab1:
        st.subheader("Bugün ne çalıştın?")
        with st.form("ders_formu", clear_on_submit=True):
            ders_adi = st.text_input("Ders Adı (Örn: Matematik)")
            sure = st.number_input("Süre (Saat)", min_value=0.5, max_value=24.0, step=0.5)
            
            gunler_listesi = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            secilen_gun = st.selectbox("Gün", gunler_listesi, index=bugun.weekday())
            
            buton = st.form_submit_button("Kaydet 💾")
            
            if buton and ders_adi:
                yeni_kayit = {
                    "ders": ders_adi,
                    "sure": sure,
                    "gun": secilen_gun,
                    "tarih": str(bugun)
                }
                
                if suanki_hafta not in benim_verilerim:
                    benim_verilerim[suanki_hafta] = []
                
                benim_verilerim[suanki_hafta].append(yeni_kayit)
                ana_veri[kullanici] = benim_verilerim
                
                with st.spinner("Kaydediliyor..."):
                    verileri_gonder(ana_veri) # Buluta yükle
                
                st.success(f"✅ {ders_adi} başarıyla kaydedildi!")
                st.rerun() # Sayfayı yenile

    # --- SEKME 2: KARNE (Tablo ve Grafikler) ---
    with tab2:
        st.subheader("📈 Senin Durumun")
        
        if suanki_hafta in benim_verilerim:
            df = pd.DataFrame(benim_verilerim[suanki_hafta])
            if not df.empty:
                toplam_saat = df["sure"].sum()
                st.metric(label="Bu Hafta Toplam", value=f"{toplam_saat} Saat")
                
                # 1. DERS GRAFİĞİ
                st.write("#### 📚 Derslere Göre Dağılım")
                ders_ozeti = df.groupby("ders")["sure"].sum()
                st.bar_chart(ders_ozeti)

                # 2. GÜN GRAFİĞİ (İŞTE BURASI YENİ!)
                st.write("#### 🗓️ Günlere Göre Dağılım")
                st.caption("Çalışılmayan günler 0 olarak görünür.")

                # Haftanın tüm günlerini içeren boş bir şablon oluştur
                tum_gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe",
