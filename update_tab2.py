import re

file_path = "src/App.vue"

with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update progress indicator
content = re.sub(
    r'<span id="progressText">{{ currentStep }} dari 1</span>',
    r'<span id="progressText">{{ currentStep }} dari 2</span>',
    content
)
content = re.sub(
    r':style="\{ width: \(currentStep / 1 \* 100\) \+ \'%\' \}"',
    r':style="{ width: (currentStep / 2 * 100) + \'%\' }"',
    content
)

# 2. Add Mobile Nav Option
content = re.sub(
    r'<option :value="1">01 Optimasi & Function</option>',
    r'<option :value="1">01 Optimasi & Function</option>\n              <option :value="2">02 Optimasi Loop & Step Count</option>',
    content
)

# 3. Add Sidebar Nav Button
sidebar_nav = """        <nav class="lesson-nav" aria-label="Daftar video">
          <button class="lesson-tab" :class="{ active: currentStep === 1 }" type="button" @click="currentStep = 1">
            <span class="tab-number">01</span>
            <span class="tab-copy">
              <strong>Optimasi & Function</strong>
              <span>Konsep dasar</span>
            </span>
            <span class="tab-arrow" aria-hidden="true">›</span>
          </button>
          <button class="lesson-tab" :class="{ active: currentStep === 2 }" type="button" @click="currentStep = 2">
            <span class="tab-number">02</span>
            <span class="tab-copy">
              <strong>Loop & Step Count</strong>
              <span>Menghitung langkah</span>
            </span>
            <span class="tab-arrow" aria-hidden="true">›</span>
          </button>
        </nav>"""
content = re.sub(
    r'        <nav class="lesson-nav".*?</nav>',
    sidebar_nav,
    content,
    flags=re.DOTALL
)

# 4. Duplicate Step 1 for Step 2
step_2_content = """        <section class="step-panel" id="step-2" v-show="currentStep === 2">
          <div class="video-frame" :class="{ 'player-ready': playerStates[2]?.isReady }" data-video-step="2">
            <div id="youtube-player-2"></div>
            <div class="custom-thumbnail" v-show="!playerStates[2]?.hasStarted" @click="togglePlay(2)">
              <img src="https://cdn-web-2.ruangguru.com/landing-pages/assets/fec32e8d-d711-48a2-bd22-59581f0594c1.jpg" alt="Thumbnail" />
            </div>
            <button class="video-center-play" type="button" v-show="!playerStates[2]?.isPlaying" @click="togglePlay(2)">▶</button>
            <div class="video-controls" aria-label="Kontrol video 2">
              <button class="video-control-button video-play" type="button" @click="togglePlay(2)">{{ playerStates[2]?.isPlaying ? "⏸" : "▶" }}</button>
              <input class="video-seek" type="range" min="0" max="100" step="0.1" :value="playerStates[2]?.progress || 0" @input="onSeekInput(2, $event)" aria-label="Posisi video">
              <span class="video-time">{{ playerStates[2]?.currentTimeFormatted || "0:00" }} / {{ playerStates[2]?.durationFormatted || "0:00" }}</span>
              <button class="video-control-button video-mute" type="button" @click="toggleMute(2)">{{ playerStates[2]?.isMuted ? "🔇" : "🔊" }}</button>
              <button class="video-control-button video-fullscreen" type="button" @click="toggleFullscreen(2)">⛶</button>
            </div>
          </div>

          <div class="bookmarks-container" v-if="courseData[2].bookmarks?.length > 0">
            <button class="bookmark-btn" v-for="bm in courseData[2].bookmarks" :key="bm.label" @click="seekToBookmark(2, bm.time)">
              <span class="bookmark-time">{{ formatVideoTime(bm.time) }}</span> {{ bm.label }}
            </button>
          </div>
          <div class="below-video">
            <article class="summary-card">
              <h3 class="card-heading">
                <span class="heading-icon" aria-hidden="true">02</span>
                Loot Box Hari Ini 🎁
              </h3>
              <ul class="takeaway-list">
                <li><strong>Looping:</strong> Cara kita memerintahkan komputer melakukan hal yang sama berulang kali.</li>
                <li><strong>Step Count di Loop:</strong> Setiap kali loop berjalan, program melakukan 1 langkah. Jika loop 10 kali, ada 10 step count!</li>
                <li><strong>Optimasi dengan Break:</strong> Hentikan loop segera setelah tujuan tercapai agar step count tidak mubazir.</li>
              </ul>
            </article>

              <aside class="focus-card">
              <div>
                <p class="label">Cheat Sheet 📝</p>
                <h3>Menggunakan Break</h3>
                <p>Bagaimana menghentikan loop di tengah jalan?</p>
              </div>
              <div class="mini-code">
                <span class="keyword">for</span> angka <span class="keyword">in</span> daftar:<br>
                &nbsp;&nbsp;<span class="keyword">if</span> angka == target:<br>
                &nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword">break</span> <span class="code-comment"># Langsung berhenti!</span>
              </div>
            </aside>
          </div>
          <details class="lesson-reading-accordion" :open="isDesktop ? true : undefined">
            <summary>Buka Materi Bacaan</summary>
          <div class="lesson-reading">
            <header class="reading-header">
              <div>
                <p class="label">Materi Bacaan 02</p>
                <h3>Optimasi Loop</h3>
                <p>Membatasi langkah berulang agar program super cepat.</p>
              </div>
              <span class="reading-badge">Konsep Utama</span>
            </header>

            <div class="concept-grid">
              <article class="concept-card">
                <span class="concept-number">A</span>
                <h4>Loop</h4>
                <p>Perulangan. Berguna jika kita ingin mengecek data satu per satu dari awal sampai akhir.</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">B</span>
                <h4>Condition</h4>
                <p>Syarat atau cek poin di dalam loop. "Apakah nilai ini yang saya cari?"</p>
              </article>
              <article class="concept-card">
                <span class="concept-number">C</span>
                <h4>Break</h4>
                <p>Tombol rem darurat! Digunakan untuk menghentikan loop seketika saat kondisi sudah terpenuhi.</p>
              </article>
            </div>

            <article class="reading-section">
              <h4>Kenapa Butuh Break? 🛑</h4>
              <p>Misalnya kamu mencari angka 5 dari list: <code>[1, 5, 10, 20, 50, 100]</code>.</p>
              <ul>
                <li><strong>Tanpa Break:</strong> Program tetap akan mengecek angka 10, 20, 50, 100 walaupun 5 sudah ketemu (6 step).</li>
                <li><strong>Dengan Break:</strong> Program berhenti langsung di langkah ke-2 karena 5 sudah ketemu (2 step).</li>
              </ul>
              <p class="reading-note"><strong>Intinya:</strong> Gunakan `break` untuk menghindari pekerjaan sia-sia. Step count berkurang, program berjalan lebih instan.</p>
            </article>
          </div>
          </details>
        </section>"""

content = re.sub(
    r'(</section>\s*<div class="navigation">)',
    lambda m: step_2_content + "\n\n" + m.group(1),
    content
)

# 5. Fix Navigation Buttons
nav_buttons = """        <div class="navigation">
          <button class="nav-button secondary" type="button" :disabled="currentStep === 1" @click="currentStep--">
            <span aria-hidden="true">←</span> Sebelumnya
          </button>
          <button class="nav-button primary" type="button" :disabled="currentStep === 2" @click="currentStep++">
            Lanjut ke video berikutnya <span aria-hidden="true">→</span>
          </button>
        </div>"""
content = re.sub(
    r'<div class="navigation">.*?</div>',
    nav_buttons,
    content,
    flags=re.DOTALL
)

# 6. Add quizState.inputAnswer
content = re.sub(
    r'essayAnswer: "",',
    r'essayAnswer: "",\n  inputAnswer: "",',
    content
)

# 7. Add submitInputAnswer
submit_input = """const submitInputAnswer = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'input') return;

  const input = quizState.value.inputAnswer.trim();
  if (!input) return;

  quizState.value.choicesDisabled = true;

  // Cek apakah string input mengandung substring correct (bisa mentolerir "4" di dalam "4 steps")
  const isCorrect = input.toLowerCase().includes(item.correct.toLowerCase());

  quizState.value.quizFeedbackType = isCorrect ? 'correct' : 'wrong';
  quizState.value.quizFeedback = (isCorrect ? "Tepat! " : "Belum tepat. ") + (item.explanation || "");

  revealQuizNext();
};"""

content = content.replace("const submitEssayAnswer = () => {", submit_input + "\n\nconst submitEssayAnswer = () => {")

# 8. Add template UI for 'input' type
input_ui = """        <div v-if="currentQuestion && currentQuestion.type === 'input'" class="input-container" style="display: flex; gap: 10px; flex-direction: column; margin-top: 15px;">
          <input type="text" v-model="quizState.inputAnswer" placeholder="Ketik jawabanmu di sini..." :disabled="quizState.choicesDisabled" style="padding: 12px 16px; border-radius: 8px; border: 2px solid rgba(226, 232, 240, 0.2); background: rgba(30, 41, 59, 0.4); color: white; font-size: 16px;">
          <button 
            class="essay-submit-btn" 
            :disabled="!quizState.inputAnswer.trim() || quizState.choicesDisabled"
            @click="submitInputAnswer"
          >Kirim Jawaban</button>
        </div>"""

content = content.replace("        <div v-if=\"currentQuestion && currentQuestion.type === 'essay'\" class=\"essay-container\">", input_ui + "\n\n        <div v-if=\"currentQuestion && currentQuestion.type === 'essay'\" class=\"essay-container\">")

# 9. Clean up quizState logic on Next
content = re.sub(
    r'quizState.value.essayAnswer = "";',
    r'quizState.value.essayAnswer = "";\n  quizState.value.inputAnswer = "";',
    content
)


with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)
