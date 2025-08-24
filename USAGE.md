# Quick Start Guide 🚀

## 1. Installation
```bash
# Install dependencies
pip install -r requirements.txt

# Test setup
python test_setup.py
```

## 2. Get OpenRouter API Key
1. Visit [OpenRouter.ai](https://openrouter.ai)
2. Sign up for an account
3. Navigate to "Keys" section
4. Create a new API key
5. Copy the key (starts with `sk-or-`)

## 3. Run the Application

### Option A: Using the run script
```bash
python run.py
```

### Option B: Direct Streamlit
```bash
streamlit run app.py
```

### Option C: Windows batch file
```cmd
run.bat
```

## 4. Using the Application

1. **Open your browser** to `http://localhost:8501`
2. **Enter API Key** in the sidebar (your OpenRouter key)
3. **Upload Resume** (PDF, PNG, JPG, or DOCX)
4. **Click "Analyze Resume"** to process the file
5. **Review Results** - see detected sections and text blocks
6. **Get AI Help** (optional):
   - Click "Improve LaTeX Code" for optimization
   - Click "Analyze Structure" for insights
7. **Download Files**:
   - Individual `.tex` and `.cls` files
   - Complete ZIP package with documentation

## 5. Compiling LaTeX

After downloading:
```bash
# Place both files in same directory
pdflatex resume.tex
```

**Requirements for compilation:**
- LaTeX distribution (TeX Live, MiKTeX)
- Both `resume.tex` and `resume.cls` in same folder

## 6. Supported File Types

| Type | Extension | Processing Method |
|------|-----------|-------------------|
| PDF | `.pdf` | PyMuPDF text extraction |
| Images | `.png`, `.jpg`, `.jpeg` | EasyOCR + computer vision |
| Word | `.docx` | Direct document parsing |

## 7. AI Models Available

- **OpenAI GPT-4o** (recommended)
- **OpenAI GPT-4 Turbo**
- **Anthropic Claude 3.5 Sonnet**
- **Google Gemini Pro 1.5**
- **Meta Llama 3.1 70B**

## 8. Troubleshooting

### Common Issues

**App won't start:**
```bash
python test_setup.py  # Check dependencies
pip install -r requirements.txt  # Reinstall if needed
```

**OCR not working:**
- Ensure image quality is good
- Try different image format
- Check that EasyOCR installed correctly

**API errors:**
- Verify OpenRouter API key is correct
- Check internet connection
- Ensure you have API credits

**LaTeX compilation errors:**
- Install LaTeX distribution
- Ensure both files are in same directory
- Check for missing LaTeX packages

### Performance Tips

- **For images:** Higher resolution = better OCR
- **For PDFs:** Native PDFs work better than scanned
- **For AI features:** GPT-4o provides best results

## 9. Example Workflow

1. Start with a clean, high-quality resume
2. Upload and analyze
3. Review detected sections for accuracy
4. Use AI to improve LaTeX formatting
5. Download and compile
6. Fine-tune LaTeX code if needed

## 10. Advanced Usage

### Environment Variables
Create `.env` file:
```env
OPENROUTER_API_KEY=your-key-here
DEBUG=True
```

### Custom Configuration
Edit `config.py` for:
- OCR confidence thresholds
- Section classification keywords
- LaTeX styling preferences

---

**Need help?** Check the main README.md or create an issue!


