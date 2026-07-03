import re

with open("src/courseData.js", "r") as f:
    content = f.read()

# 1. Update makeLesson to accept quizzes
content = content.replace(
"""  summary,
  focus,
  reading
}) => ({""",
"""  summary,
  focus,
  reading,
  quizzes = []
}) => ({""")

content = content.replace(
"""  reading,
  quizzes: []
});""",
"""  reading,
  quizzes
});""")

# 2. Update Tab 1 (key "1") startSeconds and endSeconds
content = re.sub(
    r'"1": makeLesson\(\{[\s\S]*?startSeconds: 0,[\s\S]*?endSeconds: 63,',
    lambda m: m.group(0).replace('startSeconds: 0', 'startSeconds: 3').replace('endSeconds: 63', 'endSeconds: 62'),
    content
)

# 3. Update Tab 2 (key "2") startSeconds and endSeconds, and inject quizzes
tab2_quizzes = """    ],
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
    ],"""

content = re.sub(
    r'"2": makeLesson\(\{[\s\S]*?startSeconds: 63,[\s\S]*?endSeconds: 1107,[\s\S]*?    \],',
    lambda m: m.group(0).replace('startSeconds: 63', 'startSeconds: 62').replace('endSeconds: 1107', 'endSeconds: 1102').replace('    ],', tab2_quizzes),
    content
)

with open("src/courseData.js", "w") as f:
    f.write(content)

print("courseData.js updated successfully")
