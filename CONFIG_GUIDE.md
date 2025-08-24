# Configuration Guide 🔧

## API Key Setup

### Method 1: Using config.json (Recommended)

1. **Edit the `config.json` file** in your project root:
```json
{
  "openrouter": {
    "api_key": "sk-or-your-actual-api-key-here",
    "default_model": "openai/gpt-4o"
  },
  "ui": {
    "default_port": 8501,
    "auto_open_browser": true
  },
  "processing": {
    "ocr_confidence_threshold": 0.5,
    "max_file_size_mb": 10
  }
}
```

2. **Replace `sk-or-your-actual-api-key-here`** with your real OpenRouter API key

3. **Restart the app** - the key will be automatically loaded

### Method 2: Using the UI

1. Start the app: `streamlit run app.py`
2. In the sidebar, enter your API key in the text field
3. The key will be used for that session only

### Method 3: Environment Variable

```bash
export OPENROUTER_API_KEY="your-key-here"
```

## Testing with Your Existing Resume

You have test files in the `tests/` folder. Let's test the system:

### 1. Run the Test Script
```bash
python test_with_existing.py
```

This will:
- Analyze your PDF resume
- Generate LaTeX code
- Compare with your existing LaTeX
- Show analysis statistics
- Test AI improvement (if API key is set)

### 2. Manual Testing via UI

1. **Start the app:**
```bash
streamlit run app.py
```

2. **Upload your resume:** Use `tests/data engineer eng.pdf`

3. **Compare results:** Check if the generated LaTeX captures the same content as your `tests/data engineer us.tex`

## Expected Results

Your resume uses **AltaCV class**, which is different from our default class. The generator will:

✅ **Extract all text content accurately**
✅ **Detect sections** (Professional Summary, Experience, etc.)
✅ **Identify contact information**
✅ **Preserve text hierarchy**

⚠️ **Styling differences:** Our generator uses a custom class, yours uses AltaCV

## Improving Results with AI

Once you set up your API key, you can:

1. **Upload your resume**
2. **Click "Analyze Structure"** - AI will analyze the layout
3. **Click "Improve LaTeX Code"** - AI will optimize the output
4. **Provide context:** Tell the AI about your original AltaCV style

### Example AI Prompt:
> "The original resume uses AltaCV class with dark blue headers and specific spacing. Please modify the LaTeX to match that style more closely."

## File Structure After Testing

```
resume_adapter/
├── config.json                    # Your API key and settings
├── tests/
│   ├── data engineer eng.pdf      # Your original resume
│   ├── data engineer us.tex       # Your original LaTeX
│   └── altacv(3).cls              # AltaCV class file
├── output_test/                   # Generated test results
│   ├── generated_resume.tex       # Our generated LaTeX
│   ├── generated_resume.cls       # Our custom class
│   ├── ai_improved_resume.tex     # AI-improved version
│   └── analysis.json              # Detailed analysis data
└── ...
```

## Troubleshooting

### API Key Issues
- Make sure key starts with `sk-or-`
- Check you have credits in your OpenRouter account
- Verify internet connection

### PDF Analysis Issues
- Your PDF might have complex layouts
- Try with a simpler PDF first
- Check the analysis.json for detailed extraction data

### LaTeX Compilation
```bash
# Test compilation of generated files
cd output_test
pdflatex generated_resume.tex

# Test compilation of original files
cd ../tests
pdflatex data\ engineer\ us.tex
```

## Next Steps

1. **Test the system** with your existing files
2. **Set up your API key** in config.json
3. **Compare outputs** and see how close we get
4. **Use AI assistance** to improve the results
5. **Provide feedback** on what works and what doesn't

---

**Ready to test?** Run: `python test_with_existing.py`


