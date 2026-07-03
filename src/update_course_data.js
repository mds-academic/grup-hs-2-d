const fs = require('fs');
const path = require('path');

const p = path.join(__dirname, 'courseData.js');
let content = fs.readFileSync(p, 'utf8');

// The original content has step 1 from line 2.
// Let's replace the whole file content to be safe. We'll extract the quizzes part from step 1.

// Extract the quizzes array text from courseData.js so we don't have to rewrite it.
const quizzesMatch = content.match(/quizzes: \[([\s\S]*?)\]\n  \}/);
const quizzesText = quizzesMatch ? quizzesMatch[0] : "quizzes: []\n  }";

const newContent = `export const courseData = {
  1: {
    kicker: "Materi 01",
    title: "Mengenal Input dan Validasi Data",
    duration: "12 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 9,
    endSeconds: 756,
    bookmarks: [
      { time: 9, label: "Apa Itu Input?" },
      { time: 120, label: "Masalah Input" },
      { time: 300, label: "Validasi vs Sanitasi" },
      { time: 600, label: "Validasi Nominal" }
    ],
    ${quizzesText},
  2: {
    kicker: "Materi 02",
    title: "Membuat Input yang Aman dengan Sanitasi dan Validasi",
    duration: "15 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 761,
    endSeconds: 1693,
    bookmarks: [],
    quizzes: []
  },
  3: {
    kicker: "Materi 03",
    title: "Mengatasi Error dengan Try-Except dan Debugging",
    duration: "21 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 1714,
    endSeconds: 2997,
    bookmarks: [],
    quizzes: []
  },
  4: {
    kicker: "Materi 04",
    title: "Menyimpan Transaksi dengan Dictionary",
    duration: "15 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 2998,
    endSeconds: 3897,
    bookmarks: [],
    quizzes: []
  },
  5: {
    kicker: "Materi 05",
    title: "Menganalisis Data Keuangan dengan Python",
    duration: "9 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 3932,
    endSeconds: 4473,
    bookmarks: [],
    quizzes: []
  }
};
`;

fs.writeFileSync(p, newContent);
console.log('Updated courseData.js');
