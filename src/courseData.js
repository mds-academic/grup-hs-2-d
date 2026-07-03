const VIDEO_ID = "S1j2gt3Up74";

const bookmark = (time, label) => ({ time, label });

const makeLesson = ({
  kicker,
  title,
  duration,
  startSeconds,
  endSeconds,
  bookmarks,
  summary,
  focus,
  reading,
  quizzes = []
}) => ({
  kicker,
  title,
  duration,
  videoId: VIDEO_ID,
  startSeconds,
  endSeconds,
  bookmarks,
  quickSummary: {
    headingNumber: "0" + summary.step,
    headingTitle: summary.title,
    items: summary.items,
    focus
  },
  reading,
  quizzes
});

export const courseData = {
  "1": makeLesson({
    kicker: "BERTANYA SEBELUM BERAKSI",
    title: "Design Thinking & Kebutuhan Pengguna",
    duration: "18 Menit",
    startSeconds: 3,
    endSeconds: 1102,
    bookmarks: [
      bookmark(2, "Pembuka"),
      bookmark(19, "Masalah Butuh Rencana"),
      bookmark(63, "Menuju Design Thinking"),
      bookmark(78, "Apa Itu Design Thinking"),
      bookmark(195, "Contoh Boros"),
      bookmark(321, "Analogi Sandwich"),
      bookmark(525, "Siapa User Kita"),
      bookmark(603, "Problem Statement"),
      bookmark(775, "Masalah Jadi Fitur"),
      bookmark(963, "Feasible atau Nanti")
    ],
    quizzes: [
      {
        time: 171,
        questions: [
          {
            type: "classify_problem",
            question: "Susun Kalimat Masalah Sendiri",
            statement: "Seorang siswa SMA sering kehabisan uang jajan karena tergoda membeli keinginan sehingga sulit menabung.",
            parts: [
              { id: "p1", text: "Seorang siswa SMA", target: "Siapa (Objek)" },
              { id: "p2", text: "sering kehabisan uang jajan", target: "Kesulitan (Masalah)" },
              { id: "p3", text: "karena tergoda membeli keinginan", target: "Penyebab" },
              { id: "p4", text: "sehingga sulit menabung.", target: "Dampak" }
            ],
            buckets: ["Siapa (Objek)", "Kesulitan (Masalah)", "Penyebab", "Dampak"]
          }
        ]
      },
      {
        time: 959,
        questions: [
          {
            type: "match_pairs",
            question: "Pasangkan Kebutuhan Pengguna dengan Fitur yang Cocok",
            needs: [
              { id: "A", text: "Ingin tahu belanja apa yang paling boros" },
              { id: "B", text: "Ingin tahu sisa uang di celengan saat ini" },
              { id: "C", text: "Ingin mendapat saran biar hemat" },
              { id: "D", text: "Ingin menulis uang masuk & keluar" }
            ],
            features: [
              { id: "1", text: "Saran hemat otomatis" },
              { id: "2", text: "Analisis transaksi terboros" },
              { id: "3", text: "Tambah catatan transaksi" },
              { id: "4", text: "Ringkasan sisa saldo celengan" }
            ],
            correctPairs: { "A": "2", "B": "4", "C": "1", "D": "3" }
          }
        ]
      },
      {
        time: 1101,
        questions: [
          {
            type: "feasibility_buckets",
            question: "Bisa Dibuat Sekarang atau Nanti? (Feasibility)",
            items: [
              { id: "i1", text: "Menyimpan catatan transaksi", answer: "feasible" },
              { id: "i2", text: "Login sidik jari / wajah", answer: "not_feasible" },
              { id: "i3", text: "Menghitung rata-rata jajan", answer: "feasible" },
              { id: "i4", text: "Transfer otomatis antar Bank", answer: "not_feasible" },
              { id: "i5", text: "Memberi saran tips hemat", answer: "feasible" },
              { id: "i6", text: "Grafik game 3D interaktif", answer: "not_feasible" },
              { id: "i7", text: "Cek saldo rekening asli", answer: "not_feasible" },
              { id: "i8", text: "Mengelompokkan belanja per kategori", answer: "feasible" }
            ],
            followUp: {
              type: "fill_in_blank",
              question: "Latihan: Susun Kalimat Masalah",
              template: "Siswa mengalami [kesulitan...] karena [penyebab...] sehingga [dampaknya...]",
              blanks: ["kesulitan...", "penyebab...", "dampaknya..."],
              correctAnswers: {
                "kesulitan...": "kesulitan memantau pengeluaran",
                "penyebab...": "tidak ada catatan",
                "dampaknya...": "uang cepat habis tanpa sadar"
              },
              options: [
                "kesulitan memantau pengeluaran", 
                "tidak ada catatan", 
                "uang cepat habis tanpa sadar",
                "hp nya rusak",
                "tidak bisa login"
              ]
            }
          }
        ]
      }
    ],
    summary: {
      step: 2,
      title: "Bertanya Sebelum Bikin",
      items: [
        { label: "Design Thinking", text: "Cari tahu dulu kesulitan pengguna sebelum menawarkan solusi." },
        { label: "Problem Statement", text: "Tulis siapa yang kesulitan, apa masalahnya, kenapa terjadi, dan dampaknya." },
        { label: "Prioritas", text: "Pisahkan fitur yang bisa dibuat sekarang dari ide besar yang perlu ditunda." }
      ]
    },
    focus: {
      label: "Template",
      title: "Kalimat masalah",
      body: "Gunakan pola sederhana agar masalah pengguna jelas sebelum fitur dipilih.",
      codeLines: [
        "user = \"siswa SMA\"",
        "kesulitan = \"uang jajan habis sebelum Jumat\"",
        "penyebab = \"tergoda membeli keinginan\"",
        "dampak = \"sulit menyisihkan tabungan\""
      ]
    },
    reading: {
      label: "Materi Bacaan 02",
      title: "Design Thinking & Kebutuhan Pengguna",
      subtitle: "Memahami masalah pengguna sebelum membuat solusi.",
      badge: "Perencanaan",
      concepts: [
        { number: "A", title: "Empati", body: "Cari tahu pengalaman pengguna, bukan hanya menebak dari sudut pandang pembuat aplikasi." },
        { number: "B", title: "Masalah Utama", body: "Pilih satu masalah yang paling penting dan paling mungkin diselesaikan." },
        { number: "C", title: "Fitur Tepat", body: "Fitur harus menjawab masalah, misalnya catatan transaksi untuk siswa yang lupa mencatat jajan." }
      ],
      sections: [
        {
          title: "Dari Curhat Menjadi Fitur",
          paragraphs: [
            "Kalau teman berkata uangnya cepat habis, jangan langsung membuat aplikasi super besar. Tanyakan dulu kenapa uangnya habis.",
            "Bisa jadi masalahnya sederhana: ia lupa mencatat pengeluaran, tidak sadar saldo menipis, atau bingung membedakan kebutuhan dan keinginan."
          ],
          bullets: [
            "Masalah: lupa mencatat pengeluaran. Fitur: tambah transaksi dan rekap otomatis.",
            "Masalah: tidak sadar saldo tinggal sedikit. Fitur: alarm saldo rendah.",
            "Masalah: ragu menabung cukup atau tidak. Fitur: rekomendasi hemat."
          ],
          note: "Solusi yang baik tidak harus paling canggih; yang penting cocok dengan kebutuhan pengguna."
        }
      ]
    }
  }),

  "2": makeLesson({
    kicker: "MERANCANG PROGRAM",
    title: "Flowchart & Use Case",
    duration: "19 Menit",
    startSeconds: 1107,
    endSeconds: 2231,
    bookmarks: [
      bookmark(1107, "Use Case"),
      bookmark(1284, "Rancangan Tombol"),
      bookmark(1517, "Tombol Jadi Fungsi"),
      bookmark(1695, "Flowchart"),
      bookmark(1905, "Menu Python"),
      bookmark(2045, "Pilihan Menu"),
      bookmark(2103, "Kerangka Fungsi")
    ],
    quizzes: [
      {
        time: 1847,
        questions: [
          {
            type: "arrange_flow",
            question: "Mini Activity: Rakit Peta Petualangan ⚙️\nKlik tombol alur di bawah secara berurutan agar aplikasi celengan kita berjalan benar!",
            items: [
              { id: "f1", text: "Mulai" },
              { id: "f2", text: "Tampilkan menu" },
              { id: "f3", text: "Pilih fitur" },
              { id: "f4", text: "Jalankan function" },
              { id: "f5", text: "Tampilkan hasil" },
              { id: "f6", text: "Keluar" }
            ],
            correctOrder: ["f1", "f2", "f3", "f4", "f5", "f6"]
          }
        ]
      },
      {
        time: 1996,
        questions: [
          {
            type: "info",
            question: "Cara Memasukkan ASCII Art ke Python",
            html: `
              <p style="margin-bottom: 10px;">Kamu bisa membuat teks keren menggunakan <b>Text to ASCII Art Generator</b>.</p>
              <p style="margin-bottom: 15px;"><a href="https://patorjk.com/software/taag/" target="_blank" style="color: #00c3ff; text-decoration: underline;">Buka Web ASCII Art Generator di sini</a></p>
              <p style="margin-bottom: 10px;">Copy teks ascii yang kamu mau, lalu tambahkan ke Python menggunakan tiga tanda kutip (<code>\"\"\"</code>) seperti contoh berikut:</p>
              <div style="background: #282a36; color: #f8f8f2; padding: 15px; border-radius: 8px; font-family: monospace; text-align: left; margin-bottom: 15px; font-size: 14px;">
<pre style="margin: 0;">title = """ 
Paste ascii here
"""

print(title)</pre>
              </div>
            `
          }
        ]
      },
      {
        time: 2227,
        questions: [
          {
            type: "match_pairs",
            question: "Latihan: Pasangkan Tombol & Fungsi 🧩",
            needs: [
              { id: "A", text: "Menambah data jajan baru" },
              { id: "B", text: "Menghitung sisa saldo" },
              { id: "C", text: "Mencari tahu jajan terboros" },
              { id: "D", text: "Memberi tips hemat otomatis" },
              { id: "E", text: "Membersihkan spasi input teks" }
            ],
            features: [
              { id: "1", text: "analyze_expenses()" },
              { id: "2", text: "clean_text()" },
              { id: "3", text: "add_transaction()" },
              { id: "4", text: "give_recommendation()" },
              { id: "5", text: "summarize_transactions()" }
            ],
            correctPairs: { "A": "3", "B": "5", "C": "1", "D": "4", "E": "2" }
          }
        ]
      }
    ],
    summary: {
      step: 3,
      title: "Peta Aplikasi",
      items: [
        { label: "Use Case", text: "Daftar aksi yang bisa dilakukan pengguna di aplikasi." },
        { label: "Flowchart", text: "Peta alur dari aplikasi dimulai, menu tampil, fitur dipilih, sampai selesai." },
        { label: "Function", text: "Setiap tombol atau menu sebaiknya terhubung ke fungsi Python yang jelas." }
      ]
    },
    focus: {
      label: "Kerangka",
      title: "Menu ke fungsi",
      body: "Gunakan pilihan menu untuk memanggil fungsi yang berbeda.",
      codeLines: [
        "choice = input(\"Pilih menu: \")",
        "if choice == \"1\":",
        "    add_transaction()",
        "elif choice == \"2\":",
        "    summarize_transactions()"
      ]
    },
    reading: {
      label: "Materi Bacaan 03",
      title: "Flowchart & Use Case",
      subtitle: "Membuat peta tombol, fungsi, dan alur program sebelum coding penuh.",
      badge: "Rancangan",
      concepts: [
        { number: "A", title: "Use Case", body: "Menjawab pertanyaan: pengguna akan melakukan apa saja di aplikasi?" },
        { number: "B", title: "Flowchart", body: "Menggambarkan perjalanan program dari mulai sampai selesai." },
        { number: "C", title: "Fungsi", body: "Membungkus satu tugas ke dalam blok kode yang bisa dipanggil ulang." }
      ],
      sections: [
        {
          title: "Contoh Alur Celengan Pintar",
          paragraphs: [
            "Aplikasi dimulai dengan menampilkan menu. Pengguna memilih fitur, lalu program menjalankan fungsi yang sesuai.",
            "Setelah hasil keluar, program bisa kembali ke menu atau berhenti kalau pengguna memilih keluar."
          ],
          bullets: [
            "Mulai -> tampilkan menu.",
            "Pilih fitur -> jalankan fungsi.",
            "Tampilkan hasil -> kembali ke menu atau selesai."
          ],
          note: "Flowchart membuat kita tahu kapan program mengulang dan kapan program berhenti."
        }
      ]
    }
  }),

  "3": makeLesson({
    kicker: "DATA CELENGAN",
    title: "Menganalisis Data Transaksi",
    duration: "6 Menit",
    startSeconds: 2231,
    endSeconds: 2615,
    bookmarks: [
      bookmark(2231, "Aplikasi Pintar"),
      bookmark(2298, "Insight Data"),
      bookmark(2420, "If Saldo"),
      bookmark(2555, "Dictionary")
    ],
    summary: {
      step: 4,
      title: "Data Menjadi Insight",
      items: [
        { label: "Data", text: "Transaksi berisi kategori, jenis, dan nominal yang bisa dihitung program." },
        { label: "Insight", text: "Kesimpulan dari data, misalnya pengeluaran terbesar ada di kategori makanan." },
        { label: "Dictionary", text: "Struktur key-value membantu menyimpan kategori dan jumlah uang dengan rapi." }
      ]
    },
    focus: {
      label: "Analisis",
      title: "Cari kategori terbesar",
      body: "Python bisa mencari kategori dengan nilai pengeluaran paling tinggi.",
      codeLines: [
        "kategori_total = {\"makanan\": 80000, \"transportasi\": 20000}",
        "terbesar = max(kategori_total, key=kategori_total.get)",
        "print(\"Kategori terbesar:\", terbesar)"
      ]
    },
    reading: {
      label: "Materi Bacaan 04",
      title: "Menganalisis Data Transaksi",
      subtitle: "Mengubah catatan uang menjadi kesimpulan yang bisa dipakai.",
      badge: "Data",
      concepts: [
        { number: "A", title: "Transaksi", body: "Catatan pemasukan atau pengeluaran yang dimasukkan pengguna." },
        { number: "B", title: "Insight", body: "Kesimpulan setelah program memeriksa angka-angka transaksi." },
        { number: "C", title: "Kategori", body: "Kelompok seperti makanan, transportasi, hiburan, atau tabungan." }
      ],
      sections: [
        {
          title: "Cara Program Membaca Kebiasaan Belanja",
          paragraphs: [
            "Program tidak bisa memberi saran kalau tidak punya data. Karena itu setiap transaksi perlu disimpan dengan rapi.",
            "Setelah data terkumpul, program bisa menghitung total pemasukan, total pengeluaran, sisa saldo, dan kategori yang paling besar."
          ],
          bullets: [
            "Gunakan list untuk menampung banyak transaksi.",
            "Gunakan dictionary untuk menyimpan detail tiap transaksi.",
            "Gunakan perhitungan total untuk menemukan pola belanja."
          ],
          note: "Insight yang baik selalu berasal dari data yang jelas."
        }
      ]
    }
  }),

  "4": makeLesson({
    kicker: "FINANCIAL DATA",
    title: "Logika & Rekomendasi Pintar",
    duration: "6 Menit",
    startSeconds: 2619,
    endSeconds: 2974,
    bookmarks: [
      bookmark(2619, "Mencari Kategori Terbesar"),
      bookmark(2825, "Kategori Berubah Sesuai Data"),
      bookmark(2828, "Saran Kategori"),
      bookmark(2916, "Saran Harus Jelas"),
      bookmark(2966, "Latihan Rekomendasi")
    ],
    quizzes: [
      {
        time: 2973,
        questions: [
          {
            type: "input",
            question: "Tebak Rahasia Data 🕵️",
            html: `
              <p style="margin-bottom: 10px;">Ketik nominal uang jarmu untuk menguji jalannya fungsi Python <code>give_balance_recommendation()</code>:</p>
              <div style="background: #282a36; color: #f8f8f2; padding: 15px; border-radius: 8px; font-family: monospace; text-align: left; margin-bottom: 15px; font-size: 14px;">
<pre style="margin: 0;">def kasih_saran_saldo(saldo):
    if saldo < 10000:
        return "Tunda pembelian keinginan."
    elif saldo < 30000:
        return "Hati-hati, saldo mulai terbatas."
    else:
        return "Saldo masih cukup aman."

saran = kasih_saran_saldo(<span style="color: #fbc02d; font-weight: bold;">[input]</span>)
print(saran)</pre>
              </div>
            `,
            validate: (input) => {
              const val = parseInt(input, 10);
              if (isNaN(val)) return { isCorrect: false, feedback: "Masukkan angka yang valid ya!" };
              let saran = "";
              if (val < 10000) saran = "Tunda pembelian keinginan.";
              else if (val < 30000) saran = "Hati-hati, saldo mulai terbatas.";
              else saran = "Saldo masih cukup aman.";
              return { isCorrect: true, feedback: ">>> Menjalankan kasih_saran_saldo(" + val + ")...\nSaran: \"" + saran + "\"" };
            }
          }
        ]
      }
    ],
    summary: {
      step: 5,
      title: "Saran Berdasarkan Data",
      items: [
        { label: "Logika If", text: "Program memilih pesan berdasarkan kategori terbesar atau sisa saldo." },
        { label: "Rekomendasi", text: "Saran harus menyebut alasan, bukan hanya menyuruh hemat." },
        { label: "Konteks", text: "Saran makanan, transportasi, dan hiburan harus berbeda karena masalahnya berbeda." }
      ]
    },
    focus: {
      label: "If Else",
      title: "Mesin saran",
      body: "Rekomendasi terasa pintar ketika berubah sesuai hasil analisis data.",
      codeLines: [
        "if terbesar == \"makanan\":",
        "    print(\"Coba bawa bekal besok.\")",
        "elif terbesar == \"transportasi\":",
        "    print(\"Coba berangkat bareng teman.\")"
      ]
    },
    reading: {
      label: "Materi Bacaan 05",
      title: "Logika & Rekomendasi Pintar",
      subtitle: "Membuat aplikasi memberi saran yang masuk akal.",
      badge: "Rekomendasi",
      concepts: [
        { number: "A", title: "Kondisi", body: "If-elif-else memilih jalur pesan sesuai data yang ditemukan." },
        { number: "B", title: "Alasan", body: "Saran harus menjelaskan kenapa pengguna perlu bertindak." },
        { number: "C", title: "Aksi", body: "Rekomendasi sebaiknya memberi langkah kecil yang bisa dicoba." }
      ],
      sections: [
        {
          title: "Saran yang Tidak Membingungkan",
          paragraphs: [
            "Kalimat 'kamu harus hemat' terlalu umum. Pengguna akan lebih paham kalau program memberi alasan dari data.",
            "Misalnya: 'Uangmu paling banyak habis untuk makanan, coba bawa bekal dua kali minggu ini.'"
          ],
          bullets: [
            "Sebut kategori atau saldo yang memicu saran.",
            "Gunakan saran yang bisa dilakukan siswa.",
            "Hindari pesan yang terlalu besar atau tidak jelas."
          ],
          note: "Rekomendasi pintar = data + alasan + aksi sederhana."
        }
      ]
    }
  }),

  "5": makeLesson({
    kicker: "APP INTEGRATION",
    title: "Menyatukan Kode Program",
    duration: "11 Menit",
    startSeconds: 2989,
    endSeconds: 3662,
    bookmarks: [
      bookmark(2989, "Menyatukan Konsep"),
      bookmark(3123, "Kode Modular"),
      bookmark(3203, "Loop Menu"),
      bookmark(3252, "Prinsip DRY")
    ],
    quizzes: [
      {
        time: 3121,
        questions: [
          {
            type: "match_pairs",
            question: "Pasangkan Kekuatan Konsep! 🧩",
            needs: [
              { id: "A", text: "Fungsi (Function)" },
              { id: "B", text: "Loop (`while`)" },
              { id: "C", text: "Dictionary" },
              { id: "D", text: "List" }
            ],
            features: [
              { id: "1", text: "Mencatat detail 1 belanjaan" },
              { id: "2", text: "Membuat blok fitur terpisah yang rapi" },
              { id: "3", text: "Kantong besar untuk menampung banyak data" },
              { id: "4", text: "Memutar menu agar tidak langsung mati" }
            ],
            correctPairs: { "A": "2", "B": "4", "C": "1", "D": "3" }
          }
        ]
      },
      {
        time: 3661,
        questions: [
          {
            type: "input",
            subtype: "jinakkan_loop",
            question: "Misi Penyelamatan: Jinakkan Loop Gila! 🕵️‍♂️",
            html: "",
            correct: ["break"],
            feedback: {
              correct: "Tepat sekali! Loop berhasil dihentikan. 🛡️",
              incorrect: "Loop masih berjalan, coba ingat kata kuncinya!"
            }
          }
        ]
      }
    ],
    summary: {
      step: 6,
      title: "Semua Bagian Jadi Satu",
      items: [
        { label: "Modular", text: "Program dibagi ke fungsi kecil seperti tambah transaksi dan ringkasan." },
        { label: "Loop", text: "Menu utama berulang sampai pengguna memilih keluar." },
        { label: "Validasi", text: "Input diperiksa agar data kosong atau nominal salah tidak merusak program." }
      ]
    },
    focus: {
      label: "Struktur",
      title: "Aplikasi utuh",
      body: "Gabungkan list, dictionary, function, loop, dan if-else ke satu program.",
      codeLines: [
        "transactions = []",
        "while True:",
        "    show_menu()",
        "    choice = input(\"Pilihan: \")",
        "    if choice == \"5\":",
        "        break"
      ]
    },
    reading: {
      label: "Materi Bacaan 06",
      title: "Menyatukan Kode Program",
      subtitle: "Menggabungkan konsep Python menjadi aplikasi celengan yang berjalan.",
      badge: "Integrasi",
      concepts: [
        { number: "A", title: "Function", body: "Membuat kode lebih rapi dan mudah diperbaiki." },
        { number: "B", title: "Loop", body: "Menjaga menu tetap muncul sampai pengguna keluar." },
        { number: "C", title: "Validasi", body: "Mencegah data kosong, nominal nol, atau input bukan angka." }
      ],
      sections: [
        {
          title: "Fondasi Program Celengan",
          paragraphs: [
            "Aplikasi utama perlu tempat penyimpanan transaksi, menu, fungsi tambah transaksi, fungsi ringkasan, dan logika rekomendasi.",
            "Prinsip DRY membantu kita tidak menulis kode yang sama berkali-kali. Bagian yang sering dipakai sebaiknya dimasukkan ke fungsi."
          ],
          bullets: [
            "Buat list `transactions` sebagai penyimpanan utama.",
            "Buat fungsi untuk setiap fitur.",
            "Gunakan `while True` untuk menu berulang.",
            "Gunakan `try-except` saat mengubah input nominal menjadi angka."
          ],
          note: "Saat satu fitur error, fungsi yang terpisah membuat masalah lebih mudah dicari."
        }
      ]
    }
  })
};