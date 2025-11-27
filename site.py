import streamlit as st
import requests
import datetime
import pandas as pd
import time
from streamlit_autorefresh import st_autorefresh

# --- SAYFA AYARLARI ---
st.set_page_config(page_title="Mert & Zübeyde Ders Takip", page_icon="📚", layout="centered")

# --- SENİN ŞİFRELERİN ---
BIN_ID = "691f3259d0ea881f40f4bd1b"
API_KEY = "$2a$10$ln7I9iGthRnAvR06HPE3g.USj5Li/vCQiH/XNKYpfjLb67jHguweW"
URL = f"https://api.jsonbin.io/v3/b/{BIN_ID}"
HEADERS = {"X-Master-Key": API_KEY, "Content-Type": "application/json"}

# --- SAYAÇ BAŞLANGIÇ AYARLARI ---
if 'kronometre_baslangic' not in st.session_state:
    st.session_state.kronometre_baslangic = None
if 'gecen_sure' not in st.session_state:
    st.session_state.gecen_sure = 0.0

# --- FONKSİYONLAR ---
def verileri_cek():
    try:
        response = requests.get(URL, headers=HEADERS)
        if response.status_code == 200:
            return response.json()['record']
        else:
            return {}
    except:
        return {}

def verileri_gonder(veri):
    try:
        requests.put(URL, json=veri, headers=HEADERS)
        return True
    except:
        return False

# --- ARAYÜZ ---
st.title("📚 AGS İçin Ders Takip")
st.markdown("Bu site **Mert** tarafından Python ile kodlanmıştır.")

kullanici = st.sidebar.selectbox("Kim Giriş Yapıyor?", ["Seçiniz...", "Mert", "Zübeyde"])

if kullanici != "Seçiniz...":
    # Verileri İndir
    with st.spinner('Veriler Yükleniyor...'):
        ana_veri = verileri_cek()
    
    # Hata önleyici kontroller
    if not isinstance(ana_veri, dict): ana_veri = {}
    if "Mert" not in ana_veri: ana_veri["Mert"] = {}
    if "Zübeyde" not in ana_veri: ana_veri["Zübeyde"] = {}

    benim_verilerim = ana_veri.get(kullanici, {})
    
    bugun = datetime.date.today()
    yil, hafta_no, _ = bugun.isocalendar()
    suanki_hafta = f"{yil}-{hafta_no}. Hafta"

    st.header(f"👋 Hoş geldin {kullanici}!")
    
    # --- SEKME SİSTEMİ ---
    tab1, tab2, tab3, tab4 = st.tabs(["✍️ Ders Ekle", "📊 Karnem", "👀 Diğerinin Durumu", "⏱️ CANLI SAYAÇ"])

    # --- SEKME 1: VERİ GİRİŞİ ---
    with tab1:
        st.info(f"📅 Şu anki dönem: **{suanki_hafta}**")
        st.subheader("Bugün ne çalıştın?")
        with st.form("ders_formu", clear_on_submit=True):
            ders_adi = st.text_input("Ders Adı (Örn: Matematik)")
            
            # Sayaçtan gelen süre varsa onu varsayılan yap
            # URL parametresi veya Session State kontrolü
            url_params = st.query_params
            kayitli_sure = float(url_params.get("kayitli_sure", 0.0))
            
            if kayitli_sure > 0:
                varsayilan = kayitli_sure
            elif st.session_state.gecen_sure > 0:
                varsayilan = st.session_state.gecen_sure
            else:
                varsayilan = 0.5

            sure = st.number_input("Süre (Saat)", min_value=0.1, max_value=24.0, step=0.1, value=float(varsayilan))
            
            gunler_listesi = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
            secilen_gun = st.selectbox("Gün", gunler_listesi, index=bugun.weekday())
            
            buton = st.form_submit_button("Kaydet 💾")
            
            if buton and ders_adi:
                yeni_kayit = {
                    "ders": ders_adi, "sure": sure, "gun": secilen_gun, "tarih": str(bugun)
                }
                
                if suanki_hafta not in benim_verilerim:
                    benim_verilerim[suanki_hafta] = []
                
                benim_verilerim[suanki_hafta].append(yeni_kayit)
                ana_veri[kullanici] = benim_verilerim
                
                verileri_gonder(ana_veri)
                
                # Temizlik
                st.session_state.gecen_sure = 0.0
                if "kayitli_sure" in st.query_params:
                    del st.query_params["kayitli_sure"]
                
                st.success(f"✅ {ders_adi} başarıyla kaydedildi!")
                time.sleep(1)
                st.rerun()

    # --- SEKME 2: KARNE (GEÇMİŞ HAFTALAR DAHİL) ---
    with tab2:
        st.subheader("📈 Performans Analizi")
        
        kayitli_haftalar = list(benim_verilerim.keys())
        kayitli_haftalar.sort(reverse=True)
        
        if not kayitli_haftalar:
            kayitli_haftalar = [suanki_hafta]
        elif suanki_hafta not in kayitli_haftalar:
            kayitli_haftalar.insert(0, suanki_hafta)
            
        secilen_hafta = st.selectbox("Hangi Haftayı İncelemek İstersin?", kayitli_haftalar)
        
        st.markdown(f"### 🗓️ {secilen_hafta} Raporu")

        if secilen_hafta in benim_verilerim:
            df = pd.DataFrame(benim_verilerim[secilen_hafta])
            if not df.empty:
                toplam_saat = df["sure"].sum()
                st.metric(label=f"{secilen_hafta} Toplamı", value=f"{toplam_saat:.1f} Saat")
                
                st.write("#### 📚 Ders Dağılımı")
                st.bar_chart(df.groupby("ders")["sure"].sum())

                st.write("#### 🗓️ Gün Dağılımı")
                tum_gunler = ["Pazartesi", "Salı", "Çarşamba", "Perşembe", "Cuma", "Cumartesi", "Pazar"]
                gun_sablonu = pd.DataFrame({"gun": tum_gunler, "bos_sure": 0.0})
                senin_gunlerin = df.groupby("gun")["sure"].sum().reset_index()
                sonuc_tablosu = pd.merge(gun_sablonu, senin_gunlerin, on="gun", how="left")
                sonuc_tablosu["sure"] = sonuc_tablosu["sure"].fillna(0)
                sonuc_tablosu["gun"] = pd.Categorical(sonuc_tablosu["gun"], categories=tum_gunler, ordered=True)
                sonuc_tablosu = sonuc_tablosu.sort_values("gun")
                
                st.bar_chart(sonuc_tablosu.set_index("gun")["sure"])
                
                with st.expander("Detaylı Liste"):
                    st.dataframe(df[["gun", "ders", "sure"]])
            else:
                st.warning("Bu haftada veri girişi yok.")
        else:
            st.warning("Bu hafta için henüz veri girmemişsin.")

    # --- SEKME 3: DİĞERİ ---
    with tab3:
        digeri = "Zübeyde" if kullanici == "Mert" else "Mert"
        st.subheader(f"🕵️ {digeri} Ne Yapmış?")
        
        diger_veri = ana_veri.get(digeri, {})
        diger_haftalar = list(diger_veri.keys())
        diger_haftalar.sort(reverse=True)
        if not diger_haftalar: diger_haftalar = [suanki_hafta]
        
        secilen_hafta_diger = st.selectbox(f"{digeri} - Hangi Hafta?", diger_haftalar, key="diger_select")

        if secilen_hafta_diger in diger_veri:
             df_diger = pd.DataFrame(diger_veri[secilen_hafta_diger])
             if not df_diger.empty:
                 d_toplam = df_diger["sure"].sum()
                 st.metric(label=f"{digeri} Toplam ({secilen_hafta_diger})", value=f"{d_toplam:.1f} Saat")
                 st.bar_chart(df_diger.groupby("ders")["sure"].sum())
                 st.dataframe(df_diger[["gun", "ders", "sure"]])
             else:
                 st.info(f"{digeri} bu hafta yatışta... 😴")
        else:
            st.info(f"{digeri} henüz veri girmemiş.")

    # --- SEKME 4: CANLI AKAN SAYAÇ ---
    with tab4:
        st.subheader("⏱️ Canlı Çalışma Sayacı")
        
        # URL'den başlangıç zamanını kontrol et (Ölümsüzlük Modu)
        url_params = st.query_params
        baslangic_zamani_str = url_params.get("baslangic_zamani", None)

        if baslangic_zamani_str is None:
            # Sayaç kapalı
            st.info("Hazır olduğunda başlat.")
            if st.button("▶️ BAŞLAT", type="primary", use_container_width=True):
                simdi_ts = str(datetime.datetime.now().timestamp())
                st.query_params["baslangic_zamani"] = simdi_ts
                st.rerun()
        else:
            # Sayaç açık -> Kalp pili çalışsın (Saniyede 1 yenile)
            st_autorefresh(interval=1000, key="sayac_yenileme")

            try:
                baslangic_ts = float(baslangic_zamani_str)
                baslangic_dt = datetime.datetime.fromtimestamp(baslangic_ts)
                
                simdi = datetime.datetime.now()
                fark = simdi - baslangic_dt
                
                toplam_saniye = int(fark.total_seconds())
                saat = toplam_saniye // 3600
                dakika = (toplam_saniye % 3600) // 60
                saniye = toplam_saniye % 60
                
                zaman_yazisi = f"{saat:02d}:{dakika:02d}:{saniye:02d}"
                
                # SAYAÇ GÖRÜNTÜSÜ
                st.markdown(f"<h1 style='text-align: center; color: #FF4B4B; font-size: 80px; font-family: monospace;'>{zaman_yazisi}</h1>", unsafe_allow_html=True)
                st.success(f"Başlangıç: {baslangic_dt.strftime('%H:%M:%S')}")

                if st.button("⏹️ DURDUR VE KAYDET", type="secondary", use_container_width=True):
                    hesaplanan_sure = round(fark.total_seconds() / 3600, 2)
                    
                    if "baslangic_zamani" in st.query_params:
                        del st.query_params["baslangic_zamani"]
                    
                    st.query_params["kayitli_sure"] = str(hesaplanan_sure)
                    
                    st.balloons()
                    st.success(f"Süper! {hesaplanan_sure} saat çalıştın.")
                    st.info("👈 Şimdi 'Ders Ekle' sekmesine git, süre oraya otomatik geldi.")
                    time.sleep(2)
                    st.rerun()
            except:
                st.error("Sayaç verisi bozuldu, sıfırlanıyor...")
                if "baslangic_zamani" in st.query_params:
                    del st.query_params["baslangic_zamani"]
                st.rerun()

else:
    st.warning("👈 Lütfen soldaki menüden ismini seç.")
