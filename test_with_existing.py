#!/usr/bin/env python3
"""
Test the resume analyzer with existing resume and LaTeX files.
"""

import os
import sys
from pathlib import Path
from resume_analyzer import ResumeAnalyzer
from openrouter_client import OpenRouterClient
import json

def test_with_existing_resume():
    """Test with the existing resume in tests folder."""
    
    print("🧪 Testing Resume Analyzer with Existing Files")
    print("=" * 50)
    
    # Check if test files exist
    pdf_path = Path("tests/data engineer eng.pdf")
    tex_path = Path("tests/data engineer us.tex")
    cls_path = Path("tests/altacv(3).cls")
    
    if not pdf_path.exists():
        print(f"❌ PDF file not found: {pdf_path}")
        return False
    
    if not tex_path.exists():
        print(f"❌ TEX file not found: {tex_path}")
        return False
    
    print(f"✅ Found PDF: {pdf_path}")
    print(f"✅ Found TEX: {tex_path}")
    print(f"✅ Found CLS: {cls_path}")
    
    # Initialize analyzer
    print("\n🔍 Analyzing PDF...")
    analyzer = ResumeAnalyzer()
    
    try:
        # Analyze the PDF
        success, tex_content, cls_content, analysis_data = analyzer.analyze(str(pdf_path))
        
        if not success:
            print("❌ Failed to analyze PDF")
            return False
        
        print("✅ PDF analysis successful!")
        print(f"📊 Detected {len(analysis_data['sections'])} sections")
        print(f"📝 Extracted {len(analysis_data['text_blocks'])} text blocks")
        
        # Show detected sections
        print("\n📋 Detected Sections:")
        for section in analysis_data['sections']:
            print(f"  • {section['section_type'].title()}: {section['title']}")
        
        # Save generated files
        output_dir = "output_test"
        os.makedirs(output_dir, exist_ok=True)
        
        generated_tex = os.path.join(output_dir, "generated_resume.tex")
        generated_cls = os.path.join(output_dir, "generated_resume.cls")
        analysis_json = os.path.join(output_dir, "analysis.json")
        
        with open(generated_tex, 'w', encoding='utf-8') as f:
            f.write(tex_content)
        
        with open(generated_cls, 'w', encoding='utf-8') as f:
            f.write(cls_content)
        
        with open(analysis_json, 'w', encoding='utf-8') as f:
            json.dump(analysis_data, f, indent=2, ensure_ascii=False)
        
        print(f"\n📁 Generated files saved to: {output_dir}/")
        print(f"  • {generated_tex}")
        print(f"  • {generated_cls}")
        print(f"  • {analysis_json}")
        
        # Compare with original
        print("\n🔍 Comparison with Original LaTeX:")
        with open(tex_path, 'r', encoding='utf-8') as f:
            original_tex = f.read()
        
        print(f"📄 Original LaTeX: {len(original_tex)} characters")
        print(f"📄 Generated LaTeX: {len(tex_content)} characters")
        
        # Basic content comparison
        original_lines = original_tex.lower().split('\n')
        generated_lines = tex_content.lower().split('\n')
        
        # Look for key elements
        name_in_original = any('ouahid omar' in line for line in original_lines)
        name_in_generated = any('ouahid omar' in line.lower() for line in generated_lines)
        
        print(f"📝 Name detected in original: {name_in_original}")
        print(f"📝 Name detected in generated: {name_in_generated}")
        
        # Show some statistics
        print("\n📊 Analysis Statistics:")
        print(f"  • Page width: {analyzer.processors['.pdf'].page_width}")
        print(f"  • Page height: {analyzer.processors['.pdf'].page_height}")
        print(f"  • Average font size: {sum(block['font_size'] for block in analysis_data['text_blocks']) / len(analysis_data['text_blocks']):.1f}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        return False

def test_with_ai_improvement():
    """Test AI improvement if API key is available."""
    
    print("\n🤖 Testing AI Improvement...")
    
    # Try to load API key from config
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r') as f:
                config = json.load(f)
                api_key = config.get('openrouter', {}).get('api_key', '')
                
                if api_key and api_key != 'your-openrouter-api-key-here':
                    print("✅ API key found in config.json")
                    
                    # Load generated content
                    generated_tex_path = "output_test/generated_resume.tex"
                    if os.path.exists(generated_tex_path):
                        with open(generated_tex_path, 'r', encoding='utf-8') as f:
                            tex_content = f.read()
                        
                        # Test AI client
                        client = OpenRouterClient(api_key)
                        print("🔧 Requesting AI improvement...")
                        
                        try:
                            improved_tex = client.improve_latex_code(tex_content, "")
                            
                            if improved_tex and not improved_tex.startswith("Error:"):
                                improved_path = "output_test/ai_improved_resume.tex"
                                with open(improved_path, 'w', encoding='utf-8') as f:
                                    f.write(improved_tex)
                                
                                print(f"✅ AI improved LaTeX saved to: {improved_path}")
                                print(f"📄 Improved LaTeX: {len(improved_tex)} characters")
                                return True
                            else:
                                print(f"❌ AI improvement failed: {improved_tex}")
                                
                        except Exception as e:
                            print(f"❌ AI improvement error: {e}")
                    else:
                        print(f"❌ Generated LaTeX not found: {generated_tex_path}")
                else:
                    print("⚠️  No valid API key in config.json")
    except Exception as e:
        print(f"⚠️  Could not test AI improvement: {e}")
    
    return False

def main():
    """Run all tests."""
    
    success = test_with_existing_resume()
    
    if success:
        test_with_ai_improvement()
        
        print("\n" + "=" * 50)
        print("🎉 Testing complete!")
        print("\n💡 Next steps:")
        print("  1. Check output_test/ folder for generated files")
        print("  2. Compare with your original LaTeX")
        print("  3. Compile with: pdflatex generated_resume.tex")
        print("  4. Add your OpenRouter API key to config.json for AI features")
        
    else:
        print("\n❌ Testing failed. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()


