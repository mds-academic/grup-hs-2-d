import re

with open('src/App.vue', 'r') as f:
    content = f.read()

new_below_video = """          <div class="below-video">
            <article class="summary-card">
              <h3 class="card-heading">
                <span class="heading-icon" aria-hidden="true">01</span>
                Loot Box Hari Ini 🎁
              </h3>
              <ul class="takeaway-list">
                <li><strong>Apa Itu Input:</strong> Semua data atau informasi yang dimasukkan oleh pengguna ke dalam program.</li>
                <li><strong>Validasi Input:</strong> Proses pemeriksaan data agar benar dan aman sebelum diproses (misal: mengecek uang minus).</li>
                <li><strong>Sanitasi Data:</strong> Membersihkan data agar seragam, seperti membuang spasi berlebih dengan <code>.strip()</code>.</li>
              </ul>
            </article>

              <aside class="focus-card">
              <div>
                <p class="label">Cheat Sheet 📝</p>
                <h3>Sanitasi String</h3>
                <p>Bersihkan input dengan cepat:</p>
              </div>
              <div class="mini-code">
                <span class="code-comment"># Membuang spasi kosong di awal/akhir</span><br>
                teks = input().strip()<br><br>
                <span class="code-comment"># Mengecilkan semua huruf</span><br>
                teks = input().lower()
              </div>
            </aside>
          </div>
          <details class="lesson-reading-accordion" :open="isDesktop ? true : undefined">
            <summary>Buka Materi Bacaan</summary>
          <div class="lesson-reading">
            <header class="reading-header">
              <div>
                <p class="label">Materi Bacaan 01</p>
                <h3>Input Validation & Data Safety</h3>
                <p>Mengamankan program keuangan dari data yang tidak masuk akal.</p>
              </div>
              <span class="reading-badge">Konsep Utama</span>
            </header>

            <div class="concept-grid">
              <article class="concept-card">
                <span class="concept-number">A</span>
                <h4>Validasi</h4>
                <p>Mengecek kebenaran data. Apakah nominal kurang dari nol? Tolak jika ya!</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">B</span>
                <h4>Sanitasi</h4>
                <p>Merapikan data kotor, misalnya menghapus spasi atau menyamakan huruf besar-kecil.</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">C</span>
                <h4>Keamanan</h4>
                <p>Data keuangan sangat sensitif. Angka negatif pada pengeluaran bisa jadi bug berbahaya.</p>
              </article>
            </div>

            <article class="reading-section">
              <h4>Analogi Validasi: Petugas Penjaga 👮‍♂️</h4>
              <p>Bayangkan kamu ingin bermain wahana roller coaster. Sebelum masuk, petugas akan memeriksa:</p>
              <ul>
                <li><strong>Pemeriksaan 1:</strong> Apakah kamu memegang tiket resmi? (Bukan input kosong).</li>
                <li><strong>Pemeriksaan 2:</strong> Apakah tinggi badanmu aman? (Sesuai kategori).</li>
              </ul>
              <p class="reading-note"><strong>Intinya:</strong> Jangan pernah langsung percaya pada data dari pengguna! Validasi memastikan programmu tidak crash.</p>
            </article>
          </div>
          </details>"""

content = re.sub(r'<div class="below-video">.*?</details>', new_below_video, content, flags=re.DOTALL)

with open('src/App.vue', 'w') as f:
    f.write(content)

print("Content updated successfully!")
