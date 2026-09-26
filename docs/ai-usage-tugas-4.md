# Ringkasan Penggunaan AI - Tugas Individu 4

Dokumen ini merangkum penggunaan AI dalam Tugas Individu 4 berdasarkan pekerjaan yang tersedia dalam percakapan ini. ChatGPT digunakan untuk perencanaan, penafsiran persyaratan, peninjauan, dan panduan debugging. Codex digunakan untuk perubahan kode yang terfokus, penambahan tests, audit implementasi, serta pembaruan dokumentasi. Keputusan akhir dan pemeriksaan hasil tetap menjadi tanggung jawab pengguna.

## Tahapan prompt dan perubahan penting

| Tahap | Arahan | Hasil |
| --- | --- | --- |
| Peran Editor | Pertahankan aturan superuser untuk tambah/hapus, berikan izin update kepada anggota grup `Editor`, dan sesuaikan kontrol UI. | Helper keanggotaan grup dan decorator akses Editor/superuser ditambahkan; view update dan tombol Edit mengikuti aturan baru. |
| Pengujian peran | Pastikan Editor dapat update dan star/unstar, tetapi menerima 403 untuk tambah/hapus. | Test otorisasi Editor ditambahkan tanpa mengubah aturan autentikasi, JSON, atau star yang sudah ada. |
| Audit akhir | Periksa persyaratan Tugas 4 dan tambah test hanya untuk celah penting. | Test dengan pemeriksaan CSRF aktif ditambahkan untuk membuktikan POST star tanpa token ditolak dan POST bertoken diterima. |
| Dokumentasi | Jelaskan fitur dan cara menjalankan proyek. | README mendapat ringkasan Tugas 4; dokumen ini mengikuti format disclosure Tugas 2 dan 3. |

## Pemeriksaan dan batasan

Audit meninjau view, URL, template, middleware, serta tests untuk akses tamu, pengguna biasa, Editor, dan superuser; autentikasi/sesi; CSRF; dan field JSON. Perintah `python manage.py check` dan `python manage.py test main` dijalankan dengan interpreter virtual environment proyek. Pengujian otomatis memeriksa perilaku lokal; dokumen ini tidak mengklaim verifikasi deployment atau pemeriksaan browser manual untuk Tugas 4.
