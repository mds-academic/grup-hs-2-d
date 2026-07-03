new_sidebar = """      <aside class="sidebar">
        <div class="eyebrow">Asynchronous Learning</div>
        <h1>Misi: Optimasi Algoritma & Function</h1>
        <p class="sidebar-intro">
          Pelajari cara membuat kodemu berjalan lebih cepat dan terstruktur rapi dengan <strong>function</strong>.
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
              <option :value="1">01 Optimasi & Function</option>
            </select>
          </div>
        </nav>

        <nav class="lesson-nav" aria-label="Daftar video">
          <button class="lesson-tab" :class="{ active: currentStep === 1 }" type="button" @click="currentStep = 1">

            <span class="tab-number">01</span>
            <span class="tab-copy">
              <strong>Optimasi & Function</strong>
              <span>Konsep dasar</span>
            </span>
            <span class="tab-arrow" aria-hidden="true">›</span>
          </button>
        </nav>"""

with open('src/App.vue', 'r') as f:
    lines = f.readlines()

with open('src/App.vue', 'w') as f:
    skip = False
    for i, line in enumerate(lines):
        # 1240 is 0-indexed line 1240. Let's be safe and match string instead.
        if line.strip() == '<aside class="sidebar">':
            f.write(new_sidebar + "\n")
            skip = True
            continue
        
        if skip:
            if line.strip() == '</nav>':
                skip = False
            continue
            
        if not skip:
            f.write(line)

