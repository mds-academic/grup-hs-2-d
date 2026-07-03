// Apps Script URL (After Deploy as Web App)
// Paste this code into Google Apps Script connected to your Spreadsheet.

const SPREADSHEET_ID = '1pE_YGmKFZNUz8ow2baGfxw3EMH0PwOQeRmOWVVB9Itg';
const SHEET_DATA = 'ops-student-data';
const SHEET_RESULT = 'ops-student-result-ghs2d';

// Handling GET Requests (For Login / Check Email)
function doGet(e) {
  const action = e.parameter.action;

  const sheet = SpreadsheetApp.openById(SPREADSHEET_ID).getSheetByName(SHEET_DATA);
  if (!sheet) {
    return respond({ success: false, message: "Sheet data tidak ditemukan" });
  }

  // Header row: No | Student's Name | Student's School | Student's Academia Email
  const data = sheet.getDataRange().getValues();

  if (action === 'schools') {
    const query = normalizeText(e.parameter.query || '');
    const schools = [];
    const seen = {};

    for (let i = 1; i < data.length; i++) {
      const school = String(data[i][2] || '').trim();
      const key = normalizeText(school);
      if (!school || seen[key]) continue;
      if (matchesSearchTokens(key, query)) {
        seen[key] = true;
        schools.push(school);
      }
    }

    schools.sort();
    return respond({ success: true, schools: schools });
  }

  if (action === 'students') {
    const school = normalizeText(e.parameter.school || '');
    const query = normalizeText(e.parameter.query || '');
    const students = [];

    if (!school) {
      return respond({ success: false, message: "Nama sekolah kosong" });
    }

    for (let i = 1; i < data.length; i++) {
      const rowName = String(data[i][1] || '').trim();
      const rowSchool = String(data[i][2] || '').trim();
      const rowEmail = String(data[i][3] || '').trim();

      if (!rowName || !rowEmail) continue;
      if (normalizeText(rowSchool) !== school) continue;
      if (!matchesSearchTokens(normalizeText(rowName + ' ' + rowEmail), query)) continue;

      students.push({
        name: rowName,
        school: rowSchool,
        maskedEmail: maskEmail(rowEmail)
      });
    }

    students.sort(function(a, b) {
      return a.name.localeCompare(b.name);
    });

    return respond({ success: true, students: students });
  }

  if (action === 'login') {
    const email = normalizeEmail(e.parameter.email || '');
    const school = normalizeText(e.parameter.school || '');
    const attempts = Number(e.parameter.attempts || 1);

    if (!email) {
      return respond({ success: false, message: "Email kosong" });
    }

    if (school) {
      let suggestion = null;

      for (let i = 1; i < data.length; i++) {
        const rowName = String(data[i][1] || '').trim();
        const rowSchool = String(data[i][2] || '').trim();
        const rowEmail = String(data[i][3] || '').trim();

        if (normalizeText(rowSchool) !== school || !rowEmail) continue;

        if (normalizeEmail(rowEmail) === email) {
          return respond({
            success: true,
            name: rowName,
            school: rowSchool,
            email: rowEmail
          });
        }

        if (!suggestion && looksLikeEmailTypo(email, rowEmail)) {
          suggestion = {
            name: rowName,
            school: rowSchool,
            maskedEmail: maskEmail(rowEmail)
          };
        }
      }

      return respond({
        success: false,
        message: attempts >= 3
          ? "Kami belum bisa mencocokkan emailmu. Kalau sudah dicek tapi tetap belum bisa, hubungi RFO/guru pendamping untuk memastikan email yang terdaftar di Akademia Ruangguru."
          : suggestion
            ? "Email ini mirip dengan data yang terdaftar. Coba cek lagi tanda titik, huruf yang tertukar, atau domain email."
            : "Email ini belum cocok dengan data Akademia Ruangguru untuk sekolah yang dipilih. Coba cek lagi penulisannya ya.",
        suggestion: suggestion,
        needsRfo: attempts >= 3
      });
    }

    // Backward-compatible email-only login for older deployed pages.
    for (let i = 1; i < data.length; i++) {
      let rowEmail = normalizeEmail(data[i][3]);
      if (rowEmail === email) {
        return respond({
          success: true,
          name: data[i][1],
          school: data[i][2],
          email: data[i][3]
        });
      }
    }
    
    return respond({ success: false, message: "Email tidak terdaftar" });
  }
  
  return respond({ success: false, message: "Invalid action" });
}

// Handling POST Requests (For Saving/Updating Data Progressively)
function doPost(e) {
  let payload;
  try {
    payload = JSON.parse(e.postData.contents);
  } catch (err) {
    return respond({ success: false, message: "Invalid JSON" });
  }
  
  const email = (payload.Students_Email || '').toLowerCase().trim();
  if (!email) {
    return respond({ success: false, message: "Email missing from payload" });
  }
  
  const ss = SpreadsheetApp.openById(SPREADSHEET_ID);
  let sheet = ss.getSheetByName(SHEET_RESULT);
  
  if (!sheet) {
    return respond({ success: false, message: "Sheet result tidak ditemukan" });
  }

  const headers = [
    "Timestamp", "Students_Name", "Students_School", "Students_Email",
    "V1_Q1_Att", "V1_Q2_Att", "V1_Q2_Ans", "V1_Q3_Att",
    "V1_Q3_Ans", "V2_Q1_Att", "V2_Q2_Att", "V2_Q2_Ans",
    "V2_Q3_Att", "V2_Q3_Ans", "V2_Q4_Att", "V2_Q4_Ans",
    "V2_Q5_Att", "V2_Q5_Ans", "V3_Q1_Att", "V3_Q1_Ans",
    "V4_Q1_Att", "V4_Q1_Ans", "V4_Q2_Att", "V4_Q2_Ans",
    "V4_Q3_Att", "V4_Q3_Ans", "V5_Q1_Att", "V5_Q1_Ans",
    "V6_Q1_Att", "V6_Q1_Ans", "V6_Q2_Att", "V6_Q2_Ans",
    "V7_Q1_Att", "V7_Q1_Ans", "V8_Q1_Att", "V8_Q1_Ans",
    "V8_Q2_Att", "V8_Q2_Ans", "V9_Q1_Att", "V9_Q1_Ans",
    "V9_Q2_Att", "V9_Q2_Ans", "V9_Q3_Att", "V9_Q3_Ans",
    "V9_Q4_Att", "V9_Q4_Ans", "V9_Q5_Att", "V9_Q5_Ans",
    "V9_Q6_Att", "V9_Q6_Ans", "V9_Q7_Att", "V9_Q7_Ans",
    "Final_Project_Code", "Final_Project_Attempts", "Final_Project_Score"
  ];
  
  // Ensure headers exist
  if (sheet.getLastRow() === 0) {
    sheet.appendRow(headers);
  }
  
  // Find if user already exists to update, or append new row
  const data = sheet.getDataRange().getValues();
  let rowIndex = -1;
  
  // Start from 1 to skip header
  for (let i = 1; i < data.length; i++) {
    let rowEmail = String(data[i][3]).toLowerCase().trim();
    if (rowEmail === email) {
      rowIndex = i + 1; // Google Sheets is 1-indexed
      break;
    }
  }
  
  // Map payload to array
  const rowData = headers.map(header => {
    if (header === "Timestamp") {
      return new Date();
    }
    return payload[header] !== undefined ? payload[header] : "";
  });
  
  if (rowIndex > -1) {
    // UPDATE existing row
    sheet.getRange(rowIndex, 1, 1, rowData.length).setValues([rowData]);
  } else {
    // APPEND new row
    sheet.appendRow(rowData);
  }
  
  return respond({ success: true, message: "Data saved successfully" });
}

// Helper to return JSON with CORS headers
function respond(data) {
  return ContentService.createTextOutput(JSON.stringify(data))
    .setMimeType(ContentService.MimeType.JSON);
}

function normalizeText(value) {
  return String(value || '').toLowerCase().trim().replace(/\s+/g, ' ');
}

function normalizeEmail(value) {
  return String(value || '').toLowerCase().trim().replace(/\s+/g, '');
}

function normalizeEmailLoose(value) {
  const email = normalizeEmail(value);
  const parts = email.split('@');
  if (parts.length !== 2) return email;
  return parts[0].replace(/\./g, '') + '@' + parts[1];
}

function matchesSearchTokens(source, query) {
  const normalizedSource = normalizeText(source);
  const normalizedQuery = normalizeText(query);

  if (!normalizedQuery) return true;

  const tokens = normalizedQuery.split(' ').filter(Boolean);
  return tokens.every(function(token) {
    return normalizedSource.indexOf(token) > -1;
  });
}

function looksLikeEmailTypo(inputEmail, registeredEmail) {
  const input = normalizeEmail(inputEmail);
  const registered = normalizeEmail(registeredEmail);
  if (!input || !registered) return false;

  if (normalizeEmailLoose(input) === normalizeEmailLoose(registered)) return true;

  const inputParts = input.split('@');
  const registeredParts = registered.split('@');
  if (inputParts.length !== 2 || registeredParts.length !== 2) {
    return levenshteinDistance(input, registered) <= 2;
  }

  const inputLocal = inputParts[0].replace(/\./g, '');
  const registeredLocal = registeredParts[0].replace(/\./g, '');
  const inputDomain = inputParts[1];
  const registeredDomain = registeredParts[1];

  if (inputLocal === registeredLocal && levenshteinDistance(inputDomain, registeredDomain) <= 2) return true;
  if (inputDomain === registeredDomain && levenshteinDistance(inputLocal, registeredLocal) <= 2) return true;

  return levenshteinDistance(normalizeEmailLoose(input), normalizeEmailLoose(registered)) <= 2;
}

function maskEmail(email) {
  return normalizeEmail(email);
}

function levenshteinDistance(a, b) {
  a = String(a || '');
  b = String(b || '');

  const matrix = [];
  for (let i = 0; i <= b.length; i++) matrix[i] = [i];
  for (let j = 0; j <= a.length; j++) matrix[0][j] = j;

  for (let i = 1; i <= b.length; i++) {
    for (let j = 1; j <= a.length; j++) {
      if (b.charAt(i - 1) === a.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }

  return matrix[b.length][a.length];
}
