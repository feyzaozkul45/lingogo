# LingoGo — PROJECT.md

> **LingoGo:** Gerçek hayatta kullanılan İngilizceyi, günlük durumlar üzerinden basit ve eğlenceli şekilde öğreten web uygulaması.

Bu dosya, projeyi Claude Code ile geliştirirken **tek referans kaynağıdır**. Her geliştirme adımından önce bu dosya okunmalı ve buradaki kurallara uyulmalıdır.

---

## 1. Projenin Amacı

LingoGo, İngilizce öğrenmek isteyen kullanıcılara **kafede, restoranda, havaalanında, otelde** gibi günlük durumlarda ihtiyaç duyacakları İngilizceyi öğretir.

Amaç kelime ezberletmek ya da sadece test çözdürmek değildir. Her ders şu mantıkla ilerler:

```
Öğren  →  Gör  →  Pratik yap  →  Gerçek durumda kullan
```

**Önceliğimiz:** Basit + çalışan + öğretici + güzel görünen + sonradan geliştirilebilir bir prototip.

Büyük bir eğitim platformu **yapılmayacak**. Önce küçük bir sistem kurulacak, çalıştığı görülecek, sonra özellik eklenecek.

---

## 2. Hedef Kullanıcı

- İngilizceyi günlük hayatta kullanmak isteyen, Türkçe konuşan gençler ve yetişkinler
- A1–A2 seviyesinde başlayan, kısa ve pratik dersler isteyen kullanıcılar
- Uygulamanın arayüz dili **Türkçe**, öğretilen içerik **İngilizce + Türkçe açıklama**

---

## 3. Bir Dersin Yapısı

Her konunun (ör. 🍔 Restoranda) bir dersi vardır. Ders şu bölümlerden oluşur:

| # | Bölüm | İçerik | Faz |
|---|-------|--------|-----|
| 1 | **Kelimeler** | 8–10 temel kelime, Türkçe anlamı ve örnek cümle | Phase 1 |
| 2 | **Günlük İfadeler** | 5–6 gerçek hayatta kullanılan kalıp cümle | Phase 1 |
| 3 | **Grammar İpucu** | Tek bir kısa kalıp (ör. *I'd like...*), 2–3 cümlelik açıklama + örnek | Phase 1 |
| 4 | **Örnek Cümleler** | 4–5 cümle, Türkçe karşılığıyla | Phase 1 |
| 5 | **Quiz** | 5–6 soruluk kısa quiz | Phase 1 |
| 6 | **Gerçek Hayat Senaryosu** | Cevap seçmeli kısa diyalog (4–6 adım) | Phase 2 |
| 7 | **Küçük Görev** | Dersi gerçek hayata taşıyan tek cümlelik görev | Phase 2 |

Grammar bölümü **uzun ders değildir**. Bir kalıp, kısa bir açıklama, birkaç örnek. Bir derste grammar gerekmiyorsa bu bölüm gösterilmez.

---

## 4. Temel Özellikler

### 4.1 Ana Sayfa
- **Günün konusu:** Tarihe göre otomatik seçilir (veritabanında ayrı kayıt tutulmaz).
- **Öğrenmeye devam et:** Giriş yapmış kullanıcı için tamamlanmamış ilk ders. Giriş yapılmamışsa ilk ders önerilir.
- **Günlük kelimeler:** Tarihe göre seçilen 5 kelime.
- **Konular:** Renkli konu kartları.
- **Gerçek hayat senaryoları:** Phase 2'de senaryosu olan derslere kısa yol. Phase 1'de "Yakında" kartı olarak gösterilebilir.

> Günün konusu/kelimeleri: `date.today().toordinal() % toplam_sayı` gibi basit ve deterministik bir yöntemle seçilir.

### 4.2 Konular
- Tüm aktif konular kart olarak listelenir (emoji + başlık + seviye rozeti).
- Seviyeye göre basit filtre: `Tümü / A1 / A2 / B1 / B2`.
- Giriş yapmış kullanıcı için tamamlanan konular ✓ ile işaretlenir.

### 4.3 Ders Sayfası
- Bölümler tek sayfada, adım adım (sekme/stepper) gösterilir.
- "İleri / Geri" butonları ile bölümler arasında geçilir (vanilla JS).
- JavaScript kapalıysa bölümler alt alta görünür (progressive enhancement).
- Son adımda "Quiz'e başla" butonu vardır.

### 4.4 Quiz
Tüm soru tipleri **çoktan seçmeli yapıda** saklanır. Bu sayede tek bir model ve tek bir değerlendirme mantığı yeterlidir:

| Soru tipi | Örnek |
|-----------|-------|
| `multiple_choice` | "Garsondan hesabı nasıl istersin?" |
| `meaning` | "*waiter* ne demek?" |
| `fill_blank` | "I'd ___ a coffee, please." → like / want / have |
| `correct_sentence` | Doğru cümleyi seç |

- Cevaplar sunucuda (Django) değerlendirilir.
- Sonuç sayfasında puan, doğru/yanlış cevaplar ve kısa açıklamalar gösterilir.
- Giriş yapmamış kullanıcı quiz çözebilir ama sonuç kaydedilmez; "İlerlemeni kaydetmek için kayıt ol" mesajı gösterilir.

### 4.5 Gerçek Hayat Senaryosu (Phase 2)
Uygulamanın öne çıkan özelliğidir.

```
Garson:   Hello! Are you ready to order?
Sen:      ( ) Yes, I'd like a chicken sandwich.   ✓
          ( ) I am a sandwich.                     ✗
          ( ) The bill, please.                    ✗
Garson:   Great choice! Anything to drink?
...
```

- Diyalog doğrusal ilerler (dallanma yok).
- Her adımda 2–3 cevap seçeneği vardır.
- Yanlış seçimde kısa Türkçe geri bildirim verilir, kullanıcı tekrar dener.
- Doğru seçimde konuşma bir sonraki adıma geçer.
- Senaryo tek sayfada, vanilla JS ile oynatılır. Bittiğinde sonuç sunucuya POST edilir.

### 4.6 Kullanıcı Sistemi
- Django'nun yerleşik `User` modeli ve auth sistemi kullanılır.
- Kayıt: kullanıcı adı, e-posta, şifre (e-posta benzersiz olmalı).
- Giriş: kullanıcı adı **veya e-posta** + şifre (alan etiketi "Kullanıcı adı veya e-posta"). E-posta, yalnızca tek bir hesapla eşleşiyorsa ve aynı yazımda bir kullanıcı adı yoksa kullanıcı adına çevrilir; belirsiz e-postayla giriş yapılmaz.
- Hesap **zorunlu değildir**; dersler hesapsız da açılabilir.
- Phase 1'de e-posta doğrulama ve şifre sıfırlama **yoktur**.

### 4.7 İlerleme
Profil/ilerleme sayfasında basit istatistikler:

```
5 ders tamamlandı
32 kelime öğrenildi
4 quiz tamamlandı
```

- **Ders tamamlandı:** Kullanıcı dersin quiz'ini bitirdiğinde (puan fark etmeksizin) ders tamamlanmış sayılır. Phase 2'de kural "quiz + senaryo" olarak güncellenir.
- **Öğrenilen kelime:** Tamamlanan derslerdeki kelimelerin toplamı (ayrı tablo tutulmaz).
- **Quiz sayısı:** Kullanıcının çözdüğü farklı quiz sayısı + son puanlar.

XP, rozet, seri (streak), leaderboard **Phase 1 ve 2'de yoktur**.

### 4.8 Sesli Dinleme (Phase 2) — tamamlandı
- Ders sayfasında kelime, ifade, örnek cümle ve grammar örneklerinin yanında 🔊 (normal hız) ve 🐢 (yavaş, rate 0.6) butonları bulunur.
- Tıklanınca tarayıcının yerleşik **Web Speech API**'si (`SpeechSynthesisUtterance`, `lang="en-US"`) ile İngilizce metin sesli okunur.
- Ek kütüphane veya ses dosyası **yok**; `static/js/speech.js` sadece `window.speechSynthesis` mevcutsa `<html>` etiketine `tts-supported` sınıfı ekler, butonlar CSS ile varsayılan gizli (`display:none`) olduğu için desteklenmeyen tarayıcılarda hiç görünmez.
- Ortak buton çifti `templates/partials/speak_buttons.html` include'u ile tekrar kullanılıyor (Phase 2.5 Okuma'da da aynı şekilde kullanılabilir).

### 4.9 Okuma (Phase 2.5)
- Derslerden bağımsız, ayrı bir **"📖 Okuma"** bölümü/menüsü.
- Her seviyede (A1, A2, B1, B2) 3–5 kısa metin.
- Uzunluk: A1 60–80, A2 100–120, B1 150–180, B2 200–250 kelime.
- Her metinde: İngilizce metin, **"Türkçesini göster"** butonu (çeviriyi açar/kapatır), 🔊 dinleme butonu, 3 anlama sorusu (çoktan seçmeli).
- Konular günlük hayattan seçilir, içerik JSON dosyalarında tutulur ve `load_content` benzeri bir yöntemle yüklenir.
- Veritabanı tasarımı: mümkünse mevcut `Question`/`Choice` modelleri yeniden kullanılacak; karmaşık olursa en basit ayrı model seçeneği Phase 2.5 başlarken kullanıcıya sorulup karar verilecek.
- Kapsam dışı: konuşma tanıma / telaffuz puanlama (bkz. Bölüm 14).

---

## 5. Kullanıcı Akışı

```
Ana Sayfa
   │
   ├─► Konular ──► Konu kartı seç
   │                    │
   │                    ▼
   │              Ders Sayfası
   │   Kelimeler → İfadeler → Grammar → Örnek Cümleler
   │                    │
   │                    ▼
   │                  Quiz ──► Sonuç (giriş yapılmışsa kaydedilir)
   │                    │
   │                    ▼
   │          Senaryo (Phase 2) ──► Küçük Görev ──► Ders tamamlandı 🎉
   │
   ├─► Kayıt Ol / Giriş Yap
   └─► İlerlemem
```

---

## 6. Teknolojiler

| Katman | Teknoloji |
|--------|-----------|
| Backend | Python 3.12, Django 5.2 (LTS) |
| Veritabanı | Supabase (yalnızca PostgreSQL olarak) |
| Frontend | Django Templates + HTML + CSS + Vanilla JavaScript |
| Statik dosyalar | WhiteNoise |
| Deployment | Vercel (Python runtime) |

**Python bağımlılıkları (hepsi bu kadar):**

```
Django
psycopg[binary]
dj-database-url
whitenoise
python-dotenv
```

**Kullanılmayacaklar:** React, Vue, Angular, Tailwind, Bootstrap, jQuery, npm/build aracı, Django REST Framework, Celery, Redis, Supabase Auth, Supabase JS client.

> Supabase sadece **PostgreSQL veritabanı** olarak kullanılır. Kimlik doğrulama Django'nun kendi sistemiyle yapılır. Bu, iki ayrı auth sistemini yönetme karmaşasını önler.

---

## 7. Django + Vercel: Teknik Notlar ve Sınırlamalar

Vercel öncelikle frontend ve serverless fonksiyonlar için tasarlanmıştır. Django burada **serverless bir Python fonksiyonu (WSGI)** olarak çalışır. Prototip için yeterlidir, ancak şu sınırlamalar bilinmelidir:

| Sınırlama | Etkisi | Prototip çözümü |
|-----------|--------|-----------------|
| Kalıcı dosya sistemi yok | Kullanıcı dosya yüklemesi yapılamaz, SQLite üretimde kullanılamaz | Dosya yükleme yok; veritabanı Supabase |
| Her istek ayrı fonksiyon çağrısı | Veritabanı bağlantısı çok açılabilir | Supabase **transaction pooler** (port `6543`), `CONN_MAX_AGE=0`, `DISABLE_SERVER_SIDE_CURSORS=True` |
| `migrate` deploy sırasında otomatik çalışmaz | Tablolar oluşmayabilir | Migration ve içerik yükleme **lokalden**, Supabase'e karşı çalıştırılır |
| Statik dosyalar | CSS/JS servis edilmeli | WhiteNoise; build sırasında `collectstatic`. Build'de çalıştırılamazsa `WHITENOISE_USE_FINDERS=True` yedek çözümü |
| Cold start | İlk istek birkaç saniye yavaş olabilir | Prototip için kabul edilebilir |
| Arka plan işi / cron yok | E-posta kuyruğu, zamanlanmış görev yapılamaz | Prototipte gerek yok |

**Ek not:** Supabase ücretsiz projeleri uzun süre kullanılmazsa duraklatılabilir. Uygulama açılmıyorsa önce Supabase panelinden proje durumu kontrol edilmelidir.

**Claude Code için talimat:** Vercel'in Python/Django yapılandırması zamanla değişebilir. `vercel.json` yazmadan önce güncel Vercel dokümantasyonunu kontrol et ve **en az dosya ve en az ayar gerektiren** yöntemi seç. Deployment sorun çıkarırsa önce kullanıcıya bildir; kendi başına başka bir platforma geçme.

**Lokal geliştirme:** `DATABASE_URL` tanımlı değilse SQLite'a düşülebilir. Böylece Supabase olmadan da lokal çalışma mümkündür. Üretimde her zaman Supabase kullanılır.

---

## 8. Veritabanı Yapısı

Seviye (A1–B2) ayrı tablo değil, `choices` alanıdır. Tüm modeller sade tutulur.

### `lessons` uygulaması

```
Topic
  title            CharField        "Restoranda"
  slug             SlugField        "restaurant" (unique)
  emoji            CharField        "🍔"
  color            CharField        "coral" (CSS renk anahtarı)
  description      CharField        kısa açıklama
  level            CharField        A1 | A2 | B1 | B2
  order            PositiveInteger
  is_active        Boolean

Lesson
  topic            FK → Topic
  title            CharField
  slug             SlugField (unique)
  intro            TextField        1–2 cümlelik giriş
  order            PositiveInteger

Word
  lesson           FK → Lesson
  english          CharField        "waiter"
  turkish          CharField        "garson"
  example_en       CharField        "The waiter is very friendly."
  example_tr       CharField
  order            PositiveInteger

Phrase
  lesson           FK → Lesson
  english          CharField        "Can I have the bill, please?"
  turkish          CharField
  note             CharField (boş olabilir)  kullanım ipucu
  order            PositiveInteger

GrammarTip
  lesson           FK → Lesson
  title            CharField        "I'd like..."
  explanation      TextField        kısa Türkçe açıklama
  examples         TextField        her satır bir örnek
  order            PositiveInteger

ExampleSentence
  lesson           FK → Lesson
  english          CharField
  turkish          CharField
  order            PositiveInteger

LessonProgress
  user             FK → User
  lesson           FK → Lesson
  completed_at     DateTime
  (unique: user + lesson)
```

### `quizzes` uygulaması

```
Quiz
  lesson           OneToOne → Lesson
  title            CharField

Question
  quiz             FK → Quiz
  question_type    CharField        multiple_choice | meaning | fill_blank | correct_sentence
  prompt           CharField        fill_blank için "___" içerir
  explanation      CharField        sonuç sayfasında gösterilir
  order            PositiveInteger

Choice
  question         FK → Question
  text             CharField
  is_correct       Boolean

QuizAttempt
  user             FK → User
  quiz             FK → Quiz
  score            PositiveInteger
  total            PositiveInteger
  created_at       DateTime
```

### Phase 2 eklemeleri (`lessons` uygulaması içinde)

```
Scenario
  lesson           OneToOne → Lesson
  title            CharField        "Restoranda sipariş"
  setting          CharField        "Bir restorandasın, garson masana geliyor."
  task             CharField        ders sonu küçük görev

ScenarioStep
  scenario         FK → Scenario
  speaker          CharField        "Waiter"
  line             CharField        "Are you ready to order?"
  line_tr          CharField        Türkçe ipucu
  order            PositiveInteger

ScenarioOption
  step             FK → ScenarioStep
  text             CharField
  is_correct       Boolean
  feedback         CharField        özellikle yanlış seçim için kısa açıklama

ScenarioCompletion
  user             FK → User
  scenario         FK → Scenario
  completed_at     DateTime
  (unique: user + scenario)
```

---

## 9. İçerik Yönetimi

Ders içerikleri **JSON dosyalarında** yazılır ve bir management command ile veritabanına yüklenir. Böylece:
- İçerik Git'te versiyonlanır,
- Admin panelinde tek tek veri girmek gerekmez,
- Yeni konu eklemek = yeni bir JSON dosyası eklemek.

```bash
python manage.py load_content          # content/ altındaki tüm JSON'ları yükler
```

Komut **idempotent** olmalıdır: `slug` üzerinden kaydı bulur, günceller; aynı komut tekrar çalıştırıldığında kopya oluşturmaz. Kullanıcı ilerleme kayıtlarını silmez.

**Örnek içerik dosyası** (`content/a1/restaurant.json`, kısaltılmış):

```json
{
  "topic": {
    "slug": "restaurant",
    "title": "Restoranda",
    "emoji": "🍔",
    "color": "coral",
    "level": "A1",
    "description": "Sipariş ver, hesap iste, garsonla konuş.",
    "order": 2
  },
  "lesson": {
    "slug": "restaurant-basics",
    "title": "Restoranda Sipariş Vermek",
    "intro": "Bu derste restoranda sipariş vermeyi ve hesap istemeyi öğreneceksin."
  },
  "words": [
    { "english": "menu", "turkish": "menü", "example_en": "Can I see the menu?", "example_tr": "Menüyü görebilir miyim?" },
    { "english": "waiter", "turkish": "garson", "example_en": "The waiter is very friendly.", "example_tr": "Garson çok cana yakın." },
    { "english": "order", "turkish": "sipariş vermek", "example_en": "Are you ready to order?", "example_tr": "Sipariş vermeye hazır mısınız?" },
    { "english": "bill", "turkish": "hesap", "example_en": "Can I have the bill, please?", "example_tr": "Hesabı alabilir miyim, lütfen?" }
  ],
  "phrases": [
    { "english": "Can I have the menu, please?", "turkish": "Menüyü alabilir miyim, lütfen?", "note": "" },
    { "english": "I'd like a coffee.", "turkish": "Bir kahve istiyorum.", "note": "'I want' yerine daha kibar." }
  ],
  "grammar": [
    {
      "title": "I'd like...",
      "explanation": "Bir şey istemenin daha doğal ve kibar yollarından biri. 'I would like' kalıbının kısaltmasıdır.",
      "examples": ["I'd like a coffee, please.", "I'd like the chicken sandwich."]
    }
  ],
  "examples": [
    { "english": "We'd like a table for two.", "turkish": "İki kişilik bir masa istiyoruz." }
  ],
  "quiz": {
    "title": "Restoran Quiz",
    "questions": [
      {
        "type": "meaning",
        "prompt": "\"bill\" ne demek?",
        "explanation": "Bill = hesap. Restoranda ödeme yapacağın kâğıt.",
        "choices": [
          { "text": "hesap", "correct": true },
          { "text": "menü", "correct": false },
          { "text": "garson", "correct": false }
        ]
      },
      {
        "type": "fill_blank",
        "prompt": "I'd ___ a coffee, please.",
        "explanation": "Kalıp: I'd like + istediğin şey.",
        "choices": [
          { "text": "like", "correct": true },
          { "text": "want", "correct": false },
          { "text": "have", "correct": false }
        ]
      }
    ]
  },
  "scenario": {
    "title": "Restoranda sipariş",
    "setting": "Bir restorandasın, garson masana geliyor.",
    "task": "Bir sonraki kafe/restoran ziyaretinde siparişini aklından 'I'd like...' ile ver.",
    "steps": [
      {
        "speaker": "Waiter",
        "line": "Hello! Are you ready to order?",
        "line_tr": "Merhaba! Sipariş vermeye hazır mısınız?",
        "options": [
          { "text": "Yes, I'd like a chicken sandwich.", "correct": true, "feedback": "Harika, doğal ve kibar!" },
          { "text": "Yes, the bill.", "correct": false, "feedback": "Hesabı yemekten sonra istersin." }
        ]
      }
    ]
  }
}
```

`scenario` alanı Phase 1'de JSON'da bulunabilir ama yükleyici onu **Phase 2'de** işlemeye başlar.

### İçerik (Phase 1 — A1/A2/B1/B2, her seviyede 5 konu)

| Konu | Seviye | Grammar ipucu |
|------|--------|---------------|
| ☕ Kafede (`cafe`) | A1 | *Can I have...?* |
| 🍔 Restoranda (`restaurant`) | A1 | *I'd like...* |
| 👋 Tanışma (`meeting-people`) | A1 | *to be* (I'm / You're / Where are you from?) |
| 🕐 Sayılar ve Saat (`numbers-time`) | A1 | *What time is it? / It's...* |
| 👨‍👩‍👧 Ailem (`family`) | A1 | *have / has* |
| 🛍️ Alışverişte (`shopping`) | A2 | *How much is / are...?* |
| ✈️ Havaalanında (`airport`) | A2 | *Where is...? / Where can I...?* |
| 🏨 Otelde (`hotel`) | A2 | *There is / There are* |
| 🧭 Yol Tarifi (`directions`) | A2 | Yol tarifinde emir kipi (*Turn left.*) |
| 🌦️ Hava Durumu (`weather`) | A2 | *going to* (yakın gelecek tahmini) |
| 💼 İş Görüşmesi (`job-interview`) | B1 | Present Perfect |
| 🩺 Doktorda (`doctor`) | B1 | *should / shouldn't* |
| 🚇 Toplu Taşımada (`public-transport`) | B1 | First Conditional |
| 🏠 Ev Kiralama (`renting`) | B1 | *used to* |
| 🏦 Bankada (`bank`) | B1 | *might / could* (olasılık) |
| 📊 İş Toplantısı (`business-meeting`) | B2 | Reported Speech |
| 📰 Haberler (`news`) | B2 | Passive Voice |
| 📱 Sosyal Medya (`social-media`) | B2 | Third Conditional |
| 🌱 Çevre (`environment`) | B2 | *unless* |
| 💬 Fikir Belirtme (`opinions`) | B2 | *although / despite / however* |

Her konu: 10 kelime, 6 ifade, 1 grammar ipucu, 5 örnek cümle, 7–8 quiz sorusu. B1/B2 içerikleri A1/A2'ye göre daha uzun cümleler ve daha zor çeldiriciler kullanır.

Sonraki konular (Phase 3): Günlük hayat, ileri seviye senaryolar, kullanıcıyla konuşarak seçilecek.

**İçerik kuralları:** Cümleler doğal, günlük ve gerçekten kullanılan İngilizce olmalı. A1–A2 için kısa cümleler, B1–B2 için daha karmaşık yapılar (Present Perfect, Conditional'lar, Passive, Reported Speech). Türkçe açıklamalar kısa ve samimi ("sen" diliyle).

**Senaryo (`scenario`) içerik kuralları:**
- Her adımda **3 seçenek** olur (1 doğru, 2 yanlış).
- Yanlış seçenekler saçma/anlamsız değil, **Türk öğrencilerin gerçekten yaptığı hatalar** olmalı: kaba/emir kipi ifadeler, eksik cümleler, yanlış bağlamda kullanım, Türkçeden birebir çeviri gibi. Her yanlış seçeneğin `feedback` alanı hatayı tek cümleyle kısaca açıklar (ne yanlış, doğrusu ne olurdu).
- Doğru cevaplar, mümkün olduğunca o dersin `phrases` ve `grammar` kalıplarını kullanmalı — senaryo, dersin ifadelerini gerçek hayatta uygulama alanı olmalı, dersten kopuk yeni kalıplar üretmemeli.
- Senaryoda geçen ama derste henüz olmayan bir ifade varsa (ör. yeni bir kalıp) `phrases` listesine eklenmelidir.
- **Doğal ve gerçekten kullanılan İngilizce asla yanlış olarak işaretlenmez** (ör. kafede "Bye." demek tamamen doğaldır). Bir seçenek ancak **yerli bir konuşmacının açıkça garip veya kaba bulacağı** bir cümleyse yanlış sayılır.
- Bir diyalogda **aynı hata türü tekrar edilmez**; farklı adımlarda farklı hata türleri kullanılır: kaba/emir kipi ifade, eksik cümle, Türkçeden birebir çeviri (ör. "Kolay gelsin", "Afiyet olsun", "Paket olsun"), yanlış bağlam, yanlış zaman.
- Diyalog **mantıklı bir sırayla** ilerler (ör. önce ödeme yapılır, sonra başka bir istekte bulunulur — Wi-Fi şifresi ödemeden önce istenmez).

---

## 10. Klasör Yapısı

```
lingogo/
├── PROJECT.md
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
├── vercel.json
├── manage.py
│
├── config/                     # Django proje ayarları
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── accounts/                   # Kayıt, giriş, çıkış, ilerleme sayfası
│   ├── forms.py
│   ├── views.py
│   ├── urls.py
│   └── tests.py
│
├── lessons/                    # Ana sayfa, konular, dersler, ilerleme, senaryolar
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   ├── services.py             # günün konusu, günlük kelimeler, ilerleme hesapları
│   ├── management/
│   │   └── commands/
│   │       └── load_content.py
│   └── tests.py
│
├── quizzes/                    # Quiz, sorular, sonuçlar
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
│
├── content/                    # Ders içerikleri (JSON) — a1/, a2/, b1/, b2/ (her birinde 5 dosya)
│
├── templates/
│   ├── base.html
│   ├── partials/               # header, footer, topic_card, flash mesajları
│   ├── home.html
│   ├── accounts/               # signup, login, progress
│   ├── lessons/                # topic_list, lesson_detail, scenario
│   └── quizzes/                # quiz, result
│
└── static/
    ├── css/
    │   └── main.css            # tek CSS dosyası, CSS değişkenleri ile
    ├── js/
    │   ├── main.js             # menü, küçük etkileşimler
    │   ├── lesson.js           # ders adımları (stepper)
    │   └── scenario.js         # Phase 2 diyalog oynatıcı
    └── img/
```

Sadece **3 Django app** vardır: `accounts`, `lessons`, `quizzes`. Yeni app eklenmeden önce kullanıcıya sorulmalıdır.

---

## 11. Sayfalar ve URL'ler

| URL | Sayfa | Faz |
|-----|-------|-----|
| `/` | Ana sayfa | 1 |
| `/topics/` | Konu listesi (`?level=A1` filtresi) | 1 |
| `/lessons/<slug>/` | Ders sayfası | 1 |
| `/lessons/<slug>/quiz/` | Quiz (GET: sorular, POST: cevaplar) | 1 |
| `/quiz/result/<attempt_id>/` | Quiz sonucu (giriş yapılmışsa) | 1 |
| `/accounts/signup/` | Kayıt | 1 |
| `/accounts/login/` | Giriş | 1 |
| `/accounts/logout/` | Çıkış (POST) | 1 |
| `/progress/` | İlerleme sayfası (giriş gerekli) | 1 |
| `/lessons/<slug>/scenario/` | Gerçek hayat senaryosu | 2 |
| `/scenarios/` | Tüm senaryolar listesi (`?level=A1` filtresi) | 2 |
| `/reading/` | Okuma listesi (seviye filtresi) | 2.5 |
| `/reading/<slug>/` | Okuma metni + anlama soruları | 2.5 |
| `/admin/` | Django admin | 1 |

Giriş yapmamış kullanıcının quiz sonucu, kayıt oluşturmadan doğrudan aynı istekte gösterilir.

---

## 12. UI / UX Tasarımı

### Genel his
Modern, enerjik, temiz. **Çocukça değil, kurumsal da değil.** Duolingo'nun enerjisi ile Notion'ın sadeliği arasında bir yer.

### Renk paleti (CSS değişkenleri)

```css
:root {
  --bg:        #F7F8FC;   /* açık arka plan */
  --surface:   #FFFFFF;   /* kartlar */
  --text:      #1F2340;   /* ana metin */
  --muted:     #6B7090;   /* ikincil metin */
  --border:    #E6E8F2;

  --primary:   #5B5BF7;   /* ana renk: canlı indigo */
  --coral:     #FF6B6B;
  --sun:       #FFC43D;
  --mint:      #22C993;
  --sky:       #3AB8FF;
  --pink:      #FF7AC6;

  --success:   #22C993;
  --error:     #FF5A5F;

  --radius-sm: 10px;
  --radius:    18px;
  --radius-lg: 26px;
  --shadow:    0 6px 20px rgba(31, 35, 64, 0.08);
}
```

Her konunun bir rengi vardır (`Topic.color`). Konu kartları bu rengin açık tonunu arka plan, koyu tonunu vurgu olarak kullanır.

### Tipografi
- Font: **Plus Jakarta Sans** (Google Fonts), yedek: `system-ui, sans-serif`
- Başlıklar kalın (700–800), gövde 400–500
- İngilizce örnek cümleler vurgulu ve biraz daha büyük gösterilir

### Bileşenler
- **Kartlar:** beyaz veya konu rengi, `--radius`, hafif gölge, hover'da hafif yükselme
- **Butonlar:** yuvarlak (pill) veya `--radius-sm`; ana buton `--primary` dolgulu, ikincil buton çerçeveli
- **Seviye rozeti:** küçük, renkli etiket (A1 = mint, A2 = sky, B1 = sun, B2 = coral)
- **Kelime kartı:** İngilizce kelime büyük, Türkçe anlamı altında, örnek cümle en altta
- **Quiz seçenekleri:** büyük, tıklanabilir kartlar; seçildiğinde renk değişir
- **Senaryo:** mesajlaşma uygulaması görünümü; karşı taraf solda, kullanıcı sağda baloncuk
- **İlerleme çubuğu:** ders adımlarında üstte ince renkli çubuk

### Düzen
- **Mobile-first:** önce telefon (360px) için tasarla, sonra genişlet
- İçerik genişliği en fazla ~1100px, ortalanmış
- Konu kartları: mobilde 1–2 sütun, masaüstünde 3–4 sütun (CSS Grid)
- Header: logo + menü; mobilde hamburger menü
- Sayfalar kalabalık olmamalı: bir ekranda tek bir ana eylem

### Etkileşim
- Doğru cevapta kısa yeşil vurgu, yanlışta kırmızı + açıklama
- Ders tamamlandığında basit bir kutlama ekranı (emoji + mesaj, kütüphanesiz)
- Animasyonlar kısa ve hafif (`transition: 150–250ms`)
- `prefers-reduced-motion` desteklenir

### Erişilebilirlik
- Yeterli renk kontrastı, renk tek başına anlam taşımaz (✓ / ✗ ikonları da kullanılır)
- Butonlar ve seçenekler klavyeyle kullanılabilir
- Formlarda `label` kullanılır
- Dokunma alanları en az 44px

---

## 13. Geliştirme Fazları

Her faz bitmeden bir sonrakine geçilmez. Her maddeden sonra uygulama çalışır durumda olmalıdır.

### Phase 1 — Temel Prototip

**1A. Kurulum**
- [x] Django projesi (`config/`) ve 3 app oluşturma
- [x] `settings.py`: ortam değişkenleri, `DATABASE_URL`, WhiteNoise, Türkçe dil/saat dilimi (`tr`, `Europe/Istanbul`)
- [x] `.env.example`, `.gitignore`, `requirements.txt`
- [x] Supabase bağlantısı ve ilk migration (`.env`'de `DATABASE_URL`, session pooler port 5432; lokal `manage.py test` her zaman SQLite kullanır)

**1B. Temel arayüz**
- [x] `base.html`, header, footer, `main.css` (renkler, kartlar, butonlar)
- [x] Mobil uyumlu temel düzen

**1C. İçerik**
- [x] `lessons` ve `quizzes` modelleri + admin kayıtları
- [x] `load_content` management command
- [x] 5 konunun JSON içeriği (Kafede, Restoranda, Tanışma, Alışverişte, Havaalanında)

**1D. Sayfalar**
- [x] Konu listesi + seviye filtresi
- [x] Ders sayfası (kelimeler, ifadeler, grammar, örnek cümleler) + `lesson.js` stepper
- [x] Quiz sayfası + sunucu tarafı değerlendirme + sonuç sayfası
- [x] Ana sayfa (günün konusu, devam et, günlük kelimeler, konular)

**1E. Kullanıcı ve ilerleme**
- [x] Kayıt / giriş / çıkış
- [x] `LessonProgress` ve `QuizAttempt` kaydı
- [x] İlerleme sayfası (ders, kelime, quiz sayıları)

**1F. Yayına alma**
- [x] `vercel.json` (minimal — Vercel Django için sıfır-konfigürasyon destekliyor, sadece `maxDuration` ayarlandı)
- [x] Vercel deploy (bölge: `fra1`)
- [x] Üretimde `DEBUG=False` ile test (canlı sitede kayıt, quiz, ilerleme sayfası test edildi)

**Phase 1 tamamlandı sayılır, eğer:**
- [x] Kullanıcı hesapsız bir konu seçip dersi okuyabiliyor ve quiz çözebiliyorsa,
- [x] Kayıt olan kullanıcının tamamladığı dersler ve quiz sonuçları kaydediliyorsa,
- [x] İlerleme sayfası doğru sayıları gösteriyorsa,
- [x] Site telefonda düzgün görünüyorsa,
- [x] Uygulama Vercel üzerinde Supabase'e bağlı olarak çalışıyorsa.

## ✅ Phase 1 — TAMAMLANDI

20 konu (A1/A2/B1/B2, her seviyede 5), tam kullanıcı akışı (hesapsız/hesaplı ders + quiz + ilerleme), Supabase + Vercel üzerinde canlı.

### Phase 1.5 — Tasarım Düzeltmesi

- [x] Header tasarımı güncellendi (Konular/İlerlemem linkleri, giriş/kayıt butonları veya kullanıcı avatarı, aktif sayfa vurgusu)
- [x] Ana sayfa kartı tasarımı güncellendi (konuşma balonları, seviye · kelime sayısı · süre bilgisi)

### Phase 2 — Gerçek Hayat

- [x] Kelime, ifade, örnek cümle ve grammar örneklerinin yanına Web Speech API ile 🔊 / 🐢 (yavaş) dinleme butonu (bkz. 4.8, ek kütüphane yok)
- [x] `Scenario`, `ScenarioStep`, `ScenarioOption`, `ScenarioCompletion` modelleri
- [x] `load_content` komutunun senaryoları da yüklemesi
- [x] **20 konunun tamamı** için 5 adımlık senaryolar (başlangıç hedefi 5 konuyken, kullanıcı onayıyla tüm konulara genişletildi)
- [x] Senaryo sayfası: sohbet görünümü, cevap seçme, geri bildirim (`scenario.js`)
- [x] Senaryo sonunda küçük görev kartı
- [x] Ders tamamlama kuralı: quiz + (varsa) senaryo
- [x] Ana sayfada "Gerçek hayat senaryoları" bölümünün aktif hale gelmesi

## ✅ Phase 2 — TAMAMLANDI

20 konunun tamamı için gerçek hayat senaryosu: sohbet arayüzü, seçenekler her oynanışta karışıyor, yanlış cevapta kısa Türkçe geri bildirimle tekrar deneme, doğru cevapta ilerleme, senaryo sonunda küçük görev + (varsa) "Türkçesini göster" ve 🔊/🐢 dinleme. Ders tamamlama kuralı artık "quiz + (varsa) senaryo" — senaryosu olmayan bir ders olursa yine sadece quiz ile tamamlanır (geriye dönük uyumluluk `sync_lesson_completion`'da garanti altına alınmış, mevcut bir `LessonProgress` kaydı asla silinmez).

### Phase 2.5 — Okuma

- [x] Okuma içerik modeli (`ReadingText`/`ReadingAttempt`; `Question` quiz/okuma için genelleştirildi)
- [x] Her seviye için 4 kısa metin JSON içeriği, toplam 16 (A1 60–80, A2 100–120, B1 150–180, B2 200–250 kelime) — anlatım, e-posta, blog, hikâye, duyuru, haber
- [x] Okuma listesi sayfası + seviye filtresi (`/reading/`)
- [x] Okuma detay sayfası: metin, "Türkçesini göster" butonu, 🔊 dinleme, 3 anlama sorusu, seçenekler her gösterimde karışır (`/reading/<slug>/`)
- [x] İçerik yükleme mekanizması (`load_content`, idempotent)
- [x] Supabase'e migrate + `load_content` ve push (2026-09-30; canlıda 16 metin, 48 soru doğrulandı)

**Phase 2.5 tamamlandı sayılır, eğer:** Her seviyede en az 3 okuma metni yayında, çeviri gösterme/gizleme ve dinleme butonu çalışıyor, anlama soruları doğru değerlendiriliyorsa.

## ✅ Phase 2.5 — TAMAMLANDI

Her seviyede 4 okuma metni (toplam 16) Supabase'te ve Vercel'de canlı. `/reading/` ve `/scenarios/` canlı sitede açılıyor. Migration'lar (`lessons.0003`, `quizzes.0002`) Supabase'e uygulandı.

### Phase 3 — Geliştirme (ilk fazlar çalıştıktan sonra, kullanıcıyla konuşarak seçilir)

Olası küçük geliştirmeler:
- Yeni konular: Günlük hayat, ileri seviye konular (B1/B2'de zaten 5'er konu var)
- Kelime tekrar sayfası ("Kelimelerimi tekrar et": tamamlanan derslerin kelimeleriyle mini quiz)
- Günlük seri (streak) gibi küçük bir oyunlaştırma
- Quiz'de yanlış yapılan soruları tekrar çözme
- Şifre sıfırlama (e-posta servisi gerektirir)
- Giriş için hız sınırı / kilitleme (brute-force koruması); kayıt formundaki hesap numaralandırma da bununla birlikte ele alınabilir
- CSP ve diğer güvenlik başlıkları (`vercel.json` veya middleware); Google Fonts için SRI/self-host
- Okuma/quiz sonuç açıklamalarının sayfa yenilenince kaybolması (şu an oturumda tek seferlik; sonuçları kalıcı saklamak gerekir)
- `load_content`'i hızlandırma: sadece değişen dosyaları yükle (uzak Supabase'te tam yükleme birkaç dakika sürüyor)
- `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`'i joker yerine tam production adresine daraltma. Kod değişikliği gerekmiyor, sadece Vercel ortam değişkenleri: `ALLOWED_HOSTS=lingogo-ten.vercel.app`, `CSRF_TRUSTED_ORIGINS=https://lingogo-ten.vercel.app` (deployment'a özel `VERCEL_URL` `settings.py`'da zaten otomatik ekleniyor; başka bir alias ya da özel domain kullanılacaksa virgülle eklenmeli). Değer girildikten sonra yeniden deploy + giriş/kayıt testi gerekir. **Kullanıcı yapacak.**

---

## 14. Kapsam Dışı (şimdilik yapılmayacaklar)

- Yapay zeka ile serbest sohbet, konuşma tanıma, telaffuz puanlama
- Ses dosyası yükleme / barındırma
- XP, rozet, leaderboard, arkadaş sistemi
- Ödeme, abonelik
- Sosyal giriş (Google, Apple)
- Mobil uygulama, REST API
- Çoklu dil arayüzü

---

## 15. Claude Code İçin Kurallar

### Genel
1. **Önce bu dosyayı oku.** Bir görev bu dosyayla çelişiyorsa kullanıcıya sor.
2. **Aynı anda tek faz, tek adım.** Bir sonraki adıma geçmeden önce mevcut adımın çalıştığını doğrula.
3. **Basit olanı seç.** İki çözüm varsa, daha az dosya ve daha az bağımlılık gerektireni tercih et.
4. **Yeni bağımlılık, yeni Django app veya yeni teknoloji eklemeden önce kullanıcıya sor.**
5. Kapsam dışı (Bölüm 14) özellikleri kendi başına ekleme.
6. Tamamlanan maddeleri bu dosyadaki checklist'te `[x]` olarak işaretle.

### Kod
7. Kod, değişken ve fonksiyon adları **İngilizce**; kullanıcıya görünen arayüz metinleri **Türkçe**.
8. Django'nun yerleşik özelliklerini kullan: auth, forms, admin, messages, CSRF, template inheritance.
9. View'lar kısa olsun; hesaplama mantığı `services.py` içinde tutulsun.
10. Function-based view'lar tercih edilir (daha okunabilir); Django'nun hazır auth view'ları kullanılabilir.
11. Frontend: Django template + tek `main.css` + sayfaya özel küçük JS dosyaları. JS framework, CSS framework, build aracı **yok**.
12. JS olmadan da temel işlev (ders okuma, quiz gönderme) çalışmalı.
13. Veri JS'e aktarılacaksa `json_script` template filtresi kullanılsın.
14. N+1 sorgularından kaçınmak için `select_related` / `prefetch_related` kullan.

### Güvenlik
15. `SECRET_KEY`, `DATABASE_URL` ve şifreler **asla** koda yazılmaz ve commit edilmez; `.env` kullanılır, `.env.example` güncel tutulur.
16. Üretimde `DEBUG=False`, `ALLOWED_HOSTS` ve `CSRF_TRUSTED_ORIGINS` doğru ayarlanır.
17. Kullanıcıya ait veriler (ilerleme, quiz sonuçları) her zaman `request.user` ile filtrelenir; başka kullanıcının sonucu URL değiştirilerek görülemez.
18. Quiz doğru cevapları HTML'e veya JS'e gönderilmez; değerlendirme sunucuda yapılır. (Senaryoda anlık geri bildirim gerektiği için cevaplar JS'e gönderilebilir; bu kabul edilen bir istisnadır.)

### Veritabanı
19. Model değişikliğinden sonra migration oluştur ve migration dosyalarını commit et.
20. Mevcut kullanıcı verisini silecek migration veya komut çalıştırmadan önce kullanıcıya sor.
21. Migration'lar Supabase'e **lokalden** uygulanır (Vercel build'inde değil).

### Test ve kontrol
22. Kritik noktalar için basit Django testleri yaz: quiz puanlama, ilerleme hesaplama, `load_content`'in tekrar çalıştırılabilirliği, giriş gerektiren sayfalar.
23. Her adımdan sonra `python manage.py check` ve `python manage.py test` çalıştır.
24. Arayüz değişikliklerinden sonra sayfanın mobil genişlikte de düzgün göründüğünü kontrol et.

### İletişim
25. Her adımın sonunda kısa özet ver: ne yapıldı, hangi dosyalar değişti, kullanıcının çalıştırması gereken komutlar.
26. Emin olmadığın teknik bir konu varsa (özellikle Vercel yapılandırması) varsayım yapmak yerine belirt.

---

## 16. Ortam Değişkenleri ve Komutlar

**`.env.example`**

```
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000
DATABASE_URL=postgresql://USER:PASSWORD@HOST:6543/postgres
```

> Üretimde (Vercel) `DATABASE_URL` için Supabase **transaction pooler** adresi (port `6543`) kullanılır. Lokalden migration çalıştırırken session/direct bağlantı (port `5432`) kullanılabilir.

**Sık kullanılan komutlar**

```bash
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py createsuperuser
python manage.py load_content
python manage.py runserver

python manage.py check
python manage.py test
```

---

## 17. İlerleme Günlüğü

> Yeni bir Claude Code oturumuna geçerken hızlıca bağlam kazanmak için. En son burada bırakıldı.

### Tamamlanan fazlar

- **Phase 1 (1A–1F) tamamlandı** — hesapsız/hesaplı ders okuma, quiz çözme, ilerleme takibi, kayıt/giriş/çıkış, Supabase + Vercel üzerinde canlı.
- **Phase 1–2.5 tamamlandı (2026-09-30)** — Phase 1 (temel prototip, canlıda), Phase 1.5 (tasarım düzeltmesi), Phase 2 (🔊/🐢 dinleme + 20 konunun tamamı için gerçek hayat senaryosu + `/scenarios/` listesi), Phase 2.5 (Okuma: her seviyede 4, toplam 16 metin). Hepsi Supabase + Vercel üzerinde canlı; 60 test yeşil.
- **Faz sonrası küçük düzeltmeler (2026-09-30):** Günün Kelimeleri günün konusuyla aynı seviyeden seçiliyor; okuma sayfasında 🔊/🐢 her paragrafın yanında; okuma listesinde tamamlanan metinlerde ✓; `dizzy` çevirisi "başı dönen"; girişte kullanıcı adı veya e-posta kabul ediliyor.
- İçerik sonradan genişletildi: başlangıçta 5 konu (A1/A2) vardı, şimdi **20 konu** (A1/A2/B1/B2, her seviyede 5).

### Önemli kararlar

- **Veritabanı sırası:** Önce SQLite ile geliştirildi (1A–1E), Supabase bağlantısı bilinçli olarak 1F'ye ertelendi.
- **Pooler ayrımı:** Lokalde `.env`'deki `DATABASE_URL` **session pooler** (port `5432`) kullanıyor; Vercel'in ortam değişkenlerindeki `DATABASE_URL` **transaction pooler** (port `6543`) kullanıyor.
- **Testler her zaman SQLite kullanır:** `settings.py`'da `'test' in sys.argv` kontrolüyle `manage.py test` çalıştığında `DATABASE_URL` ayarlı olsa bile SQLite'a düşülüyor. Sebep: Supabase'in pooler'ı test veritabanı oluşturma/silme döngüsünü ~660 saniyeye çıkarıyordu ve `DROP DATABASE` bazen "being accessed by other users" hatasıyla tıkanıyordu. Bu yüzden oluşan yarım kalmış bir `test_postgres` veritabanı Supabase MCP (`execute_sql`) ile elle temizlendi — sadece o veritabanı silindi, `postgres`'e dokunulmadı.
- **Vercel yapılandırması minimal tutuldu:** Güncel Vercel dokümantasyonuna göre Django için sıfır-konfigürasyon desteği var (manage.py/`WSGI_APPLICATION` otomatik algılanıyor, `STATIC_ROOT` sayesinde `collectstatic` build sırasında otomatik çalışıyor). `vercel.json` sadece `config/wsgi.py` için `maxDuration: 30` içeriyor.
- **Statik dosya storage'ı `DEBUG`'a göre seçiliyor:** `DEBUG=True` (lokal/test) → manifest gerektirmeyen WhiteNoise storage; `DEBUG=False` (üretim) → `CompressedManifestStaticFilesStorage`. Sebep: Django'nun test runner'ı `settings.DEBUG`'ı çalışırken geçici `False` yapıyor, bu da `collectstatic` çalışmadan manifest'li storage'ın `{% static %}` etiketinde hata vermesine yol açıyordu.
- **`ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS`:** Vercel'in her deployment'a (production + her preview) otomatik verdiği `VERCEL_URL` ortam değişkeni `settings.py`'da bu iki listeye otomatik ekleniyor (deploy öncesi domain bilinmediği için). Kullanıcı ayrıca Vercel ortam değişkenlerine `ALLOWED_HOSTS=.vercel.app` ve `CSRF_TRUSTED_ORIGINS=https://*.vercel.app` (Django'nun desteklediği joker karakter sözdizimi) elle girdi.
- **Vercel bölgesi:** `fra1`.
- **Git:** GitHub'da private repo (`feyzaozkul45/lingogo`); `.env` hiçbir zaman commit edilmedi.

### Eklenen içerikler (20 konu)

| Seviye | Konular |
|--------|---------|
| A1 | Kafede, Restoranda, Tanışma, Sayılar ve Saat, Ailem |
| A2 | Alışverişte, Havaalanında, Otelde, Yol Tarifi, Hava Durumu |
| B1 | İş Görüşmesi, Doktorda, Toplu Taşımada, Ev Kiralama, Bankada |
| B2 | İş Toplantısı, Haberler, Sosyal Medya, Çevre, Fikir Belirtme |

Her ders: 10 kelime, 6 ifade, 1 grammar ipucu, 5 örnek cümle, 7–8 quiz sorusu (toplam 200 kelime, 150 soru). B1/B2 gerçek CEFR gramer noktaları kullanıyor (Present Perfect, First/Third Conditional, Passive Voice, Reported Speech, *unless*, *although/despite/however* vb.).

### Yarım kalan / bilinen sorunlar

- ~~Vercel Deployment Protection belirsiz~~ — doğrulandı (2026-09-30), beklendiği gibi çalışıyor: production alias'ı (`lingogo-ten.vercel.app`) anonim erişime açık (200), deployment'a özel URL'ler (`lingogo-<hash>-….vercel.app`) korumalı ve anonim istekte 302 yönlendirme veriyor. Herkese açık site için ek bir işlem gerekmiyor.
- Özel domain bağlanmadı, site şu an `*.vercel.app` adreslerinde.
- Şifre sıfırlama ve e-posta doğrulama Phase 1'de bilinçli olarak yok (Bölüm 4.6, 13'te zaten belirtilmiş).
- ~~Senaryolar sitede kolayca bulunamıyor~~ — çözüldü: `/scenarios/` (seviye filtreli liste, tamamlananlar ✓), header'da "Senaryolar" linki, ana sayfada "Tüm senaryolar →", ders sayfasında "🎭 Senaryoyu Dene" butonu. Ders tamamlama kuralı değişmedi. Push edildi, canlıda.
- ~~Vercel canlı sitesi eski hali gösteriyor~~ — kapandı (2026-09-30). Sebep deploy hatası değildi: Phase 2.5 commit'leri (`7418f96` ve sonrası) bilinçli olarak push edilmemişti, son production deploy `4c4682d` idi. Supabase migration'ı yapıldıktan sonra push edilince yeni deploy (`da9b7da`) 26 saniyede READY oldu.
- **Bilinçli kararlar (güvenlik incelemesi, 2026-09-30):** Senaryo doğru/yanlış bilgisinin istemcide (JSON) bulunması ve ders tamamlama kuralının (senaryo POST'u ve quiz puanı doğrulanmadan sayılması) olduğu gibi kalması bilerek kabul edildi; öğrenme deneyimi içindir, sadece kullanıcının kendi ilerlemesini etkiler.
- **`load_content` uzak Supabase'e karşı yavaş** — 20 konu + 16 okuma metni yüklemesi birkaç dakika sürüyor (her kayıt için çok sayıda küçük sorgu). Phase 3 adayı olarak listelendi.

### Okuma (Phase 2.5) — tamamlandı

Kod (commit `7418f96`): `ReadingText`/`ReadingAttempt` modelleri, `Question`'ın quiz/okuma için genelleştirilmesi (CheckConstraint ile), `/reading/` sayfaları, `load_content` desteği, ilerleme sayfası istatistiği, header linki, ana sayfa kartı. İçerik: 2 örnek metin (A1 "My Morning Routine", B2 "The Rise of Remote Work") kullanıcı onayıyla küçük düzeltmelerle kabul edildi, 14 metin daha yazıldı: her seviyede 4, toplam 16 (anlatım, e-posta, blog, hikâye, duyuru, haber). Kelime aralıkları ve "doğru seçenek belirgin uzun olmasın" kuralı testlerle doğrulanıyor. Okuma soruları ve ders quiz'leri her gösterimde seçenekleri karıştırıyor (`random.shuffle`, testli). `/scenarios/` sayfası (seviye filtreli senaryo listesi) aynı push ile çıktı. Test sayısı 46, hepsi yeşil.

**Yayına alma (2026-09-30):** Önce lokal SQLite'ta prova edildi, sonra kullanıcı onayıyla Supabase'e `migrate` + `load_content` uygulandı (16 metin, 48 okuma sorusu, 144 seçenek, 150 quiz sorusu, 20 senaryo doğrulandı; kullanıcı verisi etkilenmedi), ardından push edildi (`4c4682d..da9b7da`). Vercel deploy READY; canlıda `/reading/` 16 metni, `/scenarios/` 20 senaryoyu listeliyor.

**Kural (geçerli kalır):** Model değişikliği içeren commit'ler, Supabase migration'ı uygulanmadan push edilmez (Bölüm 15, kural 21).

### Phase 2 nasıl ilerledi (senaryolar)

Başlangıçta sadece Restoran konusuyla pilot yapıldı, kullanıcı beğenince kalan 19 konuya da genişletildi (her 5 konuda bir durup örnek diyalog onayı alınarak). Süreçte içerik kurallarına iki önemli ekleme yapıldı (Bölüm 9'a işlendi):
1. Doğal/gerçek İngilizce asla yanlış olarak işaretlenmez (sadece yerli bir konuşmacının garip/kaba bulacağı cümleler yanlış olur).
2. Bir diyalogda aynı hata türü tekrar edilmez, farklı türler (kaba, eksik cümle, Türkçeden birebir çeviri, yanlış bağlam, yanlış zaman) kullanılır; diyalog mantıklı sırayla ilerler (ör. önce ödeme, sonra başka istek).

Her `load_content` çalıştırması **önce local SQLite'ta** (`DATABASE_URL=` ile boşaltılarak) test edildi, sonra kullanıcı onayıyla gerçek Supabase'e uygulandı — production'a migration/içerik hiç onaysız gönderilmedi.

Test mimarisiyle ilgili bir not: `LessonCompletionRuleTests` ve `ScenarioViewTests`'teki "senaryosu olmayan ders" davranışı artık gerçek bir konuya (ör. `cafe-basics`) değil, testin kendi oluşturduğu sentetik bir derse dayanıyor — çünkü zamanla tüm 20 konu senaryo kazandı. Aynı sebeple `quizzes/tests.py` de kendi sentetik ders+quiz'ini kullanıyor.

### Sıradaki adım

Karar verildi (2026-09-29), sıra şöyle: ~~1) Tasarım düzeltmesi~~ (tamamlandı) → ~~2) Dinleme butonları~~ (tamamlandı) → ~~3) Phase 2 senaryolar~~ (tamamlandı, 20/20 konu) → ~~4) Phase 2.5 Okuma~~ (tamamlandı, 2026-09-30, canlıda). **Sıradaki: Phase 3** — aday listesi Bölüm 13'te, kullanıcıyla konuşarak seçilecek. Konuşma tanıma/telaffuz puanlama kapsam dışı kalmaya devam ediyor (Bölüm 14). Bekleyen küçük konu: özel domain (site şu an `*.vercel.app` adreslerinde).

**Tasarım düzeltmesi sırasında bulunan ve düzeltilen bir bug:** Header'daki hamburger menü hem mobil hem masaüstü için tek bir `<details>` elementi içindeydi; masaüstünde CSS ile `display:flex !important` verilerek her zaman açık gösterilmeye çalışılıyordu. Ancak tarayıcı, kapalı bir `<details>` içindeki (summary dışı) içeriği kendi `display:none !important` UA kuralıyla gizliyor ve bu, yazarın `!important` kuralı tarafından bile ezilemiyor — sonuç olarak masaüstünde nav tamamen görünmüyordu (muhtemelen kullanıcının "sağ taraf boş" olarak fark ettiği şey buydu). Çözüm: masaüstü nav'ı `<details>`'ten tamamen ayrı, her zaman DOM'da olan bir `<nav class="site-nav--desktop">` haline getirildi; `<details>` artık sadece dar ekranlarda (≤760px) gösterilen mobil menü için kullanılıyor. Nav linkleri tekrarı önlemek için `templates/partials/nav_links.html` adında ortak bir partial'a taşındı.
