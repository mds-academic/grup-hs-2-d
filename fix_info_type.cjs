const fs = require('fs');

const path = '/Users/yazidhilmi/Documents/cloud/Kalananti-cloud/Academic_Content/B2B/UOB/Async/Highschool/sesi30-32/grup-hs-2-c/src/courseData.js';
let content = fs.readFileSync(path, 'utf8');

// A quick and safe way to update is to use a regex or replace on specific titles.
// But evaluating the file and stringifying it is better.
// courseData.js has `export const courseData = { ... };`
let dataString = content.replace('export const courseData = ', '').trim();
if (dataString.endsWith(';')) dataString = dataString.slice(0, -1);

const data = eval('(' + dataString + ')');

const infoTitles = [
  "Bahayanya Angka Negatif! ⚠️",
  "Huruf Kapital itu Berbeda! ⚠️",
  "Mini Project: Safe Transaction Input 🛡️",
  "Mini Project: Safe Input with Error Handling 🛡️",
  "Mini Project: Financial Data Analyzer 📊🔍"
];

for (const key in data) {
  const step = data[key];
  if (step.quizzes) {
    step.quizzes.forEach(quiz => {
      if (quiz.questions) {
        quiz.questions.forEach(q => {
          if (infoTitles.includes(q.title) || q.title.includes("Mini Project")) {
            q.type = "info";
            delete q.choices;
            delete q.correct;
            delete q.explanation;
          }
        });
      }
    });
  }
}

const newContent = `export const courseData = ${JSON.stringify(data, null, 2)};\n`;
fs.writeFileSync(path, newContent);
console.log('courseData.js updated for info types.');
