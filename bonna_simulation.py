
class Urun:
    """WMS satırındaki bir ürün ve miktarını gösterir."""
    def __init__(self, urun_id, en, boy, yukseklik, miktar=1):
        self.urun_id = urun_id
        self.en = en
        self.boy = boy
        self.yukseklik = yukseklik
        self.miktar = miktar
        self.hacim = en * boy * yukseklik

    def __repr__(self):
        return f"Urun(ID: {self.urun_id}, Boyut: {self.en}x{self.boy}x{self.yukseklik}, Hacim: {self.hacim}, Adet: {self.miktar})"

class Yerlesim:
    """Paletteki bir ürünün konumunu ve oryantasyonunu gösterir."""
    def __init__(self, urun, x, y, z, w, d, h):
        self.urun = urun
        self.x = x
        self.y = y
        self.z = z
        self.w = w
        self.d = d
        self.h = h

    def __repr__(self):
        return f"📦 {self.urun.urun_id} -> Konum: (x:{self.x}, y:{self.y}, z:{self.z}) | Boyut: {self.w}x{self.d}x{self.h}"

class Palet:
    """3D Yerleştirme mantığına sahip Palet sınıfı ."""
    def __init__(self, palet_id, en, boy, yukseklik):
        self.palet_id = palet_id
        self.en = en
        self.boy = boy
        self.yukseklik = yukseklik
        self.yerlesimler = []
        # Yerleştirme için koordinatlar (x, y, z). Başlangıçta sadece (0,0,0) var.
        self.noktalar = [(0, 0, 0)]

    def cakisma_var_mi(self, x, y, z, w, d, h):
        """Verilen koordinat ve boyutlarda çakışma veya taşma kontrolü."""
        # 1. Palet sınırları kontrolü
        if x + w > self.en or y + d > self.boy or z + h > self.yukseklik:
            return True
        
        # 2. Diğer kutularla çakışma kontrolü
        for p in self.yerlesimler:
            if (x < p.x + p.w and x + w > p.x and
                y < p.y + p.d and y + d > p.y and
                z < p.z + p.h and z + h > p.z):
                return True
        return False

    def ekle(self, urun):
        """Ürünü en uygun yere yerleştirmeye çalışır (3D Bin Packing)."""
        # Hacim kontrolü: Eğer ürün eklendiğinde %100 doluluk geçiliyorsa direkt reddet
        mevcut_hacim = sum(y.w * y.d * y.h for y in self.yerlesimler)
        if mevcut_hacim + urun.hacim > (self.en * self.boy * self.yukseklik):
            return False

        # Ürünün 6 farklı döndürme ihtimali (W, D, H permütasyonları)
        oryantasyonlar = list(set([
            (urun.en, urun.boy, urun.yukseklik),
            (urun.en, urun.yukseklik, urun.boy),
            (urun.boy, urun.en, urun.yukseklik),
            (urun.boy, urun.yukseklik, urun.en),
            (urun.yukseklik, urun.en, urun.boy),
            (urun.yukseklik, urun.boy, urun.en)
        ]))
        
        # Akıllı Sıralama: Paletin uzun kenarına, kutunun uzun kenarını denk getirmeye çalış.
        if self.en > self.boy:
            # Paletin eni daha geniş, kutunun enini(w) maksimize edenleri önce dene
            oryantasyonlar.sort(key=lambda x: x[0], reverse=True)
        else:
            # Paletin boyu daha uzun (1150 > 750), kutunun boyunu(d) maksimize edenleri önce dene
            oryantasyonlar.sort(key=lambda x: x[1], reverse=True)
        
        # Aday noktaları Z (yükseklik), sonra Y, sonra X'e göre sırala.
        # Bu, kutuları önce alta, sonra arkaya, sonra sola yaslamaya çalışır.
        self.noktalar.sort(key=lambda p: (p[2], p[1], p[0]))

        # Best Fit Stratejisi:
        # İlk bulduğumuz yere koymak yerine (First Fit), tüm olası nokta ve oryantasyonları deneyip
        # en iyi skoru vereni seçiyoruz.
        en_iyi_yerlesim = None
        # Skor: (Z, Y, X) -> Küçük olması iyidir.
        en_iyi_skor = (float('inf'), float('inf'), float('inf'))

        for x, y, z in self.noktalar:
            # Eğer bu noktanın Z'si bile mevcut en iyi Z'den büyükse, bu noktayı ve sonrakileri atla (Sorted olduğu için)
            if z > en_iyi_skor[0]:
                break
                
            for w, d, h in oryantasyonlar:
                if not self.cakisma_var_mi(x, y, z, w, d, h):
                    # Geçerli bir yerleşim bulundu. Skorunu hesapla.
                    # Öncelik: En alt (Z), En arka (Y), En sol (X)
                    skor = (z, y, x)
                    
                    if skor < en_iyi_skor:
                        en_iyi_skor = skor
                        en_iyi_yerlesim = (x, y, z, w, d, h)
        
        if en_iyi_yerlesim:
            x, y, z, w, d, h = en_iyi_yerlesim
            yeni_yerlesim = Yerlesim(urun, x, y, z, w, d, h)
            self.yerlesimler.append(yeni_yerlesim)
            
            # Yeni aday noktaları ekle (Sınır kontrolü ile gereksiz noktaları ele)
            if x + w < self.en:
                self.noktalar.append((x + w, y, z))
            if y + d < self.boy:
                self.noktalar.append((x, y + d, z))
            if z + h < self.yukseklik:
                self.noktalar.append((x, y, z + h))
            
            # Kullanılan noktayı listeden çıkar
            if (x, y, z) in self.noktalar:
                self.noktalar.remove((x, y, z))
            return True
            
        return False

    def __repr__(self):
        dolu_hacim = sum(y.w * y.d * y.h for y in self.yerlesimler)
        toplam_hacim = self.en * self.boy * self.yukseklik
        doluluk_orani = (dolu_hacim / toplam_hacim) * 100
        sku_sayisi = len(set(y.urun.urun_id for y in self.yerlesimler))
        return f"Palet #{self.palet_id} -> Doluluk: %{doluluk_orani:.2f} | SKU Sayısı: {sku_sayisi} | Kutu Sayısı: {len(self.yerlesimler)}"

def wms_simulasyon(wms_emri, palet_en, palet_boy, palet_yukseklik):
    """
    Verilen sipariş listesini paletlere simüle eder.
    Algoritma: First Fit Decreasing (Büyükten küçüğe sıralayıp ilk uygun yere koyma)
    """
    paletler = []
    palet_sayaci = 1
    
    # --- Gelişmiş Sıralama (Rules: IsGroupUsed=True, IsUnitloadFirst=True) ---
    # 1. Ürünleri SKU'larına göre grupla
    sku_gruplari = {}
    for urun in wms_emri:
        if urun.urun_id not in sku_gruplari:
            sku_gruplari[urun.urun_id] = []
        sku_gruplari[urun.urun_id].append(urun)
    
    # 2. Grupları TEKİL ÜRÜN HACMİNE göre sırala.
    # CubeMaster benzeri yüksek doluluk için: Fiziksel olarak büyük/kaba kutuları içeren gruplar
    # önce yerleştirilmeli, küçük kutular aralara dolgu yapmalıdır.
    sirali_gruplar = sorted(sku_gruplari.values(), key=lambda g: g[0].hacim, reverse=True)
    
    # 3. Listeyi düzleştir (Flatten)
    sirali_emir = []
    for grup in sirali_gruplar:
        # Grup içindeki ürünleri de kendi içinde büyükten küçüğe sırala (Best Fit için)
        for urun in sorted(grup, key=lambda x: x.hacim, reverse=True):
            for _ in range(urun.miktar):
                sirali_emir.append(urun)
    
    for urun in sirali_emir:
        yerlestirildi = False
        
        # Mevcut paletleri kontrol et
        for palet in paletler:
            if palet.ekle(urun):
                yerlestirildi = True
                break
        
        # Eğer hiçbir mevcut palete sığmadıysa yeni palet aç
        if not yerlestirildi:
            yeni_palet = Palet(palet_id=palet_sayaci, en=palet_en, boy=palet_boy, yukseklik=palet_yukseklik)
            if yeni_palet.ekle(urun):
                paletler.append(yeni_palet)
                palet_sayaci += 1
            else:
                print(f"UYARI: {urun} palet boyutlarından veya kapasitesinden büyük olduğu için eklenemedi!")

    return paletler


def api_calistir(wms_emri_json, palet_en, palet_boy, palet_yuk):
    urunler = []

    for u in wms_emri_json:
        urunler.append(
            Urun(
                str(u["urun_id"]),
                int(u["en"]),
                int(u["boy"]),
                int(u["yukseklik"]),
                int(u["miktar"])
            )
        )

    # 🧱 Simülasyonu çalıştır
    paletler = wms_simulasyon(
        urunler,
        int(palet_en),
        int(palet_boy),
        int(palet_yuk)
    )

    sonuc = []
    toplam_kutu = 0
    tum_skular = set()

    for p in paletler:
        # Doluluk oranı hesaplaması (hacim bazlı)
        dolu_hacim = sum(y.w * y.d * y.h for y in p.yerlesimler)
        toplam_hacim = p.en * p.boy * p.yukseklik
        doluluk_orani = (dolu_hacim / toplam_hacim) * 100

        # SKU bazlı özet
        sku_ozet = {}
        for y in p.yerlesimler:
            sku_ozet[y.urun.urun_id] = sku_ozet.get(y.urun.urun_id, 0) + 1
            tum_skular.add(y.urun.urun_id)

        toplam_kutu += len(p.yerlesimler)

        sonuc.append({
            "palet_id": p.palet_id,
            "doluluk_orani": round(doluluk_orani, 2),
            "sku_sayisi": len(sku_ozet),
            "kutu_sayisi": len(p.yerlesimler),
            "sku_detay": [{"sku": k, "adet": v} for k, v in sku_ozet.items()]
        })

    return {
        "toplam_palet": len(paletler),
        "toplam_kutu": toplam_kutu,
        "toplam_sku": len(tum_skular),
        "paletler": sonuc
    }

if __name__ == "__main__":
    # --- AYARLAR ---
    P_EN = 750
    P_BOY = 1150
    P_YUK = 910
    
    # --- ÖRNEK WMS EMRİ ---
    gelen_siparisler = [
        Urun("ADFRPL18JO", 188, 386, 175, 10),
        Urun("ADFTON10KS", 110, 221, 106, 10),
        Urun("ADFTON36OV", 326, 326, 96, 20),
        Urun("AGR16KS", 200, 380, 150, 7),
        Urun("AGR19KS", 200, 380, 150, 30),
        Urun("AGR25KS", 265, 266, 164, 20),
        Urun("BNC01DM", 340, 464, 130, 10),
        Urun("BNC02ST", 274, 402, 72, 3),
        Urun("BNC03SO", 274, 402, 72, 3),
        Urun("BNC04KHD", 281, 282, 141, 4)
    ]

    print(f"Simülasyon Başlatılıyor... (Palet: {P_EN}x{P_BOY}x{P_YUK})\n")
    
    # API fonksiyonunu test etmek için veriyi JSON formatına çevirelim
    wms_json = [
        {"urun_id": u.urun_id, "en": u.en, "boy": u.boy, "yukseklik": u.yukseklik, "miktar": u.miktar}
        for u in gelen_siparisler
    ]
    
    api_sonuc = api_calistir(wms_json, P_EN, P_BOY, P_YUK)

    print(f"--- SİMÜLASYON ÖZETİ ---")
    print(f"Toplam Palet: {api_sonuc['toplam_palet']}")
    print(f"Toplam Kutu : {api_sonuc['toplam_kutu']}")
    print(f"Toplam SKU  : {api_sonuc['toplam_sku']}")
    print("=" * 40 + "\n")

    for p in api_sonuc['paletler']:
        print(f"Palet #{p['palet_id']} -> Doluluk: %{p['doluluk_orani']} | SKU Sayısı: {p['sku_sayisi']} | Kutu Sayısı: {p['kutu_sayisi']}")
        for detay in p['sku_detay']:
            print(f"  -> SKU: {detay['sku']} | Adet: {detay['adet']}")
        print("-" * 30)

        

        #python -m uvicorn main:app --reload

        
