const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;

// 1. Route to Trigger Scraper
app.get('/api/scrape', (req, res) => {
    console.log("📥 Scrape request received...");
    const scriptPath = path.join(__dirname, 'scraper.py');
    
    let pythonCmd = "python"; 
    if (process.env.RENDER) {
        pythonCmd = "python3";
    } else {
        const venvPython = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
        if (fs.existsSync(venvPython)) pythonCmd = `"${venvPython}"`;
    }

    exec(`${pythonCmd} "${scriptPath}"`, (error, stdout, stderr) => {
        if (error) {
            console.error(`❌ Scrape Error: ${stderr}`);
            return res.status(500).json({ error: "Scrape failed", details: stderr });
        }
        console.log("✅ Scraper finished.");
        res.json({ message: "Scrape successful" });
    });
});

// 2. Route to Fetch Results (FIXED: endsWith corrected)
app.get('/api/results', (req, res) => {
    try {
        const files = fs.readdirSync(__dirname).filter(f => 
            typeof f === 'string' && f.startsWith('results_') && f.endsWith('.json')
        );
        
        if (files.length === 0) {
            return res.json([]);
        }

        let allData = [];
        files.forEach(file => {
            try {
                const fileData = fs.readFileSync(path.join(__dirname, file), 'utf8');
                const content = JSON.parse(fileData);
                if (Array.isArray(content)) allData.push(...content);
            } catch (e) {
                console.error(`⚠️ Skipping corrupted file: ${file}`);
            }
        });
        res.json(allData);
    } catch (err) {
        console.error("❌ Results Error:", err);
        res.status(500).json([]);
    }
});

// 3. PDF Route
app.get('/api/download-pdf', (req, res) => {
    const reporterPath = path.join(__dirname, 'reporter.py');
    let pythonCmd = process.env.RENDER ? "python3" : "python";
    if (!process.env.RENDER) {
        const venvPython = path.join(__dirname, 'venv', 'Scripts', 'python.exe');
        if (fs.existsSync(venvPython)) pythonCmd = `"${venvPython}"`;
    }
    exec(`${pythonCmd} "${reporterPath}"`, (error) => {
        if (error) return res.status(500).send("Error generating PDF");
        const pdfPath = path.join(__dirname, 'MentionFlow_Full_Report.pdf');
        if (fs.existsSync(pdfPath)) res.download(pdfPath);
        else res.status(404).send("PDF not found");
    });
});

// 4. Static Assets & Catch-all
app.use(express.static(__dirname));
app.get(/^\/(.*)/, (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 MentionFlow Live: http://localhost:${PORT}`);
});