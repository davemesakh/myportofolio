# Portofolio David Mesakh

- **Nama:** David Mesakh
- **NPM:** 2506604503
- **Kelas:** C

## Deskripsi Tugas Individu

Website portofolio untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom Universitas Indonesia, menggunakan Django 5.2.17, HTML, CSS, dan Django Template Language (DTL).

- **Profile (`/`):** informasi profil dan Education Journey. Data pendidikan berasal dari context `show_main`, bukan model database.
- **Experience (`/experience/`):** data model `Experience`, dengan logo, paragraf kontribusi, periode bulan/tahun, urutan tampilan, form create/update, penghapusan, serta penyajian dan pembacaan ulang data JSON.
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

Keanggotaan `Editor` menggunakan Django Group bernama persis `Editor`; buat grup dan tambahkan pengguna melalui Django admin. Tombol Add, Edit, dan Delete pada halaman Experience mengikuti izin tersebut. Star/Unstar memerlukan login dan form POST dengan token CSRF; setiap pengguna dapat memberi atau mencabut satu star pada setiap Experience. JSON Experience hanya memuat field Experience yang ditentukan, tanpa identitas pengguna atau data relasi star.

Jalankan proyek dengan langkah virtual environment, migrasi, dan `runserver` pada bagian **Cara Menjalankan Proyek**. Untuk pemeriksaan Tugas 4 dari direktori proyek, jalankan:

```powershell
python manage.py check
python manage.py test main
```

Jika virtual environment belum diaktifkan, ganti `python` dengan `.\env\Scripts\python.exe`.

## Progres Mingguan

| Periode | Progres |
| --- | --- |
| Hingga 2 September 2026 | Setup Django, Profile, Git/GitHub dan PWS, serta latihan branch dan pull request tutorial. |
| 6-7 September 2026 | Experience dan Awards statis, tema Summer Splash, logo, crop foto, serta interaksi profil. |
| Tugas Individu 2 | Awards berbasis database, pemindahan Experience, command impor berulang, admin, tests, penghapusan Projects, serta Education Journey pada Profile. |
| Tugas Individu 3 | Experience mendukung create, update, delete, validasi form, data delivery JSON, serta tampilan data setelah proses deserialization JSON. |
| Tugas Individu 4 | Autentikasi dan sesi dari Tutorial 4, hak akses Editor untuk update Experience, serta star/unstar per pengguna dengan CSRF. |

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

   Pada proyek ini, view `get_experiences_json` mengambil queryset Experience sesuai urutan tampilan, lalu `serializers.serialize("json", ...)` mengubah setiap object menjadi teks JSON yang memuat primary key UUID dan field model. Data tersebut dikirim melalui `HttpResponse` dengan content type `application/json`. View `show_experience` kemudian membaca respons itu, melakukan deserialization menjadi object Experience, dan mengirimkannya ke template. Serialization diperlukan karena queryset dan instance model adalah object Python yang tidak dapat langsung dikirim sebagai data HTTP atau dipahami sebagai JSON oleh client.

## Penggunaan AI

- **ChatGPT:** membantu memahami ketentuan, menyusun tahapan/prompt, meninjau laporan, dan memberi masukan desain, sesuai keterangan pengguna.
- **Codex:** membantu implementasi Django dan HTML/CSS, migrasi, command impor, tests, dokumentasi.

Pekerjaan dilakukan bertahap dengan batas lingkup yang eksplisit: audit, model/migrasi, impor data, halaman, validasi, lalu commit. Diff dan staged diff diperiksa agar perubahan lain tidak ikut masuk. Screenshot digunakan sebagai referensi struktur dan ukuran; revisi mencakup layout Experience/Awards, timeline Education, whitespace logo SMA, dan penggunaan logo Fasilkom atas izin pengguna.

Pada Tugas 3, ChatGPT dan Codex digunakan untuk merencanakan implementasi, mengaudit kode, membuat alur CRUD Experience, menerapkan data delivery serta deserialization JSON, menyusun strategi tests, dan memperbarui dokumentasi. Setiap perubahan ditinjau manual, diuji secara lokal, lalu diperiksa pada deployment PWS dan disesuaikan berdasarkan perilaku yang terlihat. Salah satu keterbatasannya adalah deployment PWS sempat tidak langsung menampilkan kode terbaru, sehingga versi yang aktif perlu dipastikan kembali melalui reload dan pemeriksaan manual.

[Ringkasan penggunaan AI Tugas 2](docs/ai-usage-tugas-2.md) memuat prompt dan perubahan penting yang tersedia dalam percakapan Codex. Dokumen tersebut adalah ringkasan, bukan transkrip lengkap. URL percakapan tidak dicantumkan karena tidak tersedia.

[Ringkasan penggunaan AI Tugas 3](docs/ai-usage-tugas-3.md) mencatat audit, implementasi CRUD, data delivery JSON, strategi pengujian, pembaruan dokumentasi, dan keterbatasan verifikasi yang ditemui.

[Ringkasan penggunaan AI Tugas 4](docs/ai-usage-tugas-4.md) menjelaskan peran ChatGPT dan Codex, perubahan terfokus, serta pemeriksaan yang dilakukan untuk autentikasi, hak akses, dan star/unstar Experience.
