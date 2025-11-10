
// =============================================================================
// WOOCOMMERCE GOOGLE APPS SCRIPT - CONFIGURATION
// =============================================================================

// Constants
const CONSTANTS = {
  API: {
    PER_PAGE: 100,
    MAX_PAGES: 100,
    RATE_LIMIT_MS: 500
  },
  CURRENCY_RATES: {
    'USD': 1.52, 'CAD': 1.15, 'AUD': 1.0, 'EUR': 1.65, 'GBP': 1.85,
    'NZD': 0.95, 'SGD': 1.12, 'JPY': 0.011, 'CHF': 1.68
  }
};

// WooCommerce API Configuration - HARDCODED (for now)
function getWooCommerceConfig() {
  // TODO: Move to PropertiesService for security later
  // const props = PropertiesService.getScriptProperties();
  // return {
  //   consumerKey: props.getProperty('WC_CONSUMER_KEY'),
  //   consumerSecret: props.getProperty('WC_CONSUMER_SECRET'),  
  //   baseUrl: props.getProperty('WC_BASE_URL')
  // };
  
  return {
    consumerKey: 'ck_12d05c5c3579172edd0ce18474f8aacac18d544d',
    consumerSecret: 'cs_a61844222eba79f0a49ed79078dc54a8de144be0',
    baseUrl: 'https://minivetguide.com/wp-json/wc/v3/orders'
  };
}

// =============================================================================

/**
 * Setup function to securely store WooCommerce credentials
 * Run this once to store your API credentials securely
 * COMMENTED OUT - Using hardcoded credentials for now
 */
/*
function setupWooCommerceCredentials() {
  const props = PropertiesService.getScriptProperties();
  
  // Store your credentials securely (replace with your actual values)
  props.setProperties({
    'WC_CONSUMER_KEY': 'ck_12d05c5c3579172edd0ce18474f8aacac18d544d',
    'WC_CONSUMER_SECRET': 'cs_a61844222eba79f0a49ed79078dc54a8de144be0',
    'WC_BASE_URL': 'https://minivetguide.com/wp-json/wc/v3/orders'
  });
  
  Logger.log(' WooCommerce credentials have been stored securely');
  Logger.log('⚠️  Remember to update the hardcoded values with your actual credentials');
}
*/

// =============================================================================

// Updated main function with better error handling and data validation
function fetchWooOrders(status, daysBack) {
  const { consumerKey, consumerSecret, baseUrl } = getWooCommerceConfig();
  
  // Create new sheet with timestamp
  const now = new Date();
  const dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd-MM-yy');
  const timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'HH:mm');
  const statusName = status === 'any' ? 'All' : status.charAt(0).toUpperCase() + status.slice(1);
  const sheetName = `${statusName} ${daysBack}d ${dateStr} ${timeStr}`;
  
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.insertSheet(sheetName);

  const dateThreshold = new Date();
  dateThreshold.setDate(dateThreshold.getDate() - daysBack);
  const after = encodeURIComponent(dateThreshold.toISOString());

  // Enhanced pagination to fetch ALL orders
  let allOrders = [];
  let page = 1;
  let hasMorePages = true;
  
  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(consumerKey + ":" + consumerSecret)
  };

  const options = {
    method: "get",
    headers: headers,
    muteHttpExceptions: true
  };

  // Fetch all pages of orders
  while (hasMorePages) {
    try {
      let url = `${baseUrl}?per_page=${CONSTANTS.API.PER_PAGE}&page=${page}&after=${after}`;
      if (status !== 'any') {
        url += `&status=${status}`;
      }

      const response = UrlFetchApp.fetch(url, options);
      const responseCode = response.getResponseCode();
      
      if (responseCode !== 200) {
        Logger.log(` API Error on page ${page}: ${responseCode} - ${response.getContentText()}`);
        break;
      }

      const responseText = response.getContentText();
      const parsed = JSON.parse(responseText);

      if (!Array.isArray(parsed)) {
        Logger.log(` Invalid response format on page ${page}`);
        break;
      }

      if (parsed.length === 0) {
        hasMorePages = false;
        Logger.log(` Reached end of data at page ${page}`);
        break;
      }

      allOrders = allOrders.concat(parsed);
      Logger.log(`📄 Fetched page ${page}: ${parsed.length} orders (Total: ${allOrders.length})`);
      
      page++;
      
      // Safety check to prevent infinite loops
      if (page > CONSTANTS.API.MAX_PAGES) {
        Logger.log(`⚠️ Safety limit reached - stopping at page ${CONSTANTS.API.MAX_PAGES}`);
        break;
      }
      
      // Rate limiting
      Utilities.sleep(CONSTANTS.API.RATE_LIMIT_MS);
      
    } catch (e) {
      Logger.log(` ERROR FETCHING PAGE ${page}: ${e.toString()}`);
      break;
    }
  }

  Logger.log(`📊 Total orders fetched: ${allOrders.length}`);

  if (allOrders.length === 0) {
    SpreadsheetApp.getUi().alert("No orders found for the specified criteria.");
    return;
  }

  const startRow = 2;
  const startCol = 7; // Column G
  sheet.getRange(startRow, startCol, 1000, 25).clearContent();

  // === Enhanced Header Row - All headers in row 1 ===
  const currentDate = Utilities.formatDate(new Date(), Session.getScriptTimeZone(), 'dd-MM-yy');
  const headersRow = [
    'Order ID', 'Date', 'Status', 'Shipping Label',
    'Full Print Label', 'Items (Qty x Name)', 'Items + SKU',
    'Formatted Total', 'Print Label with Codes',
    'First Name', 'Last Name', 'Company', 'Address 1', 'Address 2',
    'City', 'Postcode', 'State', 'Country',
    'Phone', 'Email', 'Time', '', '',              // AA-AB: Empty columns
    currentDate, 'CHECK ORDER', 'PACK ORDER', 'BAG CHECK', 'SEAL ORDER', 'DROPPED TO POST OFFICE', 'SENT AND PHOTO', // AC-AI: Workflow headers
    '', '', '', '', '',                             // AJ-AN: 5 additional empty columns
    'Export URL'                                    // AO (was AK): Export URL
  ];
  sheet.getRange(1, startCol, 1, headersRow.length).setValues([headersRow]);
  sheet.getRange(1, startCol, 1, headersRow.length).setFontWeight('bold').setFontSize(12);

  // Set column widths for various columns
  sheet.setColumnWidth(10, 300); // J - Shipping Label
  sheet.setColumnWidth(11, 420); // K - Full Print Label
  sheet.setColumnWidth(12, 420); // L - Items (Qty x Name)
  sheet.setColumnWidth(13, 540); // M - Items + SKU
  sheet.setColumnWidth(15, 280); // O - Print Label with Codes
  sheet.setColumnWidth(29, 280); // AC - wider for date
  sheet.setColumnWidth(30, 80);  // AD - CHECK ORDER
  sheet.setColumnWidth(31, 80);  // AE - PACK ORDER  
  sheet.setColumnWidth(32, 80);  // AF - BAG CHECK
  sheet.setColumnWidth(33, 80);  // AG - SEAL ORDER
  sheet.setColumnWidth(34, 80);  // AH - DROP TO POST OFFICE
  sheet.setColumnWidth(35, 250); // AI - SENT AND PHOTO
  
  // Apply word wrap and black borders to workflow header row (row 1)
  const workflowRange = sheet.getRange(1, 29, 1, 7); // AC (29) to AI (35)
  workflowRange.setWrap(true);
  workflowRange.setBorder(true, true, true, true, true, true, 'black', SpreadsheetApp.BorderStyle.SOLID);
  
  // Row 1 headers should be horizontal
  workflowRange.setTextRotation(0)
    .setHorizontalAlignment('center')
    .setVerticalAlignment('middle');

  // Freeze row 1 (header row) so it stays visible when scrolling
  sheet.setFrozenRows(1);
  Logger.log(`🧊 Frozen row 1 as header row`);

  let rowIndex = startRow;
  let processedCount = 0;
  let errorCount = 0;

  for (const order of allOrders) {
    try {
      // Enhanced data validation and extraction
      const processedRow = processOrderData(order);
      
      if (processedRow) {
        const dataRange = sheet.getRange(rowIndex, startCol, 1, processedRow.length);
        dataRange.setValues([processedRow]);
        dataRange.setFontSize(12);
        
        // Add processing workflow columns based on shipping location
        addProcessingWorkflowColumns(sheet, rowIndex, startCol, processedRow);
        
        rowIndex++;
        processedCount++;
      } else {
        errorCount++;
        Logger.log(`⚠️ Failed to process order ID: ${order.id || 'Unknown'}`);
      }

    } catch (e) {
      errorCount++;
      Logger.log(`⚠️ Failed to process order at row ${rowIndex}: ${e.toString()}`);
      Logger.log(`Order data: ${JSON.stringify(order).substring(0, 200)}...`);
    }
  }

  const rowsWritten = rowIndex - startRow;
  if (rowsWritten > 0) {
    const dataRange = sheet.getRange(startRow, startCol, rowsWritten, 22); // Updated to include new column
    dataRange.setWrap(true).setHorizontalAlignment('left').setVerticalAlignment('top');
  }

  // Add summary information
  addImportSummary(sheet, processedCount, errorCount, allOrders.length);

  // Export column AC (Filtered Print Labels) to Excel file
  if (processedCount > 0) {
    // First, fix missing CFS items by checking column O
    fixMissingCFSItems(sheet, startRow, processedCount);
    
    // Then export to Excel
    exportColumnACToExcel(sheet, sheetName, startRow, processedCount);
  }

  Logger.log(` Import Complete - Sheet: ${sheetName}`);
  Logger.log(`📊 Processed: ${processedCount}, Errors: ${errorCount}, Total: ${allOrders.length}`);
}

// Function to filter items for postage (only MVG, CFS, MVGEQ, MVGEM)
function filterItemsForPostage(lineItems) {
  const allowedItems = ['MVG', 'CFS', 'MVGEQ', 'MVGEM'];
  
  // Log all items for debugging
  Logger.log(`🔍 Filtering ${lineItems.length} items for postage`);
  lineItems.forEach((item, index) => {
    const sku = safeTrim(item.sku) || '';
    const name = safeTrim(item.name) || '';
    Logger.log(`Item ${index + 1}: SKU="${sku}", Name="${name}"`);
  });
  
  const filteredItems = lineItems.filter(item => {
    const sku = safeTrim(item.sku) || '';
    const name = safeTrim(item.name) || '';
    const skuUpper = sku.toUpperCase();
    const nameUpper = name.toUpperCase();
    
    // Check each allowed item explicitly
    let isAllowed = false;
    let matchReason = '';
    
    for (const allowed of allowedItems) {
      if (skuUpper.includes(allowed) || nameUpper.includes(allowed)) {
        isAllowed = true;
        matchReason = `matches ${allowed}`;
        break;
      }
      // Also check if the name/sku exactly equals the allowed item
      if (skuUpper === allowed || nameUpper === allowed) {
        isAllowed = true;
        matchReason = `exact match ${allowed}`;
        break;
      }
      // Check if name contains just the allowed item as a word
      if (nameUpper.split(/\s+/).includes(allowed)) {
        isAllowed = true;
        matchReason = `word match ${allowed}`;
        break;
      }
    }
    
    // Special debugging for potential CFS items
    if (skuUpper.includes('CFS') || nameUpper.includes('CFS') || 
        sku === 'CFS' || name === 'CFS' ||
        nameUpper.split(/\s+/).includes('CFS')) {
      Logger.log(`🔍 POTENTIAL CFS ITEM: SKU="${sku}", Name="${name}", Included: ${isAllowed}, Reason: ${matchReason}`);
    }
    
    // Log each item's filtering result
    Logger.log(`Filtering: SKU="${sku}", Name="${name}" -> ${isAllowed ? 'INCLUDED' : 'EXCLUDED'} ${matchReason ? `(${matchReason})` : ''}`);
    
    return isAllowed;
  });
  
  Logger.log(` Filtered result: ${filteredItems.length} items included for postage`);
  filteredItems.forEach((item, index) => {
    Logger.log(`Included item ${index + 1}: SKU="${item.sku}", Name="${item.name}"`);
  });
  
  return filteredItems;
}

// New function to process individual order data with enhanced validation
function processOrderData(order) {
  try {
    // Validate essential order data
    if (!order || !order.id) {
      Logger.log(' Invalid order: missing ID');
      return null;
    }

    // Safe date processing
    let orderDate, formattedDate, formattedTime;
    try {
      orderDate = new Date(order.date_created);
      if (isNaN(orderDate.getTime())) {
        throw new Error('Invalid date');
      }
      formattedDate = Utilities.formatDate(orderDate, Session.getScriptTimeZone(), 'dd-MM-yyyy');
      formattedTime = Utilities.formatDate(orderDate, Session.getScriptTimeZone(), 'HH:mm:ss');
    } catch (e) {
      Logger.log(`⚠️ Date processing error for order ${order.id}: ${e.toString()}`);
      formattedDate = 'Invalid Date';
      formattedTime = 'Invalid Time';
    }

    // Enhanced shipping data extraction with null safety
    const shipping = order.shipping || {};
    const billing = order.billing || {};
    
    const shippingParts = [
      safeStringConcatenation(shipping.first_name, shipping.last_name),
      safeTrim(shipping.company),
      safeTrim(shipping.address_1),
      safeTrim(shipping.address_2),
      safeStringConcatenation(shipping.city, shipping.postcode, ' ')
    ];

    // Enhanced state and country handling
    const stateCountry = [];
    if (safeTrim(shipping.state)) {
      stateCountry.push(safeTrim(shipping.state));
    }
    if (safeTrim(shipping.country)) {
      const fullCountryName = getFullCountryName(shipping.country);
      stateCountry.push(fullCountryName);
    }

    if (stateCountry.length > 0) {
      shippingParts.push(stateCountry.join(', '));
    }

    // Filter out empty parts and join
    const shippingLabel = shippingParts
      .filter(part => part && part.trim() && part.trim() !== ' ')
      .join('\n');

    // Enhanced line items processing
    const lineItems = order.line_items || [];
    const itemsCombined = lineItems.map(item => {
      const quantity = item.quantity || 0;
      const name = safeTrim(item.name) || 'Unknown Item';
      return `${quantity} x ${name}`;
    }).join('\n');

    const itemsWithSKU = lineItems.map(item => {
      const name = safeTrim(item.name) || 'Unknown Item';
      const sku = safeTrim(item.sku) || 'No SKU';
      return `${name} - ${sku}`;
    }).join('\n');

    // Filter items for postage (only physical items: MVG, CFS, MVGEQ, MVGEM)
    const filteredItems = filterItemsForPostage(lineItems);
    const filteredItemsCombined = filteredItems.map(item => {
      const quantity = item.quantity || 0;
      const name = safeTrim(item.name) || 'Unknown Item';
      return `${quantity} x ${name}`;
    }).join('\n');
    
    // Log the filtered items result for debugging
    Logger.log(`📦 Order ${order.id}: Filtered items combined: "${filteredItemsCombined}"`);

    // Create filtered print label with only physical items
    const filteredPrintLabelWithCodes = createPrintLabelWithCodes(
      shippingLabel, 
      safeTrim(billing.phone) || '', 
      safeTrim(billing.email) || '', 
      filteredItemsCombined
    );
    
    // Log the final filtered print label
    Logger.log(`🏷️ Order ${order.id}: Filtered print label: "${filteredPrintLabelWithCodes}"`);

    // Enhanced currency and total processing
    const currency = order.currency || 'USD';
    const total = parseFloat(order.total) || 0;
    const currencySymbol = getCurrencySymbol(currency);
    const formattedTotal = `${currencySymbol}${total.toFixed(2)} (${currency})`;

    const fullPrintLabel = `${shippingLabel}\n\n${itemsCombined}`;

    // Create print label with product codes
    const printLabelWithCodes = createPrintLabelWithCodes(
      shippingLabel, 
      safeTrim(billing.phone) || '', 
      safeTrim(billing.email) || '', 
      itemsCombined
    );

    const row = [
      order.id || '',                              // G (7)
      formattedDate,                               // H (8)
      safeTrim(order.status) || '',                // I (9)
      shippingLabel,                               // J (10)
      fullPrintLabel,                              // K (11)
      itemsCombined,                               // L (12)
      itemsWithSKU,                                // M (13)
      formattedTotal,                              // N (14)
      printLabelWithCodes,                         // O (15)
      safeTrim(shipping.first_name) || '',         // P (16)
      safeTrim(shipping.last_name) || '',          // Q (17)
      safeTrim(shipping.company) || '',            // R (18)
      safeTrim(shipping.address_1) || '',          // S (19)
      safeTrim(shipping.address_2) || '',          // T (20)
      safeTrim(shipping.city) || '',               // U (21)
      safeTrim(shipping.postcode) || '',           // V (22)
      safeTrim(shipping.state) || '',              // W (23)
      getFullCountryName(shipping.country || ''),  // X (24)
      safeTrim(billing.phone) || '',               // Y (25)
      safeTrim(billing.email) || '',               // Z (26)
      formattedTime,                               // AA (27)
      '',                                          // AB (28)
      filteredPrintLabelWithCodes,                 // AC (29) - Filtered Print Label for shipping
      '', '', '', '', '',                          // AD-AH (30-34) - 5 additional empty columns
      filteredPrintLabelWithCodes,                 // AI (35) - Filtered items for postage
      '', '', '', '', ''                           // AJ-AN (36-40) - 5 additional empty columns after AJ
    ];

    return row;

  } catch (e) {
    Logger.log(` Error processing order ${order.id || 'Unknown'}: ${e.toString()}`);
    return null;
  }
}

// Function to add processing workflow columns based on shipping location
function addProcessingWorkflowColumns(sheet, rowIndex, startCol, processedRow) {
  const workflowStartCol = 29; // AC column (fixed position)
  const printLabelWithCodes = processedRow[22]; // AC column content (Print Label Copy)
  
  // Check if the order contains "Australia" 
  const isAustralian = printLabelWithCodes && printLabelWithCodes.includes('Australia');
  
  // First, check which cells in the workflow area have content and apply formatting
  const workflowRange = sheet.getRange(rowIndex, 29, 1, 7); // AC to AI
  
  if (isAustralian) {
    // DOMESTIC (Australia) - Columns AD, AF, AI
    
    // Column AD (30) - DOMESTIC text
    const domesticText = "DOMESTIC\n(Pink Sticker)";
    const domesticCell = sheet.getRange(rowIndex, workflowStartCol + 1, 1, 1);
    domesticCell.setValue(domesticText)
      .setTextRotation(90)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle')
      .setWrap(true)
      .setFontWeight('bold');
    
    // Column AF (32) - Pink Sticker text  
    const stickerText = "Pink Sticker";
    const stickerCell = sheet.getRange(rowIndex, workflowStartCol + 3, 1, 1);
    stickerCell.setValue(stickerText)
      .setTextRotation(90)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle')
      .setWrap(true);
    
    // Column AI (35) - Checklist for domestic
    const domesticChecklist = "\n   ☐ Photo Taken\n\n   ☐ Put Pink Sticker Below\n    ______________________\n   |                                            |\n   |                                            |\n   |______________________|";
    const checklistCell = sheet.getRange(rowIndex, workflowStartCol + 6, 1, 1);
    checklistCell.setValue(domesticChecklist)
      .setHorizontalAlignment('left')
      .setVerticalAlignment('top')
      .setWrap(true);
      
  } else {
    // INTERNATIONAL (Non-Australia) - Columns AD, AF, AI
    
    // Column AD (30) - INTERNATIONAL text
    const internationalText = "INTERNATIONAL\n(No Pink Sticker)";
    const internationalCell = sheet.getRange(rowIndex, workflowStartCol + 1, 1, 1);
    internationalCell.setValue(internationalText)
      .setTextRotation(90)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle')
      .setWrap(true);
    
    // Column AF (32) - No Sticker text
    const noStickerText = "No Sticker OR\nPlain Bag";
    const noStickerCell = sheet.getRange(rowIndex, workflowStartCol + 3, 1, 1);
    noStickerCell.setValue(noStickerText)
      .setTextRotation(90)
      .setHorizontalAlignment('center')
      .setVerticalAlignment('middle')
      .setWrap(true);
    
    // Column AI (35) - Checklist for international
    const internationalChecklist = "\n   ☐ Photo Taken\n\n   ☐ Correct Bag: NO Pink Sticker";
    const intlChecklistCell = sheet.getRange(rowIndex, workflowStartCol + 6, 1, 1);
    intlChecklistCell.setValue(internationalChecklist)
      .setHorizontalAlignment('left')
      .setVerticalAlignment('top')
      .setWrap(true);
  }
  
  // Apply borders and formatting to the entire row AC-AI (29-35) after all content is set
  // Check if column AC (Print Label Copy) has content to determine if this row needs workflow formatting
  const printLabelCopyCell = sheet.getRange(rowIndex, 29, 1, 1); // AC column
  const printLabelCopyValue = printLabelCopyCell.getValue();
  
  if (printLabelCopyValue && printLabelCopyValue.toString().trim() !== '') {
    // Apply borders to the entire AC-AI range
    const fullRowRange = sheet.getRange(rowIndex, 29, 1, 7); // AC (29) to AI (35)
    fullRowRange.setBorder(true, true, true, true, true, true, 'black', SpreadsheetApp.BorderStyle.SOLID);
    fullRowRange.setWrap(true);
    fullRowRange.setFontSize(12);
    
    // Set specific alignment for column AC (Print Label Copy) - top and left aligned
    const printLabelCopyRange = sheet.getRange(rowIndex, 29, 1, 1); // AC column only
    printLabelCopyRange.setHorizontalAlignment('left');
    printLabelCopyRange.setVerticalAlignment('top');
    
    // Apply bold formatting to domestic orders in columns AD to AI only
    const domesticCheck = sheet.getRange(rowIndex, 30, 1, 1).getValue(); // Column AD
    if (domesticCheck && domesticCheck.toString().includes('DOMESTIC')) {
      // Apply bold to columns AD to AI (30-35) for domestic orders
      const domesticRange = sheet.getRange(rowIndex, 30, 1, 6); // AD (30) to AI (35)
      domesticRange.setFontWeight('bold');
    }
  }
}

// New utility functions for safe data handling
function safeTrim(value) {
  if (value === null || value === undefined) {
    return '';
  }
  return String(value).trim();
}

function safeStringConcatenation(...parts) {
  const separator = parts[parts.length - 1];
  const actualParts = typeof separator === 'string' && parts.length > 2 ? 
    parts.slice(0, -1) : parts;
  const actualSeparator = typeof separator === 'string' && parts.length > 2 ? 
    separator : ' ';
  
  return actualParts
    .filter(part => part !== null && part !== undefined && String(part).trim() !== '')
    .map(part => String(part).trim())
    .join(actualSeparator);
}

// Enhanced createPrintLabelWithCodes function
function createPrintLabelWithCodes(shippingLabel, phone, email, items) {
  // Enhanced country code conversion
  let updatedShippingLabel = enhanceShippingLabelCountries(shippingLabel);
  
  let printLabel = `TO: ${updatedShippingLabel}\nPh: ${phone}\nEmail: ${email}\n\n${items}`;
  
  // Enhanced product code replacements - order matters!
  const replacements = [
    // Specific replacements first (most specific to least specific)
    { from: /MiniVet Guide EMERGENCY EDITION/gi, to: 'MVGEM' },
    { from: /MiniVet Guide Equine Medicine/gi, to: 'MVGEQ' },
    { from: /Complete Flashcards Set/gi, to: 'CFS' },
    // General replacement last
    { from: /MiniVet Guide/gi, to: 'MVG' }
  ];
  
  for (const replacement of replacements) {
    printLabel = printLabel.replace(replacement.from, replacement.to);
  }
  
  return printLabel;
}

// New function to enhance shipping label country processing
function enhanceShippingLabelCountries(shippingLabel) {
  if (!shippingLabel) return '';
  
  const lines = shippingLabel.split('\n');
  if (lines.length === 0) return shippingLabel;
  
  // Process the last line for country conversion
  const lastLineIndex = lines.length - 1;
  const lastLine = lines[lastLineIndex];
  
  if (lastLine.includes(', ')) {
    const parts = lastLine.split(', ');
    if (parts.length >= 2) {
      const lastPart = parts[parts.length - 1];
      const fullCountryName = getFullCountryName(lastPart.trim());
      
      if (fullCountryName !== lastPart.trim()) {
        parts[parts.length - 1] = fullCountryName;
        lines[lastLineIndex] = parts.join(', ');
      }
    }
  } else {
    // Check if the last line is just a country code
    const fullCountryName = getFullCountryName(lastLine.trim());
    if (fullCountryName !== lastLine.trim()) {
      lines[lastLineIndex] = fullCountryName;
    }
  }
  
  return lines.join('\n');
}

// Enhanced getCurrencySymbol function
function getCurrencySymbol(code) {
  const map = {
    USD: '$', AUD: 'A$', CAD: 'CA$', EUR: '€', GBP: '£', 
    NZD: 'NZ$', JPY: '¥', CHF: 'CHF', SEK: 'kr', NOK: 'kr',
    DKK: 'kr', PLN: 'zł', CZK: 'Kč', HUF: 'Ft', BGN: 'лв',
    RON: 'lei', HRK: 'kn', RUB: '₽', CNY: '¥', INR: '₹',
    KRW: '₩', THB: '฿', SGD: 'S$', MYR: 'RM', IDR: 'Rp',
    PHP: '₱', VND: '₫'
  };
  return map[code] || code + ' ';
}


function getFullCountryName(countryCode) {
  const countryMap = {
    'AD': 'Andorra', 'AE': 'United Arab Emirates', 'AF': 'Afghanistan', 'AG': 'Antigua and Barbuda',
    'AI': 'Anguilla', 'AL': 'Albania', 'AM': 'Armenia', 'AO': 'Angola', 'AQ': 'Antarctica',
    'AR': 'Argentina', 'AS': 'American Samoa', 'AT': 'Austria', 'AU': 'Australia', 'AW': 'Aruba',
    'AX': 'Åland Islands', 'AZ': 'Azerbaijan', 'BA': 'Bosnia and Herzegovina', 'BB': 'Barbados',
    'BD': 'Bangladesh', 'BE': 'Belgium', 'BF': 'Burkina Faso', 'BG': 'Bulgaria', 'BH': 'Bahrain',
    'BI': 'Burundi', 'BJ': 'Benin', 'BL': 'Saint Barthélemy', 'BM': 'Bermuda', 'BN': 'Brunei',
    'BO': 'Bolivia', 'BQ': 'Caribbean Netherlands', 'BR': 'Brazil', 'BS': 'Bahamas', 'BT': 'Bhutan',
    'BV': 'Bouvet Island', 'BW': 'Botswana', 'BY': 'Belarus', 'BZ': 'Belize', 'CA': 'Canada',
    'CC': 'Cocos Islands', 'CD': 'Democratic Republic of the Congo', 'CF': 'Central African Republic',
    'CG': 'Republic of the Congo', 'CH': 'Switzerland', 'CI': 'Côte d\'Ivoire', 'CK': 'Cook Islands',
    'CL': 'Chile', 'CM': 'Cameroon', 'CN': 'China', 'CO': 'Colombia', 'CR': 'Costa Rica',
    'CU': 'Cuba', 'CV': 'Cape Verde', 'CW': 'Curaçao', 'CX': 'Christmas Island', 'CY': 'Cyprus',
    'CZ': 'Czech Republic', 'DE': 'Germany', 'DJ': 'Djibouti', 'DK': 'Denmark', 'DM': 'Dominica',
    'DO': 'Dominican Republic', 'DZ': 'Algeria', 'EC': 'Ecuador', 'EE': 'Estonia', 'EG': 'Egypt',
    'EH': 'Western Sahara', 'ER': 'Eritrea', 'ES': 'Spain', 'ET': 'Ethiopia', 'FI': 'Finland',
    'FJ': 'Fiji', 'FK': 'Falkland Islands', 'FM': 'Micronesia', 'FO': 'Faroe Islands', 'FR': 'France',
    'GA': 'Gabon', 'GB': 'United Kingdom', 'GD': 'Grenada', 'GE': 'Georgia', 'GF': 'French Guiana',
    'GG': 'Guernsey', 'GH': 'Ghana', 'GI': 'Gibraltar', 'GL': 'Greenland', 'GM': 'Gambia',
    'GN': 'Guinea', 'GP': 'Guadeloupe', 'GQ': 'Equatorial Guinea', 'GR': 'Greece', 'GS': 'South Georgia',
    'GT': 'Guatemala', 'GU': 'Guam', 'GW': 'Guinea-Bissau', 'GY': 'Guyana', 'HK': 'Hong Kong',
    'HM': 'Heard Island', 'HN': 'Honduras', 'HR': 'Croatia', 'HT': 'Haiti', 'HU': 'Hungary',
    'ID': 'Indonesia', 'IE': 'Ireland', 'IL': 'Israel', 'IM': 'Isle of Man', 'IN': 'India',
    'IO': 'British Indian Ocean Territory', 'IQ': 'Iraq', 'IR': 'Iran', 'IS': 'Iceland',
    'IT': 'Italy', 'JE': 'Jersey', 'JM': 'Jamaica', 'JO': 'Jordan', 'JP': 'Japan',
    'KE': 'Kenya', 'KG': 'Kyrgyzstan', 'KH': 'Cambodia', 'KI': 'Kiribati', 'KM': 'Comoros',
    'KN': 'Saint Kitts and Nevis', 'KP': 'North Korea', 'KR': 'South Korea', 'KW': 'Kuwait',
    'KY': 'Cayman Islands', 'KZ': 'Kazakhstan', 'LA': 'Laos', 'LB': 'Lebanon', 'LC': 'Saint Lucia',
    'LI': 'Liechtenstein', 'LK': 'Sri Lanka', 'LR': 'Liberia', 'LS': 'Lesotho', 'LT': 'Lithuania',
    'LU': 'Luxembourg', 'LV': 'Latvia', 'LY': 'Libya', 'MA': 'Morocco', 'MC': 'Monaco',
    'MD': 'Moldova', 'ME': 'Montenegro', 'MF': 'Saint Martin', 'MG': 'Madagascar', 'MH': 'Marshall Islands',
    'MK': 'North Macedonia', 'ML': 'Mali', 'MM': 'Myanmar', 'MN': 'Mongolia', 'MO': 'Macao',
    'MP': 'Northern Mariana Islands', 'MQ': 'Martinique', 'MR': 'Mauritania', 'MS': 'Montserrat',
    'MT': 'Malta', 'MU': 'Mauritius', 'MV': 'Maldives', 'MW': 'Malawi', 'MX': 'Mexico',
    'MY': 'Malaysia', 'MZ': 'Mozambique', 'NA': 'Namibia', 'NC': 'New Caledonia', 'NE': 'Niger',
    'NF': 'Norfolk Island', 'NG': 'Nigeria', 'NI': 'Nicaragua', 'NL': 'Netherlands', 'NO': 'Norway',
    'NP': 'Nepal', 'NR': 'Nauru', 'NU': 'Niue', 'NZ': 'New Zealand', 'OM': 'Oman',
    'PA': 'Panama', 'PE': 'Peru', 'PF': 'French Polynesia', 'PG': 'Papua New Guinea', 'PH': 'Philippines',
    'PK': 'Pakistan', 'PL': 'Poland', 'PM': 'Saint Pierre and Miquelon', 'PN': 'Pitcairn', 'PR': 'Puerto Rico',
    'PS': 'Palestine', 'PT': 'Portugal', 'PW': 'Palau', 'PY': 'Paraguay', 'QA': 'Qatar',
    'RE': 'Réunion', 'RO': 'Romania', 'RS': 'Serbia', 'RU': 'Russia', 'RW': 'Rwanda',
    'SA': 'Saudi Arabia', 'SB': 'Solomon Islands', 'SC': 'Seychelles', 'SD': 'Sudan', 'SE': 'Sweden',
    'SG': 'Singapore', 'SH': 'Saint Helena', 'SI': 'Slovenia', 'SJ': 'Svalbard and Jan Mayen',
    'SK': 'Slovakia', 'SL': 'Sierra Leone', 'SM': 'San Marino', 'SN': 'Senegal', 'SO': 'Somalia',
    'SR': 'Suriname', 'SS': 'South Sudan', 'ST': 'Sao Tome and Principe', 'SV': 'El Salvador',
    'SX': 'Sint Maarten', 'SY': 'Syria', 'SZ': 'Eswatini', 'TC': 'Turks and Caicos Islands',
    'TD': 'Chad', 'TF': 'French Southern Territories', 'TG': 'Togo', 'TH': 'Thailand',
    'TJ': 'Tajikistan', 'TK': 'Tokelau', 'TL': 'Timor-Leste', 'TM': 'Turkmenistan', 'TN': 'Tunisia',
    'TO': 'Tonga', 'TR': 'Turkey', 'TT': 'Trinidad and Tobago', 'TV': 'Tuvalu', 'TW': 'Taiwan',
    'TZ': 'Tanzania', 'UA': 'Ukraine', 'UG': 'Uganda', 'UM': 'United States Minor Outlying Islands',
    'US': 'United States', 'UY': 'Uruguay', 'UZ': 'Uzbekistan', 'VA': 'Vatican City',
    'VC': 'Saint Vincent and the Grenadines', 'VE': 'Venezuela', 'VG': 'British Virgin Islands',
    'VI': 'U.S. Virgin Islands', 'VN': 'Vietnam', 'VU': 'Vanuatu', 'WF': 'Wallis and Futuna',
    'WS': 'Samoa', 'YE': 'Yemen', 'YT': 'Mayotte', 'ZA': 'South Africa', 'ZM': 'Zambia', 'ZW': 'Zimbabwe'
};

  return countryMap[countryCode] || countryCode;
}


function importOrders_processing_60() {
  fetchWooOrders('processing', 60);
}

function importOrders_failed_60() {
  fetchWooOrders('failed', 60);
}

function importOrders_shipped_30() {
  fetchWooOrders('completed', 30);
}

function importOrders_shipped_60() {
  fetchWooOrders('completed', 60);
}

function importOrders_all_30() {
  fetchWooOrders('any', 30);
}

function importOrders_all_60() {
  fetchWooOrders('any', 60);
}








function pollAllWooCommerceData() {
  const { consumerKey, consumerSecret } = getWooCommerceConfig();
  const baseUrl = 'https://minivetguide.com/wp-json/wc/v3/';
  
  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(consumerKey + ":" + consumerSecret)
  };

  // Create master data sheet
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const now = new Date();
  const timestamp = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd-MM-yy HH:mm');
  const masterSheet = spreadsheet.insertSheet(`WooCommerce Data ${timestamp}`);
  
  let currentRow = 1;

  // All available WooCommerce endpoints
  const endpoints = [
    // Core Data
    { name: 'Orders', endpoint: 'orders', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Products', endpoint: 'products', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Customers', endpoint: 'customers', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    
    // Product Related
    { name: 'Product Categories', endpoint: 'products/categories', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Product Tags', endpoint: 'products/tags', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Product Attributes', endpoint: 'products/attributes', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Product Reviews', endpoint: 'products/reviews', params: `?per_page=${CONSTANTS.API.PER_PAGE}` },
    { name: 'Product Variations', endpoint: 'products/variations', params: '' }, // Requires product ID
    
    // Order Related
    { name: 'Order Notes', endpoint: 'orders/notes', params: '' }, // Requires order ID
    { name: 'Refunds', endpoint: 'refunds', params: '?per_page=100' },
    
    // Coupons & Discounts
    { name: 'Coupons', endpoint: 'coupons', params: '?per_page=100' },
    
    // Shipping & Tax
    { name: 'Shipping Zones', endpoint: 'shipping/zones', params: '' },
    { name: 'Shipping Methods', endpoint: 'shipping_methods', params: '' },
    { name: 'Tax Rates', endpoint: 'taxes', params: '?per_page=100' },
    { name: 'Tax Classes', endpoint: 'taxes/classes', params: '' },
    
    // Payment & Settings
    { name: 'Payment Gateways', endpoint: 'payment_gateways', params: '' },
    { name: 'Settings', endpoint: 'settings', params: '' },
    { name: 'System Status', endpoint: 'system_status', params: '' },
    
    // Reports (Analytics)
    { name: 'Sales Reports', endpoint: 'reports/sales', params: '' },
    { name: 'Top Sellers', endpoint: 'reports/top_sellers', params: '' },
    { name: 'Customer Reports', endpoint: 'reports/customers/totals', params: '' },
    
    // Webhooks
    { name: 'Webhooks', endpoint: 'webhooks', params: '?per_page=100' },
    
    // Data Export
    { name: 'Data Export', endpoint: 'data/continents', params: '' },
    { name: 'Data Countries', endpoint: 'data/countries', params: '' },
    { name: 'Data Currencies', endpoint: 'data/currencies', params: '' }
  ];

  // Poll each endpoint
  for (const ep of endpoints) {
    try {
      Logger.log(`📊 Polling: ${ep.name}`);
      const url = baseUrl + ep.endpoint + ep.params;
      
      const response = UrlFetchApp.fetch(url, { headers: headers, muteHttpExceptions: true });
      const data = JSON.parse(response.getContentText());
      
      if (response.getResponseCode() === 200) {
        // Write section header
        masterSheet.getRange(currentRow, 1).setValue(`=== ${ep.name.toUpperCase()} ===`);
        masterSheet.getRange(currentRow, 1).setFontWeight('bold').setFontSize(14);
        currentRow++;
        
        // Write endpoint info
        masterSheet.getRange(currentRow, 1, 1, 2).setValues([['Endpoint:', ep.endpoint]]);
        masterSheet.getRange(currentRow, 3, 1, 2).setValues([['Records Found:', Array.isArray(data) ? data.length : 1]]);
        currentRow++;
        
        // Write sample data structure
        if (Array.isArray(data) && data.length > 0) {
          const sampleRecord = data[0];
          const keys = Object.keys(sampleRecord);
          
          // Headers
          masterSheet.getRange(currentRow, 2, 1, keys.length).setValues([keys]);
          masterSheet.getRange(currentRow, 2, 1, keys.length).setFontWeight('bold');
          currentRow++;
          
          // Sample data (first 5 records)
          const sampleData = data.slice(0, 5).map(record => 
            keys.map(key => {
              const value = record[key];
              if (typeof value === 'object' && value !== null) {
                return JSON.stringify(value).substring(0, 100) + '...';
              }
              return String(value).substring(0, 100);
            })
          );
          
          if (sampleData.length > 0) {
            masterSheet.getRange(currentRow, 2, sampleData.length, keys.length).setValues(sampleData);
            currentRow += sampleData.length;
          }
        } else if (!Array.isArray(data)) {
          // Single object response
          const keys = Object.keys(data);
          masterSheet.getRange(currentRow, 2, 1, keys.length).setValues([keys]);
          masterSheet.getRange(currentRow, 2, 1, keys.length).setFontWeight('bold');
          currentRow++;
          
          const values = keys.map(key => {
            const value = data[key];
            if (typeof value === 'object' && value !== null) {
              return JSON.stringify(value).substring(0, 100) + '...';
            }
            return String(value).substring(0, 100);
          });
          masterSheet.getRange(currentRow, 2, 1, values.length).setValues([values]);
          currentRow++;
        }
        
        currentRow += 2; // Add spacing
        Logger.log(` ${ep.name}: ${Array.isArray(data) ? data.length : 1} records`);
        
      } else {
        masterSheet.getRange(currentRow, 1, 1, 3).setValues([[` ${ep.name}`, 'ERROR:', response.getResponseCode()]]);
        currentRow++;
        Logger.log(` ${ep.name}: Error ${response.getResponseCode()}`);
      }
      
      Utilities.sleep(1000); // Rate limiting
      
    } catch (error) {
      masterSheet.getRange(currentRow, 1, 1, 3).setValues([[` ${ep.name}`, 'EXCEPTION:', error.toString()]]);
      currentRow++;
      Logger.log(` ${ep.name}: ${error.toString()}`);
    }
  }
  
  // Auto-resize columns
  masterSheet.autoResizeColumns(1, 10);
  
  Logger.log(`🎉 Data polling complete! Check sheet: WooCommerce Data ${timestamp}`);
}

// Specific report generators
function generateSalesAnalyticsReport() {
  // Focused on sales analytics with your current order fetching logic
  fetchDetailedSalesAnalytics('any', 30);
}

function fetchDetailedSalesAnalytics(status, daysBack) {
  const consumerKey = 'ck_12d05c5c3579172edd0ce18474f8aacac18d544d';
  const consumerSecret = 'cs_a61844222eba79f0a49ed79078dc54a8de144be0';
  const baseUrl = 'https://minivetguide.com/wp-json/wc/v3/orders';
  
  const now = new Date();
  const dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd-MM-yy');
  const timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'HH:mm');
  const sheetName = `Sales Analytics ${dateStr} ${timeStr}`;
  
  const spreadsheet = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = spreadsheet.insertSheet(sheetName);

  const dateThreshold = new Date();
  dateThreshold.setDate(dateThreshold.getDate() - daysBack);
  const after = encodeURIComponent(dateThreshold.toISOString());

  let url = `${baseUrl}?per_page=100&after=${after}`;
  if (status !== 'any') {
    url += `&status=${status}`;
  }

  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(consumerKey + ":" + consumerSecret)
  };

  try {
    const response = UrlFetchApp.fetch(url, { headers: headers });
    const orders = JSON.parse(response.getContentText());
    
    // Create comprehensive analytics
    createSalesAnalytics(sheet, orders);
    
  } catch (e) {
    Logger.log(" ERROR: " + e.toString());
  }
}

function createSalesAnalytics(sheet, orders) {
  // Summary Statistics
  const headers = [
    'Metric', 'Value', '', 'Product', 'Quantity', 'Revenue',
    '', 'Country', 'Orders', 'Revenue', '', 'Daily Sales', 'Revenue'
  ];
  
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold');
  
  // Calculate metrics
  const totalOrders = orders.length;
  const totalRevenue = orders.reduce((sum, order) => sum + parseFloat(order.total), 0);
  const avgOrderValue = totalRevenue / totalOrders;
  
  // Product analysis
  const productStats = {};
  const countryStats = {};
  const dailyStats = {};
  
  orders.forEach(order => {
    // Product stats
    order.line_items.forEach(item => {
      const name = item.name;
      if (!productStats[name]) {
        productStats[name] = { quantity: 0, revenue: 0 };
      }
      productStats[name].quantity += item.quantity;
      productStats[name].revenue += parseFloat(item.total);
    });
    
    // Country stats
    const country = getFullCountryName(order.shipping.country || order.billing.country);
    if (!countryStats[country]) {
      countryStats[country] = { orders: 0, revenue: 0 };
    }
    countryStats[country].orders++;
    countryStats[country].revenue += parseFloat(order.total);
    
    // Daily stats
    const date = order.date_created.split('T')[0];
    if (!dailyStats[date]) {
      dailyStats[date] = { orders: 0, revenue: 0 };
    }
    dailyStats[date].orders++;
    dailyStats[date].revenue += parseFloat(order.total);
  });
  
  // Write summary metrics
  let row = 2;
  const summaryData = [
    ['Total Orders', totalOrders],
    ['Total Revenue', `$${totalRevenue.toFixed(2)}`],
    ['Average Order Value', `$${avgOrderValue.toFixed(2)}`],
    ['Unique Customers', new Set(orders.map(o => o.billing.email)).size],
    ['Unique Countries', Object.keys(countryStats).length]
  ];
  
  sheet.getRange(row, 1, summaryData.length, 2).setValues(summaryData);
  
  // Write product stats
  row = 2;
  const sortedProducts = Object.entries(productStats)
    .sort((a, b) => b[1].revenue - a[1].revenue)
    .slice(0, 10);
  
  sortedProducts.forEach(([product, stats]) => {
    sheet.getRange(row, 4, 1, 2).setValues([[product, stats.quantity, `$${stats.revenue.toFixed(2)}`]]);
    row++;
  });
  
  // Write country stats
  row = 2;
  const sortedCountries = Object.entries(countryStats)
    .sort((a, b) => b[1].revenue - a[1].revenue)
    .slice(0, 10);
  
  sortedCountries.forEach(([country, stats]) => {
    sheet.getRange(row, 8, 1, 3).setValues([[country, stats.orders, `$${stats.revenue.toFixed(2)}`]]);
    row++;
  });
  
  // Write daily stats
  row = 2;
  const sortedDays = Object.entries(dailyStats)
    .sort((a, b) => new Date(b[0]) - new Date(a[0]))
    .slice(0, 10);
  
  sortedDays.forEach(([date, stats]) => {
    sheet.getRange(row, 12, 1, 2).setValues([[date, `$${stats.revenue.toFixed(2)}`]]);
    row++;
  });
  
  sheet.autoResizeColumns(1, headers.length);
}










function generateDailySalesDashboard(sheet, timeFrameDays, startDate, endDate) {
  const orders = fetchOrdersInRange(startDate, endDate);
  
  // Headers
  const headers = ['Date', 'Orders', 'Revenue', 'Items Sold', 'Avg Order Value', 'Top Product', 'Top Product Sales'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#4285f4').setFontColor('white');
  
  // Process daily data
  const dailyData = {};
  orders.forEach(order => {
    const date = order.date_created.split('T')[0];
    if (!dailyData[date]) {
      dailyData[date] = {
        orders: 0,
        revenue: 0,
        items: 0,
        products: {}
      };
    }
    
    dailyData[date].orders++;
    dailyData[date].revenue += parseFloat(order.total);
    
    order.line_items.forEach(item => {
      dailyData[date].items += item.quantity;
      dailyData[date].products[item.name] = (dailyData[date].products[item.name] || 0) + item.quantity;
    });
  });
  
  // Sort and populate data
  const sortedDates = Object.keys(dailyData).sort().reverse();
  const data = sortedDates.map(date => {
    const dayData = dailyData[date];
    const topProduct = Object.keys(dayData.products).reduce((a, b) => 
      dayData.products[a] > dayData.products[b] ? a : b, Object.keys(dayData.products)[0]);
    
    return [
      date,
      dayData.orders,
      dayData.revenue.toFixed(2),
      dayData.items,
      (dayData.revenue / dayData.orders).toFixed(2),
      topProduct || 'None',
      dayData.products[topProduct] || 0
    ];
  });
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
  
  // Add summary metrics
  addSummaryMetrics(sheet, data, headers.length, {
    totalOrders: data.reduce((sum, row) => sum + row[1], 0),
    totalRevenue: data.reduce((sum, row) => sum + parseFloat(row[2]), 0),
    totalItems: data.reduce((sum, row) => sum + row[3], 0),
    avgDailyOrders: data.length > 0 ? (data.reduce((sum, row) => sum + row[1], 0) / data.length).toFixed(1) : 0,
    avgDailyRevenue: data.length > 0 ? (data.reduce((sum, row) => sum + parseFloat(row[2]), 0) / data.length).toFixed(2) : 0,
    peakDay: data.length > 0 ? data.reduce((max, row) => parseFloat(row[2]) > parseFloat(max[2]) ? row : max)[0] : 'None'
  });
  
  formatSheet(sheet, data.length + 1);
}




function generateRevenueByProduct(sheet, timeFrameDays, startDate, endDate) {
  const orders = fetchOrdersInRange(startDate, endDate);
  
  const headers = ['Product', 'Units Sold', 'Total Revenue', 'Avg Price', 'Revenue %', 'Orders with Product', 'Conversion Rate'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#34a853').setFontColor('white');
  
  const productData = {};
  let totalRevenue = 0;
  let totalOrders = orders.length;
  
  orders.forEach(order => {
    totalRevenue += parseFloat(order.total);
    
    order.line_items.forEach(item => {
      if (!productData[item.name]) {
        productData[item.name] = {
          units: 0,
          revenue: 0,
          orders: new Set()
        };
      }
      
      productData[item.name].units += item.quantity;
      productData[item.name].revenue += parseFloat(item.total);
      productData[item.name].orders.add(order.id);
    });
  });
  
  const data = Object.keys(productData)
    .map(product => {
      const data = productData[product];
      return [
        product,
        data.units,
        data.revenue.toFixed(2),
        (data.revenue / data.units).toFixed(2),
        ((data.revenue / totalRevenue) * 100).toFixed(1) + '%',
        data.orders.size,
        ((data.orders.size / totalOrders) * 100).toFixed(1) + '%'
      ];
    })
    .sort((a, b) => parseFloat(b[2]) - parseFloat(a[2])); // Sort by revenue desc
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
  
  // Add summary metrics
  addSummaryMetrics(sheet, data, headers.length, {
    totalProducts: data.length,
    totalUnits: data.reduce((sum, row) => sum + row[1], 0),
    totalRevenue: totalRevenue.toFixed(2),
    topProduct: data.length > 0 ? data[0][0] : 'None',
    topProductRevenue: data.length > 0 ? data[0][2] : '0',
    avgRevenuePerProduct: data.length > 0 ? (totalRevenue / data.length).toFixed(2) : '0',
    topProductShare: data.length > 0 ? data[0][4] : '0%'
  });
  
  formatSheet(sheet, data.length + 1);
}







function generateSalesByLocation(sheet, timeFrameDays, startDate, endDate) {
  const orders = fetchOrdersInRange(startDate, endDate);
  
  const headers = ['Country', 'Currency', 'Orders', 'Revenue (Original)', 'Revenue (AUD)', 'Avg Order Value', 'Top Product'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#ff9800').setFontColor('white');
  
  const locationData = {};
  
  orders.forEach(order => {
    const country = getFullCountryName(order.shipping.country || order.billing.country || 'Unknown');
    const currency = order.currency;
    const key = `${country}-${currency}`;
    
    if (!locationData[key]) {
      locationData[key] = {
        country,
        currency,
        orders: 0,
        revenue: 0,
        products: {}
      };
    }
    
    locationData[key].orders++;
    locationData[key].revenue += parseFloat(order.total);
    
    order.line_items.forEach(item => {
      locationData[key].products[item.name] = (locationData[key].products[item.name] || 0) + item.quantity;
    });
  });
  
  const data = Object.values(locationData)
    .map(loc => {
      const topProduct = Object.keys(loc.products).reduce((a, b) => 
        loc.products[a] > loc.products[b] ? a : b, Object.keys(loc.products)[0]);
      
      return [
        loc.country,
        loc.currency,
        loc.orders,
        loc.revenue.toFixed(2),
        (loc.revenue * (CONSTANTS.CURRENCY_RATES[loc.currency] || 1)).toFixed(2),
        (loc.revenue / loc.orders).toFixed(2),
        topProduct || 'None'
      ];
    })
    .sort((a, b) => parseFloat(b[4]) - parseFloat(a[4])); // Sort by AUD revenue
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
  
  // Add summary metrics
  const totalAUDRevenue = data.reduce((sum, row) => sum + parseFloat(row[4]), 0);
  const totalOrders = data.reduce((sum, row) => sum + row[2], 0);
  
  addSummaryMetrics(sheet, data, headers.length, {
    totalCountries: [...new Set(data.map(row => row[0]))].length,
    totalCurrencies: [...new Set(data.map(row => row[1]))].length,
    totalOrders: totalOrders,
    totalRevenueAUD: totalAUDRevenue.toFixed(2),
    topCountry: data.length > 0 ? data[0][0] : 'None',
    topCountryRevenue: data.length > 0 ? data[0][4] : '0',
    avgOrderValue: totalOrders > 0 ? (totalAUDRevenue / totalOrders).toFixed(2) : '0'
  });
  
  formatSheet(sheet, data.length + 1);
}





function generateOrderStatusAnalysis(sheet, timeFrameDays, startDate, endDate) {
  const orders = fetchOrdersInRange(startDate, endDate);
  
  const headers = ['Status', 'Count', 'Revenue', 'Avg Value', 'Percentage', 'Avg Processing Time', 'Success Rate'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#9c27b0').setFontColor('white');
  
  const statusData = {};
  let totalOrders = orders.length;
  let totalRevenue = 0;
  
  orders.forEach(order => {
    const status = order.status;
    totalRevenue += parseFloat(order.total);
    
    if (!statusData[status]) {
      statusData[status] = {
        count: 0,
        revenue: 0,
        processingTimes: []
      };
    }
    
    statusData[status].count++;
    statusData[status].revenue += parseFloat(order.total);
    
    // Calculate processing time if available
    if (order.date_created && order.date_modified) {
      const created = new Date(order.date_created);
      const modified = new Date(order.date_modified);
      const processingHours = (modified - created) / (1000 * 60 * 60);
      statusData[status].processingTimes.push(processingHours);
    }
  });
  
  const data = Object.keys(statusData)
    .map(status => {
      const data = statusData[status];
      const avgProcessingTime = data.processingTimes.length > 0 ? 
        (data.processingTimes.reduce((a, b) => a + b, 0) / data.processingTimes.length).toFixed(1) + 'h' : 'N/A';
      
      let successRate = 'N/A';
      if (status === 'completed') successRate = '100%';
      else if (status === 'processing') successRate = '85%'; // Estimated
      else if (status === 'failed') successRate = '0%';
      
      return [
        status.charAt(0).toUpperCase() + status.slice(1),
        data.count,
        data.revenue.toFixed(2),
        (data.revenue / data.count).toFixed(2),
        ((data.count / totalOrders) * 100).toFixed(1) + '%',
        avgProcessingTime,
        successRate
      ];
    })
    .sort((a, b) => b[1] - a[1]); // Sort by count desc
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
  
  // Add summary metrics
  const completedOrders = statusData['completed'] ? statusData['completed'].count : 0;
  const processingOrders = statusData['processing'] ? statusData['processing'].count : 0;
  const failedOrders = statusData['failed'] ? statusData['failed'].count : 0;
  
  addSummaryMetrics(sheet, data, headers.length, {
    totalOrders: totalOrders,
    completionRate: ((completedOrders / totalOrders) * 100).toFixed(1) + '%',
    processingRate: ((processingOrders / totalOrders) * 100).toFixed(1) + '%',
    failureRate: ((failedOrders / totalOrders) * 100).toFixed(1) + '%',
    totalRevenue: totalRevenue.toFixed(2),
    revenueAtRisk: statusData['failed'] ? statusData['failed'].revenue.toFixed(2) : '0',
    avgOrderValue: (totalRevenue / totalOrders).toFixed(2)
  });
  
  formatSheet(sheet, data.length + 1);
}




function generatePaymentMethodAnalysis(sheet, timeFrameDays, startDate, endDate) {
  const orders = fetchOrdersInRange(startDate, endDate);
  
  const headers = ['Payment Method', 'Orders', 'Revenue', 'Avg Order Value', 'Market Share', 'Success Rate', 'Top Country'];
  sheet.getRange(1, 1, 1, headers.length).setValues([headers]);
  sheet.getRange(1, 1, 1, headers.length).setFontWeight('bold').setBackground('#607d8b').setFontColor('white');
  
  const paymentData = {};
  let totalOrders = orders.length;
  let totalRevenue = 0;
  
  orders.forEach(order => {
    const method = order.payment_method_title || order.payment_method || 'Unknown';
    const country = getFullCountryName(order.shipping.country || order.billing.country || 'Unknown');
    totalRevenue += parseFloat(order.total);
    
    if (!paymentData[method]) {
      paymentData[method] = {
        orders: 0,
        revenue: 0,
        countries: {}
      };
    }
    
    paymentData[method].orders++;
    paymentData[method].revenue += parseFloat(order.total);
    paymentData[method].countries[country] = (paymentData[method].countries[country] || 0) + 1;
  });
  
  const data = Object.keys(paymentData)
    .map(method => {
      const data = paymentData[method];
      const topCountry = Object.keys(data.countries).reduce((a, b) => 
        data.countries[a] > data.countries[b] ? a : b, Object.keys(data.countries)[0]);
      
      // Estimate success rate based on method
      let successRate = '95%'; // Default
      if (method.includes('PayPal')) successRate = '98%';
      if (method.includes('Apple Pay')) successRate = '99%';
      if (method.includes('Credit')) successRate = '92%';
      
      return [
        method,
        data.orders,
        data.revenue.toFixed(2),
        (data.revenue / data.orders).toFixed(2),
        ((data.orders / totalOrders) * 100).toFixed(1) + '%',
        successRate,
        topCountry || 'Unknown'
      ];
    })
    .sort((a, b) => b[1] - a[1]); // Sort by orders desc
  
  if (data.length > 0) {
    sheet.getRange(2, 1, data.length, headers.length).setValues(data);
  }
  
  // Add summary metrics
  addSummaryMetrics(sheet, data, headers.length, {
    totalPaymentMethods: data.length,
    totalOrders: totalOrders,
    totalRevenue: totalRevenue.toFixed(2),
    topPaymentMethod: data.length > 0 ? data[0][0] : 'None',
    topMethodShare: data.length > 0 ? data[0][4] : '0%',
    avgOrderValue: (totalRevenue / totalOrders).toFixed(2),
    estimatedSuccessRate: '95%' // Overall estimated
  });
  
  formatSheet(sheet, data.length + 1);
}


function fetchOrdersInRange(startDate, endDate) {
  const { consumerKey, consumerSecret, baseUrl } = getWooCommerceConfig();
  
  const after = encodeURIComponent(startDate.toISOString());
  const before = encodeURIComponent(endDate.toISOString());
  
  const url = `${baseUrl}?per_page=${CONSTANTS.API.PER_PAGE}&after=${after}&before=${before}`;
  
  const headers = {
    "Authorization": "Basic " + Utilities.base64Encode(consumerKey + ":" + consumerSecret)
  };
  
  try {
    const response = UrlFetchApp.fetch(url, { headers: headers });
    return JSON.parse(response.getContentText());
  } catch (error) {
    Logger.log('Error fetching orders: ' + error.toString());
    return [];
  }
}

function addSummaryMetrics(sheet, data, numCols, metrics) {
  const startRow = data.length + 3;
  
  // Add "SUMMARY METRICS" header
  sheet.getRange(startRow, 1, 1, numCols)
    .merge()
    .setValue('📊 SUMMARY METRICS')
    .setFontWeight('bold')
    .setFontSize(14)
    .setBackground('#f1f3f4')
    .setHorizontalAlignment('center');
  
  // Add metrics
  let row = startRow + 1;
  Object.keys(metrics).forEach(key => {
    const label = key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase());
    sheet.getRange(row, 1).setValue(label + ':').setFontWeight('bold');
    sheet.getRange(row, 2).setValue(metrics[key]);
    row++;
  });
  
  // Format metrics section
  const metricsRange = sheet.getRange(startRow + 1, 1, Object.keys(metrics).length, 2);
  metricsRange.setBorder(true, true, true, true, true, true);
  sheet.getRange(startRow + 1, 1, Object.keys(metrics).length, 1).setBackground('#e8f0fe');
}

function formatSheet(sheet, dataRows) {
  // Auto-resize columns
  sheet.autoResizeColumns(1, sheet.getLastColumn());
  
  // Add borders to data
  if (dataRows > 1) {
    sheet.getRange(1, 1, dataRows, sheet.getLastColumn())
      .setBorder(true, true, true, true, true, true);
  }
  
  // Freeze header row
  sheet.setFrozenRows(1);
}

function addImportSummary(sheet, processedCount, errorCount, totalCount) {
  const startRow = sheet.getLastRow() + 2;
  const numCols = 22; // Updated to include the new column AC
  
  // Add "IMPORT SUMMARY" header
  sheet.getRange(startRow, 1, 1, numCols)
    .merge()
    .setValue('📊 IMPORT SUMMARY')
    .setFontWeight('bold')
    .setFontSize(14)
    .setBackground('#f1f3f4')
    .setHorizontalAlignment('center');
  
  // Calculate success rate
  const successRate = totalCount > 0 ? ((processedCount / totalCount) * 100).toFixed(1) + '%' : '0%';
  const importTime = new Date().toLocaleString();
  
  // Add summary metrics
  const metrics = {
    'Total Orders': totalCount,
    'Successfully Processed': processedCount,
    'Errors': errorCount,
    'Success Rate': successRate,
    'Import Date': importTime
  };
  
  let row = startRow + 1;
  Object.keys(metrics).forEach(key => {
    sheet.getRange(row, 1).setValue(key + ':').setFontWeight('bold');
    sheet.getRange(row, 2).setValue(metrics[key]);
    row++;
  });
  
  // Format summary section
  const summaryRange = sheet.getRange(startRow + 1, 1, Object.keys(metrics).length, 2);
  summaryRange.setBorder(true, true, true, true, true, true);
  sheet.getRange(startRow + 1, 1, Object.keys(metrics).length, 1).setBackground('#e8f0fe');
}

function executeReport(reportType, timeFrameDays, outputType, reportName) {
  const endDate = new Date();
  const startDate = new Date();
  startDate.setDate(startDate.getDate() - timeFrameDays);
  
  let sheet;
  if (outputType === 'new') {
    const now = new Date();
    const dateStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'dd-MM-yy');
    const timeStr = Utilities.formatDate(now, Session.getScriptTimeZone(), 'HH:mm');
    const sheetName = `${reportName} ${timeFrameDays}d ${dateStr} ${timeStr}`;
    sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet(sheetName);
  } else {
    sheet = SpreadsheetApp.getActiveSheet();
    sheet.clear();
  }
  
  // Add report header
  sheet.getRange(1, 1, 1, 7)
    .merge()
    .setValue(`${reportName} - ${timeFrameDays} Days (${Utilities.formatDate(startDate, Session.getScriptTimeZone(), 'dd/MM/yyyy')} to ${Utilities.formatDate(endDate, Session.getScriptTimeZone(), 'dd/MM/yyyy')})`)
    .setFontWeight('bold')
    .setFontSize(16)
    .setBackground('#1a73e8')
    .setFontColor('white')
    .setHorizontalAlignment('center');
  
  // Move data down one row
  const actualStartRow = 3;
  
  switch(reportType) {
    case 'dailySalesDashboard':
      generateDailySalesDashboard(sheet, timeFrameDays, startDate, endDate);
      break;
    case 'revenueByProduct':
      generateRevenueByProduct(sheet, timeFrameDays, startDate, endDate);
      break;
    case 'salesByLocation':
      generateSalesByLocation(sheet, timeFrameDays, startDate, endDate);
      break;
    case 'orderStatusAnalysis':
      generateOrderStatusAnalysis(sheet, timeFrameDays, startDate, endDate);
      break;
    case 'paymentMethodAnalysis':
      generatePaymentMethodAnalysis(sheet, timeFrameDays, startDate, endDate);
      break;
    // Add other cases here...
    default:
      throw new Error('Report type not implemented yet: ' + reportType);
  }
}

// Function to fix missing CFS items by checking column O and updating column AC
function fixMissingCFSItems(sheet, startRow, rowCount) {
  Logger.log(`🔧 Checking for missing CFS items in column AC...`);
  
  for (let row = startRow; row < startRow + rowCount; row++) {
    // Get column O content (Print Label with Codes)
    const columnOContent = sheet.getRange(row, 15, 1, 1).getValue().toString();
    
    // Get column AC content (Filtered Print Label)
    const columnACContent = sheet.getRange(row, 29, 1, 1).getValue().toString();
    
    // Check if column O contains "CFS" but column AC doesn't
    if (columnOContent.includes('CFS') && !columnACContent.includes('CFS')) {
      Logger.log(`🔍 Row ${row}: Found CFS in column O but missing in column AC`);
      
      // Extract CFS line from column O
      const lines = columnOContent.split('\n');
      const cfsLine = lines.find(line => line.trim().includes('CFS'));
      
      if (cfsLine) {
        Logger.log(`📝 Found CFS line: "${cfsLine.trim()}"`);
        
        // Add CFS line to column AC content
        let updatedACContent = columnACContent;
        
        // Find the position after the email line to insert CFS
        const emailLineIndex = updatedACContent.indexOf('@');
        if (emailLineIndex !== -1) {
          const nextLineIndex = updatedACContent.indexOf('\n', emailLineIndex);
          if (nextLineIndex !== -1) {
            // Insert CFS after the email line and blank line
            const beforeCFS = updatedACContent.substring(0, nextLineIndex + 1);
            const afterEmail = updatedACContent.substring(nextLineIndex + 1);
            
            // Add CFS line
            updatedACContent = beforeCFS + '\n' + cfsLine.trim() + afterEmail;
          }
        } else {
          // If no email found, just append CFS at the end of existing items
          updatedACContent = updatedACContent + '\n' + cfsLine.trim();
        }
        
        // Update column AC with the fixed content
        sheet.getRange(row, 29, 1, 1).setValue(updatedACContent);
        Logger.log(` Row ${row}: Added CFS to column AC`);
      }
    }
  }
  
  Logger.log(`🔧 CFS fix completed`);
}

// Function to export column AC (Filtered Print Labels) to Excel file
function exportColumnACToExcel(sheet, sheetName, startRow, rowCount) {
  try {
    Logger.log(`📤 Exporting column AC to Excel file...`);
    
    // Get the data from column AC (column 29) starting from row 10
    const columnACRange = sheet.getRange(startRow, 29, rowCount, 1);
    const columnACValues = columnACRange.getValues();
    
    // Filter out empty values
    const filteredValues = columnACValues.filter(row => row[0] && row[0].toString().trim() !== '');
    
    if (filteredValues.length === 0) {
      Logger.log('⚠️ No filtered print labels found to export');
      return;
    }
    
    // Create a new spreadsheet for export
    const exportSpreadsheet = SpreadsheetApp.create(`${sheetName}_FilteredLabels`);
    const exportSheet = exportSpreadsheet.getActiveSheet();
    
    // Set headers
    exportSheet.getRange(1, 1, 1, 1).setValue('Filtered Print Labels');
    exportSheet.getRange(1, 1, 1, 1).setFontWeight('bold').setFontSize(12);
    
    // Add the filtered data
    if (filteredValues.length > 0) {
      exportSheet.getRange(2, 1, filteredValues.length, 1).setValues(filteredValues);
    }
    
    // Format the export sheet
    exportSheet.setColumnWidth(1, 400);
    exportSheet.getRange(2, 1, filteredValues.length, 1).setWrap(true);
    exportSheet.getRange(2, 1, filteredValues.length, 1).setVerticalAlignment('top');
    exportSheet.getRange(2, 1, filteredValues.length, 1).setHorizontalAlignment('left');
    
    // Get the file ID and create download link
    const fileId = exportSpreadsheet.getId();
    const downloadUrl = `https://docs.google.com/spreadsheets/d/${fileId}/export?format=xlsx`;
    
    Logger.log(` Excel export created: ${exportSpreadsheet.getName()}`);
    Logger.log(`📁 File ID: ${fileId}`);
    Logger.log(`⬇️ Download URL: ${downloadUrl}`);
    Logger.log(`📊 Exported ${filteredValues.length} filtered print labels`);
    Logger.log(`💾 TO SAVE TO C:\\Users\\gpoli\\Documents\\Mvg:`);
    Logger.log(`   1. Click the download URL above`);
    Logger.log(`   2. Save the file to: C:\\Users\\gpoli\\Documents\\Mvg`);
    Logger.log(`   3. Rename if needed to: ${sheetName}_FilteredLabels.xlsx`);
    
    // Save download URL to column AO (37) row 1 only
    sheet.getRange(1, 37, 1, 1).setValue(downloadUrl);
    
  } catch (error) {
    Logger.log(` Error exporting to Excel: ${error.toString()}`);
  }
}
