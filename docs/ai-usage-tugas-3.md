# Ringkasan Penggunaan AI - Tugas Individu 3

Dokumen ini merangkum penggunaan ChatGPT dan Codex selama pengerjaan Tugas Individu 3. ChatGPT membantu memahami ketentuan, menyusun tahap kerja, meninjau hasil, dan memberi masukan. Codex membantu audit kode, implementasi, pengujian, dan dokumentasi. Keputusan akhir serta pemeriksaan hasil tetap dilakukan oleh pengguna.

## Tahapan prompt dan perubahan penting

| Tahap | Ringkasan arahan pengguna | Hasil |
| --- | --- | --- |
| 1. Audit | Periksa model, form, view, URL, template, dan persyaratan Tugas 3 tanpa mengubah berkas. | Ditemukan bahwa Experience sudah tampil dari database, tetapi belum memiliki form CRUD dan data delivery JSON. |
| 2. Create Experience | Buat `ExperienceForm`, validasi tanggal, view create, URL, template form, tombol tambah, dan tests. | Experience dapat dibuat melalui form tanpa mengekspos UUID, timestamp otomatis, field tanggal lama, atau `source_key`. |
| 3. Update dan delete | Gunakan template form yang sama untuk update dan tambahkan penghapusan POST-only berbasis UUID. | Experience dapat diperbarui dan dihapus, sementara `source_key` internal tetap dipertahankan saat update. |
| 4. Data delivery JSON | Tambahkan endpoint JSON dan tampilkan Experience setelah serialization serta deserialization sesuai pola Tutorial 03. | `/experience/json/` mengembalikan data terurut dan halaman Experience merender kembali object hasil deserialization. |
| 5. Dokumentasi | Tambahkan progres, jawaban refleksi, dan disclosure AI tanpa mengubah aplikasi. | README dan ringkasan penggunaan AI Tugas 3 diperbarui. |

## Strategi kerja

Pekerjaan dibagi menjadi fase kecil agar perubahan form, CRUD, JSON, dan dokumentasi dapat diperiksa secara terpisah. Setiap fase menentukan berkas yang boleh berubah dan melarang commit sampai pengguna memberi izin. Implementasi memakai pola yang sudah ada pada Award, seperti `ModelForm`, CSRF, named URL, `get_object_or_404`, dan `require_POST`, agar struktur proyek tetap konsisten.

Form hanya mengekspos field Experience yang digunakan oleh tampilan. Validasi tambahan menolak bulan tanpa tahun, pengalaman aktif yang memiliki tanggal akhir, dan tanggal akhir yang lebih awal daripada tanggal mulai. Data JSON diurutkan berdasarkan `display_order` dan UUID sebelum diserialisasi. Halaman Experience kemudian melakukan deserialization server-side sesuai pola Tutorial 03 tanpa mengubah layout yang sudah ada.

## Pemeriksaan dan penyesuaian manual

- Perubahan kode ditinjau melalui diff dan diperiksa dengan `git diff --check`.
- `manage.py check` lulus tanpa issue dan `makemigrations --check --dry-run` melaporkan tidak ada perubahan model.
- Seluruh 46 tests lulus setelah implementasi form, CRUD, endpoint JSON, urutan data, UUID, dan tampilan hasil deserialization.
- Pengguna memeriksa deployment PWS dan menyesuaikan proses berdasarkan perilaku yang terlihat.
- Deployment PWS sempat tidak langsung mencerminkan kode terbaru. Versi aktif perlu dipastikan melalui reload dan pemeriksaan manual sebelum hasil dianggap sesuai.
- Warning bahwa direktori `staticfiles` belum tersedia tetap muncul saat tests. Warning tersebut sudah ada sebelumnya dan tidak disembunyikan melalui perubahan konfigurasi.

