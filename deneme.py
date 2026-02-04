class Urun:
    """Depodaki tek bir ürünü temsil eder."""
    def __init__(self, urun_id, en, boy, yukseklik):
        self.urun_id = urun_id
        self.en = en
        self.boy = boy
        self.yukseklik = yukseklik
        self.hacim = en * boy * yukseklik

    def __repr__(self):
        return f"Urun(ID: {self.urun_id}, Boyut: {self.en}x{self.boy}x{self.yukseklik}, Hacim: {self.hacim})"

class Palet:
    """Ürünlerin yerleştirildiği paleti temsil eder."""
    def __init__(self, palet_id, en, boy, yukseklik):
        self.palet_id = palet_id
        self.en = en
        self.boy = boy
        self.yukseklik = yukseklik
        self.max_hacim = en * boy * yukseklik
        self.mevcut_hacim = 0
        self.urunler = []

    def ekle(self, urun):
        """Eğer yer varsa ve boyutlar uygunsa ürünü palete ekler."""
        # 1. Hacim kontrolü
        if self.mevcut_hacim + urun.hacim > self.max_hacim:
            return False

        # 2. Boyut kontrolü (Döndürme ihtimali dahil)
        # Ürünün boyutlarını ve paletin boyutlarını sıralayıp karşılaştırıyoruz.
        urun_dims = sorted([urun.en, urun.boy, urun.yukseklik])
        palet_dims = sorted([self.en, self.boy, self.yukseklik])
        
        if any(u > p for u, p in zip(urun_dims, palet_dims)):
            return False

        self.urunler.append(urun)
        self.mevcut_hacim += urun.hacim
        return True

    def __repr__(self):
        doluluk_orani = (self.mevcut_hacim / self.max_hacim) * 100
        return f"Palet #{self.palet_id} [Doluluk: %{doluluk_orani:.1f} - {self.mevcut_hacim}/{self.max_hacim}]"

def wms_simulasyon(wms_emri, palet_en, palet_boy, palet_yukseklik):
    """
    Verilen sipariş listesini paletlere simüle eder.
    Algoritma: First Fit Decreasing (Büyükten küçüğe sıralayıp ilk uygun yere koyma)
    """
    paletler = []
    palet_sayaci = 1
    
    # Ürünleri hacimlerine göre büyükten küçüğe sıralıyoruz.
    # Bu genellikle en verimli paketlemeyi sağlar.
    sirali_emir = sorted(wms_emri, key=lambda x: x.hacim, reverse=True)
    
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

if __name__ == "__main__":
    # --- AYARLAR ---
    # Palet Boyutları (Örn: Euro Palet 80x120, Yükseklik sınırı 150 cm)
    P_EN = 80
    P_BOY = 120
    P_YUK = 150
    
    # --- ÖRNEK WMS EMRİ ---
    gelen_siparisler = [
        Urun("Kutu-A", 30, 40, 50),
        Urun("Kutu-B", 50, 60, 40),
        Urun("Kutu-C", 40, 40, 40),
        Urun("Kutu-D", 20, 20, 20),
        Urun("Kutu-E", 60, 80, 50),
        Urun("Kutu-F", 10, 10, 10),
        Urun("Kutu-G", 35, 35, 35),
        Urun("Dev-Kutu", 200, 200, 200), # Bu sığmamalı
    ]

    print(f"Simülasyon Başlatılıyor... (Palet: {P_EN}x{P_BOY}x{P_YUK})\n")
    
    sonuc_paletler = wms_simulasyon(gelen_siparisler, P_EN, P_BOY, P_YUK)

    print(f"Toplam {len(sonuc_paletler)} adet palet oluşturuldu:\n")
    for p in sonuc_paletler:
        print(p)
        for u in p.urunler:
            print(f"  └── {u}")
        print("-" * 30)
