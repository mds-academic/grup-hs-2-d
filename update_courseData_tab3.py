import re

with open("src/courseData.js", "r") as f:
    content = f.read()

tab3_quizzes = '''    ],
    quizzes: [
      {
        time: 1847,
        questions: [
          {
            type: "arrange_flow",
            question: "Mini Activity: Rakit Peta Petualangan ⚙️\\nKlik tombol alur di bawah secara berurutan agar aplikasi celengan kita berjalan benar!",
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
              <p style="margin-bottom: 10px;">Copy teks ascii yang kamu mau, lalu tambahkan ke Python menggunakan tiga tanda kutip (<code>\\"\\"\\"</code>) seperti contoh berikut:</p>
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
    ],'''

content = re.sub(
    r'"3": makeLesson\(\{[\s\S]*?endSeconds: 2231,[\s\S]*?    \],',
    lambda m: m.group(0).replace('    ],', tab3_quizzes),
    content
)

with open("src/courseData.js", "w") as f:
    f.write(content)

print("courseData.js updated successfully for Tab 3")
