// Configuration
const SPREADSHEET_ID = 'YOUR_SPREADSHEET_ID'; // Replace with your Google Sheet ID
const SHEET_NAME = 'Form Submissions';

// Column headers for the spreadsheet
const HEADERS = [
  'Timestamp',
  'City',
  'State',
  'Name',
  'Email',
  'Message',
  'Section',
  'Page URL'
];

function doPost(e) {
  try {
    // Verify reCAPTCHA
    const recaptchaResponse = e.parameter['g-recaptcha-response'];
    if (!verifyRecaptcha(recaptchaResponse)) {
      return ContentService.createTextOutput(JSON.stringify({
        'success': false,
        'error': 'Invalid reCAPTCHA'
      })).setMimeType(ContentService.MimeType.JSON);
    }

    // Get the spreadsheet and sheet
    const spreadsheet = SpreadsheetApp.openById(SPREADSHEET_ID);
    let sheet = spreadsheet.getSheetByName(SHEET_NAME);
    
    // Create sheet if it doesn't exist
    if (!sheet) {
      sheet = spreadsheet.insertSheet(SHEET_NAME);
      sheet.getRange(1, 1, 1, HEADERS.length).setValues([HEADERS]);
      sheet.setFrozenRows(1);
    }

    // Prepare form data
    const timestamp = new Date();
    const formData = [
      timestamp,
      e.parameter.city || '',
      e.parameter.state || '',
      e.parameter.name || '',
      e.parameter.email || '',
      e.parameter.message || '',
      e.parameter.section || '',
      e.parameter.pageUrl || ''
    ];

    // Append data to sheet
    sheet.appendRow(formData);

    // Send email notification
    sendNotificationEmail(formData);

    // Return success response
    return ContentService.createTextOutput(JSON.stringify({
      'success': true,
      'message': 'Form submitted successfully'
    })).setMimeType(ContentService.MimeType.JSON);

  } catch (error) {
    Logger.log('Error in doPost: ' + error.toString());
    return ContentService.createTextOutput(JSON.stringify({
      'success': false,
      'error': 'Server error occurred'
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function verifyRecaptcha(response) {
  if (!response) return false;

  const secret = 'YOUR_RECAPTCHA_SECRET_KEY'; // Replace with your reCAPTCHA secret key
  const url = 'https://www.google.com/recaptcha/api/siteverify';
  const payload = {
    'secret': secret,
    'response': response
  };

  const options = {
    'method': 'post',
    'payload': payload
  };

  try {
    const result = UrlFetchApp.fetch(url, options);
    const json = JSON.parse(result.getContentText());
    return json.success;
  } catch (error) {
    Logger.log('Error verifying reCAPTCHA: ' + error.toString());
    return false;
  }
}

function sendNotificationEmail(formData) {
  const emailAddress = 'your-email@example.com'; // Replace with your email
  const subject = `New Lead from ${formData[1]}, ${formData[2]}`;
  const body = `
    New form submission received:
    
    City: ${formData[1]}
    State: ${formData[2]}
    Name: ${formData[3]}
    Email: ${formData[4]}
    Message: ${formData[5]}
    Section: ${formData[6]}
    Page URL: ${formData[7]}
    
    Timestamp: ${formData[0]}
  `;

  try {
    MailApp.sendEmail(emailAddress, subject, body);
  } catch (error) {
    Logger.log('Error sending email: ' + error.toString());
  }
}
