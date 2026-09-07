# Portofolio David Mesakh

- **Nama:** David Mesakh
- **NPM:** 2506604503
- **Kelas:** C

## Deskripsi Tugas Individu

Website portofolio pribadi untuk mata kuliah Pemrograman Berbasis Platform (PBP), Fasilkom Universitas Indonesia. Proyek ini melanjutkan Tutorial 0 dan Tutorial 1 dengan halaman HTML5 dan CSS3 yang disajikan melalui Django.

Halaman memuat Profile, Experience, dan Awards dengan tema biru Summer Splash serta layout responsif. Foto Profile terhubung ke Instagram melalui bubble "Contact me!" dan animasi wobble yang mendukung preferensi reduced motion. Konten portofolio masih ditulis langsung dalam HTML.

## Cara Menjalankan Proyek

Jalankan perintah berikut melalui PowerShell. Python yang digunakan saat setup awal adalah 3.13.7.

1. Clone repositori dan masuk ke folder proyek. Lewati langkah ini jika proyek sudah tersedia secara lokal.

   ```powershell
   git clone https://github.com/davemesakh/myportofolio.git
   cd myportofolio
   ```

2. Buat virtual environment jika belum ada, lalu aktifkan.

   ```powershell
   python -m venv env
   .\env\Scripts\Activate.ps1
   ```

3. Pasang dependensi dan jalankan server lokal.

   ```powershell
   python -m pip install -r requirements.txt
   python manage.py runserver
   ```

4. Buka http://127.0.0.1:8000/ di browser. Hentikan server dengan `Ctrl+C`.

Untuk pengembangan lokal, gunakan mode nonproduksi (`PRODUCTION=False`). Jika aktivasi virtual environment diblokir PowerShell, perintah Python dapat dijalankan langsung melalui `.\env\Scripts\python.exe`, misalnya `.\env\Scripts\python.exe manage.py runserver`.

## Progres Mingguan

| Periode | Progres |
| --- | --- |
| Hingga 2 September 2026 | Setup proyek Django, halaman Profile, konfigurasi Git/GitHub dan PWS, serta latihan branch dan pull request dari tutorial. |
| 6-7 September 2026 | Penambahan Experience dan Awards, revisi layout serta crop foto, interaksi Instagram pada foto Profile, tema Summer Splash, logo organisasi, peningkatan ukuran teks kecil|

## Pertanyaan Reflektif

### Tugas 1

1. **Pada Tutorial dan Tugas 1, Anda diberi kebebasan untuk menentukan tampilan dari website portofolio Anda. Saat Anda merancang struktur HTML yang digunakan, apakah Anda menggunakan elemen semantik HTML5 seperti `<section>`, `<article>`, atau `<aside>`? Jika iya, bagaimana elemen tersebut membantu Anda dalam membuat *static web*? Jika tidak, mengapa tanpa elemen tersebut sudah memenuhi kebutuhan desain Anda?**

   Ya, saya menggunakan `<section>` untuk membagi Profile, Experience, dan Awards, serta `<article>` untuk setiap pengalaman dan penghargaan yang dapat dipahami secara mandiri. Elemen `<header>`, `<nav>`, `<main>`, dan `<footer>` menandai bagian pembuka, navigasi, konten utama, dan penutup halaman. Struktur ini membantu saya memahami fungsi setiap bagian, memudahkan penambahan konten, serta membantu pembaca layar mengenali bagian halaman. Saya tidak menggunakan `<aside>` karena belum ada konten sampingan yang memerlukannya.

2. **Ketika Anda mengatur CSS Anda agar tetap *responsive*, tantangan tata letak apa yang Anda temukan? Bagaimana Anda mengevaluasi elemen mana yang harus diubah posisinya atau diprioritaskan ukurannya saat berpindah dari tampilan desktop ke mobile?**

   Tantangannya adalah menjaga teks dan foto tetap rapi saat layar mengecil. Saya memprioritaskan keterbacaan teks: pada mobile, periode Experience diletakkan di bawah jabatan dan deskripsinya dibuat selebar area konten. Pada Awards, susunan dua kolom diubah menjadi teks lalu foto agar tidak terlalu sempit.

3. **Website yang Anda buat saat ini adalah *static web* murni. Batasan apa yang Anda rasakan saat mencoba menyajikan informasi pada portofolio Anda secara optimal? Berdasarkan batasan tersebut, fungsionalitas dinamis apa yang paling ingin Anda persiapkan dan tambahkan pada iterasi proyek selanjutnya?**

   Batasan yang saya rasakan adalah pembaruan informasi masih harus dilakukan dengan mengedit HTML secara langsung, termasuk menambah struktur elemen saat menambahkan item baru. Fitur pengelolaan konten berbasis database dapat menjadi pengembangan berikutnya agar informasi bisa diperbarui melalui formulir tanpa mengedit HTML setiap kali.

## Penggunaan AI

### Tools dan Bagian yang Dibantu

- **ChatGPT:** membantu memahami ketentuan tugas dan mendiskusikan usulan awal pengembangan portofolio.
- **Codex:** membantu implementasi dan revisi HTML/CSS, layout responsif, penanganan foto dan logo, interaksi Instagram, palet warna, keterbacaan teks, diagnosis pemuatan CSS, pemeriksaan lokal, serta penyusunan dokumentasi dan redaksi jawaban reflektif. AI membantu merapikan data tersebut

### Strategi Prompting

Saya memberikan konteks proyek, ketentuan tugas, data pribadi yang akan ditampilkan, dan batasan seperti penggunaan HTML5/CSS3. Permintaan dibuat bertahap dengan arahan desktop/mobile dan referensi visual. Saya memberikan koreksi ketika hasil belum sesuai, misalnya pada kepadatan Experience, crop foto Awards, dan ukuran teks. Commit dan push juga dibatasi sesuai instruksi saya.

### Evaluasi dan Perbaikan Manual

Saya memeriksa hasil di browser dan memberikan revisi desain. Ketika permintaan foto 1:1 ditampilkan sebagai bingkai tanpa crop, saya mengoreksinya agar foto benar-benar di-crop persegi. Saya juga meminta diagnosis saat HTML terbaru muncul tanpa styling yang sesuai. Revisi kode tersebut dibantu Codex; edit manual saya mencakup teks nama dan judul, sedangkan aset foto dan logo saya sediakan sendiri.

AI tidak selalu mengerti arahan visual dengan tepat. Pemeriksaan kode, respons HTTP, dan kontras warna membantu verifikasi, tetapi tidak menggantikan pengujian tampilan dan interaksi di browser. Codex belum melakukan pengujian visual browser secara langsung. 

### Chat atau Log Prompting

1. **Menambahkan Experience berdasarkan data pribadi**  
   “Tambahkan section Experience setelah Profile dengan minimal tiga pengalaman. Tanyakan datanya sebelum mengedit dan jangan mengarang fakta. Gunakan HTML semantik, CSS responsif, serta navigasi menuju section.”

2. **Mendiagnosis styling yang tidak muncul**  
   “HTML Experience sudah berubah, tetapi styling belum terlihat. Periksa template, selector, sintaks CSS, file yang disajikan Django melalui `findstatic`, dan kemungkinan cache. Perbaiki penyebabnya tanpa menumpuk CSS override.”

3. **Merevisi Experience dengan logo organisasi**  
   “Tambahkan logo organisasi di kiri dan periode di kanan atas pada desktop. Pada mobile, letakkan periode di bawah jabatan dan deskripsi selebar konten. Gunakan Django static tag, pertahankan seluruh data, dan verifikasi pemuatan logo serta CSS.”

