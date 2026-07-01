/**
 * PLATINUM MASTER ARCHITECTURE - GOOGLE APPS SCRIPT ENGINE
 * VERSION: FIXED TYPE-SAFE NUMERIC PASSCODE VALIDATION ENGINE
 * + FIXED REWARD-COLUMN MATCHING (numeric reward_key vs "Reward N" headers)
 */

function doGet(e) {
  return handleEngineRequest(e);
}

function doPost(e) {
  return handleEngineRequest(e);
}

function handleEngineRequest(e) {
  var params = {};
  try {
    if (e && e.parameter && e.parameter.action) {
      params = e.parameter;
    } else if (e && e.postData && e.postData.contents) {
      params = JSON.parse(e.postData.contents);
    } else if (e && e.parameter) {
      params = e.parameter;
    }
  } catch(err) {
    if (e && e.parameter) params = e.parameter;
  }

  var action = params.action || "";
  var item = params.item || "";
  var pinCode = params.pin || "";
  var userPasscode = params.passcode || params.user_passcode || "";

  if (action === "executeStoreTrade" && params.payload) {
    try {
      var unpacked = JSON.parse(params.payload);
      if (unpacked.passcode) userPasscode = unpacked.passcode;
    } catch(payloadErr) {}
  }

  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var masterSheet = ss.getSheetByName("master_sheet") || ss.getSheets()[0];
  var medalSheet = ss.getSheetByName("Medallions");
  var pinSheet = ss.getSheetByName("PINs");
  var rewardsSheet = ss.getSheetByName("rewards");
  
  // ====================================================================
  // ROUTINE A: AUTHENTICATE PASSCODE & FETCH PROFILE IN POINTS
  // ====================================================================
  if (action === "fetchData") {
    try {
      var lastRow = masterSheet.getLastRow();
      var targetRowIndex = -1;
      var cleanInputPasscode = String(userPasscode).trim();
      
      // Match by exact display value string representation of your 4-digit numbers
      if (cleanInputPasscode !== "") {
        for (var r = 3; r <= lastRow; r++) {
          var displayPasscode = String(masterSheet.getRange(r, 2).getDisplayValue()).trim();
          if (displayPasscode === cleanInputPasscode) {
            targetRowIndex = r; 
            break;
          }
        }
      }
      
      if (targetRowIndex === -1) {
        return ContentService.createTextOutput(JSON.stringify({
          "status": "unauthorized",
          "message": "Invalid credentials. Profile match not located inside database."
        })).setMimeType(ContentService.MimeType.JSON);
      }
      
      var row2Headers = masterSheet.getRange(2, 1, 1, masterSheet.getLastColumn()).getValues()[0];
      var targetAccountRow = masterSheet.getRange(targetRowIndex, 1, 1, masterSheet.getLastColumn()).getValues()[0];
      var activeUsername = String(targetAccountRow[0]).trim(); 
      
      // Fetch medallions metrics natively
      var medallions = [];
      if (medalSheet) {
        var medalData = medalSheet.getDataRange().getValues();
        for (var i = 1; i < medalData.length; i++) {
          if (!medalData[i][0]) continue;
          medallions.push({
            "Medallion": String(medalData[i][0]).trim(),
            "Rarity": medalData[i][1] || "Common",
            "Value": parseInt(medalData[i][2]) || 0,
            "Availability": medalData[i][3] || "0",
            "Probability": medalData[i][4] || "0%"
          });
        }
      }
      
      // Fetch catalog matrix dynamically directly from the 'rewards' tab
      var dynamicRewards = [];
      if (rewardsSheet) {
        var rewardsData = rewardsSheet.getRange(1, 1, rewardsSheet.getLastRow(), 4).getValues();
        for (var k = 1; k < rewardsData.length; k++) {
          if (!rewardsData[k][0] || String(rewardsData[k][1]).trim() === "TBD") continue;
          dynamicRewards.push({
            "reward_key": String(rewardsData[k][0]).trim(),
            "title": String(rewardsData[k][1]).trim(),
            "description": String(rewardsData[k][2]).trim(),
            "cost": parseInt(rewardsData[k][3]) || 0
          });
        }
      }
      
      var inventoryCounts = {};
      for (var j = 4; j <= 15; j++) {
        var medallionName = String(row2Headers[j]).trim().toLowerCase();
        if (!medallionName) continue;
        inventoryCounts[medallionName] = parseInt(targetAccountRow[j]) || 0;
      }
      
      var rawExactValue = String(masterSheet.getRange(targetRowIndex, 3).getDisplayValue()).trim();
      var exactCollected = String(masterSheet.getRange(targetRowIndex, 4).getDisplayValue()); 

      return ContentService.createTextOutput(JSON.stringify({
        "status": "success",
        "username": activeUsername,
        "medallions": medallions,
        "catalog": dynamicRewards,
        "master_summary": {
          "Inventory": inventoryCounts,
          "CollectionValue": rawExactValue + " PTS",
          "MedallionsCollected": exactCollected
        }
      })).setMimeType(ContentService.MimeType.JSON);
      
    } catch(fetchErr) {
      return ContentService.createTextOutput(JSON.stringify({
        "status": "error",
        "message": "Fetch core crash: " + fetchErr.toString()
      })).setMimeType(ContentService.MimeType.JSON);
    }
  }

  // ====================================================================
  // ROUTINE B: MINE MEDALLION
  // ====================================================================
  if (action === "mineMedallion") {
    try {
      var headers = masterSheet.getRange("2:2").getValues()[0]; 
      var itemColIndex = -1;
      
      for (var j = 0; j < headers.length; j++) {
        if (String(headers[j]).trim().toLowerCase() === String(item).trim().toLowerCase()) {
          itemColIndex = j + 1;
          break;
        }
      }
      
      if (itemColIndex !== -1) {
        var lastRow = masterSheet.getLastRow();
        var writeRow = 3; 
        var inboundKey = String(userPasscode).trim();

        for (var k = 3; k <= lastRow; k++) {
          if (String(masterSheet.getRange(k, 2).getDisplayValue()).trim() === inboundKey && inboundKey !== "") {
            writeRow = k;
            break;
          }
        }
        
        var cell = masterSheet.getRange(writeRow, itemColIndex);
        var currentCount = parseInt(cell.getValue()) || 0;
        cell.setValue(currentCount + 1);
        
        return ContentService.createTextOutput("").setMimeType(ContentService.MimeType.TEXT);
      }
    } catch(saveErr) {}
  }

  // ====================================================================
  // ROUTINE C: VERIFY ONE-TIME PIN
  // ====================================================================
  if (action === "verifyPin") {
    try {
      if (!pinSheet || !pinCode) {
        return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Missing PIN registry reference."})).setMimeType(ContentService.MimeType.JSON);
      }
      
      var pinData = pinSheet.getDataRange().getValues();
      var cleanInputPin = String(pinCode).trim();
      
      for (var r = 1; r < pinData.length; r++) {
        var sheetPin = String(pinData[r][0]).trim();
        var sheetStatus = String(pinData[r][1]).trim().toLowerCase();
        
        if (sheetPin === cleanInputPin) {
          if (sheetStatus === "active") {
            pinSheet.getRange(r + 1, 2).setValue("Expired");
            SpreadsheetApp.flush(); 
            return ContentService.createTextOutput(JSON.stringify({"status": "success", "message": "PIN unlocked successfully!"})).setMimeType(ContentService.MimeType.JSON);
          } else {
            return ContentService.createTextOutput(JSON.stringify({"status": "invalid", "message": "This PIN has already been used."})).setMimeType(ContentService.MimeType.JSON);
          }
        }
      }
      return ContentService.createTextOutput(JSON.stringify({"status": "invalid", "message": "Invalid PIN entry. Try again."})).setMimeType(ContentService.MimeType.JSON);
    } catch(pinErr) { return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": pinErr.toString()})).setMimeType(ContentService.MimeType.JSON); }
  }

  // ====================================================================
  // ROUTINE D: STORE CHECKOUT MECHANIC
  // ====================================================================
  if (action === "executeStoreTrade") {
    try {
      if (!params.payload) {
        return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Missing payload execution packet"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      var data = JSON.parse(decodeURIComponent(params.payload));
      var basket = data.basket || {}; 
      var barterSpent = data.barter_spent || {};
      
      var lastRow = masterSheet.getLastRow();
      // Headers are on Row 2
      var row2Headers = masterSheet.getRange(2, 1, 1, masterSheet.getLastColumn()).getValues()[0];
      var targetRowIndex = -1;
      
      var cleanInputPasscode = String(userPasscode).trim();
      for (var k = 3; k <= lastRow; k++) {
        if (String(masterSheet.getRange(k, 2).getDisplayValue()).trim() === cleanInputPasscode && cleanInputPasscode !== "") {
          targetRowIndex = k;
          break;
        }
      }
      
      if (targetRowIndex === -1) {
        return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": "Passcode synchronization error"})).setMimeType(ContentService.MimeType.JSON);
      }
      
      // 1. DEDUCT MEDALLIONS
      for (var key in barterSpent) {
        var deductionQty = parseInt(barterSpent[key]) || 0;
        if (deductionQty <= 0) continue;
        
        var colIndex = -1;
        var cleanKey = String(key).replace(/\s+/g, '').toLowerCase();
        
        for (var c = 4; c <= 15; c++) {
          var cleanHeader = String(row2Headers[c]).replace(/\s+/g, '').toLowerCase();
          if (cleanHeader === cleanKey) {
            colIndex = c + 1;
            break;
          }
        }
        
        if (colIndex !== -1) {
          var currentStock = parseInt(masterSheet.getRange(targetRowIndex, colIndex).getValue()) || 0;
          masterSheet.getRange(targetRowIndex, colIndex).setValue(Math.max(0, currentStock - deductionQty));
        }
      }
      
      // 2. INCREMENT REWARDS QUANTITIES
      // NOTE: reward_key values from the 'rewards' sheet are plain numbers (e.g. "1", "2"),
      // while master_sheet headers are worded "Reward 1", "Reward 2", etc. A straight
      // string-equality match (even after stripping spaces) never matches "1" against
      // "reward1", so quantities never landed in Q:V. Fix: extract the numeric portion
      // from both the cart key and the sheet header and compare those instead.
      for (var rewardKey in basket) {
        var qtyClaimed = parseInt(basket[rewardKey]) || 0;
        if (qtyClaimed <= 0) continue;
        
        var targetCol = -1;
        var keyDigitsMatch = String(rewardKey).match(/\d+/);
        var keyDigits = keyDigitsMatch ? keyDigitsMatch[0] : null;
        if (!keyDigits) continue;
        
        for (var c = 16; c < row2Headers.length; c++) { 
          var headerDigitsMatch = String(row2Headers[c]).match(/\d+/);
          var headerDigits = headerDigitsMatch ? headerDigitsMatch[0] : null;
          
          if (headerDigits && headerDigits === keyDigits) {
            targetCol = c + 1;
            break;
          }
        }
        
        if (targetCol !== -1) {
          // Get current numeric amount in column, add new purchase qty, and update
          var currentRewardQty = parseInt(masterSheet.getRange(targetRowIndex, targetCol).getValue()) || 0;
          masterSheet.getRange(targetRowIndex, targetCol).setValue(currentRewardQty + qtyClaimed);
        }
      }
      
      SpreadsheetApp.flush();
      return ContentService.createTextOutput(JSON.stringify({"status": "success"})).setMimeType(ContentService.MimeType.JSON);
      
    } catch(tradeErr) {
      return ContentService.createTextOutput(JSON.stringify({"status": "error", "message": tradeErr.toString()})).setMimeType(ContentService.MimeType.JSON);
    }
  }

  return ContentService.createTextOutput("Processed").setMimeType(ContentService.MimeType.TEXT);
}
