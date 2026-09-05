const fs = require('fs');
const path = require('path');

const files = [
  'src/pages/Dashboard.js',
  'src/pages/PlateSearch.js',
  'src/pages/Incidents.js'
];

for (const file of files) {
  let content = fs.readFileSync(file, 'utf8');

  // Wrapper height/gap
  content = content.replace(/flex: 1; overflow-y: auto;/g, 'height: 100%; overflow-y: auto;');
  content = content.replace(/gap: 20px;/g, 'gap: 16px;');
  content = content.replace(/padding: 24px;/g, 'padding: 16px;');

  // KPI fonts and padding
  content = content.replace(/font-size:24px;/g, 'font-size:20px;');
  content = content.replace(/padding: 16px;/g, 'padding: 12px 16px;');
  content = content.replace(/padding: 16px 20px;/g, 'padding: 12px 16px;');
  
  // Icon sizes
  content = content.replace(/width="32" height="32"/g, 'width="28" height="28"');
  content = content.replace(/width="36" height="36"/g, 'width="28" height="28"');

  // Gaps in grids
  content = content.replace(/gap: 16px;/g, 'gap: 12px;'); // might be too aggressive, but let's see. Wait, "gap: 16px" was just replaced above? No, the first one was 20px to 16px.

  // Specific to Dashboard
  if (file.includes('Dashboard.js')) {
    content = content.replace(/min-height: 400px;/g, 'min-height: 0; flex: 1.5;');
    content = content.replace(/height: 180px;/g, 'min-height: 0; flex: 1;');
  }

  // Specific to PlateSearch
  if (file.includes('PlateSearch.js')) {
    content = content.replace(/height: 400px;/g, 'min-height: 0; flex: 1.5;');
  }

  // Specific to Incidents
  if (file.includes('Incidents.js')) {
    content = content.replace(/min-height: 500px;/g, 'min-height: 0; flex: 1;');
  }

  fs.writeFileSync(file, content);
  console.log('Updated', file);
}
