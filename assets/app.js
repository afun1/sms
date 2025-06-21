const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const PORT = 3001;

console.log('🚀 Starting Sparky Assets Server...');

// Enable CORS and JSON parsing
app.use(cors());
app.use(express.json());
app.use(express.static(__dirname));
app.use('/uploads', express.static('uploads'));

// Create uploads directory if it doesn't exist
const uploadsDir = 'uploads';
if (!fs.existsSync(uploadsDir)) {
    fs.mkdirSync(uploadsDir, { recursive: true });
    console.log('📁 Created uploads directory');
}

// Configure multer for file uploads
const storage = multer.diskStorage({
    destination: (req, file, cb) => {
        cb(null, 'uploads/');
    },
    filename: (req, file, cb) => {
        const uniqueSuffix = Date.now() + '-' + Math.round(Math.random() * 1E9);
        cb(null, file.fieldname + '-' + uniqueSuffix + path.extname(file.originalname));
    }
});

const upload = multer({
    storage: storage,
    limits: {
        fileSize: 10 * 1024 * 1024 // 10MB limit
    },
    fileFilter: (req, file, cb) => {
        const allowedTypes = /jpeg|jpg|png|gif|mp4|mov|avi|pdf|doc|docx/;
        const extname = allowedTypes.test(path.extname(file.originalname).toLowerCase());
        const mimetype = allowedTypes.test(file.mimetype);
        
        if (mimetype && extname) {
            return cb(null, true);
        } else {
            cb(new Error('Only images, videos, and documents are allowed!'));
        }
    }
});

// Serve the upload page
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, 'uploads.html'));
});

// Upload multiple files
app.post('/upload-multiple', upload.array('files', 10), (req, res) => {
    if (!req.files || req.files.length === 0) {
        return res.status(400).json({ error: 'No files uploaded' });
    }
    
    const fileInfo = req.files.map(file => {
        console.log('📤 File uploaded:', file.filename);
        return {
            filename: file.filename,
            originalname: file.originalname,
            size: file.size,
            url: `http://localhost:${PORT}/uploads/${file.filename}`
        };
    });
    
    res.json({
        success: true,
        files: fileInfo
    });
});

// Get all uploaded files
app.get('/api/files', (req, res) => {
    if (!fs.existsSync(uploadsDir)) {
        return res.json({ files: [] });
    }
    
    fs.readdir(uploadsDir, (err, files) => {
        if (err) {
            return res.status(500).json({ error: 'Unable to read files' });
        }
        
        const fileList = files.map(file => {
            const stats = fs.statSync(path.join(uploadsDir, file));
            return {
                filename: file,
                size: stats.size,
                created: stats.birthtime,
                url: `http://localhost:${PORT}/uploads/${file}`
            };
        });
        
        res.json({ files: fileList });
    });
});

// Delete file
app.delete('/api/files/:filename', (req, res) => {
    const filename = req.params.filename;
    const filePath = path.join(uploadsDir, filename);
    
    fs.unlink(filePath, (err) => {
        if (err) {
            return res.status(404).json({ error: 'File not found' });
        }
        console.log('🗑️ File deleted:', filename);
        res.json({ success: true, message: 'File deleted' });
    });
});

// API status endpoint
app.get('/api/status', (req, res) => {
    res.json({ 
        message: '🎉 Sparky Assets Server is running!',
        port: PORT,
        time: new Date().toISOString(),
        uploadsDir: uploadsDir
    });
});

app.listen(PORT, () => {
    console.log(`✅ Assets server running on http://localhost:${PORT}`);
    console.log('📂 Upload page available at http://localhost:3001');
    console.log('🔗 API status at http://localhost:3001/api/status');
    console.log('🔄 Server is running... Press Ctrl+C to stop');
});

console.log('📝 Server setup complete with upload functionality...');