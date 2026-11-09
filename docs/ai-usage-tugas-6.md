# Ringkasan Penggunaan AI - Tugas Individu 6

ChatGPT membantu menafsirkan tugas, menyusun rencana arsitektur/implementasi dan prompt, menjelaskan konsep, serta meninjau laporan Codex dan keputusan implementasi. Codex membantu audit repository secara read-only, implementasi AJAX editing melalui endpoint PATCH DRF yang sudah ada, penambahan test API terfokus, pemeriksaan JavaScript/Django, serta penyusunan dokumentasi dan draf jawaban reflektif Tugas 6 di README.

Strategi prompt menetapkan target `Experience`, batas file, empat peran dan izin, perlindungan CSRF/XSS, kompatibilitas route serta fitur lama, dan ekspektasi pengujian. Pekerjaan dipisahkan menjadi audit, implementasi, review, dan dokumentasi, dengan larangan perubahan tidak terkait, migrasi baru, commit/push, dan deployment selama implementasi. Sebelum dokumentasi, Git diperiksa untuk memastikan implementasi sudah berada pada commit `2ba3419` (`feat(experience): add AJAX editing through DRF`), sehingga perubahan README tidak dicampur dengan fitur.

Saya menentukan lingkup tugas, meninjau dan menyetujui rencana implementasi, mengevaluasi kode serta laporan tests, mengawasi keputusan implementasi, dan meninjau keterbatasan verifikasi. Kode dan jawaban yang dibantu AI tidak saya klaim sebagai tulisan mandiri untuk setiap barisnya. Saya tetap bertanggung jawab memahami hasilnya dan memastikan kesesuaiannya dengan tugas; laporan otomatis tidak menggantikan pemeriksaan browser yang belum selesai.

| Alat | Tugas | Contoh prompt/instruksi representatif | Hasil | Metode verifikasi |
| --- | --- | --- | --- | --- |
| ChatGPT | Interpretasi, konsep, dan perencanaan | Tetapkan Experience sebagai target; pisahkan audit, PATCH editing, dan dokumentasi. | Rencana fase, penjelasan konsep, dan prompt terarah | Ditinjau mahasiswa terhadap ketentuan dan laporan implementasi |
| ChatGPT | Review keputusan dan laporan Codex | Evaluasi pilihan halaman edit lama, izin peran, hasil tests, dan keterbatasan browser. | Masukan untuk supervisi implementasi | Mahasiswa menilai rekomendasi dan menentukan lingkup lanjut |
| Codex | Audit read-only | “Do not assume this is the only gap.” dan “This phase is READ-ONLY.” | Pemetaan source, fitur yang ada, dan celah AJAX editing | Inspeksi Git, serializer, view, URL, template, JavaScript, dan tests |
| Codex | AJAX editing | “Implement editing through the existing DRF detail endpoint using PATCH.” | Form edit memakai fetch JSON/CSRF dan toast tanpa submit halaman biasa | Review diff, tests API, dan harness JavaScript |
| Codex | Test dan verifikasi | “Do not duplicate tests that already exist.” serta pertahankan test sesi nyata tanpa token CSRF | Dua test tambahan; hasil Phase 1 tercantum di README | 139 Django tests, delapan skenario JavaScript, syntax/system checks, dan pemeriksaan whitespace |
| Codex | Dokumentasi TI6 | “Only modify README.md.” dan jangan mengklaim verifikasi browser berhasil | Dokumentasi implementasi, empat jawaban reflektif, disclosure, dan log ringkas | Perbandingan dengan source, pertanyaan yang diberikan mahasiswa, serta diff README |
| Codex | Audit akhir dan penutupan celah | “Implement the smallest safe correction.” dan jangan commit/push/deploy otomatis | Sinkronisasi form setelah PATCH, test spoofing star/CSRF tambahan, dan penjelasan deserialization | 141 Django tests, dua test Node tersimpan, 20 skenario frontend sementara, checks, HTTP lokal, serta GitHub publik anonim |

Tabel ini merangkum instruksi representatif, bukan transkrip lengkap. Teks persis empat pertanyaan reflektif dan daftar persyaratan audit akhir diberikan mahasiswa dalam percakapan. Audit akhir menggunakan daftar tersebut sebagai acuan. Tidak ada URL percakapan AI yang tersedia untuk ditautkan, sehingga tidak dibuat tautan fiktif.

## Evaluasi kritis dan perbaikan

AI dapat mengira fitur sudah lengkap hanya karena endpoint tersedia, padahal alur frontend belum memakainya, atau menganggap test API membuktikan perilaku browser. Pada TI6, audit source membedakan dukungan PUT/PATCH di server dari form edit yang semula masih memakai POST biasa. Mahasiswa menetapkan agar halaman edit lama dipertahankan, menyetujui rencana PATCH, dan menilai laporan tests serta batasan hasilnya. Keputusan ini menjaga perubahan tetap kecil dan mempertahankan kompatibilitas.

Audit akhir menemukan bahwa setelah PATCH sukses, form dan teks pengantar belum diselaraskan dengan respons tersimpan, termasuk hasil sanitasi server. Perbaikan menggunakan nilai respons dan `textContent`, disertai test JavaScript untuk pembaruan tampilan dan retensi input saat gagal. Test API juga diperkuat dengan relasi star yang sudah ada pada penolakan write, percobaan identitas pemberi star palsu, dan request sesi nyata bertoken. Ini merupakan perbaikan berbantuan Codex yang masih perlu dievaluasi mahasiswa, bukan klaim mahasiswa menulis seluruh kode sendiri.

Tests otomatis memiliki batas: mock DOM/fetch tidak membuktikan layout, fokus, popover, kebijakan cookie browser, atau tidak adanya navigasi pada browser sebenarnya. Otomasi browser TI6 sebelumnya tidak dapat diselesaikan karena host browser tidak tersedia dan fallback tidak dapat memastikan URL. Pemeriksaan HTTP lokal dapat membuktikan respons serta rendering HTML server, tetapi tidak menggantikan pengamatan visual. Hasil dan keterbatasan tersebut dipisahkan dalam README agar keluaran AI tidak diterima sebagai bukti yang melebihi pemeriksaan aktual.

Lihat [pengujian dan keterbatasan TI6 di README](../README.md#pengujian-dan-keterbatasan) untuk rincian hasil Phase 1.

## Klarifikasi prasyarat Tutorial 07

Mahasiswa mengonfirmasi bahwa Tutorial 07 telah diselesaikan dan dikumpulkan pada 2 November 2026 melalui implementasi DRF Experience, dengan commit penyelesaian `3ad43215dbeafc744992354c140e7bb6b809ed0a`. Tidak ada halaman tutorial terpisah yang diwajibkan. Ketidakpastian audit sebelumnya berasal dari belum adanya pemetaan eksplisit tersebut dalam dokumentasi, bukan dari endpoint yang tidak bekerja. Klarifikasi ini dicocokkan dengan riwayat serializer/API/permissions/frontend/tests yang sudah ada, tests regresi, dan respons HTTP Experience/Browsable API yang berhasil.
