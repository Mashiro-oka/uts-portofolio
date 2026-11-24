# Portofolio 'Athif

Portofolio pribadi berbasis Django 5.2 dengan HTML, CSS, dan JavaScript. Pengunjung bisa melihat profil, catatan studi, dan proyek yang sudah dipublikasikan serta mengirim pesan lewat formulir kontak. Dashboard khusus admin digunakan untuk mengelola proyek, gambar, dan pesan.

Aplikasi sudah dirilis di Vercel dengan Supabase sebagai database produksi. Pemilik proyek mengonfirmasi fitur berjalan tanpa kendala setelah deploy.

Lihat [dokumentasi proyek](docs/dokumentasi.md) untuk arsitektur, diagram CRUD, dan alur pesan. [Dokumentasi pengujian](docs/testing.md) mencatat hasil uji lokal dan konfirmasi produksi.

## Jalankan lokal

Proyek menetapkan Python 3.12 untuk deploy. Pastikan perintah `python3 --version` menunjuk ke versi Python yang ingin digunakan, lalu jalankan dari direktori proyek.

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
test -f .env || cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Django membaca `.env` otomatis. Jika `DATABASE_URL` kosong, Django memakai `db.sqlite3`. Kalau `.env` sudah berisi URL Supabase, perintah migrasi dan pembuatan akun akan memakai database tersebut.

| Alamat lokal                                                      | Fungsi             |
| ----------------------------------------------------------------- | ------------------ |
| [127.0.0.1:8000](http://127.0.0.1:8000/)                          | Portofolio publik  |
| [127.0.0.1:8000/admin/login/](http://127.0.0.1:8000/admin/login/) | Login admin        |
| [127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)             | Dashboard proyek   |
| [127.0.0.1:8000/admin/pesan/](http://127.0.0.1:8000/admin/pesan/) | Kotak masuk kontak |

## Kelola portofolio

Akses dashboard diberikan kepada akun admin aktif yang dibuat dengan `python manage.py createsuperuser`.

- Dari dashboard, buat, edit, atau hapus proyek. Centang **Tampilkan di portofolio** untuk memublikasikannya. Draf dan gambarnya hanya dapat diakses oleh admin.
- Isi **URL repositori** bila tersedia. Tautan **Buka repo** akan muncul di kartu dan detail proyek yang terbit.
- Unggah gambar JPG, PNG, atau WebP hingga 2 MB dan 16 megapiksel. Gambar dapat dipertahankan, diganti, atau dihapus melalui form edit. Django menyimpan gambar bersama data proyek di database.
- Pesan dari formulir Kontak tersimpan di menu **Pesan**.
- Login dibatasi 5 percobaan gagal per IP dalam 10 menit terakhir. Formulir Kontak dibatasi 8 pengiriman per IP dalam 60 detik terakhir. Permintaan yang melampaui batas mendapat HTTP `429` dan header `Retry-After`.

## Konfigurasi lingkungan

| Variabel                      | Kegunaan                                                                                                                                  |
| ----------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `DJANGO_DEBUG`                | Gunakan `1` untuk pengembangan lokal dan `0` untuk produksi.                                                                              |
| `DJANGO_SECRET_KEY`           | Kunci Django. Isi dengan nilai unik untuk produksi.                                                                                       |
| `DATABASE_URL`                | URL PostgreSQL Supabase. Kosongkan untuk memakai SQLite lokal.                                                                            |
| `DJANGO_DB_SCHEMA`            | Skema PostgreSQL yang dipakai Django. Nilai bawaan `public`.                                                                              |
| `DJANGO_DB_SSLROOTCERT`       | Jalur opsional ke sertifikat CA yang dipercaya. Jika diisi, PostgreSQL memverifikasi sertifikat dan hostname server dengan `verify-full`. |
| `DJANGO_ALLOWED_HOSTS`        | Host tambahan, dipisahkan dengan koma. Isi hostname tanpa protokol.                                                                       |
| `DJANGO_CSRF_TRUSTED_ORIGINS` | Origin HTTPS tambahan, dipisahkan dengan koma. Isi URL lengkap termasuk protokol.                                                         |

## Hubungkan Supabase

1. Di dashboard Supabase, buka **Connect** dan salin URL **Session pooler** pada port `5432` ke `DATABASE_URL`. Gunakan percent encoding untuk karakter khusus pada kata sandi. Django mengaktifkan TLS pada koneksi ini.
2. Untuk database yang sudah berisi tabel proyek, gunakan skema yang sama melalui `DJANGO_DB_SCHEMA`. Untuk instalasi baru, kamu bisa membuat skema khusus melalui SQL Editor, misalnya `CREATE SCHEMA athif;`, lalu isi `DJANGO_DB_SCHEMA=athif`. Biarkan skema khusus ini di luar daftar **Exposed schemas** jika Data API Supabase diaktifkan.
3. Jalankan `python manage.py migrate` melalui role pemilik tabel, lalu `python manage.py createsuperuser` jika akun admin belum tersedia di database tersebut. Migrasi `0003` membuat tabel pembatas pengiriman dan mencabut grant langsung ke `PUBLIC`, `anon`, dan `authenticated` pada tabel proyek, pesan, dan autentikasi Django. Pastikan tabel-tabel tersebut tidak ditawarkan melalui Data API. Jika Data API tidak dibutuhkan di proyek Supabase ini, nonaktifkan di pengaturannya.

[Dokumentasi koneksi PostgreSQL Supabase](https://supabase.com/docs/guides/database/connecting-to-postgres)

## Deploy manual ke Vercel

Gunakan langkah ini saat menyiapkan instalasi baru di Vercel.

1. Impor repositori dari dashboard Vercel. Pilih direktori akar yang berisi `manage.py` dan gunakan konfigurasi Django yang terdeteksi. Aset statis dikumpulkan melalui `STATIC_ROOT`.
2. Isi environment variables produksi di Vercel. Setel `DJANGO_DEBUG=0`, `DJANGO_SECRET_KEY`, `DATABASE_URL`, serta `DJANGO_DB_SCHEMA` bila memakai skema khusus. Buat kunci Django dengan `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`. Jika memakai domain kustom, isi juga `DJANGO_ALLOWED_HOSTS` dan `DJANGO_CSRF_TRUSTED_ORIGINS`.
3. Terapkan migrasi ke database produksi sebelum deploy. Sesudah deploy, uji halaman publik, login admin, publikasi proyek, unggahan gambar, dan formulir kontak. Saat berjalan di Vercel, Django mematikan mode debug dan mengirim header HSTS selama 300 detik.

Untuk pembaruan situs yang sudah live, uji perubahan secara lokal, terapkan migrasi baru ke Supabase jika ada, lalu deploy versi terbaru. Setelah itu, ulangi [pengecekan produksi](docs/testing.md#4-cek-ulang-setelah-deploy).

[Contoh deployment Django di Vercel](https://vercel.com/templates/python/django-hello-world)

## Pengujian

```sh
DATABASE_URL= DJANGO_DEBUG=1 VERCEL=0 python manage.py test portfolio
```

Perintah ini memakai database uji SQLite, sehingga aman dijalankan saat `.env` berisi alamat Supabase. Lihat [docs/testing.md](docs/testing.md) untuk cakupan uji dan pengecekan sebelum rilis.

## Struktur proyek

```text
config/                     Pengaturan Django, URL, dan WSGI
portfolio/                  Model, formulir, view, dan migrasi
templates/
├── home.html               Beranda dan detail proyek
├── login.html              Login admin
└── dashboard.html          Proyek dan pesan untuk admin
static/portfolio/
├── css/style.css           Seluruh gaya antarmuka
├── js/site.js              Menu HP dan pratinjau unggahan
└── images/                 Logo onigiri dan ilustrasi Okayu
docs/
├── dokumentasi.md          Arsitektur dan diagram alur
└── testing.md              Hasil dan panduan uji
manage.py                   Perintah pengelolaan Django
requirements.txt            Dependensi Python
.env.example                Contoh pengaturan lingkungan
```

`.env`, virtual environment, database SQLite, hasil `collectstatic`, dan gambar sumber di `assets/source/` disimpan secara lokal dan diabaikan Git. Aset yang dipakai situs berada di `static/portfolio/images/`.

---

## Kredit Aset Visual

- **Ilustrasi Nekomata Okayu:** [@Kukie_nyan](https://ko-fi.com/kukie_nyan)
  - Menggunakan versi ilustrasi yang dipublikasikan secara gratis oleh kreatornya, bukan versi berbayar.
- **Ikon onigiri:** [Noto Emoji](https://github.com/googlefonts/noto-emoji)

Seluruh hak cipta atas aset visual tetap menjadi milik pemegang hak cipta masing-masing.

Proyek ini dibuat untuk kebutuhan pembelajaran dan praktikum Ujian Tengah Semester (UTS), serta tidak ditujukan untuk kepentingan komersial.
