<script setup>
import { ref, computed, onMounted, onUnmounted, watch, nextTick, reactive } from 'vue';
import { courseData } from './courseData.js';
import { getProject, types } from '@theatre/core';

const theatreState = {
  "revisionHistory": [],
  "definitionVersion": "0.4.0",
  "sheetsById": {
    "QuizSheet": {
      "sequence": {
        "type": "PositionalSequence",
        "length": 1,
        "tracksByObject": {
          "QuizOverlay": {
            "trackDataByPropertyPath": {
              "y": {
                "type": "BasicKeyframedTrack",
                "keyframes": [
                  { "id": "k1", "position": 0, "value": 80, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] },
                  { "id": "k1b", "position": 0.3, "value": -15, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] },
                  { "id": "k2", "position": 0.45, "value": 0, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] }
                ]
              },
              "opacity": {
                "type": "BasicKeyframedTrack",
                "keyframes": [
                  { "id": "k3", "position": 0, "value": 0, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] },
                  { "id": "k4", "position": 0.25, "value": 1, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] }
                ]
              },
              "scale": {
                "type": "BasicKeyframedTrack",
                "keyframes": [
                  { "id": "k5", "position": 0, "value": 0.8, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] },
                  { "id": "k5b", "position": 0.3, "value": 1.05, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] },
                  { "id": "k6", "position": 0.45, "value": 1, "connectedRight": true, "handles": [ 0.5, 1, 0.5, 0 ] }
                ]
              }
            }
          }
        }
      }
    }
  }
};
const proj = getProject('LMSProject', { state: theatreState });
const sheet = proj.sheet('QuizSheet');
const quizObj = sheet.object('QuizOverlay', { y: 50, opacity: 0, scale: 0.95 });
const quizModalStyles = ref({ transform: 'translateY(50px) scale(0.95)', opacity: 0, display: 'none' });


// Reactive App States
const currentStep = ref(1);
const totalSteps = Object.keys(courseData).length;
const APP_SCRIPT_URL = 'https://script.google.com/macros/s/AKfycbz58EffczfpcNL0bvbD6VZvrY3mrVNtmpWasSwJT0baOowD2yGu_KNM0YNul9EtxxKVpg/exec';
const isLoggedIn = ref(false);
const loginSchool = ref('');
const loginEmail = ref('');
const selectedSchool = ref('');
const isLoggingIn = ref(false);
const showLoginError = ref(false);
const loginErrorTitle = ref('');
const loginErrorMessage = ref('');
const schoolOptions = ref([]);
const isSchoolLoading = ref(false);
const isSchoolDropdownOpen = ref(false);
const loginEmailAttempts = ref(0);
const loginEmailSuggestion = ref(null);
const emailHelpOpen = ref(false);
const emailHelpQuery = ref('');
const emailHelpResults = ref([]);
const isEmailHelpLoading = ref(false);

const showProfileMenu = ref(false);

const isDesktop = ref(window.innerWidth > 1024);
const updateWidth = () => { isDesktop.value = window.innerWidth > 1024; };
let schoolSearchTimer = null;
let schoolSearchRequestId = 0;

const studentData = ref({ name: '', school: '', email: '' });
const studentProgress = ref({}); // Menyimpan progress jawaban & attempts

const hasInlinePyQuiz = (lessonData) => {
  return lessonData?.quizzes?.[0]?.questions?.[0]?.type === 'pyscript';
};

// Tambahkan auto-ID ke semua soal agar gampang ditrack
Object.keys(courseData).forEach(stepId => {
  let qCounter = 1;
  courseData[stepId].quizzes?.forEach(quiz => {
    quiz.questions.forEach(q => {
      q.qid = `V${stepId}_Q${qCounter}`;
      qCounter++;
    });
  });
});

const saveProgress = (key, value) => {
  studentProgress.value[key] = value;
  localStorage.setItem('mds_student_progress', JSON.stringify(studentProgress.value));
  syncToSheets();
};

const syncToSheets = async () => {
  if (!isLoggedIn.value) return;
  const payload = {
    Group: 'ghs2d',
    Students_Email: studentData.value.email,
    Students_Name: studentData.value.name,
    Students_School: studentData.value.school,
    ...studentProgress.value
  };
  try {
    await fetch(APP_SCRIPT_URL, {
      method: 'POST',
      body: JSON.stringify(payload),
      headers: { 'Content-Type': 'text/plain;charset=utf-8' } // text/plain untuk bypass CORS AppScript
    });
  } catch(err) {
    console.error("Sync error", err);
  }
};

const recordQuestionAttempt = (qid, answerStr, isCorrect) => {
  if (!qid) return;

  const attKey = `${qid}_Att`;
  const ansKey = `${qid}_Ans`;
  const attempts = (studentProgress.value[attKey] || 0) + 1;

  studentProgress.value[attKey] = attempts;
  if (isCorrect || attempts >= 3) {
    studentProgress.value[ansKey] = isCorrect ? answerStr : '-';
  }

  localStorage.setItem('mds_student_progress', JSON.stringify(studentProgress.value));
  syncToSheets();
};

const handleLogin = async () => {
  if (!selectedSchool.value || !loginEmail.value.trim()) {
    loginErrorTitle.value = 'Lengkapi dulu ya';
    loginErrorMessage.value = 'Pilih sekolah, lalu masukkan email yang terdaftar di Akademia Ruangguru.';
    showLoginError.value = true;
    return;
  }
  
  isLoggingIn.value = true;
  showLoginError.value = false;
  loginEmailSuggestion.value = null;

  try {
    const nextAttempt = loginEmailAttempts.value + 1;
    const params = new URLSearchParams({
      action: 'login',
      school: selectedSchool.value,
      email: loginEmail.value,
      attempts: String(nextAttempt)
    });
    const res = await fetch(`${APP_SCRIPT_URL}?${params.toString()}`);
    const data = await res.json();
    if (data.success) {
      studentData.value = { name: data.name, school: data.school, email: data.email };
      isLoggedIn.value = true;
      loginEmailAttempts.value = 0;
      localStorage.setItem('mds_student_login', JSON.stringify(studentData.value));
    } else {
      loginEmailAttempts.value = nextAttempt;
      loginErrorTitle.value = data.needsRfo ? 'Perlu bantuan RFO' : 'Email belum cocok';
      loginErrorMessage.value = data.message || 'Email ini belum cocok dengan data Akademia Ruangguru untuk sekolah yang dipilih. Coba cek lagi penulisannya ya.';
      loginEmailSuggestion.value = data.suggestion || null;
      showLoginError.value = true;
    }
  } catch (err) {
    console.error("Login error", err);
    loginErrorTitle.value = 'Belum bisa masuk';
    loginErrorMessage.value = 'Koneksi ke data siswa belum berhasil. Coba lagi sebentar ya.';
    showLoginError.value = true;
  } finally {
    isLoggingIn.value = false;
  }
};

const fetchSchoolOptions = async (query = loginSchool.value) => {
  const requestId = ++schoolSearchRequestId;
  isSchoolLoading.value = true;
  try {
    const params = new URLSearchParams({ action: 'schools', query });
    const res = await fetch(`${APP_SCRIPT_URL}?${params.toString()}`);
    const data = await res.json();
    if (requestId === schoolSearchRequestId && data.success) schoolOptions.value = data.schools || [];
  } catch (err) {
    console.error("School search error", err);
  } finally {
    if (requestId === schoolSearchRequestId) isSchoolLoading.value = false;
  }
};

const fetchEmailHelpResults = async (query = emailHelpQuery.value) => {
  if (!selectedSchool.value || !query.trim()) {
    emailHelpResults.value = [];
    return;
  }
  isEmailHelpLoading.value = true;
  try {
    const params = new URLSearchParams({ action: 'students', school: selectedSchool.value, query });
    const res = await fetch(`${APP_SCRIPT_URL}?${params.toString()}`);
    const data = await res.json();
    if (data.success) emailHelpResults.value = data.students || [];
  } catch (err) {
    console.error("Email help search error", err);
  } finally {
    isEmailHelpLoading.value = false;
  }
};

const handleSchoolInput = () => {
  selectedSchool.value = '';
  loginEmail.value = '';
  emailHelpQuery.value = '';
  emailHelpResults.value = [];
  isSchoolDropdownOpen.value = true;
  loginEmailAttempts.value = 0;
  loginEmailSuggestion.value = null;
  showLoginError.value = false;
  if (schoolSearchTimer) clearTimeout(schoolSearchTimer);
  schoolSearchTimer = setTimeout(() => fetchSchoolOptions(), 250);
};

const handleEmailInput = () => {
  loginEmailSuggestion.value = null;
  showLoginError.value = false;
};

const handleEmailHelpInput = () => {
  fetchEmailHelpResults();
};

const openSchoolDropdown = () => {
  isSchoolDropdownOpen.value = true;
  fetchSchoolOptions('');
};

const closeSchoolDropdownSoon = () => {
  setTimeout(() => {
    isSchoolDropdownOpen.value = false;
  }, 120);
};

const selectSchool = (school) => {
  loginSchool.value = school;
  selectedSchool.value = school;
  loginEmail.value = '';
  emailHelpQuery.value = '';
  emailHelpResults.value = [];
  isSchoolDropdownOpen.value = false;
  loginEmailAttempts.value = 0;
  loginEmailSuggestion.value = null;
  showLoginError.value = false;
};

const toggleEmailHelp = () => {
  emailHelpOpen.value = !emailHelpOpen.value;
  if (!emailHelpOpen.value) return;
  emailHelpQuery.value = '';
  emailHelpResults.value = [];
};


onUnmounted(() => {
  window.removeEventListener('resize', updateWidth);
});

const handleLogout = () => {
  localStorage.removeItem('mds_student_login');
  isLoggedIn.value = false;
  loginSchool.value = '';
  loginEmail.value = '';
  selectedSchool.value = '';
  isSchoolDropdownOpen.value = false;
  loginEmailAttempts.value = 0;
  loginEmailSuggestion.value = null;
  emailHelpOpen.value = false;
  emailHelpQuery.value = '';
  emailHelpResults.value = [];
  studentData.value = { email: '', name: '', school: '' };
};


onMounted(() => {
  initQuizPyodide();
  window.addEventListener('resize', updateWidth);

  const savedLogin = localStorage.getItem('mds_student_login');
  if (savedLogin) {
    studentData.value = JSON.parse(savedLogin);
    isLoggedIn.value = true;
  }
  const savedProgress = localStorage.getItem('mds_student_progress');
  if (savedProgress) {
    studentProgress.value = JSON.parse(savedProgress);
  }
});

const videoWatchedStatus = ref({
  1: false, 2: false, 3: false, 4: false, 5: false, 6: false, 7: false
});

const youtubeReady = ref(false);
const players = {};
const timeCheckers = {};

const initialPlayerStates = {};
for (const step in courseData) {
  initialPlayerStates[step] = { isPlaying: false, currentTime: 0, duration: 0, isMuted: false, isReady: false, isError: false, hasStarted: false, isBuffering: false };
}
const playerStates = ref(initialPlayerStates);

const introRefs = ref({});
const introPlayed = ref({});
const introVideoSrc = import.meta.env.BASE_URL + 'intro.mp4';


const isFullscreen = ref(false);
const videoContainers = ref({});

// Quiz Overlay States

// --- NEW QUIZ TYPES STATE ---
const classifyProblemAnswers = ref({});
const activeClassifyPart = ref(null);

const matchPairsAnswers = ref({});
const activeMatchNeed = ref(null);

const feasibilityAnswers = ref({});
const activeFeasibilityItem = ref(null);

const fillInBlankAnswers = ref({});
const isFeasibilityFollowUp = ref(false);

const quizState = ref({
  isOpen: false,
  shuffledQuestions: [],
  currentQuestionIdx: 0,
  resumeVideoAfterQuiz: false,
  resumeVideoTime: null,
  quizFeedback: '',
  quizFeedbackType: '',
  essayAnswer: '',
  isNextBtnVisible: false,
  nextBtnText: 'Soal berikutnya →',
  activeQuizConfig: null,
  activeQuizStep: null,
  replayingQuizVideo: false,
  replayCheckpointArmed: false,
  choicesDisabled: false,
  inputAnswer: '',
  arrangeFlowAnswers: []
});

const quizReturn = ref({
  isVisible: false
});

// Pyodide State
let pyodide = null;
const isPyodideLoading = ref(true);
const pyodideOutput = ref('');
const pyscriptCode = ref('');

const initQuizPyodide = async () => {
  if (window.loadPyodide) {
    try {
      pyodide = await window.loadPyodide();
      pyodide.globals.set('custom_input', (msg) => {
        const val = prompt(msg);
        return val !== null ? val : '';
      });
      await pyodide.runPythonAsync(`
import builtins
builtins.input = custom_input
      `);
      isPyodideLoading.value = false;
      console.log('Pyodide ready');
    } catch (e) {
      console.error('Pyodide failed to load', e);
    }
  } else {
    setTimeout(initQuizPyodide, 500);
  }
};

const runPython = async () => {
  if (!pyodide) return;
  pyodideOutput.value = '';
  quizState.value.quizFeedback = '';
  quizState.value.quizFeedbackType = '';
  let logs = [];
  pyodide.setStdout({ batched: (msg) => logs.push(msg) });
  pyodide.setStderr({ batched: (msg) => logs.push("ERROR: " + msg) });
  try {
    await pyodide.runPythonAsync(pyscriptCode.value);
    pyodideOutput.value = logs.join('\\n');
  } catch (err) {
    pyodideOutput.value = logs.join('\\n') + '\\n' + err.message;
  }
};

const submitPython = async () => {
  if (!pyodide) return;
  quizState.value.quizFeedback = '';
  quizState.value.quizFeedbackType = '';

  const getActivePythonQuestion = () => {
    const modalQuestion = quizState.value.shuffledQuestions[quizState.value.currentQuestionIdx];
    if (modalQuestion?.type === 'pyscript') return modalQuestion;

    const stepKey = String(currentStep.value);
    const inlineQuestion = courseData[stepKey]?.quizzes?.[0]?.questions?.[0];
    return inlineQuestion?.type === 'pyscript' ? inlineQuestion : null;
  };
  
  const mockInputs = ["Snack", "pengeluaran", "10000"];
  let inputIndex = 0;
  pyodide.globals.set('custom_input', (msg) => mockInputs[inputIndex++]);
  
  let logs = [];
  pyodide.setStdout({ batched: (msg) => logs.push(msg) });
  pyodide.setStderr({ batched: (msg) => logs.push("ERROR: " + msg) });
  
  try {
    const currQ = getActivePythonQuestion();
    const codeToRun = currQ?.validationTest
      ? `${pyscriptCode.value}\n\n${currQ.validationTest}`
      : pyscriptCode.value;

    await pyodide.runPythonAsync(codeToRun);
    pyodideOutput.value = logs.join('\n');

    const missingRequired = currQ?.requiredCodeIncludes?.filter(token => !pyscriptCode.value.includes(token)) || [];
    if (missingRequired.length > 0) {
       quizState.value.quizFeedback = `Kode sudah bisa jalan, tapi belum lengkap. Pastikan ada bagian ini: ${missingRequired.join(', ')}`;
       quizState.value.quizFeedbackType = 'wrong';
       recordQuestionAttempt(currQ?.qid, pyscriptCode.value, false);
       return;
    }
    
    if (currQ && currQ.expectedOutput) {
       if (pyodideOutput.value.trim() === String(currQ.expectedOutput).trim()) {
         quizState.value.quizFeedback = "Luar biasa! Kode kamu berhasil dijalankan dan outputnya tepat! 🚀";
         quizState.value.quizFeedbackType = 'success';
         quizState.value.isNextBtnVisible = true;
         recordQuestionAttempt(currQ.qid, pyscriptCode.value, true);
       } else {
         quizState.value.quizFeedback = "Hmm, outputnya belum sesuai target. Coba cek lagi kodemu!";
         quizState.value.quizFeedbackType = 'wrong';
         recordQuestionAttempt(currQ.qid, pyscriptCode.value, false);
       }
    } else if (currQ && currQ.allowAnyOutput) {
       quizState.value.quizFeedback = "Luar biasa! Kode kamu berhasil dijalankan! 🚀";
       quizState.value.quizFeedbackType = 'success';
       quizState.value.isNextBtnVisible = true;
       recordQuestionAttempt(currQ.qid, pyscriptCode.value, true);
    } else if (currQ && currQ.successKeywords) {
       const normalizedOutput = pyodideOutput.value.toLowerCase();
       const allKeywordsFound = currQ.successKeywords.every(keyword => normalizedOutput.includes(String(keyword).toLowerCase()));
       if (allKeywordsFound) {
         quizState.value.quizFeedback = "Luar biasa! Kode kamu berhasil dijalankan dan outputnya sesuai! 🚀";
         quizState.value.quizFeedbackType = 'success';
         quizState.value.isNextBtnVisible = true;
         recordQuestionAttempt(currQ.qid, pyscriptCode.value, true);
       } else {
         quizState.value.quizFeedback = "Hmm, outputnya belum sesuai target. Coba cek lagi validasi dan hasil print-mu!";
         quizState.value.quizFeedbackType = 'wrong';
         recordQuestionAttempt(currQ.qid, pyscriptCode.value, false);
       }
    } else if (pyodideOutput.value.includes("Transaksi valid:") || pyodideOutput.value.toLowerCase().includes("ditemukan")) {
       quizState.value.quizFeedback = "Luar biasa! Kode kamu berhasil dijalankan dan outputnya sesuai! 🚀";
       quizState.value.quizFeedbackType = 'success';
       quizState.value.isNextBtnVisible = true;
       recordQuestionAttempt(currQ?.qid, pyscriptCode.value, true);
    } else {
       quizState.value.quizFeedback = "Hmm, outputnya belum sesuai target. Coba cek validasimu!";
       quizState.value.quizFeedbackType = 'wrong';
       recordQuestionAttempt(currQ?.qid, pyscriptCode.value, false);
    }
  } catch (err) {
    pyodideOutput.value = logs.join('\n') + '\n' + err.message;
    quizState.value.quizFeedback = "Ada error di kodemu. Cek log output di bawah ya!";
    quizState.value.quizFeedbackType = 'wrong';
    recordQuestionAttempt(getActivePythonQuestion()?.qid, pyscriptCode.value, false);
  } finally {
    pyodide.globals.set('custom_input', (msg) => {
      const val = prompt(msg);
      return val !== null ? val : '';
    });
  }
};

const showCompletionToast = ref(false);
const failedAttempts = ref({});

// Time formatting helper
const formatVideoTime = (value) => {
  const totalSeconds = Number.isFinite(value) ? Math.max(0, Math.floor(value)) : 0;
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = String(totalSeconds % 60).padStart(2, "0");
  return minutes + ":" + seconds;
};

const getBookmarks = (stepId) => {
  return courseData[stepId]?.bookmarks || [];
};

const getVideoStartBoundary = (stepId) => {
  return courseData[stepId]?.startSeconds || 0;
};

// Seek boundary enforcement
const enforceVideoBoundaries = (stepId) => {
  const player = players[stepId];
  if (!player || typeof player.getCurrentTime !== "function" || typeof player.seekTo !== "function") return;
  const currentTime = player.getCurrentTime();
  const startBoundary = getVideoStartBoundary(stepId);
  const endBoundary = courseData[stepId]?.endSeconds;

  const skipSegments = courseData[stepId]?.skipSegments || [];
  for (const seg of skipSegments) {
    if (currentTime >= seg.start && currentTime < seg.end) {
      player.seekTo(seg.end, true);
      return;
    }
  }

  if (startBoundary > 0 && currentTime < startBoundary - 0.5) {
    player.seekTo(startBoundary, true);
  } else if (endBoundary > 0 && currentTime >= endBoundary) {
    player.seekTo(endBoundary, true);
    player.pauseVideo();
  }
};

const updateVideoControls = (stepId) => {
  const player = players[stepId];
  if (!player || typeof player.getCurrentTime !== "function") return;

  const startBoundary = getVideoStartBoundary(stepId);
  const endBoundary = courseData[stepId]?.endSeconds;
  
  const rawDuration = endBoundary || player.getDuration() || 0;
  const rawCurrentTime = player.getCurrentTime() || 0;
  let duration = Math.max(0, rawDuration - startBoundary);
  let currentTime = Math.max(0, rawCurrentTime - startBoundary);

  const skipSegments = courseData[stepId]?.skipSegments || [];
  let totalSkippedForDuration = 0;
  let totalSkippedForCurrent = 0;
  for (const seg of skipSegments) {
    totalSkippedForDuration += (seg.end - seg.start);
    if (rawCurrentTime > seg.start) {
      if (rawCurrentTime < seg.end) {
        totalSkippedForCurrent += (rawCurrentTime - seg.start);
      } else {
        totalSkippedForCurrent += (seg.end - seg.start);
      }
    }
  }
  
  duration = Math.max(0, duration - totalSkippedForDuration);
  currentTime = Math.max(0, currentTime - totalSkippedForCurrent);

  playerStates.value[stepId].duration = duration;
  playerStates.value[stepId].currentTime = currentTime;
  playerStates.value[stepId].progress = duration > 0 ? (currentTime / duration * 100) : 0;
  playerStates.value[stepId].durationFormatted = formatVideoTime(duration);
  playerStates.value[stepId].currentTimeFormatted = formatVideoTime(currentTime);
};

// Video actions
const playVideo = (stepId) => {
  playerStates.value[stepId].hasStarted = true;
  const player = players[stepId];
  if (!player || typeof player.getPlayerState !== "function") {
    initializeYouTubePlayer(stepId);
    // YouTube player onReady will not autoplay unless we tell it to,
    // but the player itself is now visible so the user can click it or we can play it if ready.
    setTimeout(() => {
      if (players[stepId] && typeof players[stepId].playVideo === 'function') {
         players[stepId].playVideo();
      }
    }, 500);
    return;
  }
  player.playVideo();
};

const playIntroThenVideo = async (stepId) => {
  const introEl = introRefs.value[stepId];
  if (introEl && !introPlayed.value[stepId]) {
    playerStates.value[stepId].introPlaying = true;
    playerStates.value[stepId].hasStarted = true;
    await nextTick();
    introEl.currentTime = 0;
    introEl.play().catch(e => {
      console.error("Intro video play error:", e);
      onIntroEnded(stepId);
    });
  } else {
    onIntroEnded(stepId);
  }
};

const onIntroEnded = (stepId) => {
  introPlayed.value[stepId] = true;
  playerStates.value[stepId].introPlaying = false;
  
  const p = players.value[stepId];
  if (p && typeof p.playVideo === 'function') {
    p.playVideo();
  } else {
    pendingPlay.value[stepId] = true;
    initYouTubePlayer(stepId);
  }
};

const togglePlay = (stepId) => {
  if (playerStates.value[stepId] && !introPlayed.value[stepId]) {
    playIntroThenVideo(stepId);
    return;
  }
  const player = players[stepId];
  if (!player || typeof player.getPlayerState !== "function") {
    initializeYouTubePlayer(stepId);
    return;
  }
  if (playerStates.value[stepId].isPlaying) {
    player.pauseVideo();
  } else {
    player.playVideo();
  }
};

const toggleMute = (stepId) => {
  const player = players[stepId];
  if (!player || typeof player.isMuted !== "function") return;
  if (player.isMuted()) {
    player.unMute();
    playerStates.value[stepId].isMuted = false;
  } else {
    player.mute();
    playerStates.value[stepId].isMuted = true;
  }
};

const onSeekInput = (stepId, event) => {
  const player = players[stepId];
  if (!player || typeof player.seekTo !== "function") return;
  const startBoundary = getVideoStartBoundary(stepId);
  const duration = playerStates.value[stepId].duration || 0;
  const requestedRelativeTime = (duration * Number(event.target.value)) / 100;
  player.seekTo(startBoundary + requestedRelativeTime, true);
};

const toggleFullscreen = (stepId) => {
  const el = document.querySelector(`.video-frame[data-video-step="${stepId}"]`);
  if (!el) return;
  if (document.fullscreenElement) {
    document.exitFullscreen();
  } else {
    el.requestFullscreen();
  }
};

const seekToBookmark = (stepId, time) => {
  const player = players[stepId];
  if (player && typeof player.seekTo === "function") {
    player.seekTo(time, true);
    if (typeof player.playVideo === "function") player.playVideo();
    
    const container = videoContainers.value[stepId];
    if (container) {
      container.scrollIntoView({ behavior: "smooth", block: "center" });
    }
  }
};

// YouTube player setup
const initializeYouTubePlayer = (stepId) => {
  const normalizedStepId = String(stepId);
  if (!youtubeReady.value || players[normalizedStepId] || !courseData[normalizedStepId]) return;

  const playerId = "youtube-player-" + normalizedStepId;
  const domEl = document.getElementById(playerId);
  if (!domEl) return;

  playerStates.value[normalizedStepId].isError = false;

  players[normalizedStepId] = new window.YT.Player(playerId, {
    videoId: courseData[normalizedStepId].videoId,
    playerVars: {
      playsinline: 1,
      rel: 0,
      controls: 0,
      vq: 'hd1080',
      disablekb: 1,
      fs: 0,
      iv_load_policy: 3,
      start: courseData[normalizedStepId].startSeconds || 0,
      origin: window.location.origin
    },
    events: {
      onReady: (event) => {
        const iframe = event.target.getIframe();
        iframe.removeAttribute("allowfullscreen");
        iframe.setAttribute("tabindex", "-1");
        iframe.setAttribute("aria-hidden", "true");
        
        playerStates.value[normalizedStepId].isReady = true;
        playerStates.value[normalizedStepId].duration = event.target.getDuration() || 0;
        
        event.target.setPlaybackQuality('hd1080');
        enforceVideoBoundaries(normalizedStepId);
        updateVideoControls(normalizedStepId);
      },
      onError: () => {
        playerStates.value[normalizedStepId].isError = true;
      },
      onStateChange: (event) => handlePlayerStateChange(normalizedStepId, event)
    }
  });
};

const handlePlayerStateChange = (stepId, event) => {
  const isPlaying = event.data === window.YT.PlayerState.PLAYING;
  const isBuffering = event.data === window.YT.PlayerState.BUFFERING;
  playerStates.value[stepId].isBuffering = isBuffering;
  playerStates.value[stepId].isPlaying = isPlaying;

  if (isPlaying) {
    playerStates.value[stepId].hasStarted = true;
    enforceVideoBoundaries(stepId);
  }

  if (event.data === window.YT.PlayerState.ENDED) {
    videoWatchedStatus.value[stepId] = true;
  }

  updateVideoControls(stepId);

  window.clearInterval(timeCheckers[stepId]);
  if (isPlaying) {
    timeCheckers[stepId] = window.setInterval(() => {
      enforceVideoBoundaries(stepId);
      updateVideoControls(stepId);
      checkVideoQuizzes(stepId);
    }, 300);
  }
};

const checkVideoQuizzes = (stepId) => {
  const player = players[stepId];
  if (!player || typeof player.getCurrentTime !== 'function') return;

  const currentTime = player.getCurrentTime();
  const stepConfig = courseData[stepId];
  if (!stepConfig || !stepConfig.quizzes) return;

  for (let quiz of stepConfig.quizzes) {
    if (quizState.value.replayingQuizVideo && quiz === quizState.value.activeQuizConfig) {
      if (currentTime < quiz.time - 0.5) {
        quizState.value.replayCheckpointArmed = true;
      }
      if (!quizState.value.replayCheckpointArmed) continue;
    }

    if (!quiz.shown && currentTime >= quiz.time) {
      quiz.shown = true;
      player.pauseVideo();
      window.clearInterval(timeCheckers[stepId]);

      const shouldResume = quiz.resume !== undefined ? quiz.resume : true;
      openQuiz(quiz.questions, shouldResume, quiz.resumeTime, quiz, stepId);
      break;
    }
  }
};

// Quiz Functions
const shuffle = (items) => {
  const result = [...items];
  for (let i = result.length - 1; i > 0; i--) {
    const randomIndex = Math.floor(Math.random() * (i + 1));
    [result[i], result[randomIndex]] = [result[randomIndex], result[i]];
  }
  return result;
};

const openQuiz = (questionsArray, shouldResume = false, seekTime = null, quizConfig = null, stepId = currentStep.value) => {
  try {
    if (document.fullscreenElement) {
      const exitPromise = document.exitFullscreen();
      if (exitPromise !== undefined) exitPromise.catch(e => console.log(e));
    } else if (document.webkitFullscreenElement && document.webkitExitFullscreen) {
      document.webkitExitFullscreen();
    }
  } catch (err) {
    console.log('Exit fullscreen error:', err);
  }

  if (quizConfig) {
    quizState.value.activeQuizConfig = quizConfig;
    quizState.value.activeQuizStep = Number(stepId);
  } else {
    quizState.value.activeQuizConfig = null;
    quizState.value.activeQuizStep = null;
  }

  quizState.value.replayingQuizVideo = false;
  quizState.value.replayCheckpointArmed = false;
  quizReturn.value.isVisible = false;

  quizState.value.resumeVideoAfterQuiz = shouldResume;
  quizState.value.resumeVideoTime = seekTime;

  quizState.value.shuffledQuestions = shuffle([...questionsArray]);
  quizState.value.currentQuestionIdx = 0;
  quizState.value.isOpen = true;
  sheet.sequence.play({ direction: 'normal', range: [0, 0.4] });
  quizState.value.choicesDisabled = false;
  quizState.value.quizFeedback = '';
  quizState.value.quizFeedbackType = '';
  quizState.value.essayAnswer = '';
  quizState.value.arrangeFlowAnswers = [];
  quizState.value.isNextBtnVisible = false;
  quizState.value.nextBtnText = 'Soal berikutnya →';

  nextTick(() => {
    renderQuestion();
  });
};

const closeQuiz = (resumeVideo = false, seekTime = null) => {
  sheet.sequence.play({ direction: 'reverse', range: [0, 0.4] }).then(() => {
    quizState.value.isOpen = false;
  });
  if (resumeVideo && players[currentStep.value]) {
    const player = players[currentStep.value];
    if (seekTime !== null && typeof player.seekTo === "function") {
      player.seekTo(seekTime, true);
    }
    if (typeof player.playVideo === "function") {
      player.playVideo();
    }
  }
};

const currentQuestion = computed(() => {
  const questions = quizState.value.shuffledQuestions;
  const idx = quizState.value.currentQuestionIdx;
  if (questions && questions.length > 0 && idx < questions.length) {
    return questions[idx];
  }
  return null;
});

const isQuizFinished = computed(() => {
  return quizState.value.shuffledQuestions.length > 0 && 
         quizState.value.currentQuestionIdx >= quizState.value.shuffledQuestions.length;
});

const attachCustomHtmlListeners = () => {
  setTimeout(() => { // ensure DOM is fully updated
    document.querySelectorAll('.answer-opt-btn').forEach(btn => {
      btn.onclick = function() {
        this.innerHTML = "Memeriksa...";
        const isCorrect = this.getAttribute('data-correct') === 'true';
        const expl = this.getAttribute('data-explanation');
        if (window.checkGuess) window.checkGuess(this, isCorrect, expl);
      };
    });

    const wrapHandler = (btnId, handlerFn) => {
      const btn = document.getElementById(btnId);
      if (btn) {
        btn.onclick = function() {
          const originalText = this.innerHTML;
          this.innerHTML = "Memeriksa...";
          handlerFn(this);
          // Restore text after 1 second if still enabled
          setTimeout(() => { if (!this.disabled) this.innerHTML = originalText; }, 1000);
        };
      }
    };

    wrapHandler('mb1-check-btn', (btn) => {
      const kw = document.getElementById('mb1-kw');
      const cond = document.getElementById('mb1-cond');
      if (window.checkMB1QGuess) window.checkMB1QGuess(kw ? kw.value : '', cond ? cond.value : '', btn, 'Syarat yang benar adalah elif dan age < 18.');
    });
    wrapHandler('mb2-check-btn', (btn) => {
      const v1 = document.getElementById('mb2-val1');
      const v2 = document.getElementById('mb2-val2');
      if (window.checkMB2QGuess) window.checkMB2QGuess(v1 ? v1.value : '', v2 ? v2.value : '', btn, 'Kondisi yang lebih ketat harus ditaruh di atas!');
    });
    wrapHandler('paren-check-btn', (btn) => {
      const input = document.getElementById('paren-input');
      if (window.checkParenGuess) window.checkParenGuess(input ? input.value : '', btn, 'Kita harus mengevaluasi or di dalam kurung terlebih dahulu.');
    });
    wrapHandler('and-check-btn', (btn) => {
      const input = document.getElementById('and-input');
      if (window.checkAndGuess) window.checkAndGuess(input ? input.value : '', btn, 'Kedua syarat harus terpenuhi untuk mendapatkan beasiswa.');
    });
    wrapHandler('or-check-btn', (btn) => {
      const input = document.getElementById('or-input');
      if (window.checkOrGuess) window.checkOrGuess(input ? input.value : '', btn, 'Salah satu syarat harus terpenuhi.');
    });
    wrapHandler('logical-check-btn', (btn) => {
      const input = document.getElementById('logical-input');
      if (window.checkNestedToLogicalGuess) window.checkNestedToLogicalGuess(input ? input.value : '', btn, 'Dengan operator and kita bisa menggabungkan dua if bersarang.');
    });
    wrapHandler('needs-check-btn', (btn) => {
      if (window.checkNeedsWantsGuess) window.checkNeedsWantsGuess('needs-input', btn);
    });
    wrapHandler('wants-check-btn', (btn) => {
      if (window.checkNeedsWantsGuess) window.checkNeedsWantsGuess('wants-input', btn);
    });
    wrapHandler('ide6-run-btn', (btn) => {
      if (window.runPyodideCode) window.runPyodideCode('python-ide-6', 'ide-output-6');
    });
    wrapHandler('ide6-submit-btn', (btn) => {
      if (window.checkIde6Guess) window.checkIde6Guess(btn);
    });

    const dragItems = document.querySelectorAll('.drag-item');
    const dropZones = document.querySelectorAll('.drop-zone');
    const dragContainer = document.querySelector('.drag-container');

    dragItems.forEach(item => {
      item.addEventListener('dragstart', (e) => {
        e.dataTransfer.setData('text/plain', e.target.dataset.type);
        setTimeout(() => { e.target.style.opacity = '0.5'; }, 0);
      });
      item.addEventListener('dragend', (e) => {
        e.target.style.opacity = '1';
      });
    });

    if (dragContainer) {
      dragContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
      });
      dragContainer.addEventListener('drop', (e) => {
        e.preventDefault();
        const type = e.dataTransfer.getData('text/plain');
        const draggedItem = document.querySelector(`.drag-item[data-type="${type}"]`);
        if (draggedItem) {
          dragContainer.appendChild(draggedItem);
        }
      });
    }

    dropZones.forEach(zone => {
      zone.addEventListener('dragover', (e) => {
        e.preventDefault();
        zone.style.backgroundColor = '#e0f7fa';
      });
      zone.addEventListener('dragleave', (e) => {
        zone.style.backgroundColor = '#fafafa';
      });
      zone.addEventListener('drop', (e) => {
        e.preventDefault();
        zone.style.backgroundColor = '#fafafa';
        const type = e.dataTransfer.getData('text/plain');
        const draggedItem = document.querySelector(`.drag-item[data-type="${type}"]`);
        
        if (draggedItem) {
           const existingItem = zone.querySelector('.drag-item');
           if (existingItem) {
             if (dragContainer) dragContainer.appendChild(existingItem);
           } else {
             // Clear the "Tarik ke sini" text by checking if there's a span
             const span = zone.querySelector('span');
             if (span) span.remove();
           }
           zone.appendChild(draggedItem);
           draggedItem.style.margin = '0';
        }
      });
    });

    wrapHandler('check-drag-btn', (btn) => {
      let allCorrect = true;
      let allFilled = true;
      const placedAnswers = [];
      
      dropZones.forEach(zone => {
        const expected = zone.dataset.expected;
        const item = zone.querySelector('.drag-item');
        if (!item) {
          allFilled = false;
          allCorrect = false;
        } else {
          placedAnswers.push(`${expected}:${item.dataset.type}`);
          if (item.dataset.type !== expected) {
            allCorrect = false;
          }
        }
      });
      
      const feedbackEl = document.getElementById('drag-feedback');
      if (!allFilled) {
        recordQuestionAttempt(currentQuestion.value?.qid, placedAnswers.join(', ') || 'Belum lengkap', false);
        feedbackEl.innerHTML = '<span style="color: #ff3333;">Harap isi semua kotak terlebih dahulu!</span>';
        quizState.value.isNextBtnVisible = false;
      } else if (!allCorrect) {
        recordQuestionAttempt(currentQuestion.value?.qid, placedAnswers.join(', '), false);
        feedbackEl.innerHTML = '<span style="color: #ff3333;">Jawaban masih ada yang kurang tepat. Periksa kembali dan coba lagi!</span>';
        quizState.value.isNextBtnVisible = false;
      } else {
        recordQuestionAttempt(currentQuestion.value?.qid, placedAnswers.join(', '), true);
        feedbackEl.innerHTML = '<span style="color: #1a1a1a;">Luar biasa! Semua jawaban benar! 🎉</span>';
        btn.style.display = 'none';
        quizState.value.isNextBtnVisible = true;
        quizState.value.quizFeedbackType = 'correct';
        revealQuizNext();
      }
    });
  }, 100);
};

const renderQuestion = () => {
  if (currentQuestion.value && !currentQuestion.value.html) {
    nextTick(() => {
      const trueBtn = document.querySelector('.choice-btn.true-btn');
      if (trueBtn) trueBtn.focus();
    });
  } else if (currentQuestion.value && currentQuestion.value.html) {
    nextTick(() => {
      attachCustomHtmlListeners();
    });
  }
};

const revealQuizNext = (label = "Soal berikutnya →") => {
  quizState.value.nextBtnText = label;
  quizState.value.isNextBtnVisible = true;
  
  nextTick(() => {
    const nextBtn = document.querySelector('.quiz-next-btn');
    if (nextBtn) {
      nextBtn.scrollIntoView({ behavior: "smooth", block: "nearest" });
      nextBtn.focus({ preventScroll: true });
    }
  });
};

const registerFailedInputAttempt = (btn, feedbackEl) => {
  const key = btn.id || btn.className || 'default-btn';
  const attempts = (failedAttempts.value[key] || 0) + 1;
  failedAttempts.value[key] = attempts;
  quizState.value.isNextBtnVisible = false;

  const attemptStatus = document.createElement("div");
  attemptStatus.className = "attempt-status";

  if (attempts >= 3) {
    attemptStatus.classList.add("limit-reached");
    attemptStatus.innerHTML = "<strong>Sudah 3 kali mencoba.</strong><br>Jawabanmu masih belum tepat. Perhatikan lagi videonya, ya. Untuk sekarang kamu boleh lanjut dulu.";
    btn.disabled = true;
    btn.style.opacity = "0.55";
    revealQuizNext("Lanjut dulu →");
  } else {
    attemptStatus.textContent = `Percobaan ${attempts} dari 3. Periksa kembali kode atau jawabanmu sebelum mencoba lagi.`;
  }

  feedbackEl.appendChild(attemptStatus);
};

const handleStandardAnswer = (answer) => {
  const item = currentQuestion.value;
  if (!item) return;
  if (quizState.value.choicesDisabled) return;

  const isCorrect = answer === item.answer || answer === item.correct;
  quizState.value.selectedChoice = answer;
  
  let attempts = 0;
  if (item.qid) {
    const attKey = `${item.qid}_Att`;
    attempts = (studentProgress.value[attKey] || 0) + 1;
    studentProgress.value[attKey] = attempts;
    if (isCorrect || attempts >= 3) {
      const ansKey = `${item.qid}_Ans`;
      studentProgress.value[ansKey] = isCorrect ? String(answer) : '-';
    }
    localStorage.setItem('mds_student_progress', JSON.stringify(studentProgress.value));
    syncToSheets();
  } else {
    attempts = (failedAttempts.value[item.question] || 0) + 1;
    failedAttempts.value[item.question] = attempts;
  }

  if (isCorrect) {
    quizState.value.choicesDisabled = true;
    quizState.value.quizFeedbackType = 'correct';
    quizState.value.quizFeedback = "Tepat. " + (item.explanation || "");
    revealQuizNext();
  } else {
    quizState.value.quizFeedbackType = 'wrong';
    if (attempts >= 3) {
      quizState.value.choicesDisabled = true;
      quizState.value.quizFeedback = "Sudah 3 kali mencoba namun belum tepat. Tidak apa-apa, kamu boleh lanjut dulu!";
      revealQuizNext("Lanjut dulu →");
    } else {
      quizState.value.quizFeedback = `Belum tepat. Coba cek lagi perlahan dan perhatikan petunjuk dari video. (Percobaan ${attempts}/3)`;
      setTimeout(() => {
        if (!quizState.value.choicesDisabled) {
          quizState.value.selectedChoice = null;
        }
      }, 2000);
    }
  }
};


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
  if (isCorrect) {
    quizState.value.choicesDisabled = true;
    quizState.value.quizFeedbackType = 'success';
    quizState.value.quizFeedback = "Tepat sekali! Kamu menyusun kalimat masalah dengan sempurna.";
    revealQuizNext();
  } else {
    let attempts = (failedAttempts.value[item.qid] || 0) + 1;
    failedAttempts.value[item.qid] = attempts;
    quizState.value.quizFeedbackType = 'wrong';
    
    if (attempts >= 3) {
      quizState.value.choicesDisabled = true;
      quizState.value.quizFeedback = "Sudah 3 kali mencoba namun belum tepat. Tidak apa-apa, kamu boleh lanjut dulu!";
      revealQuizNext("Lanjut dulu →");
    } else {
      quizState.value.quizFeedback = `Masih ada yang keliru, coba baca ulang kalimat masalahnya. (Percobaan ${attempts}/3)`;
      // Let them retry
    }
  }
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

const submitArrangeFlow = () => {
  const q = currentQuestion.value;
  if (!q) return;
  quizState.value.choicesDisabled = true;

  const isCorrect = JSON.stringify(quizState.value.arrangeFlowAnswers) === JSON.stringify(q.correctOrder);

  if (isCorrect) {
    quizState.value.quizFeedback = "Benar sekali! Urutan alur aplikasinya sudah tepat. 🚀";
    quizState.value.quizFeedbackType = "success";
    quizState.value.isNextBtnVisible = true;
    quizState.value.nextBtnText = "Lanjut";
  } else {
    let attempts = (failedAttempts.value[q.qid] || 0) + 1;
    failedAttempts.value[q.qid] = attempts;
    quizState.value.quizFeedbackType = "wrong";
    
    if (attempts >= 3) {
      quizState.value.quizFeedback = "Sudah 3 kali mencoba. Urutannya masih belum tepat. Boleh lanjut dulu!";
      revealQuizNext("Lanjut dulu →");
    } else {
      quizState.value.quizFeedback = `Hmm, urutannya belum tepat. Coba cek lagi ya! (Percobaan ${attempts}/3)`;
      setTimeout(() => {
        quizState.value.choicesDisabled = false;
        quizState.value.quizFeedback = '';
        quizState.value.quizFeedbackType = '';
      }, 2500);
    }
  }
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
  if (isCorrect) {
    quizState.value.choicesDisabled = true;
    quizState.value.quizFeedbackType = 'success';
    quizState.value.quizFeedback = "Luar biasa! Semua fitur terpasang dengan tepat.";
    revealQuizNext();
  } else {
    let attempts = (failedAttempts.value[item.qid] || 0) + 1;
    failedAttempts.value[item.qid] = attempts;
    quizState.value.quizFeedbackType = 'wrong';
    
    if (attempts >= 3) {
      quizState.value.choicesDisabled = true;
      quizState.value.quizFeedback = "Sudah 3 kali salah. Ada yang kurang pas dengan kebutuhan user. Boleh lanjut dulu!";
      revealQuizNext("Lanjut dulu →");
    } else {
      quizState.value.choicesDisabled = false;
      quizState.value.quizFeedback = `Ada yang kurang pas, ingat fitur harus sesuai dengan kebutuhan user. (Percobaan ${attempts}/3)`;
    }
  }
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
      let attempts = (failedAttempts.value[item.qid + '_S1'] || 0) + 1;
      failedAttempts.value[item.qid + '_S1'] = attempts;
      quizState.value.quizFeedbackType = 'wrong';
      if (attempts >= 3) {
        quizState.value.quizFeedback = "Sudah 3 kali salah kamar. Tidak apa-apa, ayo coba pertanyaan bagian kedua!";
        setTimeout(() => {
          isFeasibilityFollowUp.value = true;
          quizState.value.quizFeedback = "";
          quizState.value.quizFeedbackType = "";
        }, 2500);
      } else {
        quizState.value.quizFeedback = `Ada fitur yang salah kamar. Coba ingat lagi apa yang paling feasible dibuat. (Percobaan ${attempts}/3)`;
      }
    }
  } else if (isFeasibilityFollowUp.value) {
    // Stage 2: fill_in_blank
    let correctCount = 0;
    item.followUp.blanks.forEach(b => {
      if (fillInBlankAnswers.value[b] === item.followUp.correctAnswers[b]) correctCount++;
    });
    const isCorrect = correctCount === item.followUp.blanks.length;
    if (isCorrect) {
      quizState.value.choicesDisabled = true;
      quizState.value.quizFeedbackType = 'success';
      quizState.value.quizFeedback = "Kalimat masalahmu sudah lengkap dan benar!";
      revealQuizNext();
    } else {
      let attempts = (failedAttempts.value[item.qid + '_S2'] || 0) + 1;
      failedAttempts.value[item.qid + '_S2'] = attempts;
      quizState.value.quizFeedbackType = 'wrong';
      if (attempts >= 3) {
        quizState.value.choicesDisabled = true;
        quizState.value.quizFeedback = "Sudah 3 kali salah. Kalimat masalah belum tepat. Boleh lanjut dulu!";
        revealQuizNext("Lanjut dulu →");
      } else {
        quizState.value.quizFeedback = `Kalimat masalah belum tepat, periksa lagi hubungannya. (Percobaan ${attempts}/3)`;
      }
    }
  }
};


const submitInputAnswer = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'input') return;

  const input = quizState.value.inputAnswer.trim();
  if (!input) return;

  let isCorrect = false;
  let feedbackText = "";

  if (typeof item.validate === 'function') {
    const result = item.validate(input);
    isCorrect = result.isCorrect;
    feedbackText = result.feedback;
  } else {
    const correctVals = Array.isArray(item.correct) ? item.correct : [item.correct];
    const normalize = (value) => String(value).trim().toLowerCase().replace(/\s+/g, '');
    const normalizeNumber = (value) => String(value).trim().replace(/\./g, '');
    const isLooseCodeFragment = (value) => String(value).includes('.') || String(value).includes('(');

    isCorrect = correctVals.some(c => {
      const expected = String(c);
      const normalizedInput = normalize(input);
      const normalizedExpected = normalize(expected);

      if (/^[0-9.]+$/.test(expected)) {
        return normalizeNumber(input) === normalizeNumber(expected);
      }

      if (/^[<>=!]+$/.test(expected) || /^[a-z_]+$/i.test(expected)) {
        return normalizedInput === normalizedExpected;
      }

      if (isLooseCodeFragment(expected)) {
        return normalizedInput === normalizedExpected || normalizedInput.includes(normalizedExpected);
      }

      return normalizedInput === normalizedExpected;
    });
    if (isCorrect) {
      feedbackText = "Tepat! " + (item.explanation || "");
    } else {
      feedbackText = "Belum tepat. Coba periksa kembali sintaks dan urutannya.";
    }
  }

  quizState.value.quizFeedbackType = isCorrect ? 'correct' : 'wrong';
  quizState.value.quizFeedback = feedbackText;
  recordQuestionAttempt(item.qid, input, isCorrect);

  if (isCorrect) {
    quizState.value.choicesDisabled = true;
    revealQuizNext();
  } else {
    // Biarkan tetap bisa mengisi lagi jika salah
    quizState.value.choicesDisabled = false;
  }
};

const submitEssayAnswer = () => {
  const item = currentQuestion.value;
  if (!item || item.type !== 'essay') return;

  const input = quizState.value.essayAnswer.trim();
  const minChars = item.minChars || 150;
  if (input.length < minChars) return;

  quizState.value.choicesDisabled = true;

  let isCorrect = false;
  let feedbackText = "";

  if (typeof item.validate === 'function') {
    const result = item.validate(input);
    isCorrect = result.isCorrect;
    feedbackText = result.feedback;
  } else {
    const lowerInput = input.toLowerCase();
    const keywords = item.keywords || [];
    const foundKeyword = keywords.some(kw => lowerInput.includes(kw));

    isCorrect = keywords.length === 0 || foundKeyword;
    feedbackText = isCorrect 
      ? "Luar biasa! Analisamu sangat mendalam. " + (item.explanation || "")
      : "Hmm, sepertinya ada poin penting yang terlewat. " + (item.explanation || "");
  }

  quizState.value.quizFeedbackType = isCorrect ? 'correct' : 'wrong';
  quizState.value.quizFeedback = feedbackText;

  if (isCorrect) {
    revealQuizNext("Selesai!");
  } else {
    // Biarkan tetap bisa mengisi lagi jika salah
    quizState.value.choicesDisabled = false;
  }
};

const goToNextQuestion = () => {
  if (quizState.value.currentQuestionIdx + 1 >= quizState.value.shuffledQuestions.length) {
    closeQuiz(quizState.value.resumeVideoAfterQuiz, quizState.value.resumeVideoTime);
    return;
  }
  quizState.value.currentQuestionIdx += 1;
  quizState.value.choicesDisabled = false;
  quizState.value.quizFeedback = '';
  quizState.value.quizFeedbackType = '';
  quizState.value.essayAnswer = '';
  quizState.value.isNextBtnVisible = false;
  
  nextTick(() => {
    renderQuestion();
  });
};

const replayActiveQuizVideo = () => {
  if (!quizState.value.activeQuizConfig || quizState.value.activeQuizStep === null) return;

  const player = players[quizState.value.activeQuizStep];
  if (!player || typeof player.seekTo !== "function") return;

  const replayStart = Math.max(0, quizState.value.activeQuizConfig.time - 30);
  if (currentStep.value !== quizState.value.activeQuizStep) {
    currentStep.value = quizState.value.activeQuizStep;
  }

  quizState.value.activeQuizConfig.shown = false;
  quizState.value.replayingQuizVideo = true;
  quizState.value.replayCheckpointArmed = false;
  
  closeQuiz(false);
  quizReturn.value.isVisible = true;

  nextTick(() => {
    player.seekTo(replayStart, true);
    if (typeof player.playVideo === "function") {
      player.playVideo();
    }
    setTimeout(() => {
      if (!quizState.value.replayingQuizVideo || typeof player.getCurrentTime !== "function") return;
      if (Math.abs(player.getCurrentTime() - replayStart) > 2) {
        player.seekTo(replayStart, true);
      }
    }, 300);
  });
};

const returnToActiveQuiz = () => {
  if (!quizState.value.activeQuizConfig || quizState.value.activeQuizStep === null) return;

  const player = players[quizState.value.activeQuizStep];
  if (player && typeof player.pauseVideo === "function") {
    player.pauseVideo();
  }
  quizState.value.activeQuizConfig.shown = true;
  openQuiz(
    quizState.value.activeQuizConfig.questions,
    quizState.value.activeQuizConfig.resume !== undefined ? quizState.value.activeQuizConfig.resume : true,
    quizState.value.activeQuizConfig.resumeTime,
    quizState.value.activeQuizConfig,
    quizState.value.activeQuizStep
  );
};

// Pyodide Integration
const pyodideBaseUrl = "https://cdn.jsdelivr.net/pyodide/v0.25.0/full/";
let pyodideReadyPromise = null;

function ensurePyodideScript() {
  if (typeof window.loadPyodide === "function") return Promise.resolve();

  return new Promise((resolve, reject) => {
    const existingScript = document.querySelector('script[data-pyodide-loader]');
    if (existingScript) {
      existingScript.addEventListener("load", resolve, { once: true });
      existingScript.addEventListener("error", reject, { once: true });
      return;
    }

    const script = document.createElement("script");
    script.src = pyodideBaseUrl + "pyodide.js";
    script.dataset.pyodideLoader = "true";
    script.addEventListener("load", resolve, { once: true });
    script.addEventListener("error", () => reject(new Error("Pyodide gagal dimuat.")), { once: true });
    document.head.appendChild(script);
  });
}

function initPyodide() {
  if (!pyodideReadyPromise) {
    pyodideReadyPromise = ensurePyodideScript()
      .then(() => window.loadPyodide({ indexURL: pyodideBaseUrl }));
  }
  return pyodideReadyPromise;
}

const runPyodideCode = async (inputId, outputId) => {
  const codeEl = document.getElementById(inputId);
  const outputEl = document.getElementById(outputId);
  if (!codeEl || !outputEl) return;
  outputEl.innerHTML = "Menjalankan...";
  outputEl.style.color = "white";

  try {
    let pyodide = await initPyodide();
    pyodide.setStdout({ batched: (msg) => {
      if (outputEl.innerHTML === "Menjalankan...") outputEl.innerHTML = "";
      outputEl.innerHTML += msg + "\n";
    }});
    
    await pyodide.runPythonAsync(codeEl.value);
    if (outputEl.innerHTML === "Menjalankan...") {
      outputEl.innerHTML = "Program selesai tanpa output teks.";
    }
  } catch (err) {
    outputEl.innerHTML = err;
    outputEl.style.color = "#FF4444";
  }
};

const exposeGlobalMethods = () => {
  const trackAttempt = (qid, answerStr, isCorrect) => {
    if(!qid) return;
    const attKey = qid + "_Att";
    const ansKey = qid + "_Ans";
    let att = (studentProgress.value[attKey] || 0) + 1;
    studentProgress.value[attKey] = att;
    
    // Mapping spesifik Video 6
    let finalAnsKey = ansKey;
    if (qid === 'V6_Q1') finalAnsKey = 'V6_Needs_Ans';
    if (qid === 'V6_Q2') finalAnsKey = 'V6_Wants_Ans';
    if (qid === 'V6_Q3') { finalAnsKey = 'V6_IDE_Code'; studentProgress.value['V6_IDE_Att'] = att; }
    
    if (isCorrect || att >= 3) {
      studentProgress.value[finalAnsKey] = isCorrect ? answerStr : '-';
    }
    saveProgress(attKey, att); 
  };

  window.checkGuess = function(btn, isCorrect, explanation) {
    const qid = currentQuestion.value?.qid;
    trackAttempt(qid, btn.innerText, isCorrect);
    
    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    const buttons = container.querySelectorAll('button');
    buttons.forEach(b => {
      b.disabled = true;
      b.style.opacity = '0.5';
    });
    btn.style.opacity = '1';
    
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "var(--black)";
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>SALAH!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      revealQuizNext("Lanjut dulu →");
    }
  };

  window.checkMB1QGuess = function(kwVal, condVal, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let kw = kwVal.replace(/\s+/g, '').toLowerCase();
    let cond = condVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (kw === 'elif' && (cond === 'age<18' || cond === 'age<=17'));
    trackAttempt(qid, `${kwVal} ${condVal}`, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    const isCorrectCondition = isCorrect;
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrectCondition) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "var(--black)";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const kwInput = document.getElementById('mb1-kw');
      const condInput = document.getElementById('mb1-cond');
      if (kwInput) kwInput.disabled = true;
      if (condInput) condInput.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Coba lagi! Kata kunci percabangan yang dipakai adalah <code>elif</code> dan kondisinya mengecek apakah usia di bawah 18 tahun (<code>age &lt; 18</code>).`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkMB2QGuess = function(val1, val2, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let v1 = val1.replace(/\s+/g, '');
    let v2 = val2.replace(/\s+/g, '');
    const isCorrect = (v1 === '90' && v2 === '80');
    trackAttempt(qid, `${val1} ${val2}`, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "var(--black)";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const val1Input = document.getElementById('mb2-val1');
      const val2Input = document.getElementById('mb2-val2');
      if (val1Input) val1Input.disabled = true;
      if (val2Input) val2Input.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>URUTAN MASIH SALAH!</strong><br>Ingat, kondisi paling ketat/sulit (nilai &gt;= 90 untuk A) harus dicek paling atas!`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkParenGuess = function(userVal, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let normalizedUser = userVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (normalizedUser === 'password_okand(is_adminoris_premium)' || normalizedUser === '(is_adminoris_premium)andpassword_ok' || normalizedUser === 'password_ok==trueand(is_admin==trueoris_premium==true)');
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const parenInput = document.getElementById('paren-input');
      if (parenInput) parenInput.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Pastikan kamu menggabungkan 'is_admin or is_premium' di dalam tanda kurung (), lalu gunakan 'and password_ok'.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkAndGuess = function(userVal, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let normalizedUser = userVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (normalizedUser === 'andaktif_organisasi==true' || normalizedUser === 'andaktif_organisasi' || normalizedUser === 'and(aktif_organisasi==true)');
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const andInput = document.getElementById('and-input');
      if (andInput) andInput.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Coba lagi! Kamu butuh operator logika 'and' diikuti dengan kondisi pengecekan variabel aktif_organisasi.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkOrGuess = function(userVal, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let normalizedUser = userVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (normalizedUser === 'orada_kupon==true' || normalizedUser === 'orada_kupon' || normalizedUser === 'or(ada_kupon==true)');
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const orInput = document.getElementById('or-input');
      if (orInput) orInput.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Coba lagi! Kamu butuh operator logika 'or' diikuti dengan kondisi pengecekan variabel ada_kupon.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkNestedToLogicalGuess = function(userVal, btn, explanation) {
    const qid = currentQuestion.value?.qid;
    let normalizedUser = userVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (normalizedUser === 'andcuaca=="cerah"' || normalizedUser === 'and(cuaca=="cerah")' || normalizedUser === 'andcuaca==\'cerah\'');
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>${explanation}`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      const logicalInput = document.getElementById('logical-input');
      if (logicalInput) logicalInput.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Pastikan kamu menggunakan operator 'and' lalu cek apakah 'cuaca == "cerah"'.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkNeedsWantsGuess = function(inputClass, btn) {
    const qid = currentQuestion.value?.qid;
    const inputs = document.querySelectorAll('.' + inputClass);
    let allFilled = true;
    let vals = [];
    inputs.forEach(input => {
      if (!input.value.trim()) allFilled = false;
      else vals.push(input.value.trim());
    });
    
    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    
    if (!allFilled) {
      feedback.style.display = 'block';
      setTimeout(() => {
        if (window.innerWidth <= 650) {
          feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }, 100);
      feedback.innerHTML = `❌ Lengkapi kelima contohnya terlebih dahulu ya!`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
      return;
    }
    
    trackAttempt(qid, vals.join(', '), true);

    btn.disabled = true;
    btn.style.opacity = '0.5';
    
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    feedback.innerHTML = `✅ <strong>Tersimpan!</strong><br>Terima kasih sudah membagikan pemikiranmu.`;
    feedback.style.backgroundColor = "#27c881";
    feedback.style.color = "var(--black)";
    revealQuizNext();
  };

  window.checkIde6Guess = function(btn) {
    const qid = currentQuestion.value?.qid;
    const codeEl = document.getElementById('python-ide-6');
    const code = codeEl ? codeEl.value.toLowerCase() : '';
    trackAttempt(qid, code, true);
    const keywords = ['buku tulis', 'air minum', 'skin game', 'snack tambahan', 'pulsa', 'gantungan kunci'];
    let matchCount = 0;
    
    keywords.forEach(kw => {
      if (code.includes(kw)) matchCount++;
    });

    const container = btn.parentElement;
    const feedback = container.nextElementSibling.nextElementSibling;
    
    feedback.style.display = 'block';
    // NEW: Auto-scroll on mobile
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);
    if (matchCount >= 3) {
      feedback.innerHTML = `✅ <strong>Bagus!</strong> Kamu sudah memakai setidaknya 3 barang dari tabel.`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "var(--black)";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ Kamu baru memasukkan ${matchCount} barang dari tabel di kodemu. Minimal butuh 3 barang (misal: "Buku tulis", "Skin game", dsb).`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkTab6Guess = function(btn) {
    const qid = currentQuestion.value?.qid;
    const inputEl = document.getElementById('tab6-inline-input');
    if (!inputEl) return;
    
    let userVal = inputEl.value.trim();
    let normalizedUser = userVal.replace(/\s+/g, '').toLowerCase();
    const isCorrect = (normalizedUser === 'returnprice*quantity' || normalizedUser === 'returnquantity*price');
    
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    
    feedback.style.display = 'block';
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);

    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>Nama variabel sebelumnya salah, dan harus menggunakan operator perkalian (*) agar mendapatkan 30000.`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      inputEl.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Coba lagi! Pastikan nama variabel sesuai dengan parameter (<code>price</code> dan <code>quantity</code>), lalu gunakan operator yang tepat (ditambah atau dikali?).`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkTab8Guess = function(btn) {
    const qid = currentQuestion.value?.qid;
    const input1 = document.getElementById('tab8-input-1');
    const input2 = document.getElementById('tab8-input-2');
    if (!input1 || !input2) return;
    
    let userVal1 = input1.value;
    let userVal2 = input2.value;
    let val1 = userVal1.replace(/\s+/g, '').toLowerCase();
    let val2 = userVal2.trim().toLowerCase();
    
    const isVal1Correct = val1.includes('principal') && val1.includes('rate') && val1.includes('years') && val1.includes('*');
    const isVal2Correct = val2 === 'return';
    const isCorrect = isVal1Correct && isVal2Correct;
    
    trackAttempt(qid, userVal1 + ' | ' + userVal2, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    
    feedback.style.display = 'block';
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);

    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>Kamu berhasil mengingat rumusnya: <code>interest = principal * rate * years</code> dan mengembalikan nilainya dengan <code>return</code>.`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      input1.disabled = true;
      input2.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>KODE BELUM TEPAT!</strong><br>Coba cek lagi! Di baris pertama pastikan ada perkalian <code>principal</code>, <code>rate</code>, dan <code>years</code>. Di baris kedua gunakan keyword untuk mengembalikan nilai fungsi.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.checkTab8Quiz2Guess = function(btn) {
    const qid = currentQuestion.value?.qid;
    const inputEl = document.getElementById('tab8-quiz2-input');
    if (!inputEl) return;
    
    let userVal = inputEl.value.trim();
    let normalizedUser = userVal.replace(/\s+/g, '').replace(/,/g, '');
    
    const isCorrect = (normalizedUser === '210000' || normalizedUser === '210000.0' || normalizedUser === '210.000');
    
    trackAttempt(qid, userVal, isCorrect);

    const container = btn.parentElement;
    const feedback = container.nextElementSibling;
    
    feedback.style.display = 'block';
    setTimeout(() => {
      if (window.innerWidth <= 650) {
        feedback.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
      }
    }, 100);

    if (isCorrect) {
      feedback.innerHTML = `✅ <strong>TEPAT SEKALI!</strong><br>Hasilnya adalah <strong>210000</strong>. Pertama, bunga dihitung: 200000 * 0.05 = 10000. Lalu uang ditambahkan dengan bunga: 200000 + 10000 = 210000.`;
      feedback.style.backgroundColor = "#27c881";
      feedback.style.color = "#1A1A1A";
      btn.disabled = true;
      btn.style.opacity = '0.5';
      inputEl.disabled = true;
      revealQuizNext();
    } else {
      feedback.innerHTML = `❌ <strong>JAWABAN BELUM TEPAT!</strong><br>Coba hitung perlahan. Berapa 5% dari 200.000? Lalu tambahkan hasil itu ke 200.000.`;
      feedback.style.backgroundColor = "#ff5c8a";
      feedback.style.color = "white";
      registerFailedInputAttempt(btn, feedback);
    }
  };

  window.runPyodideCode = runPyodideCode;
  let finalProjectAttempts = 0;
  window.runAssignmentCode = function() {
    finalProjectAttempts++;
    studentProgress.value['Final_Project_Attempts'] = finalProjectAttempts;
    saveProgress('Final_Project_Attempts', finalProjectAttempts);
    runPyodideCode('python-ide-4', 'ide-output-4');
  };
  window.runAssignmentCode7 = function() {
    runPyodideCode('python-ide-7', 'ide-output-7');
  };
  window.submitAssignmentCode = function() {
    const codeEl = document.getElementById('python-ide-4');
    const code = codeEl ? codeEl.value : '';
    let score = 'Submit';
    if (code.includes('for ') && code.includes('if ') && code.includes('break')) score = 'Bagus';

    
    studentProgress.value['Final_Project_Code'] = code;
    studentProgress.value['Final_Project_Score'] = score;
    saveProgress('Final_Project_Code', code);
    saveProgress('Final_Project_Score', score);

    alert("✅ Tugas berhasil dikumpulkan! Progress kamu otomatis tersimpan di server. Selamat kamu telah menyelesaikan Misi Safe Finance Tracker!");
  };
};

onMounted(() => {
  quizObj.onValuesChange((values) => {
    quizModalStyles.value = {
      transform: `translateY(${values.y}px) scale(${values.scale})`,
      opacity: values.opacity
    };
  });

  if (window.YT && typeof window.YT.Player === "function") {
    youtubeReady.value = true;
    initializeYouTubePlayer(currentStep.value);
  } else {
    const oldReady = window.onYouTubeIframeAPIReady;
    window.onYouTubeIframeAPIReady = () => {
      if (oldReady) oldReady();
      youtubeReady.value = true;
      initializeYouTubePlayer(currentStep.value);
    };
  }
  exposeGlobalMethods();
});

watch(currentQuestion, (newQ) => {
  if (newQ && newQ.type === 'pyscript') {
    pyscriptCode.value = newQ.initialCode || '';
    pyodideOutput.value = '';
  }
});

watch(currentStep, (newStep) => {
  const stepKey = newStep.toString();
  if (hasInlinePyQuiz(courseData[stepKey])) {
    pyscriptCode.value = courseData[stepKey].quizzes[0].questions[0].initialCode || '';
    pyodideOutput.value = '';
    quizState.value.quizFeedback = '';
  }

  Object.keys(players).forEach(id => {
    if (Number(id) !== newStep && players[id] && typeof players[id].pauseVideo === 'function') {
      players[id].pauseVideo();
    }
  });

  if (quizState.value.activeQuizStep !== null && quizState.value.activeQuizStep !== newStep) {
    quizState.value.replayingQuizVideo = false;
    quizState.value.replayCheckpointArmed = false;
    quizReturn.value.isVisible = false;
  }

  nextTick(() => {
    initializeYouTubePlayer(newStep);
  });
});

const openQuizButtonHandler = () => {
  if (players[currentStep.value] && typeof players[currentStep.value].pauseVideo === "function") {
    players[currentStep.value].pauseVideo();
  }
  const questions = courseData[2]?.quizzes?.[0]?.questions || [];
  if (questions.length > 0) {
    openQuiz(questions, false);
  }
};

const prevStep = () => {
  if (currentStep.value > 1) {
    currentStep.value -= 1;
  }
};

const nextStep = () => {
  if (currentStep.value < totalSteps) {
    currentStep.value += 1;
    return;
  }

  showCompletionToast.value = true;
  setTimeout(() => {
    showCompletionToast.value = false;
  }, 3800);
};

const getStepConfig = (stepId) => {
  return courseData[stepId];
};
const cdnCovers = [
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/fec32e8d-d711-48a2-bd22-59581f0594c1.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/2925ebc7-89c3-4010-a057-9807aacc6a32.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/ec2aeaa6-e2e2-4e83-861e-223bfb9e1138.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/47f3ef56-348b-4c3c-a767-aa4a40c5b833.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/00c64b24-9e45-4a7e-8665-0817c04217c3.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/c179c0a4-8817-4f1b-a9ef-cf6dcaa093c9.jpg",
  "https://cdn-web-2.ruangguru.com/landing-pages/assets/98bcac2b-e88e-46d8-b1c1-deebd6a12c03.jpg"
];

const getCover = (key) => {
  const index = (Number(key) - 1) % cdnCovers.length;
  return cdnCovers[index];
};
</script>

<template>
  <img class="planet planet-one" src="https://cdn-web-2.ruangguru.com/landing-pages/assets/e49806a2-dcc4-4858-a261-c4e33b798180.png" alt="">
  <img class="planet planet-two" src="https://cdn-web-2.ruangguru.com/landing-pages/assets/eaa66ac5-e69c-46f2-b942-909bcaad579a.png" alt="">

  <transition name="fade">
    <div v-if="!isLoggedIn" class="login-overlay">
      <div class="login-card">
        <div class="login-copy">
          <div class="brand-group-login">
            <img class="rg-logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Ruangguru_logo.svg/3840px-Ruangguru_logo.svg.png" alt="Ruangguru">
            <img class="uob-logo" src="https://cdn-web-2.ruangguru.com/landing-pages/assets/37185db7-24a8-467d-aabb-1d5df48f9bc0.png" alt="UOB">
          </div>
          <span class="login-kicker">UOB My Digital Space</span>
          <h1>Python Learning Dashboard</h1>
          <p>Masuk dengan email siswa untuk membuka materi kelasmu.</p>
          <div class="login-highlights" aria-label="Fitur pembelajaran">
            <span>High School</span>
            <span>Python</span>
            <span>Async Class</span>
          </div>
        </div>

        <div class="login-form-panel">
          <span class="login-step">Materi Grup D - HS - 2D</span>
          <h2>Masuk ke kelas</h2>
          <div class="input-group">
            <label for="login-school-c">Nama sekolah</label>
            <div class="login-combobox">
              <input id="login-school-c" type="text" v-model="loginSchool" placeholder="Cari nama sekolah" autocomplete="off" @focus="openSchoolDropdown" @blur="closeSchoolDropdownSoon" @input="handleSchoolInput" :disabled="isLoggingIn">
              <div v-if="isSchoolDropdownOpen" class="login-dropdown">
                <template v-if="!isSchoolLoading">
                  <button v-for="school in schoolOptions" :key="school" type="button" @mousedown.prevent="selectSchool(school)">
                    {{ school }}
                  </button>
                </template>
                <p v-if="isSchoolLoading">Memuat data sekolah...</p>
                <p v-else-if="!schoolOptions.length">Sekolah tidak ditemukan.</p>
              </div>
            </div>

            <label for="login-email-c">Email terdaftar di Akademia Ruangguru</label>
            <input id="login-email-c" type="email" v-model="loginEmail" placeholder="nama@email.com" @input="handleEmailInput" @keyup.enter="handleLogin" :disabled="isLoggingIn || !selectedSchool">

            <button type="button" class="login-help-toggle" @click="toggleEmailHelp" :disabled="!selectedSchool">
              Tidak yakin emailnya? Cari bantuan lewat nama/email
            </button>

            <div v-if="emailHelpOpen" class="email-help-panel">
              <label for="login-help-c">Cari nama siswa/orang tua atau email</label>
              <input id="login-help-c" type="text" v-model="emailHelpQuery" placeholder="Contoh: Taylor atau gmail" @input="handleEmailHelpInput">
              <div class="email-help-results">
                <p v-if="!emailHelpQuery.trim()">Ketik nama atau sebagian email yang mungkin terdaftar.</p>
                <p v-else-if="isEmailHelpLoading">Mencari data...</p>
                <p v-else-if="!emailHelpResults.length">Belum ada data yang mirip di sekolah ini.</p>
                <div v-for="student in emailHelpResults" :key="`${student.school}-${student.name}-${student.maskedEmail}`" class="email-help-result">
                  <strong>{{ student.name }}</strong>
                  <span class="email-help-label">Email terdaftar:</span>
                  <code v-if="student.maskedEmail">{{ student.maskedEmail }}</code>
                  <span v-else class="email-help-missing">Email belum tersedia. Coba cek lagi email yang didaftarkan di Akademia Ruangguru.</span>
                </div>
                <p v-if="emailHelpResults.length" class="email-help-note">Gunakan email terdaftar di atas untuk masuk ke kelas.</p>
              </div>
            </div>

            <button @click="handleLogin" :disabled="isLoggingIn || !selectedSchool || !loginEmail.trim()" class="login-btn">
              {{ isLoggingIn ? 'Memuat...' : 'Mulai Belajar' }}
            </button>
          </div>
          <p class="login-helper">Gunakan email pribadi yang sudah didaftarkan di Akademia Ruangguru.</p>

          <transition name="pop">
            <div v-if="showLoginError" class="login-error-msg">
              <span class="icon">!</span>
              <div>
                <strong>{{ loginErrorTitle }}</strong>
                <p>{{ loginErrorMessage }}</p>
                <div v-if="loginEmailSuggestion" class="registered-email-card">
                  <span>Email terdaftar di sekolah ini:</span>
                  <strong>{{ loginEmailSuggestion.maskedEmail || 'Email belum tersedia' }}</strong>
                  <p>Coba cek lagi tanda titik, huruf yang tertukar, atau domain emailnya.</p>
                </div>
              </div>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </transition>

  <div class="site-shell" v-show="isLoggedIn">
    <header class="topbar">
      <div class="brand-group">
        <img class="rg-logo" src="https://upload.wikimedia.org/wikipedia/commons/thumb/6/6d/Ruangguru_logo.svg/3840px-Ruangguru_logo.svg.png" alt="Ruangguru">
        <img class="uob-logo" src="https://cdn-web-2.ruangguru.com/landing-pages/assets/37185db7-24a8-467d-aabb-1d5df48f9bc0.png" alt="UOB">
      </div>
      <div class="student-chip" aria-label="Profil siswa" @click="showProfileMenu = !showProfileMenu">
        <div class="avatar" aria-hidden="true"></div>
        <div class="student-info">
          <strong>
            {{ studentData.name || 'Siswa Kalananti' }}
            <span class="dropdown-icon">▼</span>
          </strong>
          <span v-if="studentData.school">{{ studentData.school }}</span>
          <span v-else>Siap lanjut belajar</span>
        </div>
        
        <transition name="fade">
          <div v-if="showProfileMenu" class="profile-dropdown">
            <button @click.stop="handleLogout" class="dropdown-item">⏏ Keluar</button>
          </div>
        </transition>
      </div>
    </header>

    <main class="dashboard">
            <aside class="sidebar">
        <div class="eyebrow">Asynchronous Learning - Grup D Sesi 40-44</div>
        <h1>Misi: Safe Finance Tracker</h1>
        <p class="sidebar-intro">
          Pelajari cara memvalidasi input agar program lebih aman.
        </p>

        <div class="mission-progress" aria-label="Progres pembelajaran">
          <div class="progress-copy">
            <span>Progres misi</span>
            <span id="progressText">{{ currentStep }} dari {{ totalSteps }}</span>
          </div>
          <div class="progress-track">
            <div class="progress-fill" :style="{ width: (currentStep / totalSteps * 100) + '%' }"></div>
          </div>
        </div>

        <nav class="mobile-nav">
          <label for="mobile-lesson-select">Pilih Modul</label>
          <div class="select-wrapper">
            <select id="mobile-lesson-select" v-model="currentStep">
              <option v-for="(data, key) in courseData" :key="key" :value="Number(key)">0{{ key }} {{ data.title }}</option>
            </select>
          </div>
        </nav>

        <nav class="lesson-nav" aria-label="Daftar video">
          <button v-for="(data, key) in courseData" :key="key" class="lesson-tab" :class="{ active: currentStep === Number(key) }" type="button" @click="currentStep = Number(key)">
            <span class="tab-number">0{{ key }}</span>
            <span class="tab-copy">
              <strong>{{ data.title }}</strong>
              <span>{{ data.kicker }}</span>
            </span>
            <span class="tab-arrow" aria-hidden="true">›</span>
          </button>
        </nav>

        <div class="help-card">
          Ada bagian yang masih membingungkan?
          <a href="mailto:fasilitator@kalananti.id">Tanya fasilitator</a>
        </div>
      </aside>

      <section class="content">
        <div class="content-top">
          <div>
            <p class="lesson-kicker">{{ courseData[currentStep].kicker }}</p>
            <h2 class="lesson-title">{{ courseData[currentStep].title }}</h2>
          </div>
          <span class="duration-pill">{{ courseData[currentStep].duration }}</span>
        </div>

        <template v-for="(data, key) in courseData" :key="key">
          <section class="step-panel" :id="'step-' + key" v-show="currentStep === Number(key)">
            <div class="video-frame" :class="{ 'player-ready': playerStates[key]?.isReady }" :data-video-step="key">
            <video 
              v-show="playerStates[key]?.introPlaying"
              :ref="(el) => { if (el) introRefs[key] = el; }"
              :src="introVideoSrc"
              style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; object-fit: cover; z-index: 10; background: black;"
              controls
              @ended="onIntroEnded(key)"
              @play="onIntroPlay(key)"
              @pause="onIntroPause(key)"
              playsinline
              preload="auto"
            ></video>
              <div :id="'youtube-player-' + key"></div>
              <div class="custom-thumbnail" v-show="!playerStates[key]?.hasStarted" @click="togglePlay(Number(key))">
                <div class="thumb-card-blue-bg"></div>
                <div class="thumb-card">
                  <div class="thumb-kicker" v-if="data.kicker">{{ data.kicker }}</div>
                  <div class="thumb-title">{{ data.title }}</div>
                  <svg class="thumb-decoration" viewBox="0 0 100 100" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M10 50 L50 10 L90 50 L50 90 Z" fill="#ffe600" stroke="#1a1a1a" stroke-width="4" stroke-linejoin="round"/>
                    <path d="M10 60 L50 100 L90 60" fill="none" stroke="#1a1a1a" stroke-width="4" stroke-linejoin="round"/>
                    <path d="M50 100 L50 90" stroke="#1a1a1a" stroke-width="4"/>
                    <path d="M10 60 L10 50" stroke="#1a1a1a" stroke-width="4"/>
                    <path d="M90 60 L90 50" stroke="#1a1a1a" stroke-width="4"/>
                  </svg>
                </div>
              </div>
              <button class="video-center-play" type="button" v-show="!playerStates[key]?.isPlaying && !playerStates[key]?.isBuffering && (playerStates[key]?.isReady || !playerStates[key]?.hasStarted)" @click="togglePlay(Number(key))">▶</button>
              <div class="video-loading-overlay" v-show="playerStates[key]?.isBuffering || (playerStates[key]?.hasStarted && !playerStates[key]?.isReady)">
                <div class="spinner"></div>
              </div>
              <div class="video-controls" :aria-label="'Kontrol video ' + key">
                <button class="video-control-button video-play" type="button" @click="togglePlay(Number(key))">{{ playerStates[key]?.isPlaying ? "⏸" : "▶" }}</button>
                <input class="video-seek" type="range" min="0" max="100" step="0.1" :value="playerStates[key]?.progress || 0" @input="onSeekInput(Number(key), $event)" aria-label="Posisi video">
                <span class="video-time">{{ playerStates[key]?.currentTimeFormatted || "0:00" }} / {{ playerStates[key]?.durationFormatted || "0:00" }}</span>
                <button class="video-control-button video-mute" type="button" @click="toggleMute(Number(key))">{{ playerStates[key]?.isMuted ? "🔇" : "🔊" }}</button>
                <button class="video-control-button video-fullscreen" type="button" @click="toggleFullscreen(Number(key))">⛶</button>
              </div>
            </div>

            <div class="bookmarks-container" v-if="data.bookmarks?.length > 0">
              <button class="bookmark-btn" v-for="bm in data.bookmarks" :key="bm.label" @click="seekToBookmark(Number(key), bm.time)">
                <span class="bookmark-time">{{ formatVideoTime(bm.time) }}</span> {{ bm.label }}
              </button>
            </div>
            <div class="inline-quiz-container" v-if="hasInlinePyQuiz(data)" style="margin-top: 20px;">
              <div class="pyscript-container" style="background: #1a1a1a; padding: 20px; border-radius: 12px; border: 2px solid #ffe600; box-shadow: 4px 4px 0px #ffe600;">
                <div v-html="data.quizzes[0].questions[0].html" style="color: white; margin-bottom: 15px;"></div>
                <div v-if="isPyodideLoading" style="color: #ffcc00; margin-bottom: 10px; font-weight: bold; text-align: center;">Sedang memuat Mesin Python... ⏳ (Mohon tunggu sebentar)</div>
                <textarea 
                  v-model="pyscriptCode" 
                  class="code-editor" 
                  rows="14" 
                  style="width: 100%; background: #282a36; color: #f8f8f2; font-family: 'Courier New', Courier, monospace; font-size: 14px; padding: 15px; border-radius: 12px; border: 3px solid #6272a4; margin-bottom: 10px; resize: vertical;"
                  :disabled="isPyodideLoading"
                ></textarea>
                <div style="display: flex; gap: 10px; margin-bottom: 15px;">
                  <button @click="runPython" style="background-color: #6272a4; color: white; padding: 10px 15px; border-radius: 8px; border: 2px solid #44475a; cursor: pointer; flex: 1; font-weight: bold; font-size: 16px;" :disabled="isPyodideLoading">▶️ Coba Jalankan (Run)</button>
                  <button @click="submitPython" style="background-color: #50fa7b; color: #282a36; font-weight: bold; padding: 10px 15px; border-radius: 8px; border: 2px solid #282a36; cursor: pointer; flex: 1; font-size: 16px; box-shadow: 2px 2px 0px #282a36;" :disabled="isPyodideLoading">🚀 Kirim Jawaban (Submit)</button>
                </div>
                <div class="pyscript-output" style="background-color: #000; color: #50fa7b; font-family: 'Courier New', Courier, monospace; font-size: 14px; padding: 15px; border-radius: 12px; min-height: 80px; text-align: left; white-space: pre-wrap; margin-bottom: 15px; border: 2px solid #44475a;">> Console Output:<br>{{ pyodideOutput }}</div>
                <div class="quiz-feedback" v-show="quizState.quizFeedback" :class="quizState.quizFeedbackType" style="padding: 15px; border-radius: 8px; font-weight: bold; text-align: center; margin-bottom: 15px; background: white;">
                  <span v-html="quizState.quizFeedback"></span>
                </div>
              </div>
            </div>
                    <div class="below-video" v-if="data.quickSummary">
            <article class="summary-card">
              <h3 class="card-heading">
                <span class="heading-icon" aria-hidden="true">{{ data.quickSummary.headingNumber }}</span>
                {{ data.quickSummary.headingTitle }}
              </h3>
              <ul class="takeaway-list">
                <li v-for="item in data.quickSummary.items" :key="item.label"><strong>{{ item.label }}:</strong> {{ item.text }}</li>
              </ul>
            </article>

              <aside class="focus-card" v-if="data.quickSummary.focus">
              <div>
                <p class="label">{{ data.quickSummary.focus.label }}</p>
                <h3>{{ data.quickSummary.focus.title }}</h3>
                <p>{{ data.quickSummary.focus.body }}</p>
              </div>
              <div class="mini-code">
                <template v-for="line in data.quickSummary.focus.codeLines" :key="line">
                  <span>{{ line }}</span><br>
                </template>
              </div>
            </aside>
          </div>
          <details class="lesson-reading-accordion" :open="isDesktop ? true : undefined" v-if="data.reading">
            <summary>Buka Materi Bacaan</summary>
          <div class="lesson-reading">
            <header class="reading-header">
              <div>
                <p class="label">{{ data.reading.label }}</p>
                <h3>{{ data.reading.title }}</h3>
                <p>{{ data.reading.subtitle }}</p>
              </div>
              <span class="reading-badge">{{ data.reading.badge }}</span>
            </header>

            <div class="concept-grid">
              <article class="concept-card" v-for="concept in data.reading.concepts" :key="concept.number">
                <span class="concept-number">{{ concept.number }}</span>
                <h4>{{ concept.title }}</h4>
                <p>{{ concept.body }}</p>
              </article>
            </div>

            <article class="reading-section" v-for="section in data.reading.sections" :key="section.title">
              <h4>{{ section.title }}</h4>
              <p v-for="paragraph in section.paragraphs" :key="paragraph">{{ paragraph }}</p>
              <ul v-if="section.bullets?.length">
                <li v-for="bullet in section.bullets" :key="bullet">{{ bullet }}</li>
              </ul>
              <p class="reading-note" v-if="section.note"><strong>Intinya:</strong> {{ section.note }}</p>
            </article>
          </div>
          </details>
        </section>
        </template>
        

        

        

        

        

        

        

        <div class="navigation">
          <button class="nav-button secondary" type="button" :disabled="currentStep === 1" @click="currentStep--">
            <span aria-hidden="true">←</span> Sebelumnya
          </button>
          <button class="nav-button primary" type="button" :disabled="currentStep === totalSteps" @click="currentStep++">
            Lanjut ke video berikutnya <span aria-hidden="true">→</span>
          </button>
        </div>
      </section>
    </main>

    <footer class="footer-note">
      Copyright © 2025 PT Ruang Raya Indonesia. Materi tidak boleh disebarluaskan tanpa izin.
    </footer>
  </div>

  
  <div class="quiz-overlay" id="quizOverlay" role="dialog" aria-modal="true" aria-labelledby="quizTitle" :class="{ open: quizState.isOpen }">
    <div class="quiz-dialog">
      <header class="quiz-header">
        <span class="quiz-header-icon" aria-hidden="true">?</span>
        <div>
          <p class="quiz-kicker">Checkpoint pemahaman</p>
          <h2 id="quizTitle">Mini Quiz Waktu!</h2>
          <p class="quiz-subtitle">Jawab berdasarkan materi yang baru kamu tonton.</p>
        </div>
      </header>
      <div class="quiz-body">
        <div class="quiz-progress" id="quizProgress" aria-label="Progres kuis">
          <span 
            v-for="(_, index) in quizState.shuffledQuestions" 
            :key="index" 
            class="quiz-dot"
            :class="{ 
              done: index < quizState.currentQuestionIdx, 
              active: index === quizState.currentQuestionIdx 
            }"
          ></span>
        </div>
        <div v-show="currentQuestion && !currentQuestion.html" class="quiz-question" id="quizQuestion">
          {{ currentQuestion ? currentQuestion.question : 'Memuat pertanyaan...' }}
        </div>
        <div v-if="currentQuestion && currentQuestion.html" id="quizCustomHtml" v-html="currentQuestion.html"></div>
        <div v-show="currentQuestion && currentQuestion.type !== 'arrange_flow' && currentQuestion.type !== 'essay' && currentQuestion.type !== 'card_choice' && currentQuestion.type !== 'input' && currentQuestion.type !== 'info' && currentQuestion.type !== 'classify_problem' && currentQuestion.type !== 'match_pairs' && currentQuestion.type !== 'feasibility_buckets'" class="answer-row" id="answerRow">
          <button 
            v-for="(choice, cIdx) in (currentQuestion ? currentQuestion.choices : [])" 
            :key="cIdx" 
            class="answer-button"
            :class="{ 
              true: choice === 'TRUE' || choice === 'True',
              false: choice === 'FALSE' || choice === 'False'
            }"
            @click="handleStandardAnswer(choice)"
            :disabled="quizState.choicesDisabled"
            :style="{ opacity: quizState.choicesDisabled ? (quizState.selectedChoice === choice ? 1 : 0.5) : 1 }"
          >
            {{ choice }}
          </button>
        </div>


        <!-- NEW QUIZ UI: Classify Problem -->
        <div v-if="currentQuestion && currentQuestion.type === 'classify_problem'" class="classify-problem-container" style="margin-top: 15px;">
          <p class="quiz-instruction" style="font-size: 13px; color: #a0aec0; margin-bottom: 10px; font-style: italic; line-height: 1.4;">💡 <b>Cara Menjawab (Klik, BUKAN Drag & Drop):</b> Klik potongan kalimat yang mau dipindah, lalu klik tujuannya di kotak bawah. Jika ingin membatalkan, klik isian di dalam kotak.</p>
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
          <p class="quiz-instruction" style="font-size: 13px; color: #a0aec0; margin-bottom: 10px; font-style: italic; line-height: 1.4;">💡 <b>Cara Menjawab (Klik, BUKAN Drag & Drop):</b> Klik pada kotak di sisi kiri (yang ingin dipasangkan), lalu klik pada tujuannya di sisi kanan. Jika ingin membatalkan/mengubah, klik lagi pada jawaban di kiri.</p>
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

        <!-- Arrange Flow Quiz -->
        <div v-if="currentQuestion && currentQuestion.type === 'arrange_flow'" class="arrange-flow-container">
          <p class="quiz-instruction" style="font-size: 13px; color: #a0aec0; margin-bottom: 10px; font-style: italic; line-height: 1.4;">💡 <b>Cara Menjawab (Klik, BUKAN Drag & Drop):</b> Klik pilihan kotak di atas secara berurutan untuk menyusunnya ke bawah. Jika ingin membatalkan, klik pada jawaban di bawah.</p>
          <div class="arrange-pool">
            <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Pilihan Alur (Klik untuk menyusun)</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 8px;">
              <button 
                v-for="item in currentQuestion.items.filter(i => !quizState.arrangeFlowAnswers.includes(i.id))" 
                :key="item.id"
                @click="quizState.arrangeFlowAnswers.push(item.id)"
                class="arrange-item-btn"
                :disabled="quizState.choicesDisabled"
                style="padding: 8px 12px; border: 2px solid #ccc; border-radius: 6px; background: white; cursor: pointer; font-size: 14px; font-weight: bold;"
              >
                {{ item.text }}
              </button>
            </div>
          </div>
          
          <div class="arrange-answers" style="margin-top: 20px; padding: 15px; border: 2px dashed #ccc; border-radius: 8px; min-height: 100px;">
            <h4 style="margin: 0 0 10px 0; font-size: 14px; color: #666;">Alur yang disusun (Klik untuk membatalkan)</h4>
            <div style="display: flex; flex-direction: column; gap: 8px;">
              <div 
                v-for="(ansId, index) in quizState.arrangeFlowAnswers" 
                :key="ansId"
                @click="!quizState.choicesDisabled && quizState.arrangeFlowAnswers.splice(index, 1)"
                style="padding: 10px; background: #e0f7fa; border: 2px solid #00acc1; border-radius: 6px; font-weight: bold; cursor: pointer; display: flex; align-items: center; gap: 10px;"
              >
                <span style="background: white; width: 24px; height: 24px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 12px; color: #00acc1;">{{ index + 1 }}</span>
                {{ currentQuestion.items.find(i => i.id === ansId)?.text }}
              </div>
            </div>
          </div>
          
          <button 
            v-if="quizState.arrangeFlowAnswers.length === currentQuestion.items.length" 
            @click="submitArrangeFlow" 
            class="submit-btn" 
            style="margin-top: 15px; width: 100%; padding: 12px; background: #fbc02d; border: 3px solid #333; border-radius: 8px; font-weight: bold; font-size: 16px; cursor: pointer;"
            :disabled="quizState.choicesDisabled"
          >
            Cek Susunan
          </button>
        </div>

        <!-- NEW QUIZ UI: Feasibility Buckets -->
        <div v-if="currentQuestion && currentQuestion.type === 'feasibility_buckets'" class="feasibility-buckets-container" style="margin-top: 15px;">
          
          <!-- Stage 1 -->
          <div v-if="!isFeasibilityFollowUp">
            <p class="quiz-instruction" style="font-size: 13px; color: #a0aec0; margin-bottom: 10px; font-style: italic; line-height: 1.4;">💡 <b>Cara Menjawab (Klik, BUKAN Drag & Drop):</b> Klik pada fitur yang mau dipindah, lalu klik tujuannya di salah satu kotak (bucket) di bawah. Jika ingin membatalkan, klik isian di dalam kotak.</p>
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


        <div v-if="currentQuestion && currentQuestion.type === 'input'">
          <div v-if="currentQuestion.subtype === 'jinakkan_loop'" class="tamer-layout" style="display: flex; gap: 15px; align-items: stretch; margin-top: 15px; text-align: left;">
            <div class="playground-card" style="margin: 0; padding: 15px; display: flex; flex-direction: column; gap: 10px; background: #fff; border: 2px solid #000; border-radius: 8px; flex: 1;">
                <h4 style="font-size: 15px; margin: 0; color: #000;">Kode Program:</h4>
                <div class="code-block" style="margin: 0; font-size: 14px; line-height: 1.4; background: #282a36; color: #f8f8f2; padding: 10px; border-radius: 6px; font-family: monospace;">
                    <span class="keyword" style="color: #ff79c6;">if</span> pilihan == <span class="string" style="color: #f1fa8c;">"5"</span>:<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<span class="keyword" style="color: #8be9fd;">print</span>(<span class="string" style="color: #f1fa8c;">"Terima kasih!"</span>)<br>
                    &nbsp;&nbsp;&nbsp;&nbsp;<input @keyup.enter="!quizState.choicesDisabled && submitInputAnswer()" type="text" v-model="quizState.inputAnswer" placeholder="[Ketik kode penyetop...]" style="width: 150px; padding: 4px 6px; font-size: 14px; border: 2px solid #000; border-radius: 4px; font-family: monospace; color: #000; outline: none; background: #fff;" :disabled="quizState.choicesDisabled">
                </div>
                <button 
                  :class="['cek-jawaban-btn', { 'disabled': !quizState.inputAnswer.trim() || quizState.choicesDisabled }]"
                  :disabled="!quizState.inputAnswer.trim() || quizState.choicesDisabled"
                  @click="submitInputAnswer" 
                  style="background: #ff4757; color: white; padding: 10px; border-radius: 6px; border: 2px solid #000; font-weight: bold; cursor: pointer; box-shadow: 2px 2px 0px #000; text-transform: none; height: auto;"
                >Jinakkan Loop ⚙️</button>
            </div>
            <div class="tamer-console-card" style="background: #1e1e1e; color: #00ff00; padding: 10px; border-radius: 6px; font-family: monospace; font-size: 12px; flex: 1; border: 2px solid #000; overflow: hidden; display: flex; flex-direction: column;">
                <div class="tamer-console-line">=== CELENGAN PINTAR ===</div>
                <div class="tamer-console-line">1. Tambah jajanan</div>
                <div class="tamer-console-line">5. Keluar</div>
                <div class="tamer-console-line">Pilih menu: 5</div>
                <div class="tamer-console-line">Terima kasih!</div>
                <div class="tamer-console-line" style="opacity: 0.7;">=== CELENGAN PINTAR ===</div>
                <div class="tamer-console-line" style="opacity: 0.5;">1. Tambah jajanan</div>
                <div class="tamer-console-line" style="opacity: 0.3;">...</div>
            </div>
          </div>
          <div v-else class="input-container" style="display: flex; gap: 15px; flex-direction: row; align-items: center; margin-top: 20px;">
            <input @keyup.enter="!quizState.choicesDisabled && submitInputAnswer()" type="text" v-model="quizState.inputAnswer" placeholder="..." :disabled="quizState.choicesDisabled" style="padding: 10px 14px; border-radius: 4px; border: 1px solid #757575; background: #ffffff; color: #000000; font-size: 16px; width: 120px; outline: none;">
            <button 
              :class="['cek-jawaban-btn', { 'disabled': !quizState.inputAnswer.trim() || quizState.choicesDisabled }]"
              :disabled="!quizState.inputAnswer.trim() || quizState.choicesDisabled"
              @click="submitInputAnswer"
            >Cek Jawaban!</button>
          </div>
        </div>

        <div v-if="currentQuestion && currentQuestion.type === 'card_choice'" class="card-choice-container" style="display: flex; gap: 15px; flex-direction: row; align-items: stretch; margin-top: 15px;">
          <button 
            v-for="(card, cIdx) in currentQuestion.cards" 
            :key="cIdx"
            class="card-choice-btn"
            :disabled="quizState.choicesDisabled"
            :style="{ opacity: quizState.choicesDisabled ? (quizState.selectedChoice === card.id ? 1 : 0.5) : 1 }"
            @click="handleStandardAnswer(card.id)"
          >
            <div class="card-title" style="background-color: #00c3ff; color: #000; font-weight: 800; font-size: 16px; padding: 4px 12px; border-radius: 8px; border: 2px solid #000; display: inline-block; margin-bottom: 10px; box-shadow: 2px 2px 0px #000;">{{ card.title }}</div>
            <div class="card-text" style="text-align: left; font-size: 15px; font-weight: 600; color: #1a1a1a; line-height: 1.4;" v-html="card.html"></div>
          </button>
        </div>

        <div v-if="currentQuestion && currentQuestion.type === 'essay'" class="essay-container">
          <textarea v-model="quizState.essayAnswer" placeholder="Tulis jawaban logismu di sini..." rows="5" :disabled="quizState.choicesDisabled"></textarea>
          <div class="char-count" :class="{ 'error': quizState.essayAnswer.length < (currentQuestion.minChars || 150) }">
            {{ quizState.essayAnswer.length }} / {{ currentQuestion.minChars || 150 }} karakter minimal
          </div>
          <button 
            class="essay-submit-btn" 
            :disabled="quizState.essayAnswer.length < (currentQuestion.minChars || 150) || quizState.choicesDisabled"
            @click="submitEssayAnswer"
          >Kirim Jawaban</button>
        </div>
        <div v-if="currentQuestion && currentQuestion.type === 'pyscript'" class="pyscript-container" style="margin-top: 15px;">
          <div v-if="isPyodideLoading" style="color: #ffcc00; margin-bottom: 10px; font-weight: bold; text-align: center;">Sedang memuat Mesin Python... ⏳ (Mohon tunggu sebentar)</div>
          <textarea 
            v-model="pyscriptCode" 
            class="code-editor" 
            rows="14" 
            style="width: 100%; background: #282a36; color: #f8f8f2; font-family: 'Courier New', Courier, monospace; font-size: 14px; padding: 15px; border-radius: 12px; border: 3px solid #6272a4; margin-bottom: 10px; resize: vertical;"
            :disabled="quizState.choicesDisabled || isPyodideLoading"
          ></textarea>
          <div style="display: flex; gap: 10px; margin-bottom: 15px;">
            <button @click="runPython" style="background-color: #6272a4; color: white; padding: 10px 15px; border-radius: 8px; border: 2px solid #44475a; cursor: pointer; flex: 1; font-weight: bold; font-size: 16px;" :disabled="isPyodideLoading">▶️ Coba Jalankan (Run)</button>
            <button @click="submitPython" style="background-color: #50fa7b; color: #282a36; font-weight: bold; padding: 10px 15px; border-radius: 8px; border: 2px solid #282a36; cursor: pointer; flex: 1; font-size: 16px; box-shadow: 2px 2px 0px #282a36;" :disabled="quizState.choicesDisabled || isPyodideLoading">🚀 Kirim Jawaban (Submit)</button>
          </div>
          <div class="pyscript-output" style="background-color: #000; color: #50fa7b; font-family: 'Courier New', Courier, monospace; font-size: 14px; padding: 15px; border-radius: 12px; min-height: 80px; text-align: left; white-space: pre-wrap; margin-bottom: 15px; border: 2px solid #44475a;">> Console Output:<br>{{ pyodideOutput }}</div>
        </div>

        <div class="quiz-feedback" id="quizFeedback" role="status" v-show="quizState.quizFeedback" :class="quizState.quizFeedbackType">
          <span v-html="quizState.quizFeedback"></span>
        </div>
        <div v-if="currentQuestion && currentQuestion.type === 'info'" class="info-action-container" style="text-align: center; margin-top: 20px;">
          <button 
            class="quiz-next" 
            style="display: inline-block; padding: 12px 30px; font-size: 18px; font-weight: bold;"
            @click="goToNextQuestion"
          >
            Lanjut Nonton 👉
          </button>
        </div>

        <div class="quiz-actions" v-show="!currentQuestion || currentQuestion.type !== 'info'">
          <button class="quiz-review" type="button" @click="replayActiveQuizVideo">↺ Ulangi 30 detik video</button>
          <button class="quiz-next" type="button" v-show="quizState.isNextBtnVisible" @click="goToNextQuestion">{{ quizState.nextBtnText || (quizState.currentQuestionIdx < quizState.shuffledQuestions.length - 1 ? 'Soal berikutnya →' : 'Selesai →') }}</button>
        </div>
      </div>
    </div>
  </div>

  <div class="quiz-return" id="quizReturn" role="status" :class="{ visible: quizReturn.isVisible }">
    <p>Sudah cukup mengulang materinya? Kamu bisa kembali ke checkpoint kapan saja.</p>
    <button type="button" @click="returnToActiveQuiz">Kembali ke kuis sekarang →</button>
  </div>

  <div class="completion-toast" id="completionToast" role="status">
    Misi selesai. Kamu sudah mempelajari input validation, sanitasi, dan penerapannya dalam program keuangan.
  </div>
</template>
