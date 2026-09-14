# Ringkasan Penggunaan AI - Tugas Individu 2

Dokumen ini adalah ringkasan. Ringkasan berikut bersumber dari permintaan dan hasil kerja yang tersedia dalam percakapan Codex. Peran ChatGPT dijelaskan oleh pengguna: membantu memahami ketentuan, menyusun tahapan/prompt, meninjau laporan, dan memberi masukan desain. 

## Tahapan prompt dan perubahan penting

Empat butir berikut menggabungkan beberapa permintaan terkait:

| Tahap | Ringkasan arahan pengguna | Hasil yang tersedia dalam percakapan |
| --- | --- | --- |
| 1. Audit dan pemetaan | Periksa Git, model, migrasi, dan data; petakan pemindahan Experience/Awards dengan desain Profile sebagai acuan. | Ditemukan satu Experience Calculus dan Project kosong; fitur Projects yang sempat dibuat kemudian dibatalkan. |
| 2. Implementasi Awards | Buat model, migrasi, impor berulang dengan dry-run dan pemeriksaan konflik, serta halaman dengan loop DTL dan layout lama. | Dua Award tersimpan tanpa duplikasi dan tampil di `/awards/`; navbar memakai named URL. |
| 3. Pemindahan dan pembersihan | Pindahkan Experience tanpa kehilangan ID Calculus, hapus section lama dan Projects yang kosong, lalu lengkapi admin dan tests. | Empat Experience dan dua Award tetap utuh; admin mendukung keduanya. Deskripsi Calculus diselaraskan dengan izin pengguna, sedangkan ID, kategori, dan timestamp dipertahankan. |
| 4. Education Journey | Tambahkan dan revisi timeline berdasarkan screenshot, gunakan logo asli, serta pertahankan teks terbaru pengguna. | Education memakai context, logo SMA dan Fasilkom, serta CSS responsif. Science track dan periode SMA 2022-2025 dikonfirmasi pengguna. |

## Strategi kerja

Permintaan dibagi menjadi tahap kecil dengan daftar file yang boleh berubah, larangan perubahan data/commit pada tahap tertentu, dan validasi sebelum melanjutkan. Codex memeriksa diff sebelum staging dan staged diff sebelum commit. Perubahan `main/admin.py` dipertahankan sampai pengguna secara eksplisit mengizinkan penggantian ProjectAdmin. Migrasi yang sudah diterapkan tidak ditulis ulang; pembatalan Projects memakai migrasi baru.

Screenshot menjadi referensi desain, bukan sumber identitas orang lain. Revisi ukuran, alignment, teks, logo, dan responsivitas mengikuti arahan pengguna. File logo asli dipakai tanpa menggambar ulang; penggunaan logo Fasilkom pada Education mendapat izin eksplisit.

## Bukti pemeriksaan dan batasannya

- Pemeriksaan otomatis terakhir sebelum pembaruan dokumen: seluruh 23 tests lulus, `manage.py check` dan `git diff --check` lulus. Ada warning direktori `staticfiles` belum tersedia; konfigurasi tidak diubah untuk menyembunyikannya.
- Django test client memverifikasi HTTP 200 untuk `/`, `/experience/`, dan `/awards/`. URL logo Education diperiksa melalui staticfiles handler. Pemeriksaan ini bukan sesi browser.
- Impor Awards: 2 dibuat lalu 2 dilewati. Impor Experience: 3 dibuat dan 1 direkonsiliasi, lalu 4 dilewati. Tests impor Experience mencakup konflik, ambiguitas, aset hilang, rollback, dan data lain yang harus tetap utuh.
- Sebelum section lama dihapus, HTML hasil render Experience/Awards dibandingkan dengan sumber setelah normalisasi whitespace/entitas. Saat pembersihan, hash seluruh data Experience dan Award sebelum/sesudah cocok.
- Pengguna memberikan screenshot, revisi teks/desain, dan laporan bahwa Ctrl+F5 menyelesaikan tampilan CSS yang tertinggal. Tidak ada bukti pemeriksaan visual mobile atau interaksi pause secara lengkap. Codex tidak memiliki browser untuk memverifikasinya.
- Tests tidak dijalankan ulang untuk perubahan dokumentasi saja. Perintah setup dan `createsuperuser` didokumentasikan sebagai petunjuk; penyusunan dokumen tidak menjalankannya atau membuat kredensial.

## Commit terkait yang tercatat

| Hash | Perubahan |
| --- | --- |
| `b846291` | Model dan migrasi Award |
| `e01b89e` | Command impor Awards |
| `3f2041e` | Halaman Awards dengan layout portfolio lama |
| `96b791c` | Field tampilan dan migrasi Experience |
| `a06b34d` | Pemindahan Experience dan command impor/tests |
| `974c902` | Penghapusan Projects, pemisahan halaman, admin, dan tests Awards |
| `6546554` | Education timeline dengan logo institusi |

Tidak ada push atau deployment yang dilakukan pada rangkaian kerja ini. Validasi lingkungan PWS dan URL percakapan AI belum tersedia. Lihat [README](../README.md) untuk setup dan refleksi Tugas 2.
