
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
        
        # Aday noktaları Z (yükseklik), sonra Y, sonra X'e göre sırala.
        # Bu, kutuları önce alta, sonra arkaya, sonra sola yaslamaya çalışır.
        self.noktalar.sort(key=lambda p: (p[2], p[1], p[0]))

        for x, y, z in self.noktalar:
            for w, d, h in oryantasyonlar:
                if not self.cakisma_var_mi(x, y, z, w, d, h):
                    # Yerleştirme başarılı
                    yeni_yerlesim = Yerlesim(urun, x, y, z, w, d, h)
                    self.yerlesimler.append(yeni_yerlesim)
                    
                    # Yeni aday noktaları ekle (Kutunun sağ üstü, sol üstü, önü vs.)
                    self.noktalar.append((x + w, y, z))
                    self.noktalar.append((x, y + d, z))
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
    
    # Miktarları dikkate alarak paketlenecek tüm kutuların listesini oluştur
    paketlenecek_kutular = []
    for urun in wms_emri:
        for _ in range(urun.miktar):
            paketlenecek_kutular.append(urun)

    # Ürünleri hacimlerine göre büyükten küçüğe sıralıyoruz.
    # Bu genellikle en verimli paketlemeyi sağlar.
    sirali_emir = sorted(paketlenecek_kutular, key=lambda x: x.hacim, reverse=True)
    
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
                u["urun_id"],
                u["en"],
                u["boy"],
                u["yukseklik"],
                u["miktar"]
            )
        )

    paletler = wms_simulasyon(
        urunler,
        palet_en,
        palet_boy,
        palet_yuk
    )

    sonuc = []
    toplam_kutu = 0
    tum_skular = set()

    for p in paletler:
        dolu_hacim = sum(y.w * y.d * y.h for y in p.yerlesimler)
        toplam_hacim = p.en * p.boy * p.yukseklik
        doluluk_orani = (dolu_hacim / toplam_hacim) * 100

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
    # Palet Boyutları (Örn: Sandık 750x1150, Yükseklik sınırı 910 cm)
    P_EN = 750
    P_BOY = 1150
    P_YUK = 910
    
    # --- ÖRNEK WMS EMRİ ---
    gelen_siparisler = [
        Urun("ASCVNT18KS", 378, 202, 114, 15),
        Urun("ASCBNC28CK", 284, 290, 124, 20),
        Urun("ASCGRM21DZ", 228, 228, 142, 5),
        Urun("ASCGRM30DZ", 316, 316, 106, 20)
       
    ]

    print(f"Simülasyon Başlatılıyor... (Palet: {P_EN}x{P_BOY}x{P_YUK})\n")
    
    sonuc_paletler = wms_simulasyon(gelen_siparisler, P_EN, P_BOY, P_YUK)

    toplam_kutu = sum(len(p.yerlesimler) for p in sonuc_paletler)
    tum_skular = set(y.urun.urun_id for p in sonuc_paletler for y in p.yerlesimler)

    print(f"--- SİMÜLASYON ÖZETİ ---")
    print(f"Toplam Palet: {len(sonuc_paletler)}")
    print(f"Toplam Kutu : {toplam_kutu}")
    print(f"Toplam SKU  : {len(tum_skular)}")
    print("=" * 40 + "\n")

    for p in sonuc_paletler:
        print(p)
        # SKU bazında gruplama ve sayım
        sku_ozet = {}
        for y in p.yerlesimler:
            sku_ozet[y.urun.urun_id] = sku_ozet.get(y.urun.urun_id, 0) + 1
        
        for sku, adet in sku_ozet.items():
            print(f"  -> SKU: {sku} | Adet: {adet}")
        print("-" * 30)

        
