# DOPPELGANGER STUDIO™ - Environment Setup Guide

## ✅ FIXED: Virtual Environment Issues

### **Problem Solved:**
- Had two conflicting virtual environments (`.venv` and `.venv-1`)
- Consolidated all packages into `.venv` (standard name)
- All required packages now installed and working

---

## 🚀 Quick Start

### **Activate Virtual Environment:**

**Option 1: Use the quick activation script (recommended)**
```powershell
.\activate.ps1
```

**Option 2: Manual activation**
```powershell
.\.venv\Scripts\Activate.ps1
```

### **Verify Installation:**
```powershell
python --version  # Should show Python 3.13.7
pip list          # Show all installed packages
```

---

## 📦 Installed Packages

All packages from `requirements.txt` are installed in `.venv`:

### **AI & LLM:**
- anthropic==0.69.0 (Claude Sonnet 4.5)
- openai==2.1.0 (GPT-4 fallback)

### **Web Scraping & Research:**
- aiohttp==3.12.15 (Async HTTP)
- beautifulsoup4==4.14.2 (HTML parsing)
- Wikipedia-API==0.8.1 (Wikipedia data)

### **Database:**
- pymongo==4.15.2 (MongoDB)
- pinecone-client==6.0.0 (Vector DB)

### **API Framework:**
- fastapi==0.118.0 (Microservices)
- pydantic==2.11.10 (Validation)

### **Testing:**
- pytest==8.4.2
- pytest-asyncio==1.2.0
- pytest-cov==7.0.0
- coverage==7.10.7

### **Code Quality:**
- black==25.9.0 (Formatter)
- flake8==7.3.0 (Linter)
- mypy==1.18.2 (Type checker)

### **Utilities:**
- python-dotenv==1.1.1 (Environment variables)
- httpx==0.28.1 (HTTP client)

---

## 🔧 Common Commands

### **Install New Packages:**
```powershell
# Activate first
.\.venv\Scripts\Activate.ps1

# Install package
pip install package-name

# Update requirements.txt
pip freeze > requirements.txt
```

### **Reinstall All Packages:**
```powershell
pip install -r requirements.txt
```

### **Run Tests:**
```powershell
pytest tests/ -v
pytest tests/ --cov=src --cov-report=html
```

### **Code Quality:**
```powershell
black src/              # Format code
flake8 src/             # Check style
mypy src/               # Type check
```

---

## ⚠️ Troubleshooting

### **"Execution policies" error:**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### **Virtual environment not activating:**
1. Make sure you're in the project root directory
2. Try manual activation: `.\.venv\Scripts\Activate.ps1`
3. Check if Python is installed: `python --version`

### **Packages not found after activation:**
```powershell
# Verify you're in the right venv
echo $VIRTUAL_ENV  # Should show .venv path

# Reinstall if needed
pip install -r requirements.txt
```

### **Old `.venv-1` folder still present:**
- You can safely delete `.venv-1` once you verify `.venv` works
- It's already in `.gitignore` so won't be committed

---

## 📁 Project Structure

```
DOPPELGANGER STUDIO/
├── .venv/                    # ✅ Active virtual environment (use this)
├── .venv-1/                  # ⚠️ Old duplicate (can delete)
├── activate.ps1              # 🚀 Quick activation script
├── requirements.txt          # 📦 All package dependencies
├── src/                      # 💻 Source code
│   ├── services/
│   │   ├── research/         # Phase 2: Research systems
│   │   └── creative/         # Phase 3: Creative intelligence
│   └── utils/
├── tests/                    # 🧪 Test suite (38+ tests)
├── docs/                     # 📚 Documentation
└── README.md
```

---

## ✅ Status: READY TO GO!

Your environment is now properly configured with:
- ✅ Virtual environment working (`.venv`)
- ✅ All 50+ packages installed
- ✅ Python 3.13.7 active
- ✅ Quick activation script ready
- ✅ Requirements.txt updated

**Next steps:**
1. Run `.\activate.ps1` to activate
2. Run `pytest tests/ -v` to verify everything works
3. Start coding! 🎬

---

**DOPPELGANGER STUDIO™ - Ready to create magic!** ✨
