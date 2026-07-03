import fs from 'fs';
import path from 'path';

const file = '/Users/yazidhilmi/Documents/cloud/Kalananti-cloud/Academic_Content/B2B/UOB/Async/Highschool/sesi30-32/hrup-hs-2-c/src/courseData.js';
let content = fs.readFileSync(file, 'utf8');

const quizzesMatch = content.match(/quizzes: \[([\s\S]*?)\]\n  \},/);
const quizzesText = quizzesMatch ? `quizzes: [${quizzesMatch[1]}]` : "quizzes: []";

const newContent = `export const courseData = {
  1: {
    kicker: "PYTHON BASICS",
    title: "Safe Finance Tracker",
    duration: "12 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 9,
    endSeconds: 756,
    bookmarks: [
      { time: 9, label: "Apa yang Akan Kita Pelajari? 🎯" },
      { time: 180, label: "Apa Itu Input? 📥" },
      { time: 360, label: "Apa Itu Validasi Input? 🚦" },
      { time: 540, label: "Apa Itu Sanitasi Input? 🧼" }
    ],
    ${quizzesText}
  },
  2: {
    kicker: "INPUT VALIDATION",
    title: "Membuat Input Aman",
    duration: "15 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 761,
    endSeconds: 1693,
    bookmarks: [
      { time: 761, label: "Validasi Input Kosong 📭" },
      { time: 900, label: "Validasi Jenis Transaksi 🔄" },
      { time: 1200, label: "Validasi Nominal 💸" },
      { time: 1500, label: "Mini Project: Safe Transaction 🛡️" }
    ],
    quizzes: []
  },
  3: {
    kicker: "ERROR HANDLING",
    title: "Try-Except & Debugging",
    duration: "21 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 1714,
    endSeconds: 2997,
    bookmarks: [
      { time: 1714, label: "Jenis Error yang Sering Muncul 🐛" },
      { time: 1900, label: "Mengenal Penyelamat: try-except 🛡️" },
      { time: 2200, label: "Debugging Bagaikan Memperbaiki Lampu 💡" },
      { time: 2600, label: "Cara Debugging Step-by-Step 🕵️‍♂️" }
    ],
    quizzes: []
  },
  4: {
    kicker: "DATA STRUCTURES",
    title: "Transaction Recorder",
    duration: "15 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 2998,
    endSeconds: 3897,
    bookmarks: [
      { time: 2998, label: "Apa Itu Dictionary di Python? 📖" },
      { time: 3200, label: "Menyimpan Banyak Transaksi 🗂️" },
      { time: 3500, label: "Menghitung Ringkasan Data 🧮" },
      { time: 3700, label: "Mini Project: Transaction Recorder 📝" }
    ],
    quizzes: []
  },
  5: {
    kicker: "FINANCIAL DATA",
    title: "Data Analysis",
    duration: "9 Menit",
    videoId: "pKYN1E60xtU",
    startSeconds: 3932,
    endSeconds: 4473,
    bookmarks: [
      { time: 3932, label: "Dataset Pengeluaran Bulanan 📝" },
      { time: 4050, label: "Menghitung Total dengan sum() ➕" },
      { time: 4150, label: "Menganalisis Berdasarkan Kategori 📂" },
      { time: 4300, label: "10 Fitur Wajib Program 📋" }
    ],
    quizzes: []
  }
};
`;

fs.writeFileSync(file, newContent);
console.log('Updated courseData.js');
