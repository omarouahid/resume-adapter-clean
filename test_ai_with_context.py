#!/usr/bin/env python3
"""
Test AI improvement with context from the original LaTeX file.
"""

import os
import json
from openrouter_client import OpenRouterClient

def test_ai_with_original_context():
    """Test AI improvement by providing the original LaTeX as context."""
    
    print("🤖 Testing AI with Original LaTeX Context")
    print("=" * 50)
    
    # Load API configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('openrouter', {}).get('api_key', '')
            model = config.get('openrouter', {}).get('default_model', 'openai/gpt-4o')
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return
    
    if not api_key or api_key == 'your-openrouter-api-key-here':
        print("❌ Please set your OpenRouter API key in config.json")
        return
    
    # Read the original LaTeX file
    try:
        with open('tests/data engineer us.tex', 'r', encoding='utf-8') as f:
            original_latex = f.read()
    except Exception as e:
        print(f"❌ Error reading original LaTeX: {e}")
        return
    
    # Read the generated LaTeX
    try:
        with open('output_test/generated_resume.tex', 'r', encoding='utf-8') as f:
            generated_latex = f.read()
    except Exception as e:
        print(f"❌ Error reading generated LaTeX: {e}")
        return
    
    print("✅ Loaded original and generated LaTeX files")
    
    # Create AI client
    client = OpenRouterClient(api_key, model)
    
    # Create a detailed prompt with context
    prompt = f"""
You are a LaTeX expert specializing in resume formatting. I have an original resume written in AltaCV class and a basic generated version. Please improve the generated LaTeX to match the original style and structure as closely as possible.

ORIGINAL RESUME (AltaCV style):
{original_latex[:2000]}... [truncated for brevity]

GENERATED RESUME (basic version):
{generated_latex}

Please create an improved version that:
1. Uses a similar layout and structure to the original
2. Maintains the professional appearance
3. Includes proper section headings
4. Uses appropriate spacing and formatting
5. Captures the same content organization

Return ONLY the improved LaTeX code, no explanations or markdown formatting.
"""
    
    print("🔧 Requesting AI improvement with original context...")
    
    try:
        # Make the request
        response = client._make_request(prompt, max_tokens=3000)
        
        if response and not response.startswith("Error:"):
            # Clean up the response (remove markdown if present)
            improved_latex = response.strip()
            if improved_latex.startswith("```latex"):
                improved_latex = improved_latex.replace("```latex", "").replace("```", "").strip()
            
            # Save the improved version
            output_path = "output_test/ai_improved_with_context.tex"
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(improved_latex)
            
            print(f"✅ AI improved LaTeX with context saved to: {output_path}")
            print(f"📄 Improved LaTeX: {len(improved_latex)} characters")
            
            # Show a preview
            lines = improved_latex.split('\n')
            print("\n📝 Preview (first 20 lines):")
            for i, line in enumerate(lines[:20]):
                print(f"  {i+1:2d}| {line}")
            
            if len(lines) > 20:
                print(f"  ... and {len(lines) - 20} more lines")
            
            return True
            
        else:
            print(f"❌ AI improvement failed: {response}")
            return False
            
    except Exception as e:
        print(f"❌ Error during AI improvement: {e}")
        return False

def compare_all_versions():
    """Compare all three versions of the LaTeX."""
    
    print("\n📊 Comparing All Versions")
    print("=" * 30)
    
    files = [
        ("Original (AltaCV)", "tests/data engineer us.tex"),
        ("Generated (Basic)", "output_test/generated_resume.tex"),
        ("AI Improved", "output_test/ai_improved_resume.tex"),
        ("AI with Context", "output_test/ai_improved_with_context.tex")
    ]
    
    for name, path in files:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            print(f"📄 {name:20}: {len(content):5d} characters, {len(content.split())} lines")
        else:
            print(f"❌ {name:20}: File not found")

def main():
    """Run the enhanced AI test."""
    success = test_ai_with_original_context()
    
    if success:
        compare_all_versions()
        
        print("\n" + "=" * 50)
        print("🎉 Enhanced AI testing complete!")
        print("\n💡 Files generated:")
        print("  • output_test/ai_improved_with_context.tex - AI improved with original context")
        print("  • output_test/analysis.json - Detailed analysis data")
        print("\n🔍 Next steps:")
        print("  1. Review the AI-improved version")
        print("  2. Test compilation: cd output_test && pdflatex ai_improved_with_context.tex")
        print("  3. Use the Streamlit app for interactive improvements")
    else:
        print("\n❌ Enhanced AI testing failed.")

if __name__ == "__main__":
    main()


