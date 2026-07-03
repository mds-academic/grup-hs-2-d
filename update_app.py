import re

new_content = """          <div class="below-video">
            <article class="summary-card">
              <h3 class="card-heading">
                <span class="heading-icon" aria-hidden="true">01</span>
                Loot Box Hari Ini 🎁
              </h3>
              <ul class="takeaway-list">
                <li><strong>Algoritma Efisien:</strong> Program yang baik tidak hanya jalan, tapi cepat! Gunakan optimasi (seperti break atau built-in sum()).</li>
                <li><strong>Function itu Resep:</strong> Simpan blok kodemu di dalam fungsi (def) agar bisa dipanggil berkali-kali tanpa harus menulis ulang.</li>
                <li><strong>Parameter & Return:</strong> Berikan data lewat parameter, dan kembalikan hasil perhitungan dengan return agar bisa digunakan.</li>
                <li><strong>Modular Design:</strong> Pecah program yang rumit menjadi function-function kecil yang fokus pada 1 tugas (seperti koki yang membagi tugas).</li>
              </ul>
            </article>

            <aside class="focus-card">
              <div>
                <p class="label">Cheat Sheet 📝</p>
                <h3>Membuat Function</h3>
                <p>Bagaimana cara menyimpan rumus agar bisa dipanggil berkali-kali?</p>
              </div>
              <div class="mini-code">
                <span class="keyword">def</span> hitung_harga(harga, diskon):<br>
                &nbsp;&nbsp;total = harga - diskon<br>
                &nbsp;&nbsp;<span class="keyword">return</span> total<br><br>
                bayar = hitung_harga(50000, 10000)
              </div>
            </aside>
          </div>
          <details class="lesson-reading-accordion" :open="isDesktop ? true : undefined">
            <summary>Buka Materi Bacaan</summary>
          <div class="lesson-reading">
            <header class="reading-header">
              <div>
                <p class="label">Materi Bacaan 01</p>
                <h3>Optimasi Algoritma & Function</h3>
                <p>Belajar cara membuat kode yang cepat dan rapi seperti profesional.</p>
              </div>
              <span class="reading-badge">Konsep Utama</span>
            </header>

            <div class="concept-grid">
              <article class="concept-card">
                <span class="concept-number">A</span>
                <h4>Optimasi</h4>
                <p>Menghitung step count untuk membuat algoritma lebih cepat.</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">B</span>
                <h4>Function</h4>
                <p>Membungkus kode di dalam def layaknya resep atau mesin jus.</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">C</span>
                <h4>Return vs Print</h4>
                <p>Print hanya mencetak ke layar, Return memberikan nilai untuk diolah kembali.</p>
              </article>
            </div>

            <article class="reading-section">
              <h4>Analogi Optimasi: Mencari Buku 📚</h4>
              <ul>
                <li><strong>Cara Lambat (Step Count Banyak):</strong> Cek setiap buku dari ujung ke ujung.</li>
                <li><strong>Cara Cepat:</strong> Cek kategori dulu, jika ketemu langsung berhenti (menggunakan <code>break</code>).</li>
              </ul>
              <div class="reading-code"><span class="code-comment"># Komputer mengeksekusi lebih sedikit langkah dengan built-in sum()</span>
angka = [10, 20, 30]
total = sum(angka)</div>
              <p class="reading-note"><strong>Intinya:</strong> Optimasi algoritma memastikan programmu berjalan efisien dengan mengurangi tugas berulang yang tidak perlu.</p>
            </article>

            <article class="reading-section">
              <h4>Modular Design: Seperti Restoran 🍽️</h4>
              <p>Program yang besar sebaiknya tidak ditulis di satu tempat, tapi dipecah menjadi fungsi-fungsi kecil:</p>
              <ul>
                <li><code>potong_sayur()</code></li>
                <li><code>masak_nasi()</code></li>
                <li><code>sajikan()</code></li>
              </ul>
              <p>Hal ini membuat kode lebih mudah dibaca dan diperbaiki jika ada error.</p>
            </article>
          </div>
          </details>"""

with open('src/App.vue', 'r') as f:
    lines = f.readlines()

with open('src/App.vue', 'w') as f:
    for i, line in enumerate(lines):
        if 1374 <= i <= 1455:
            if i == 1374:
                f.write(new_content + "\n")
            continue
        f.write(line)
