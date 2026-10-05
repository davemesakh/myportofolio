# Portofolio David Mesakh

- **Nama:** David Mesakh
- **NPM:** 2506604503
- **Kelas:** C

## Deskripsi Tugas Individu

Website portofolio untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom Universitas Indonesia, menggunakan Django 5.2.17, HTML, CSS, dan Django Template Language (DTL).

- **Profile (`/`):** informasi profil dan Education Journey. Data pendidikan berasal dari context `show_main`, bukan model database.
- **Experience (`/experience/`):** data model `Experience` dimuat melalui AJAX, dengan logo, paragraf kontribusi, periode bulan/tahun, urutan tampilan, pencarian, star/unstar, penambahan melalui modal, serta form update dan penghapusan.
- **Awards (`/awards/`):** bagian baru untuk memenuhi Tugas Individu 2 melalui alur Model-View-Template (MVT). Model `Award` menyimpan judul, pencapaian, tahun, deskripsi, referensi foto, alt text, dimensi, dan urutan.
- **Admin (`/admin/`):** pengelolaan Experience dan Award dengan pencarian, filter, dan pengurutan.

Tema biru Summer Splash, font, floating hearts, kontrol pause, dan dukungan reduced motion dipertahankan. Foto profil memiliki tautan Instagram dan interaksi "Contact me!". Experience dan Awards tidak lagi ditulis sebagai artikel statis di Profile. Fitur Projects dibatalkan dan dihapus melalui migrasi baru `0006_delete_project.py`; riwayat migrasi lamanya tetap dipertahankan.

## Cara Menjalankan Proyek

Perintah berikut menggunakan PowerShell dari direktori proyek. Environment pengembangan yang digunakan dalam pekerjaan ini memakai Python 3.13.7.

1. Clone repository jika belum tersedia.

   ```powershell
   git clone https://github.com/davemesakh/myportofolio.git
   cd myportofolio
   ```

2. Buat dan aktifkan virtual environment, lalu pasang dependensi.

   ```powershell
   python -m venv env
   .\env\Scripts\Activate.ps1
   python -m pip install -r requirements.txt
   ```

   Jika aktivasi diblokir, gunakan `.\env\Scripts\python.exe` sebagai pengganti `python` pada perintah berikutnya.

3. Pilih database lokal sebelum menjalankan migrasi atau impor.

   ```powershell
   $env:PRODUCTION = "False"
   ```

   `portofolio/settings.py` memanggil `load_dotenv()`, sehingga `.env` dapat memuat `PRODUCTION=False`. Variabel proses yang sudah disetel tidak ditimpa oleh pemuatan `.env` default. Dalam mode ini database berada di `db.sqlite3` dan tidak membutuhkan kredensial database.

   Jika `PRODUCTION=True`, konfigurasi menggunakan PostgreSQL dan membaca `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, serta `SCHEMA` (default `public`). Produksi juga wajib menyediakan `SECRET_KEY` yang acak dan rahasia melalui environment; aplikasi menolak untuk mulai jika variabel ini kosong. `DEBUG` menjadi `False`, sedangkan cookie sesi dan CSRF hanya dikirim melalui HTTPS. Nilai environment produksi harus berasal dari lingkungan PWS; jangan menyalin rahasia ke README atau Git. Panduan ini hanya untuk lokal, bukan prosedur deployment PWS.

   Pengalihan HTTPS, kepercayaan header HTTPS dari proxy, dan HSTS belum diaktifkan di Django karena perilaku reverse proxy PWS belum terverifikasi. Pastikan HTTPS pada domain PWS dan alur login/POST bekerja setelah konfigurasi environment diterapkan, lalu evaluasi pengaturan tersebut berdasarkan konfigurasi proxy yang sebenarnya.

4. Terapkan migrasi yang sudah tersedia.

   ```powershell
   python manage.py migrate
   ```

5. Pratinjau impor konten, lalu jalankan jika tidak ada konflik.

   ```powershell
   python manage.py import_portfolio_experiences --dry-run
   python manage.py import_portfolio_awards --dry-run
   python manage.py import_portfolio_experiences
   python manage.py import_portfolio_awards
   ```

   Pada database baru, command menambahkan empat Experience dan dua Award dari salinan konten portfolio lama yang tersimpan dalam command. Awards membaca database melalui view/context; Experience mengambil data dari endpoint AJAX setelah kerangka halaman dimuat. Kedua command memeriksa aset melalui staticfiles finders dan seluruh konflik sebelum penulisan dalam `transaction.atomic`. `--dry-run` tidak menulis data. Pengulangan melewati record dengan `source_key` dan data impor identik; perbedaan dilaporkan tanpa ditimpa.

   Impor Awards menolak kandidat tanpa `source_key` dengan judul dan tahun yang sama. Impor Experience menolak pencocokan tanpa key yang ambigu atau tidak diizinkan. Pengecualian terbatasnya adalah rekonsiliasi satu record lama "Teaching Assistant, Calculus 1" yang cocok dengan bentuk data lama yang dikenali: deskripsi diselaraskan dengan sumber HTML, sedangkan ID, kategori, dan timestamp dipertahankan. Deskripsi sebelum/sesudah ditampilkan. Record lain tidak diubah. Jika ada konflik atau aset hilang, periksa laporan dan selesaikan penyebabnya sebelum menjalankan ulang; jangan menghapus data hanya untuk meloloskan impor.

6. Buat akun admin lokal dan jalankan server.

   ```powershell
   python manage.py createsuperuser
   python manage.py runserver
   ```

   Isi kredensial sendiri melalui prompt interaktif. Buka [Profile](http://127.0.0.1:8000/), [Experience](http://127.0.0.1:8000/experience/), [Awards](http://127.0.0.1:8000/awards/), atau [admin](http://127.0.0.1:8000/admin/). Di admin, kelola Experience dan Award; `display_order` menentukan urutan. Path gambar berupa referensi aset statis seperti `img/award-osnk-2024.jpeg`, bukan unggahan gambar. Perubahan manual pada field impor dapat menyebabkan konflik saat command dijalankan ulang. Hentikan server dengan `Ctrl+C`.

7. Jalankan pemeriksaan dan seluruh tests.

   ```powershell
   python manage.py check
   python manage.py makemigrations --check --dry-run
   python manage.py test
   ```

   Tests memakai database test tersendiri. Hasil terakhir sebelum pembaruan dokumentasi Tugas 3: 46 tests lulus. Warning direktori `staticfiles` belum tersedia muncul saat tests; konfigurasi tidak diubah untuk menyembunyikannya. Tests tidak diulang untuk perubahan dokumentasi ini.

`db.sqlite3`, `.env`, `env/`, dan `__pycache__/` diabaikan Git. Database lokal tidak ikut di-push; lingkungan lain memerlukan migrasi, pengisian data, dan akun admin tersendiri. Jangan mengedit migrasi lama yang sudah diterapkan. Deployment Tugas 3 pada PWS telah diperiksa secara manual setelah kode terbaru dimuat ulang.

## Tugas Individu 4

Autentikasi dari Tutorial 4 menggunakan registrasi, login, dan logout bawaan Django. Login menyimpan sesi dan cookie `last_login` dalam waktu Asia/Jakarta; logout mengakhiri sesi serta menghapus cookie tersebut. Pengunjung tanpa akun dapat membaca Profile, Experience, Awards, dan endpoint JSON, tetapi aksi akun mengarah ke halaman login.

Hak akses Experience mengikuti peran berikut:

| Peran | Baca | Star/Unstar | Tambah | Ubah | Hapus |
| --- | --- | --- | --- | --- | --- |
| Pengunjung | Ya | Login diperlukan | Login diperlukan | Login diperlukan | Login diperlukan |
| Pengguna biasa | Ya | Ya | 403 | 403 | 403 |
| Anggota grup `Editor` | Ya | Ya | 403 | Ya | 403 |
| Superuser | Ya | Ya | Ya | Ya | Ya |

Keanggotaan `Editor` menggunakan Django Group bernama persis `Editor`; buat grup dan tambahkan pengguna melalui Django admin. Tombol Add, Edit, dan Delete pada halaman Experience mengikuti izin tersebut. Star/Unstar memerlukan login dan form POST dengan token CSRF; setiap pengguna dapat memberi atau mencabut satu star pada setiap Experience. Endpoint `/experience/json/` hanya memuat field Experience yang ditentukan, tanpa identitas pengguna atau data relasi star. Endpoint AJAX yang ditambahkan pada Tutorial 5 juga memuat jumlah star dan status star pengguna yang sedang mengakses, tetapi tidak mengungkap identitas pemberi star.

Jalankan proyek dengan langkah virtual environment, migrasi, dan `runserver` pada bagian **Cara Menjalankan Proyek**. Untuk pemeriksaan Tugas 4 dari direktori proyek, jalankan:

```powershell
python manage.py check
python manage.py test main
```

Jika virtual environment belum diaktifkan, ganti `python` dengan `.\env\Scripts\python.exe`.

## Tugas Individu 5

Halaman Experience kini dirender sebagai kerangka antarmuka oleh Django, lalu `fetchExperiences()` mengambil data dari `/experience/ajax/`. View `get_experiences_ajax` menyusun dictionary secara manual dan mengembalikannya dengan `JsonResponse`, termasuk jumlah star, status star pengguna saat ini, periode, logo, serta aksi yang diizinkan. Pengunjung anonim menerima status belum memberi star tanpa identitas pengguna lain. Antarmuka membedakan kondisi loading, data kosong/tidak cocok dengan pencarian, dan kegagalan permintaan.

Pencarian judul, organisasi, dan kategori memakai AJAX/fetch tanpa memuat ulang halaman. Input diberi debounce 300 ms; `AbortController` membatalkan permintaan sebelumnya dan pemeriksaan identitas controller mencegah respons lama mengganti hasil permintaan terbaru.

Superuser dapat menambah Experience melalui dialog modal berbasis popover. Endpoint POST menggunakan `ExperienceForm`: data valid disimpan dengan respons JSON HTTP 201, data tidak valid mendapat HTTP 400 beserta pesan validasi, dan pengguna tanpa izin mendapat HTTP 403 JSON. CSRF middleware tetap aktif; form memuat token dan fetch mengirim `FormData`, kredensial same-origin, serta header `X-CSRFToken`. Penolakan CSRF oleh middleware dapat menghasilkan respons 403 standar Django, bukan JSON dari view. Setelah berhasil, form direset, dialog ditutup, toast sukses muncul, dan daftar diambil ulang tanpa reload dengan pencarian saat ini. Kegagalan pembuatan menampilkan toast error, termasuk pesan validasi dari server.

Teks kartu dan toast ditampilkan dengan DOM API seperti `textContent`, bukan interpolasi `innerHTML`; alt text dan atribut diatur melalui property/attribute yang sesuai. Sumber logo divalidasi dan protokol URL diperiksa sebelum ditampilkan. Di server, `clean_title`, `clean_description`, `clean_organization`, dan `clean_logo_alt` memakai `strip_tags` serta memangkas whitespace. Judul/deskripsi yang hanya berisi tag ditolak, sedangkan organisasi dan alt text tetap boleh kosong. Hak akses Tugas 4 tetap berlaku: semua peran dapat membaca, pengguna login dapat star/unstar, Editor dapat mengubah, dan hanya superuser dapat menambah atau menghapus. Pembatasan diterapkan di view, bukan hanya pada tombol.

Verifikasi Phase 2 menghasilkan 32 tests terarah dan 104 tests `main` yang lulus, tanpa masalah pada Django check, perubahan migrasi, kesalahan sintaks kedua file JavaScript, atau whitespace diff. Warning direktori `staticfiles` belum tersedia tetap muncul tanpa menggagalkan tests. Pemeriksaan browser manual dan deployment Tugas 5 masih akan dilakukan pada tahap berikutnya; keduanya belum dibuktikan oleh tests backend atau pemeriksaan kode ini.

## Progres Mingguan

| Periode | Progres |
| --- | --- |
| Hingga 2 September 2026 | Setup Django, Profile, Git/GitHub dan PWS, serta latihan branch dan pull request tutorial. |
| 6-7 September 2026 | Experience dan Awards statis, tema Summer Splash, logo, crop foto, serta interaksi profil. |
| Tugas Individu 2 | Awards berbasis database, pemindahan Experience, command impor berulang, admin, tests, penghapusan Projects, serta Education Journey pada Profile. |
| Tugas Individu 3 | Experience mendukung create, update, delete, validasi form, data delivery JSON, serta tampilan data setelah proses deserialization JSON. |
| Tugas Individu 4 | Autentikasi dan sesi dari Tutorial 4, hak akses Editor untuk update Experience, serta star/unstar per pengguna dengan CSRF. |
| Tugas Individu 5 | Audit fitur AJAX dari Tutorial 5, pencarian dengan debounce 300 ms dan pembatalan request lama, penambahan lewat modal dan toast, pelengkapan sanitasi teks Experience, 104 tests lulus, serta refleksi dan disclosure AI. |

## Pertanyaan Reflektif

Jawaban Tugas 1 berikut dipertahankan sebagai refleksi tahap sebelumnya, ketika konten masih statis.

### Tugas 1

1. **Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat *static web*? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?**

   Ya, saya menggunakan `<section>` untuk membagi Profile, Experience, dan Awards, serta `<article>` untuk setiap pengalaman dan penghargaan yang dapat dipahami secara mandiri. Elemen `<header>`, `<nav>`, `<main>`, dan `<footer>` menandai bagian pembuka, navigasi, konten utama, dan penutup halaman. Struktur ini membantu saya memahami fungsi setiap bagian, memudahkan penambahan konten, serta membantu pembaca layar mengenali bagian halaman. Saya tidak menggunakan `<aside>` karena belum ada konten sampingan yang memerlukannya.

2. **Ketika Anda mengatur CSS Anda agar tetap *responsive*, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?**

   Tantangannya adalah menjaga teks dan foto tetap rapi saat layar mengecil. Saya memprioritaskan keterbacaan teks: pada mobile, periode Experience diletakkan di bawah jabatan dan deskripsinya dibuat selebar area konten. Pada Awards, susunan dua kolom diubah menjadi teks lalu foto agar tidak terlalu sempit.

3. **Website yang Anda buat saat ini adalah *static web* murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?**

   Batasan yang saya rasakan adalah pembaruan informasi masih harus dilakukan dengan mengedit HTML secara langsung, termasuk menambah struktur elemen saat menambahkan item baru. Fitur pengelolaan konten berbasis database dapat menjadi pengembangan berikutnya agar informasi bisa diperbarui melalui formulir tanpa mengedit HTML setiap kali.

### Tugas 2

1. **Bagaimana alur saat pengguna membuka `/awards/`?**

   `portofolio/urls.py` meneruskan URL melalui `include("main.urls")`. Di `main/urls.py`, path `awards/` dengan nama `main:show_awards` memanggil `show_awards` pada `main/views.py`. View mengambil `Award.objects.all()` dari model di `main/models.py`, mengikuti urutan `display_order` lalu `id`, dan mengirim context `award_list` serta `name` ke `templates/awards.html`. Template mengulang data menggunakan DTL, menampilkan foto melalui tag `static`, dan membalik layout item genap. Django merender HTML menjadi respons HTTP yang diterima browser; browser kemudian memuat CSS dan gambar yang dirujuk.

2. **Mengapa data Awards disimpan di model, bukan hard-coded dalam template?**

   Pemisahan ini membuat data penghargaan bisa ditambah atau diubah melalui admin tanpa menyalin artikel HTML. Template cukup mengatur tampilan untuk seluruh record dan pesan saat data kosong. Field model memberi struktur yang konsisten, sementara `display_order` mengatur urutan dan `source_key` mendukung impor berulang tanpa duplikasi. Pengembangan seperti pencarian atau penyaringan juga dapat memakai data yang sama tanpa mengubah setiap artikel secara manual.

3. **Apa perbedaan `makemigrations` dan `migrate`?**

   `makemigrations` membuat berkas migrasi dari perbedaan model terhadap riwayat migrasi; perintah ini belum menerapkan perubahan skema ke database. Saat model `Award` ditambahkan, `python manage.py makemigrations main` menghasilkan `main/migrations/0004_award.py` dengan operasi `CreateModel Award`. Setelah isinya diperiksa, `python manage.py migrate` menerapkan operasi tersebut untuk membuat tabel Award pada database yang dipilih. Pengisian dua penghargaan dilakukan terpisah melalui `import_portfolio_awards`, bukan melalui migrasi skema itu.

### Tugas 3

1. **Jelaskan mengapa kita menggunakan `ModelForm` pada Django alih-alih membuat form HTML secara manual. Selain itu, jelaskan pula mengapa kita diwajibkan menambahkan `{% csrf_token %}` pada form tersebut!**

   `ModelForm` membentuk field dan aturan validasi dari model Django, sehingga form lebih konsisten dengan struktur database dan tidak perlu mengulang seluruh definisi input secara manual. Pada proyek ini, `ExperienceForm` dapat dipakai untuk create dan update, sementara validasi tanggal tetap berada di satu tempat. `{% csrf_token %}` menambahkan token yang diperiksa Django ketika form POST dikirim. Pemeriksaan ini mencegah situs lain mengirim permintaan perubahan data dengan memanfaatkan sesi pengguna tanpa izin.

2. **Pada Tutorial 03, kita membahas format data JSON dan XML. Mengapa JSON lebih disukai dalam pengembangan aplikasi web modern dibandingkan XML?**

   JSON lebih ringkas, mudah dibaca, dan langsung cocok dengan struktur object serta array yang umum dipakai JavaScript. Ukuran data dan sintaksnya biasanya lebih sederhana daripada XML karena tidak memerlukan tag pembuka dan penutup untuk setiap nilai. Dukungan parsing JSON juga tersedia secara bawaan di browser dan banyak bahasa pemrograman, sehingga praktis untuk pertukaran data pada aplikasi web dan API modern.

3. **Jelaskan alur yang terjadi saat kamu menggunakan fungsi view untuk mengembalikan data portofoliomu dalam bentuk JSON. Mengapa kita perlu melakukan proses serialization pada model Django sebelum datanya dikembalikan?**

   Pada tahap Tugas 3, view `get_experiences_json` mengambil queryset Experience sesuai urutan tampilan, lalu `serializers.serialize("json", ...)` mengubah setiap object menjadi teks JSON yang memuat primary key UUID dan field model. Data tersebut dikirim melalui `HttpResponse` dengan content type `application/json`. Saat itu, view `show_experience` membaca respons tersebut, melakukan deserialization menjadi object Experience, dan mengirimkannya ke template. Serialization diperlukan karena queryset dan instance model adalah object Python yang tidak dapat langsung dikirim sebagai data HTTP atau dipahami sebagai JSON oleh client. Sejak Tutorial 5, halaman mengambil data melalui fetch dari `get_experiences_ajax` yang memakai `JsonResponse`; alur sebelumnya dipertahankan di sini sebagai konteks Tugas 3.

### Tugas 5

1. **Jelaskan apa itu debouncing dan mengapa teknik ini penting diterapkan pada fitur pencarian yang menggunakan AJAX.**

   Saya memahami debouncing sebagai menunda suatu aksi sampai input berhenti berubah selama waktu tertentu. Pada pencarian Experience, setiap ketikan mengatur ulang timer, sehingga fetch baru berjalan setelah saya berhenti mengetik selama 300 ms. Ini mengurangi request untuk setiap tombol yang ditekan, mengurangi beban server, dan menghindari pembaruan hasil yang terlalu sering. Tombol Search tetap bisa menjalankan pencarian langsung.

   Debouncing berbeda dari `AbortController`: debounce mengurangi request sebelum dikirim, sedangkan controller membatalkan request sebelumnya ketika request baru dimulai. Kode juga memeriksa identitas controller sebelum merender hasil, agar respons lama yang terlambat tidak mengganti hasil terbaru. Jadi keduanya membantu pencarian AJAX, tetapi menangani masalah yang berbeda.

2. **Jelaskan fungsi penggunaan `await` ketika menggunakan `fetch()`. Apa yang akan terjadi jika kita tidak menggunakan `await`?**

   `fetch()` langsung mengembalikan Promise, bukan respons HTTP yang sudah tersedia. Di `fetchExperiences()`, `await fetch(...)` menunda kelanjutan fungsi async sampai Response tersedia, lalu kode memeriksa `response.ok`. Setelah itu, `await response.json()` menunggu body selesai dibaca dan diparsing menjadi data JavaScript. Kedua langkah perlu ditunggu secara terpisah.

   Tanpa `await`, variabel berisi Promise, sehingga saya belum bisa memperlakukannya sebagai Response atau data hasil parsing. Alternatifnya adalah memakai `.then()` untuk menjalankan langkah berikutnya setelah Promise selesai. `await` tidak membekukan seluruh browser atau UI; hanya kelanjutan fungsi async tersebut yang menunggu, sehingga interaksi lain tetap dapat diproses.

3. **Jelaskan apa itu serangan XSS (Cross-Site Scripting) dan mengapa data yang ditampilkan melalui AJAX/JavaScript lebih rentan terhadap serangan ini daripada data yang ditampilkan langsung melalui template Django.**

   XSS terjadi ketika input penyerang diperlakukan sebagai HTML atau JavaScript aktif oleh browser. Payload bisa disimpan dalam database lalu muncul saat orang lain membuka halaman (stored XSS), atau berasal dari request yang dipantulkan kembali dalam respons (reflected XSS). Saya perlu memisahkan data teks dari kode yang boleh dijalankan.

   Template Django biasanya melakukan auto-escape pada variabel, termasuk karakter `<` dan `>`, agar input tampil sebagai teks. Saat fetch mengambil string mentah dari JSON dan JavaScript memasukkannya sendiri ke DOM, auto-escaping template tidak melindungi operasi tersebut. JSON hanya format pertukaran data, bukan sanitizer HTML. Jika string diinterpolasi ke `innerHTML`, markup penyerang seperti gambar dengan event handler dapat dijalankan. AJAX bukan otomatis tidak aman, tetapi saya harus memilih cara rendering yang aman secara eksplisit.

   Pada proyek ini, kartu dan toast menggunakan `textContent`; alt text dan atribut diatur melalui property/attribute yang sesuai, dan URL logo divalidasi. Form juga memakai `strip_tags` untuk judul, deskripsi, organisasi, dan alt text. Fungsi itu membuang tag, bukan seluruh isinya: `<script>alert('x')</script>` menjadi teks `alert('x')`, yang tetap tidak dijalankan oleh `textContent`. Sanitasi server membantu membersihkan input, sedangkan DOM API yang aman tetap diperlukan untuk melindungi rendering, termasuk data lama yang tidak melalui form.

## Penggunaan AI

- **ChatGPT:** membantu memahami ketentuan, menyusun tahapan/prompt, meninjau laporan, dan memberi masukan desain, sesuai keterangan pengguna.
- **Codex:** membantu implementasi Django dan HTML/CSS, migrasi, command impor, tests, dokumentasi.

Pekerjaan dilakukan bertahap dengan batas lingkup yang eksplisit: audit, model/migrasi, impor data, halaman, validasi, lalu commit. Diff dan staged diff diperiksa agar perubahan lain tidak ikut masuk. Screenshot digunakan sebagai referensi struktur dan ukuran; revisi mencakup layout Experience/Awards, timeline Education, whitespace logo SMA, dan penggunaan logo Fasilkom atas izin pengguna.

Pada Tugas 3, ChatGPT dan Codex digunakan untuk merencanakan implementasi, mengaudit kode, membuat alur CRUD Experience, menerapkan data delivery serta deserialization JSON, menyusun strategi tests, dan memperbarui dokumentasi. Setiap perubahan ditinjau manual, diuji secara lokal, lalu diperiksa pada deployment PWS dan disesuaikan berdasarkan perilaku yang terlihat. Salah satu keterbatasannya adalah deployment PWS sempat tidak langsung menampilkan kode terbaru, sehingga versi yang aktif perlu dipastikan kembali melalui reload dan pemeriksaan manual.

[Ringkasan penggunaan AI Tugas 2](docs/ai-usage-tugas-2.md) memuat prompt dan perubahan penting yang tersedia dalam percakapan Codex. Dokumen tersebut adalah ringkasan, bukan transkrip lengkap. URL percakapan tidak dicantumkan karena tidak tersedia.

[Ringkasan penggunaan AI Tugas 3](docs/ai-usage-tugas-3.md) mencatat audit, implementasi CRUD, data delivery JSON, strategi pengujian, pembaruan dokumentasi, dan keterbatasan verifikasi yang ditemui.

[Ringkasan penggunaan AI Tugas 4](docs/ai-usage-tugas-4.md) menjelaskan peran ChatGPT dan Codex, perubahan terfokus, serta pemeriksaan yang dilakukan untuk autentikasi, hak akses, dan star/unstar Experience.

Pada Tugas 5, ChatGPT membantu menafsirkan ketentuan dan menyusun prompt serta batas tiap phase. Codex mengaudit kode Tutorial 5 terhadap setiap persyaratan yang diberikan, meninjau XSS dan izin, menemukan cleaner `strip_tags` yang belum ada untuk organisasi/alt text, lalu membantu mengimplementasikan cleaner dan merancang tests terarah. AI juga membantu menyusun dan meninjau jawaban reflektif serta dokumentasi ini, dan merencanakan pemeriksaan validasi, browser, serta deployment berikutnya. Jawaban reflektif di atas adalah draf dengan bantuan AI; saya tetap perlu memahami dan meninjaunya sebagai bagian dari pertanggungjawaban tugas.

Kesimpulan AI tidak diterima hanya berdasarkan klaim bahwa fitur tersedia. Codex memeriksa source repository aktual, menjalankan Django check, pemeriksaan migrasi, tests otomatis (104 lulus pada Phase 2), pemeriksaan sintaks JavaScript, serta meninjau diff. Batas pekerjaan ditentukan melalui prompt pengguna; perubahan Phase 2 dibatasi pada form dan tests, sedangkan Phase 3 hanya dokumentasi. Ini merupakan verifikasi berbantuan AI dan alat, bukan klaim bahwa seluruh implementasi atau pengujian dilakukan sendiri tanpa bantuan. Pemeriksaan manual di browser, audit akhir, dan deployment masih direncanakan untuk tahap selanjutnya, bukan sudah selesai.

AI dapat salah memahami kondisi repository atau menganggap fitur memenuhi rubrik hanya karena kodenya terlihat serupa. Saran keamanan tetap perlu ditinjau pada source dan diuji; penilaian kelengkapan harus dibandingkan dengan rubrik resmi, dan perilaku browser tidak boleh disimpulkan hanya dari analisis statis atau tests backend. Keterangan Tugas 5 ini dicatat langsung di README; tidak ada URL percakapan yang tersedia untuk ditautkan, sehingga tidak dibuat tautan atau log percakapan fiktif.
