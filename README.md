# Portofolio David Mesakh

- **Nama:** David Mesakh
- **NPM:** 2506604503
- **Kelas:** C

## Deskripsi Tugas Individu

Website portofolio untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom Universitas Indonesia, menggunakan Django 5.2.17, HTML, CSS, dan Django Template Language (DTL).

- **Profile (`/`):** informasi profil dan Education Journey. Data pendidikan berasal dari context `show_main`, bukan model database.
- **Experience (`/experience/`):** data model `Experience`, dengan logo, paragraf kontribusi, periode bulan/tahun, dan urutan tampilan.
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

   Jika `PRODUCTION=True`, konfigurasi menggunakan PostgreSQL dan membaca `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`, serta `SCHEMA` (default `public`). Nilainya harus berasal dari lingkungan tujuan; jangan menyalin rahasia ke README atau Git. Panduan ini hanya untuk lokal, bukan prosedur deployment PWS. `PRODUCTION` memilih database, bukan otomatis mengatur seluruh konfigurasi keamanan; `DEBUG` saat ini disetel langsung dalam settings.

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

   Pada database baru, command menambahkan empat Experience dan dua Award dari salinan konten portfolio lama yang tersimpan dalam command. Template halaman tetap membaca database melalui view/context. Kedua command memeriksa aset melalui staticfiles finders dan seluruh konflik sebelum penulisan dalam `transaction.atomic`. `--dry-run` tidak menulis data. Pengulangan melewati record dengan `source_key` dan data impor identik; perbedaan dilaporkan tanpa ditimpa.

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

   Tests memakai database test tersendiri. Hasil terakhir sebelum pembaruan dokumentasi: 23 tests lulus. Warning direktori `staticfiles` belum tersedia muncul saat tests; konfigurasi tidak diubah untuk menyembunyikannya. Tests tidak diulang untuk perubahan dokumentasi ini.

`db.sqlite3`, `.env`, `env/`, dan `__pycache__/` diabaikan Git. Database lokal tidak ikut di-push; lingkungan lain memerlukan migrasi, pengisian data, dan akun admin tersendiri. Jangan mengedit migrasi lama yang sudah diterapkan. Perintah khusus PWS belum diverifikasi dalam rangkaian ini dan tidak dicantumkan.

## Progres Mingguan

| Periode | Progres |
| --- | --- |
| Hingga 2 September 2026 | Setup Django, Profile, Git/GitHub dan PWS, serta latihan branch dan pull request tutorial. |
| 6-7 September 2026 | Experience dan Awards statis, tema Summer Splash, logo, crop foto, serta interaksi profil. |
| Tugas Individu 2 | Awards berbasis database, pemindahan Experience, command impor berulang, admin, tests, penghapusan Projects, serta Education Journey pada Profile. |

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

## Penggunaan AI

- **ChatGPT:** membantu memahami ketentuan, menyusun tahapan/prompt, meninjau laporan, dan memberi masukan desain, sesuai keterangan pengguna.
- **Codex:** membantu implementasi Django dan HTML/CSS, migrasi, command impor, tests, dokumentasi, serta commit yang diizinkan. Data dan aset berasal dari pengguna atau konten proyek; keputusan dan revisi tetap diarahkan pengguna.

Pekerjaan dilakukan bertahap dengan batas lingkup yang eksplisit: audit, model/migrasi, impor data, halaman, validasi, lalu commit. Diff dan staged diff diperiksa agar perubahan lain tidak ikut masuk. Screenshot digunakan sebagai referensi struktur dan ukuran; revisi mencakup layout Experience/Awards, timeline Education, whitespace logo SMA, dan penggunaan logo Fasilkom atas izin pengguna.

**Pemeriksaan otomatis:** Codex menjalankan tests, Django system check, pemeriksaan migrasi dan diff, reverse/resolve, HTTP melalui Django test client, serta akses aset melalui staticfiles handler. Impor dijalankan ulang untuk memeriksa duplikasi; data dan ID Calculus dibandingkan sebelum/sesudah. Pada validasi terakhir fitur Education, 23 tests lulus. Ini bukan bukti kesamaan visual di browser.

**Pemeriksaan visual pengguna:** pengguna memberikan screenshot, penyesuaian teks, dan umpan balik bahwa CSS tampil setelah Ctrl+F5. Codex membaca aset gambar dan aturan CSS, tetapi tidak melakukan pemeriksaan halaman melalui browser desktop/mobile. Tidak tersedia bukti pemeriksaan mobile atau kontrol pause secara menyeluruh; keduanya masih perlu diperiksa manual.

[Ringkasan penggunaan AI Tugas 2](docs/ai-usage-tugas-2.md) memuat prompt dan perubahan penting yang tersedia dalam percakapan Codex. Dokumen tersebut adalah ringkasan, bukan transkrip lengkap. URL percakapan tidak dicantumkan karena tidak tersedia.
