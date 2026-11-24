# Pengujian Portofolio 'Athif

Dokumen ini mencatat hasil uji lokal, konfirmasi produksi dari pemilik proyek, dan langkah untuk mengulang pengujian. Lihat [dokumentasi proyek](dokumentasi.md) untuk arsitektur dan diagram alur.

## 1. Jalankan pemeriksaan lokal

Dari direktori proyek, aktifkan virtual environment yang sudah berisi dependensi dari `requirements.txt`.

```sh
source .venv/bin/activate
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py test portfolio
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py check
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py makemigrations --check --dry-run
```

`DATABASE_URL=` memilih SQLite untuk perintah tersebut meskipun `.env` menunjuk ke Supabase. Test runner Django membuat dan membuang database uji terpisah. `makemigrations --check --dry-run` memeriksa apakah model dan riwayat migrasi cocok.

Jika Node.js tersedia, cek sintaks JavaScript.

```sh
node --check static/portfolio/js/site.js
```

## 2. Hasil yang sudah diverifikasi

Uji lokal ini dijalankan dengan database SQLite sementara. Konfirmasi dari penggunaan di Vercel dan Supabase dicatat pada bagian produksi di bawah.

| Pemeriksaan                                                     | Hasil                                                                                                                                                                           |
| --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Dua uji otomatis di [portfolio/tests.py](../portfolio/tests.py) | Lulus. Uji mencakup batas kontak saat jam berganti menit, pemisahan IP, batas lima kali gagal login, `Retry-After`, dan pemulihan setelah batas berakhir.                       |
| Akses publik dan admin                                          | Lulus. Beranda tersedia tanpa sesi, tautan admin tidak tampil di beranda, kotak masuk mengarahkan pengunjung ke login, dan login serta logout admin berfungsi.                  |
| CSRF pada kontak                                                | Lulus. Django menolak POST tanpa token CSRF. Pengiriman yang valid dengan token diterima.                                                                                       |
| CRUD dan publikasi                                              | Lulus. Proyek dapat dibuat, diedit, dipublikasikan, dan dihapus. Pengunjung tidak dapat membuka detail atau gambar draf. URL repositori tampil pada proyek yang terbit.         |
| Unggah dan penghapusan gambar                                   | Lulus. PNG valid tersimpan dan tampil, file rusak ditolak, gambar dapat dihapus serta diunggah kembali, dan penghapusan proyek ikut menghapus gambar.                           |
| Form kontak dan kotak masuk                                     | Lulus. Pesan valid tersimpan dan tampil di dashboard. Email tidak valid dan isian pada honeypot tidak menghasilkan rekaman.                                                     |
| Pemeriksaan Django dan aset                                     | Lulus. Migrasi dari database baru berhasil, tidak ada migrasi model yang tertunda, sintaks JavaScript valid, dan `collectstatic` memuat CSS, JavaScript, logo, serta ilustrasi. |

### Perilaku batas yang diuji

| Aksi                  | Jumlah yang diterima per IP               | Saat batas terlampaui                                                                                           |
| --------------------- | ----------------------------------------- | --------------------------------------------------------------------------------------------------------------- |
| Kirim formulir kontak | 8 permintaan dalam 60 detik terakhir      | Permintaan ke-9 mendapat HTTP `429` dan tidak menambah pesan. Pergantian menit pada jam tidak mereset hitungan. |
| Login admin           | 5 percobaan gagal dalam 10 menit terakhir | Percobaan ke-6 mendapat HTTP `429` meskipun sandinya benar. Login berhasil tidak mengurangi jatah gagal.        |

`Retry-After` menunjukkan sisa waktu dalam detik sampai slot paling lama tersedia. Permintaan yang ditolak tidak memperpanjang waktu tunggu. Uji otomatis mengendalikan waktu pada SQLite, sehingga pemeriksaan batas tidak perlu menunggu sungguhan.

## 3. Pengujian manual di browser

Untuk mencoba tanpa database produksi, gunakan SQLite lokal melalui perintah berikut. Jalankan `createsuperuser` hanya jika SQLite lokal belum punya akun admin.

```sh
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py migrate
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py createsuperuser
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py runserver
```

Buka `http://127.0.0.1:8000/`. Pakai jendela privat untuk pengujian publik dan jendela biasa untuk dashboard admin.

| Bagian              | Langkah dan hasil yang diharapkan                                                                                                                                                                                                    |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Desktop dan tablet  | Coba lebar 1280 dan 768 px. Pastikan navbar, banner, panel, dan form mudah dibaca. Menu dan konten tidak menyebabkan scroll horizontal.                                                                                              |
| HP                  | Coba lebar 360 dan 390 px atau HP Android. Tombol hamburger tampil di kanan. Pilih tautan untuk memastikan menu menutup dan halaman menuju bagian yang benar. Buka lagi lalu usap halaman untuk memastikan menu menutup saat scroll. |
| Keyboard            | Gunakan Tab untuk berpindah kontrol. Fokus terlihat. Tombol hamburger dapat dibuka lewat keyboard dan ditutup dengan Escape saat layout HP aktif.                                                                                    |
| Login               | Buka `/admin/login/`. Dengan satu kata sandi salah, periksa pesan tampil sekali dalam kotak ungu. Masukkan kredensial benar dan pastikan diarahkan ke dashboard. Hindari menguji batas berulang pada akun produksi.                  |
| Draf dan repositori | Buat proyek draf dengan URL repo dan gambar. Pastikan draf hanya terlihat di dashboard. Terbitkan, lalu buka kartu, detail, gambar, dan **Buka repo** dari jendela publik.                                                           |
| Editor gambar       | Pilih gambar untuk melihat pratinjau. Simpan, ganti gambar, lalu hapus gambar dan cek kembali halaman proyek.                                                                                                                        |
| Pesan               | Kirim satu pesan uji dengan isi yang mudah dikenali. Periksa notifikasi di beranda dan cari pesan yang sama di `/admin/pesan/`.                                                                                                      |

Hentikan server lokal dengan Ctrl+C setelah pengujian.

## 4. Cek ulang setelah deploy

**Status rilis:** layanan sudah live di Vercel dengan database Supabase. Pemilik proyek mengonfirmasi fitur berjalan tanpa kendala setelah deploy. Konfirmasi ini mencatat hasil penggunaan produksi yang dilaporkan. Detail per skenario, perangkat, dan hasil pemeriksaan izin database dapat dicatat saat pengecekan berikutnya.

Gunakan langkah berikut setelah menerbitkan pembaruan.

1. Pastikan deploy memakai `DATABASE_URL` dan `DJANGO_DB_SCHEMA` yang benar. Dari lingkungan yang tersambung ke database tujuan, jalankan `python manage.py showmigrations portfolio` dan cek migrasi `0001`, `0002`, dan `0003` bertanda `[X]`.
2. Buka URL hasil deploy dan pastikan beranda, aset, serta login admin bisa dimuat melalui HTTPS.
3. Kirim satu pesan lewat formulir publik dengan penanda yang mudah dicari. Di Supabase Table Editor, buka `portfolio_contactmessage` pada skema yang dikonfigurasi dan cari pesan tersebut. Cocokkan isinya di **Dashboard → Pesan**.
4. Untuk memeriksa izin, verifikasi pengaturan Data API dan grant pada tabel aplikasi. Migrasi `0003` mencabut grant langsung untuk `PUBLIC`, `anon`, dan `authenticated`. Pastikan tabel proyek, pesan, autentikasi, dan sesi tidak dapat diakses melalui Data API oleh role publik.
5. Ulangi cek proyek terbit, gambar, URL repositori, dan menu HP lewat URL deploy. Catat tanggal, URL, perangkat, hasil, dan tangkapan layar jika ada masalah.
