# Resume to LaTeX Generator 📄

A beautiful Streamlit platform that transforms resume files into professional LaTeX code with AI assistance from OpenRouter.

## Features ✨

- **Smart Document Processing**: Support for PDF, PNG, JPG, and DOCX files
- **Advanced OCR**: EasyOCR and TrOCR integration for accurate text extraction
- **Layout Analysis**: Intelligent section detection and text block grouping
- **AI-Powered Optimization**: OpenRouter integration for LaTeX code improvement
- **Professional Styling**: Custom LaTeX class with modern resume formatting
- **Easy Download**: Complete package with documentation and instructions

## Installation 🚀

### Quick Start (Minimal Features)
```bash
git clone <repository-url>
cd resume_adapter
pip install -r requirements-minimal.txt
streamlit run app.py
```

### Standard Installation (Recommended)
```bash
git clone <repository-url>
cd resume_adapter
pip install -r requirements.txt
streamlit run app.py
```

### Full Installation (All Features)
```bash
git clone <repository-url>
cd resume_adapter
pip install -r requirements-full.txt
streamlit run app.py
```

#### Installation Options:

| Requirements File | Features Included | Best For |
|------------------|-------------------|-----------|
| `requirements-minimal.txt` | Core functionality, basic downloads | Testing, lightweight setup |
| `requirements.txt` | Standard features, enhanced downloads | Most users, production |
| `requirements-full.txt` | All features, advanced PDF/image generation | Power users, full capabilities |

#### System Dependencies (for full installation):

**For Advanced PDF Generation:**
- **Ubuntu/Debian:** `sudo apt-get install libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0 wkhtmltopdf`
- **macOS:** `brew install wkhtmltopdf`
- **Windows:** Download wkhtmltopdf installer from official website

**For Image Generation:**
- Chrome/Chromium browser (for Selenium)
- ChromeDriver (auto-installed with webdriver-manager)

## Usage 💡

1. **Start the Application**: Run `streamlit run app.py`
2. **Get OpenRouter API Key**: Sign up at [OpenRouter](https://openrouter.ai) and get your API key
3. **Upload Resume**: Support for PDF, images, and DOCX files
4. **Analyze**: The system will extract text and analyze layout
5. **AI Assistance**: Use AI to improve and optimize the LaTeX code
6. **Download**: Get the complete LaTeX package

## Supported Formats 📁

| Format | Description | OCR Method |
|--------|-------------|------------|
| PDF | Native text extraction | PyMuPDF |
| PNG/JPG | Image-based resumes | EasyOCR/TrOCR |
| DOCX | Word documents | Direct parsing |

## Download Options 📥

The application provides multiple download formats to suit different needs:

### 📦 **ZIP Package**
- Complete HTML + CSS bundle
- Print-optimized version included
- README file with instructions
- Works offline in any browser

### 📄 **PDF Export**
- Browser-based conversion (recommended)
- Server-side generation (weasyprint/pdfkit)
- Print-optimized CSS for perfect formatting
- A4 and Letter paper size support

### 📝 **DOCX Export**
- Microsoft Word compatible format
- ATS-friendly for job applications
- Maintains structure (headings, lists, formatting)
- Editable in Word, Google Docs, and other editors

### 🖼️ **Image Export**
- PNG format with transparent background
- JPG format with white background
- High resolution for portfolios and social media
- Perfect for LinkedIn backgrounds and quick previews

## AI Models Available 🤖

- OpenAI GPT-4o
- OpenAI GPT-4 Turbo  
- Anthropic Claude 3.5 Sonnet
- Google Gemini Pro 1.5
- Meta Llama 3.1 70B

## Project Structure 📂

```
resume_adapter/
├── app.py                 # Main Streamlit application
├── resume_analyzer.py     # Core resume analysis logic
├── openrouter_client.py   # OpenRouter API integration
├── config.py              # Configuration settings
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Configuration ⚙️

You can set environment variables for configuration:

- `OPENROUTER_API_KEY`: Your OpenRouter API key
- `DEBUG`: Enable debug mode (True/False)
- `TEMP_DIR`: Temporary directory for file processing

## Generated LaTeX Structure 📝

The system generates two files:

### resume.tex
```latex
\documentclass[11pt,a4paper,sans]{resume}
\usepackage[left=0.7in,top=0.6in,right=0.7in,bottom=0.6in]{geometry}
% ... document content
```

### resume.cls
Custom LaTeX class with:
- Professional formatting commands
- Responsive layout design
- Color scheme definitions
- Typography optimization

## How It Works 🔧

1. **Document Upload**: File is temporarily stored for processing
2. **Text Extraction**: OCR or direct parsing based on file type
3. **Layout Analysis**: Text blocks are grouped into logical sections
4. **Section Classification**: AI identifies resume sections (header, experience, etc.)
5. **LaTeX Generation**: Creates optimized LaTeX code
6. **AI Enhancement**: Optional improvement with OpenRouter models
7. **Package Creation**: Downloads complete LaTeX project

## Examples 📋

### Input Formats
- `resume.pdf` → Professional PDF resume
- `resume.png` → Scanned resume image  
- `resume.docx` → Word document resume

### Output
- `resume.tex` → Main LaTeX document
- `resume.cls` → Custom formatting class
- `README.md` → Compilation instructions

## Troubleshooting 🔧

### Common Issues

1. **OCR Not Working**
   - Install EasyOCR: `pip install easyocr`
   - Check image quality and resolution

2. **API Errors**
   - Verify OpenRouter API key
   - Check internet connection
   - Ensure sufficient API credits

3. **LaTeX Compilation**
   - Install LaTeX distribution (TeX Live, MiKTeX)
   - Ensure both .tex and .cls files are in same directory
   - Run `pdflatex resume.tex`

### System Requirements

- Python 3.8+
- 2GB+ RAM (for OCR models)
- Internet connection (for AI features)
- LaTeX distribution (for compilation)

## Contributing 🤝

Contributions are welcome! Please feel free to submit a Pull Request.

## License 📄

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments 🙏

- [Streamlit](https://streamlit.io/) for the web framework
- [OpenRouter](https://openrouter.ai/) for AI model access
- [EasyOCR](https://github.com/JaidedAI/EasyOCR) for text recognition
- [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing

---

**Made with ❤️ for developers who love LaTeX resumes**


