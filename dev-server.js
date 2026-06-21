const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Ensure live-server is installed locally
try {
  require.resolve('live-server');
} catch (e) {
  console.log('Installing live-server development dependency...');
  try {
    execSync('npm install live-server --no-save', { stdio: 'inherit' });
  } catch (err) {
    console.error('Failed to automatically install live-server. Please run "npm install" manually.', err);
    process.exit(1);
  }
}

const liveServer = require('live-server');

const params = {
  port: 8080,
  host: '0.0.0.0',
  root: './',
  open: true,
  wait: 100,
  middleware: [
    function(req, res, next) {
      // Clean URLs middleware
      let urlPath = req.url.split('?')[0]; // Strip query string
      
      // If trailing slash, remove it for standardizing (except for root)
      if (urlPath.length > 1 && urlPath.endsWith('/')) {
        urlPath = urlPath.slice(0, -1);
      }
      
      // Intercept request to brochure.pdf to rebuild it with fresh database values
      if (urlPath === "/assets/brochure.pdf") {
        try {
          console.log('Regenerating brochure PDF with live Supabase metrics...');
          execSync('python3 generate_brochure.py', { stdio: 'inherit' });
        } catch (err) {
          console.error('Failed to regenerate brochure PDF:', err);
        }
      }
      
      if (urlPath !== "/" && !urlPath.includes(".")) {
        const filePath = path.join(__dirname, urlPath + ".html");
        if (fs.existsSync(filePath)) {
          // Rewrite req.url to resolve to the HTML file
          const query = req.url.includes('?') ? '?' + req.url.split('?')[1] : '';
          req.url = urlPath + ".html" + query;
        } else {
          // If the file doesn't exist, rewrite req.url to /404.html
          req.url = "/404.html";
        }
      }
      next();
    }
  ]
};

console.log('Starting Lixten dev server with Clean URLs and 404 routing...');
liveServer.start(params);
