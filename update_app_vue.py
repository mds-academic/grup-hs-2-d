import re

with open("src/App.vue", "r") as f:
    content = f.read()

# 1. Insert State Variables
state_vars = """
// --- NEW QUIZ TYPES STATE ---
const classifyProblemAnswers = ref({});
const activeClassifyPart = ref(null);

const matchPairsAnswers = ref({});
const activeMatchNeed = ref(null);

const feasibilityAnswers = ref({});
const activeFeasibilityItem = ref(null);

const fillInBlankAnswers = ref({});
const isFeasibilityFollowUp = ref(false);
"""
content = re.sub(
    r'(const quizState = ref\(\{)',
    lambda m: state_vars + "\n" + m.group(1),
    content
)

# 2. Reset state
reset_code = """  quizState.value.inputAnswer = "";
  classifyProblemAnswers.value = {};
  activeClassifyPart.value = null;
  matchPairsAnswers.value = {};
  activeMatchNeed.value = null;
  feasibilityAnswers.value = {};
  activeFeasibilityItem.value = null;
  fillInBlankAnswers.value = {};
  isFeasibilityFollowUp.value = false;"""
content = content.replace('quizState.value.inputAnswer = "";', reset_code)

# 3. Handlers
handlers = """
// --- NEW QUIZ HANDLERS ---
const handleClassifySelect = (partId, targetBucket) => {
  if (quizState.value.choicesDisabled) return;
  
  if (partId && !targetBucket) {
    // Select part
    activeClassifyPart.value = activeClassifyPart.value === partId ? null : partId;
  } else if (targetBucket && activeClassifyPart.value) {
    // Assign to bucket
    for (let k in classifyProblemAnswers.value) {
      if (classifyProblemAnswers.value[k] === activeClassifyPart.value) {
        classifyProblemAnswers.value[k] = null;
      }
    }
    classifyProblemAnswers.value[targetBucket] = activeClassifyPart.value;
    activeClassifyPart.value = null;
  } else if (targetBucket && !activeClassifyPart.value) {
      // Click bucket to clear it
      classifyProblemAnswers.value[targetBucket] = null;
  }
};

const submitClassifyProblem = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'classify_problem') return;

  quizState.value.choicesDisabled = true;

  let correctCount = 0;
  item.parts.forEach(part => {
    if (classifyProblemAnswers.value[part.target] === part.id) correctCount++;
  });

  const isCorrect = correctCount === item.parts.length;
  quizState.value.quizFeedbackType = isCorrect ? 'success' : 'wrong';
  quizState.value.quizFeedback = isCorrect ? "Tepat sekali! Kamu menyusun kalimat masalah dengan sempurna." : "Masih ada yang keliru, coba baca ulang kalimat masalahnya.";
  revealQuizNext();
};

const handleMatchSelect = (needId, featureId) => {
  if (quizState.value.choicesDisabled) return;

  if (needId && !featureId) {
    activeMatchNeed.value = activeMatchNeed.value === needId ? null : needId;
  } else if (featureId && activeMatchNeed.value) {
    matchPairsAnswers.value[activeMatchNeed.value] = featureId;
    activeMatchNeed.value = null;
  }
};

const clearMatchPair = (needId) => {
  if (quizState.value.choicesDisabled) return;
  matchPairsAnswers.value[needId] = null;
};

const submitMatchPairs = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'match_pairs') return;
  quizState.value.choicesDisabled = true;

  let correctCount = 0;
  Object.keys(item.correctPairs).forEach(needId => {
    if (matchPairsAnswers.value[needId] === item.correctPairs[needId]) correctCount++;
  });

  const isCorrect = correctCount === Object.keys(item.correctPairs).length;
  quizState.value.quizFeedbackType = isCorrect ? 'success' : 'wrong';
  quizState.value.quizFeedback = isCorrect ? "Luar biasa! Semua fitur terpasang dengan tepat." : "Ada yang kurang pas, ingat fitur harus sesuai dengan kebutuhan user.";
  revealQuizNext();
};

const handleFeasibilitySelect = (itemId, bucketId) => {
  if (quizState.value.choicesDisabled) return;

  if (itemId && !bucketId) {
    activeFeasibilityItem.value = activeFeasibilityItem.value === itemId ? null : itemId;
  } else if (bucketId && activeFeasibilityItem.value) {
    feasibilityAnswers.value[activeFeasibilityItem.value] = bucketId;
    activeFeasibilityItem.value = null;
  }
};

const submitFeasibilityBuckets = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'feasibility_buckets') return;

  if (!isFeasibilityFollowUp.value && item.followUp) {
    // Stage 1: buckets
    let correctCount = 0;
    item.items.forEach(i => {
      if (feasibilityAnswers.value[i.id] === i.answer) correctCount++;
    });

    if (correctCount === item.items.length) {
      quizState.value.quizFeedbackType = 'success';
      quizState.value.quizFeedback = "Hebat! Pengelompokanmu akurat. Lanjut ke tantangan berikutnya!";
      // Show followup instead of revealing next
      setTimeout(() => {
        isFeasibilityFollowUp.value = true;
        quizState.value.quizFeedback = "";
        quizState.value.quizFeedbackType = "";
      }, 1500);
    } else {
      quizState.value.quizFeedbackType = 'wrong';
      quizState.value.quizFeedback = "Ada fitur yang salah kamar. Coba ingat lagi apa yang paling feasible dibuat dengan Python dasar.";
      revealQuizNext();
    }
  } else if (isFeasibilityFollowUp.value) {
    // Stage 2: fill_in_blank
    quizState.value.choicesDisabled = true;
    let correctCount = 0;
    item.followUp.blanks.forEach(b => {
      if (fillInBlankAnswers.value[b] === item.followUp.correctAnswers[b]) correctCount++;
    });
    const isCorrect = correctCount === item.followUp.blanks.length;
    quizState.value.quizFeedbackType = isCorrect ? 'success' : 'wrong';
    quizState.value.quizFeedback = isCorrect ? "Kalimat masalahmu sudah lengkap dan benar!" : "Kalimat masalah belum tepat, periksa lagi hubungannya.";
    revealQuizNext();
  }
};
"""

content = content.replace("const submitInputAnswer = () => {", handlers + "\n\nconst submitInputAnswer = () => {")

# 4. Hide submit button and Next button logic for new types? No, just rely on their own buttons.
# In the template, we need to hide the answerRow for these new types.
content = re.sub(
    r'v-show="currentQuestion && currentQuestion.type !== \'essay\' && currentQuestion.type !== \'card_choice\' && currentQuestion.type !== \'input\' && currentQuestion.type !== \'info\'"',
    r'v-show="currentQuestion && currentQuestion.type !== \'essay\' && currentQuestion.type !== \'card_choice\' && currentQuestion.type !== \'input\' && currentQuestion.type !== \'info\' && currentQuestion.type !== \'classify_problem\' && currentQuestion.type !== \'match_pairs\' && currentQuestion.type !== \'feasibility_buckets\'"',
    content
)


templates = """
        <!-- NEW QUIZ UI: Classify Problem -->
        <div v-if="currentQuestion && currentQuestion.type === 'classify_problem'" class="classify-problem-container" style="margin-top: 15px;">
          <div style="background: rgba(30, 41, 59, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
            <p style="font-weight: bold; margin-bottom: 5px;">Potongan Kalimat:</p>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <button 
                v-for="part in currentQuestion.parts" 
                :key="part.id"
                @click="handleClassifySelect(part.id, null)"
                :disabled="Object.values(classifyProblemAnswers).includes(part.id) || quizState.choicesDisabled"
                :style="{
                  padding: '8px 12px', borderRadius: '4px', border: '1px solid #757575', 
                  background: activeClassifyPart === part.id ? '#00c3ff' : '#fff',
                  color: activeClassifyPart === part.id ? '#000' : '#000',
                  opacity: Object.values(classifyProblemAnswers).includes(part.id) ? 0.3 : 1,
                  cursor: 'pointer'
                }"
              >{{ part.text }}</button>
            </div>
          </div>
          <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
            <div 
              v-for="bucket in currentQuestion.buckets" 
              :key="bucket"
              @click="handleClassifySelect(null, bucket)"
              style="border: 2px dashed #00c3ff; border-radius: 8px; padding: 10px; text-align: center; cursor: pointer;"
            >
              <div style="font-size: 14px; font-weight: bold; color: #00c3ff; margin-bottom: 8px;">{{ bucket }}</div>
              <div v-if="classifyProblemAnswers[bucket]" style="background: #00c3ff; color: #000; padding: 6px; border-radius: 4px; font-size: 14px;">
                {{ currentQuestion.parts.find(p => p.id === classifyProblemAnswers[bucket])?.text }}
              </div>
              <div v-else style="color: #94a3b8; font-size: 13px;">Klik untuk isi</div>
            </div>
          </div>
          <button 
            class="cek-jawaban-btn" 
            :disabled="Object.values(classifyProblemAnswers).filter(v => v).length < currentQuestion.buckets.length || quizState.choicesDisabled"
            @click="submitClassifyProblem"
          >Kirim Jawaban</button>
        </div>

        <!-- NEW QUIZ UI: Match Pairs -->
        <div v-if="currentQuestion && currentQuestion.type === 'match_pairs'" class="match-pairs-container" style="margin-top: 15px;">
          <div style="display: flex; gap: 20px;">
            <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
              <p style="font-weight: bold;">Kebutuhan Pengguna</p>
              <button 
                v-for="need in currentQuestion.needs" 
                :key="need.id"
                @click="matchPairsAnswers[need.id] ? clearMatchPair(need.id) : handleMatchSelect(need.id, null)"
                :disabled="quizState.choicesDisabled"
                :style="{
                  padding: '10px', borderRadius: '4px', border: '2px solid #757575',
                  background: activeMatchNeed === need.id ? '#00c3ff' : (matchPairsAnswers[need.id] ? '#50fa7b' : '#fff'),
                  color: '#000', cursor: 'pointer', textAlign: 'left'
                }"
              >
                {{ need.id }}. {{ need.text }}
                <div v-if="matchPairsAnswers[need.id]" style="margin-top: 5px; font-size: 12px; font-weight: bold; color: #000;">
                  => {{ currentQuestion.features.find(f => f.id === matchPairsAnswers[need.id])?.text }} (Klik untuk batal)
                </div>
              </button>
            </div>
            <div style="flex: 1; display: flex; flex-direction: column; gap: 10px;">
              <p style="font-weight: bold;">Fitur Aplikasi</p>
              <button 
                v-for="feature in currentQuestion.features" 
                :key="feature.id"
                @click="handleMatchSelect(null, feature.id)"
                :disabled="Object.values(matchPairsAnswers).includes(feature.id) || quizState.choicesDisabled"
                :style="{
                  padding: '10px', borderRadius: '4px', border: '1px solid #757575',
                  background: Object.values(matchPairsAnswers).includes(feature.id) ? '#ddd' : '#fff',
                  color: Object.values(matchPairsAnswers).includes(feature.id) ? '#999' : '#000',
                  cursor: Object.values(matchPairsAnswers).includes(feature.id) ? 'not-allowed' : 'pointer', textAlign: 'left'
                }"
              >
                {{ feature.id }}. {{ feature.text }}
              </button>
            </div>
          </div>
          <div style="margin-top: 15px;">
            <button 
              class="cek-jawaban-btn" 
              :disabled="Object.values(matchPairsAnswers).filter(v => v).length < currentQuestion.needs.length || quizState.choicesDisabled"
              @click="submitMatchPairs"
            >Kirim Jawaban</button>
          </div>
        </div>

        <!-- NEW QUIZ UI: Feasibility Buckets -->
        <div v-if="currentQuestion && currentQuestion.type === 'feasibility_buckets'" class="feasibility-buckets-container" style="margin-top: 15px;">
          
          <!-- Stage 1 -->
          <div v-if="!isFeasibilityFollowUp">
            <div style="background: rgba(30, 41, 59, 0.4); border-radius: 8px; padding: 10px; margin-bottom: 15px;">
              <p style="font-weight: bold; margin-bottom: 5px;">Daftar Fitur (Klik untuk pilih):</p>
              <div style="display: flex; flex-wrap: wrap; gap: 8px;">
                <button 
                  v-for="item in currentQuestion.items" 
                  :key="item.id"
                  @click="handleFeasibilitySelect(item.id, null)"
                  :disabled="feasibilityAnswers[item.id] || quizState.choicesDisabled"
                  :style="{
                    padding: '8px 12px', borderRadius: '4px', border: '1px solid #757575', 
                    background: activeFeasibilityItem === item.id ? '#00c3ff' : '#fff',
                    color: '#000',
                    opacity: feasibilityAnswers[item.id] ? 0.3 : 1,
                    cursor: 'pointer'
                  }"
                >{{ item.text }}</button>
              </div>
            </div>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 15px;">
              <!-- Feasible Bucket -->
              <div @click="handleFeasibilitySelect(null, 'feasible')" style="border: 2px dashed #50fa7b; border-radius: 8px; padding: 10px; text-align: center; cursor: pointer;">
                <div style="font-size: 16px; font-weight: bold; color: #50fa7b; margin-bottom: 8px;">🟢 Bisa Dibuat Sekarang (Feasible)</div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                  <div v-for="(ans, key) in feasibilityAnswers" :key="key" v-show="ans === 'feasible'" style="background: #50fa7b; color: #000; padding: 6px; border-radius: 4px; font-size: 13px; display: flex; justify-content: space-between;">
                    {{ currentQuestion.items.find(i => i.id === key)?.text }}
                    <span @click.stop="feasibilityAnswers[key] = null" style="cursor: pointer; font-weight: bold;">✖</span>
                  </div>
                </div>
              </div>
              <!-- Not Feasible Bucket -->
              <div @click="handleFeasibilitySelect(null, 'not_feasible')" style="border: 2px dashed #ff5555; border-radius: 8px; padding: 10px; text-align: center; cursor: pointer;">
                <div style="font-size: 16px; font-weight: bold; color: #ff5555; margin-bottom: 8px;">🔴 Nanti Saja (Not Feasible)</div>
                <div style="display: flex; flex-direction: column; gap: 5px;">
                  <div v-for="(ans, key) in feasibilityAnswers" :key="key" v-show="ans === 'not_feasible'" style="background: #ff5555; color: #000; padding: 6px; border-radius: 4px; font-size: 13px; display: flex; justify-content: space-between;">
                    {{ currentQuestion.items.find(i => i.id === key)?.text }}
                    <span @click.stop="feasibilityAnswers[key] = null" style="cursor: pointer; font-weight: bold;">✖</span>
                  </div>
                </div>
              </div>
            </div>
            <button 
              class="cek-jawaban-btn" 
              :disabled="Object.keys(feasibilityAnswers).filter(k => feasibilityAnswers[k]).length < currentQuestion.items.length || quizState.choicesDisabled"
              @click="submitFeasibilityBuckets"
            >Kirim Pengelompokan</button>
          </div>

          <!-- Stage 2: Fill in Blank -->
          <div v-else>
            <p style="font-weight: bold; color: #00c3ff;">{{ currentQuestion.followUp.question }}</p>
            <div style="background: rgba(30, 41, 59, 0.4); padding: 15px; border-radius: 8px; font-size: 16px; line-height: 2;">
              <template v-for="(part, idx) in currentQuestion.followUp.template.split(/(\[.*?\])/)" :key="idx">
                <span v-if="!part.startsWith('[')">{{ part }}</span>
                <select 
                  v-else 
                  v-model="fillInBlankAnswers[part.replace('[','').replace(']','')]" 
                  :disabled="quizState.choicesDisabled"
                  style="padding: 4px; margin: 0 5px; border-radius: 4px; background: #fff; color: #000; border: 1px solid #757575; outline: none; font-size: 14px;"
                >
                  <option disabled value="">- Pilih Jawaban -</option>
                  <option v-for="opt in currentQuestion.followUp.options" :key="opt" :value="opt">{{ opt }}</option>
                </select>
              </template>
            </div>
            <button 
              class="cek-jawaban-btn" 
              style="margin-top: 15px;"
              :disabled="Object.keys(fillInBlankAnswers).length < currentQuestion.followUp.blanks.length || quizState.choicesDisabled"
              @click="submitFeasibilityBuckets"
            >Kirim Kalimat</button>
          </div>
        </div>
"""

content = content.replace("        <div v-if=\"currentQuestion && currentQuestion.type === 'input'\"", templates + "\n\n        <div v-if=\"currentQuestion && currentQuestion.type === 'input'\"")

with open("src/App.vue", "w") as f:
    f.write(content)
print("App.vue updated successfully")
