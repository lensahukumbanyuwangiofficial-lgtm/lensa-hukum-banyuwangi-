LENSA HUKUM BANYUWANGI — WEBSITE + CMS REDAKSI
Versi penyempurnaan: 1.1

FITUR
- Website responsif untuk desktop dan ponsel.
- CMS di /admin menggunakan Sveltia CMS dan penyimpanan konten di GitHub.
- Manajemen berita, kategori, halaman Tentang, Pedoman Redaksi, Kontak, dan Info Situs.
- Status Draf/Terbit, berita utama, pilihan redaksi, foto utama, sumber/rujukan.
- Pencarian berita, navigasi rubrik, berita terkait, tombol berbagi dan salin tautan.
- SEO dasar: meta description, Open Graph, sitemap.xml, robots.txt, dan feed.xml.
- Header keamanan dasar dan halaman admin noindex.
- Generator statis Python tanpa pustaka tambahan.

ARSITEKTUR DAN ALUR PUBLIKASI
1. Redaktur masuk ke /admin melalui autentikasi GitHub.
2. Redaktur membuat atau mengedit berita. Simpan sebagai Draf untuk pemeriksaan.
3. Setelah verifikasi dan persetujuan editor, ubah status menjadi Terbit lalu Publish.
4. CMS menyimpan perubahan ke repositori GitHub.
5. Netlify menjalankan build.py dan menerbitkan situs dari folder dist/.

PENTING: CMS ini bukan sistem login mandiri. Hak akses redaktur mengikuti izin GitHub pada repositori. Jangan membagikan Personal Access Token melalui chat, dokumen publik, atau kepada orang yang tidak berwenang. Cabut token yang bocor dan batasi izin token hanya ke repositori ini.

PERSIAPAN DEPLOY
1. Buat repositori GitHub baru. Unggah isi folder proyek ini; jangan mengunggah folder dist sebagai sumber utama.
2. Edit admin/config.yml:
   - backend.repo: GANTI-USERNAME/GANTI-NAMA-REPO
   - site_url dan display_url: alamat HTTPS situs yang benar-benar aktif.
3. Pada Netlify pilih Add new site > Import an existing project > GitHub, lalu pilih repositori.
4. Build command: python3 build.py. Publish directory: dist.
5. Setelah deploy berhasil, uji alamat situs dan /admin.
6. Masuk ke Pengaturan > Info situs dan isi URL resmi situs, email, kontak, alamat, serta wilayah liputan.
7. Kirim sitemap.xml ke Google Search Console setelah domain aktif.

AKSES CMS / REDAKTUR
- Otorisasi dilakukan oleh GitHub. Tambahkan setiap redaktur sebagai collaborator dengan hak minimum yang diperlukan.
- Untuk penggunaan token, gunakan tombol Sign In with Token jika tersedia pada versi CMS. Buat fine-grained token yang dibatasi pada satu repositori dan izin Contents: Read and write. Jangan menggunakan token akun utama dengan cakupan luas.
- Untuk login GitHub OAuth, konfigurasi OAuth App dan provider sesuai dokumentasi Sveltia CMS/Netlify yang berlaku. Jangan menaruh Client Secret di file frontend atau repositori publik.
- Uji akun redaktur terpisah sebelum operasional. Jangan menggunakan satu akun bersama jika dapat dihindari.

STANDAR PENERBITAN BERITA
- Draf harus melalui pemeriksaan fakta, tanggal, lokasi, nama, angka, kutipan, dan dokumen pendukung.
- Upayakan konfirmasi kepada pihak yang diberitakan dan catat upaya konfirmasi secara internal.
- Terapkan asas praduga tak bersalah; hindari label yang menyimpulkan kesalahan sebelum putusan berkekuatan hukum tetap.
- Lindungi identitas anak, korban kekerasan seksual, dan pihak rentan sesuai hukum dan kode etik jurnalistik.
- Cantumkan sumber/rujukan. Gunakan foto milik sendiri atau yang memiliki izin/lisensi yang sesuai.
- Sediakan mekanisme koreksi, klarifikasi, dan hak jawab. Simpan jejak komunikasi dan versi koreksi.
- Berita contoh wajib diverifikasi, ditulis ulang secara independen, atau dihapus sebelum peluncuran publik.

PENGUJIAN LOKAL
Jalankan: python3 build.py
Hasil berada di dist/. Buka dist/index.html melalui server lokal sederhana atau deploy preview; jangan mengandalkan file:// untuk menguji semua perilaku browser.

CHECKLIST SEBELUM PELUNCURAN
[ ] Ganti placeholder repo GitHub dan domain.
[ ] Ganti seluruh berita contoh dan gambar ilustrasi.
[ ] Lengkapi badan hukum/perusahaan pers, alamat kantor, penanggung jawab, dan susunan redaksi.
[ ] Pastikan email dan nomor WhatsApp redaksi aktif.
[ ] Uji login dan hak akses setiap redaktur.
[ ] Uji alur draf > review > terbit dan koreksi berita.
[ ] Periksa tampilan ponsel, tautan, gambar, pencarian, sitemap, dan halaman 404.
[ ] Aktifkan HTTPS dan verifikasi domain di Google Search Console.

BATASAN
- Situs ini bersifat statis; tidak memiliki database komentar, akun pembaca, atau panel analitik bawaan.
- Setiap perubahan konten memicu build/deploy Netlify.
- Repo dan domain belum dapat diisi otomatis karena nama repo dan domain final belum diberikan.
- Sitemap memakai URL relatif sampai site_url diisi dengan domain final.


PEMBARUAN DESAIN — EDISI EDITORIAL
Tampilan publik diperbarui dengan pendekatan portal berita nasional modern:
- masthead putih dengan aksen merah editorial;
- navigasi rubrik merah kontras;
- headline utama besar dengan foto latar;
- daftar berita dan sidebar pilihan redaksi;
- tipografi sans-serif untuk keterbacaan berita;
- layout responsif untuk desktop dan ponsel.
Identitas LENSA HUKUM BANYUWANGI tetap dipertahankan. Desain ini mengambil inspirasi umum dari pola editorial portal berita, bukan menyalin logo atau aset Kompas.

DEPLOY NETLIFY
1. Unggah folder proyek ini ke repository GitHub.
2. Di Netlify, pilih Add new site > Import an existing project.
3. Build command: python3 build.py
4. Publish directory: dist
5. Deploy. Jangan mengunggah folder dist saja apabila ingin CMS berbasis file tetap bisa dibangun ulang.


PERBAIKAN NAVIGASI & TAUTAN — MENU V2
- Menu utama kini memuat Beranda, seluruh 6 rubrik, Tentang Kami, Redaksi, dan Kontak.
- Memperbaiki path relatif pada halaman artikel agar logo, stylesheet, navigasi, footer, dan berita terkait tetap terbuka.
- Memperbaiki perilaku menu pada ponsel: menu menutup kembali setelah tautan dipilih.
- Audit tautan internal hasil build: seluruh tautan internal pada halaman publik lolos pemeriksaan (di luar path absolut khusus halaman 404).
- Halaman pencarian, kategori, artikel, tentang, redaksi, kontak, dan admin dibangkitkan dalam output.


PEMBARUAN KONTEN REDAKSI — 10 NOVEMBER 2026
- Ditambahkan berita dugaan pencurian Honda Scoopy di Purwoharjo, ditulis ulang dari rilis resmi Polresta Banyuwangi dan memuat unsur 5W+1H.
- Ditambahkan artikel opini edukasi hukum di sekolah.
- Ditambahkan ilustrasi AI dengan keterangan jelas bahwa gambar bukan dokumentasi TKP/kegiatan nyata.
- Ditambahkan menu dan halaman Video Berita, tautan liputan JTV, serta galeri video resmi Polresta (ditandai sebagai arsip karena unggahan terakhir yang terindeks bertanggal 22 Mei 2025).
- Ditambahkan teaser video pada beranda.
- Pemeriksaan build: 9 artikel terbit; halaman video tersedia; seluruh referensi relatif internal lolos pemeriksaan.


MODUL VIDEO REDAKSI
- Buka /admin lalu pilih koleksi "Video Redaksi".
- Buat entri, isi judul, status, tanggal, kategori, deskripsi, reporter.
- Unggah file MP4/WebM dan thumbnail. Simpan sebagai Draf untuk pemeriksaan; pilih Terbit untuk tampil di /video.html dan slot Video Terbaru pada beranda.
- Alternatif: isi URL video eksternal bila tidak mengunggah file.
- File video disimpan di GitHub pada uploads/video. Setiap unggahan menambah ukuran repository dan memicu build/deploy Netlify.
- Rekomendasi teknis: MP4 H.264/AAC, 720p atau 1080p, bitrate moderat. Untuk video panjang/sering, gunakan layanan video hosting/CDN (misalnya YouTube embed) agar repository tidak membengkak.
- Akses /admin memakai backend GitHub. Repo dan domain placeholder pada admin/config.yml wajib diganti sebelum login CMS dapat digunakan.


PANDUAN OPERASIONAL VIDEO REDAKSI
1. Login melalui https://DOMAIN-ANDA/admin/ menggunakan akun GitHub yang memiliki akses tulis ke repository.
2. Buka koleksi "Video Redaksi" > "New Video".
3. Isi judul, tanggal, kategori, deskripsi, nama reporter/videografer.
4. Unggah MP4/WebM pada kolom "Unggah file video"; unggah thumbnail pada kolom "Thumbnail".
5. Simpan sebagai Draf untuk pemeriksaan. Setelah lolos pemeriksaan hak cipta, privasi, akurasi, dan persetujuan pihak yang direkam, ubah status menjadi Terbit.
6. Setelah commit dan Netlify selesai deploy, video otomatis muncul di halaman depan (Video Terbaru) dan halaman /video.html.
7. Jika video disimpan di layanan pihak ketiga, isi URL video eksternal; gunakan tautan kanal resmi dan pastikan hak embed tersedia.

BATASAN HOSTING
Unggah file video ke GitHub akan menambah ukuran repository, dan setiap commit memicu build Netlify. Hindari file besar/rekaman panjang. Gunakan MP4 H.264/AAC dengan resolusi 720p/1080p dan kompresi wajar. Untuk volume rutin, sebaiknya migrasikan penyimpanan ke layanan video/CDN khusus. Jangan mengunggah video yang melanggar privasi, hak cipta, atau menampilkan anak/korban tanpa dasar dan persetujuan yang sah.

PENTING SEBELUM ONLINE
- Ganti GANTI-USERNAME/GANTI-NAMA-REPO dan GANTI-DOMAIN-ANDA di admin/config.yml.
- Backend CMS menggunakan GitHub. Wartawan harus diberi akses repository yang sesuai; jangan berbagi akun pemilik.
- Setiap video baru memerlukan status Terbit dan proses deploy selesai sebelum tampil ke publik.


MODUL E-PAPER & DIGITAL NEWSROOM — V5
- Koleksi CMS baru: E-Paper / Edisi Digital.
- Buat file edisi pada content/epaper; isi nomor edisi, judul, tanggal, status, pengantar, dan daftar slug artikel.
- Status Terbit akan menghasilkan halaman arsip epaper.html dan PDF otomatis di /epaper/edisi-NOMOR.pdf.
- PDF berisi sampul tipografis, pengantar, daftar artikel terpilih, penulis, tanggal, dan nomor halaman.
- Digital Newsroom tersedia pada /newsroom.html sebagai pusat akses CMS, Studio Video, Kanal Video, E-Paper, Live, dan Pedoman Redaksi.
- Homepage memiliki tautan menuju arsip E-Paper.
- Netlify menginstal ReportLab dari requirements.txt sebelum menjalankan build.
- Hak akses CMS tetap dikendalikan GitHub Teams/branch protection; halaman dashboard publik bukan pengganti autentikasi.
