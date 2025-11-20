import streamlit as st
import requests
import datetime
import pandas as pd

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Mert & Yenge Ders Takip", page_icon="📚", layout="centered")

# --- API BİLGİLERİ (BURALARI DOLDUR) ---
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
    except:
        return {}
    return {}

def verileri_gonder(veri):
    requests.put(URL, json=veri, headers=HEADERS)

# --- ARAYÜZ BAŞLIYOR ---
st.title("❤️ Çiftler İçin Ders Takip")
st.markdown("Bu site **Mert** tarafından Python ile kodlanmıştır. 😎")

# Yan Menü (Kullanıcı Seçimi)
kullanici = st.sidebar.selectbox("Kim Giriş Yapıyor?", ["Seçiniz...", "Mert", "Yenge"])

if kullanici != "Seçiniz...":
    # Verileri İnternetten Çek
    with st.spinner('Veriler Buluttan İndiriliyor...'):
        ana_veri = verileri_cek()
    
    # Veri yapısı yoksa oluştur
    if "Mert" not in ana_veri: ana_veri["Mert"] = {}
    if "Yenge" not in ana_veri: ana_veri["Yenge"] = {}

    benim_verilerim = ana_veri[kullanici]
    
    # Tarih Bilgisi
    bugun = datetime.date.today()
    yil, hafta_no, _ = bugun.isocalendar()
    suanki_hafta = f"{yil}-{hafta_no}. Hafta"

    st.header(f"👋 Hoş geldin {kullanici}!")
    st.info(f"📅 Şu anki dönem: **{suanki_hafta}**")

    # --- SEKME 1: VERİ GİRİŞİ ---
    tab1, tab2, tab3 = st.tabs(["✍️ Ders Ekle", "📊 Karnem", "👀 Diğerinin Durumu"])

    with tab1:
        st.subheader("Bugün ne çalıştın?")
        with st.form("ders_formu"):
            ders_adi = st.text_input("Ders Adı (Örn: Matematik)")
            sure = st.number_input("Süre (Saat)", min_value=0.5, max_value=24.0, step=0.5)
            gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            secilen_gun = st.selectbox("Gün", gunler, index=bugun.weekday())
            
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
                
                verileri_gonder(ana_veri) # Buluta yükle
                st.success(f"✅ {ders_adi} başarıyla kaydedildi!")
                st.rerun() # Sayfayı yenile

    # --- SEKME 2: KARNE (Tablo ve Grafik) ---
    with tab2:
        st.subheader("📈 Senin Durumun")
        
        if suanki_hafta in benim_verilerim:
            df = pd.DataFrame(benim_verilerim[suanki_hafta])
            if not df.empty:
                toplam_saat = df["sure"].sum()
                st.metric(label="Bu Hafta Toplam", value=f"{toplam_saat} Saat")
                
                # Tabloyu göster
                st.dataframe(df[["gun", "ders", "sure"]])
                
                # Grafik Çiz (Bar Chart)
                ders_ozeti = df.groupby("ders")["sure"].sum()
                st.bar_chart(ders_ozeti)
            else:
                st.warning("Bu hafta veri yok.")
        else:
            st.warning("Henüz veri girişi yapmadın.")

    # --- SEKME 3: DİĞERİNİ GÖR ---
    with tab3:
        digeri = "Yenge" if kullanici == "Mert" else "Mert"
        st.subheader(f"🕵️ {digeri} Ne Yapmış?")
        
        diger_veri = ana_veri[digeri]
        if suanki_hafta in diger_veri:
             df_diger = pd.DataFrame(diger_veri[suanki_hafta])
             if not df_diger.empty:
                 d_toplam = df_diger["sure"].sum()
                 st.metric(label=f"{digeri} Toplam", value=f"{d_toplam} Saat")
                 st.dataframe(df_diger[["gun", "ders", "sure"]])
             else:
                 st.info(f"{digeri} bu hafta yatışta... 😴")
        else:
            st.info(f"{digeri} henüz veri girmemiş.")

else:
    st.warning("👈 Lütfen soldaki menüden ismini seç.")

