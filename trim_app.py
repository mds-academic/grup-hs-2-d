import re

with open('src/App.vue', 'r') as f:
    content = f.read()

# 1. Replace the sidebar
new_sidebar = """      <aside class="sidebar">
        <div class="eyebrow">Asynchronous Learning</div>
        <h1>Misi: Safe Finance Tracker</h1>
        <p class="sidebar-intro">
          Pelajari cara memvalidasi input agar program lebih aman.
        </p>

        <div class="mission-progress" aria-label="Progres pembelajaran">
          <div class="progress-copy">
            <span>Progres misi</span>
            <span id="progressText">{{ currentStep }} dari 1</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: (currentStep / 1 * 100) + '%' }"></div>
          </div>
        </div>

        <nav class="mobile-nav">
          <label for="mobile-lesson-select">Pilih Modul</label>
          <div class="select-wrapper">
            <select id="mobile-lesson-select" v-model="currentStep">
              <option :value="1">01 Safe Finance Tracker</option>
            </select>
          </div>
        </nav>

        <nav class="lesson-nav" aria-label="Daftar video">
          <button class="lesson-tab" :class="{ active: currentStep === 1 }" type="button" @click="currentStep = 1">
            <span class="tab-number">01</span>
            <span class="tab-copy">
              <strong>Safe Finance Tracker</strong>
              <span>Validasi Input</span>
            </span>
            <span class="tab-arrow" aria-hidden="true">›</span>
          </button>
        </nav>"""

content = re.sub(r'<aside class="sidebar">.*?</nav>\s*<div class="help-card">', new_sidebar + '\n\n        <div class="help-card">', content, flags=re.DOTALL)

# 2. Remove step panels 2 to 8
for i in range(2, 9):
    content = re.sub(rf'<section class="step-panel" id="step-{i}".*?</section>', '', content, flags=re.DOTALL)

# 3. Update the Misi Selesai / progress limit text
content = content.replace('currentStep / 6 * 100', 'currentStep / 1 * 100')
content = content.replace('currentStep / 8 * 100', 'currentStep / 1 * 100')
content = content.replace('dari 8', 'dari 1')
content = content.replace('Misi selesai. Kamu sudah mempelajari conditional, logical operator, dan penerapannya dalam perencanaan keuangan.', 'Misi selesai. Kamu sudah mempelajari input validation, sanitasi, dan penerapannya dalam program keuangan.')
content = content.replace('Selamat kamu telah menyelesaikan Misi Conditional!', 'Selamat kamu telah menyelesaikan Misi Safe Finance Tracker!')
content = content.replace('Misi: Optimasi Algoritma & Function', 'Misi: Safe Finance Tracker')

with open('src/App.vue', 'w') as f:
    f.write(content)

print("App.vue successfully trimmed!")
