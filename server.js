const express = require('express');
const cors = require('cors');
const { exec } = require('child_process');
const fs = require('fs');
const path = require('path');
const { MongoClient } = require('mongodb');

const app = express();
app.use(cors());
app.use(express.json());

const PORT = process.env.PORT || 5000;


const MONGO_URI = process.env.MONGO_URI || "mongodb://erthirukumaran_db_user:Thiru1234@ac-fmw4blu-shard-00-00.l358pfx.mongodb.net:27017/MentionFlow?ssl=true&authSource=admin&directConnection=true";
const client = new MongoClient(MONGO_URI);


app.get('/api/scrape', (req, res) => {
    console.log("📥 Scrape request received...");
    const scriptPath = path.join(__dirname, 'scraper.py');
    
    let pythonCmd = "python"; 
    if (process.env.RENDER) {
        pythonCmd = "python3";
    } else {
       
        const venvPath = fs.existsSync(path.join(__dirname, 'venv')) ? 'venv' : '.venv';
        const venvPython = path.join(__dirname, venvPath, 'Scripts', 'python.exe');
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


app.get('/api/results', async (req, res) => {
    try {
        await client.connect();
        const database = client.db('MentionFlowDB');
        const mentions = database.collection('mentions');
        
        const allData = await mentions.find({}).sort({ extracted_at: -1 }).toArray();
        
        console.log(`📡 Fetched ${allData.length} items from MongoDB Atlas.`);
        res.json(allData);
    } catch (err) {
        console.error("❌ MongoDB Results Error:", err);
        res.status(500).json({ error: "Database fetch failed" });
    }
});


app.get('/api/download-pdf', (req, res) => {
    const reporterPath = path.join(__dirname, 'reporter.py');
    let pythonCmd = process.env.RENDER ? "python3" : "python";
    if (!process.env.RENDER) {
        const venvPath = fs.existsSync(path.join(__dirname, 'venv')) ? 'venv' : '.venv';
        const venvPython = path.join(__dirname, venvPath, 'Scripts', 'python.exe');
        if (fs.existsSync(venvPython)) pythonCmd = `"${venvPython}"`;
    }
    exec(`${pythonCmd} "${reporterPath}"`, (error) => {
        if (error) return res.status(500).send("Error generating PDF");
        const pdfPath = path.join(__dirname, 'MentionFlow_Full_Report.pdf');
        if (fs.existsSync(pdfPath)) res.download(pdfPath);
        else res.status(404).send("PDF not found");
    });
});


app.use(express.static(__dirname));
app.get(/^\/(.*)/, (req, res) => {
    res.sendFile(path.join(__dirname, 'index.html'));
});

app.listen(PORT, () => {
    console.log(`🚀 MentionFlow Live: http://localhost:${PORT}`);
});