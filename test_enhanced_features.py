#!/usr/bin/env python3
"""
Test enhanced features: preview, job adaptation, and enhanced generation.
"""

import json
from enhanced_latex_generator import EnhancedLaTeXGenerator
from pdf_compiler import PreviewService
from job_adaptation_service import JobAdaptationService, ResumeImprovementService
from openrouter_client import OpenRouterClient

def test_enhanced_generator():
    """Test the enhanced LaTeX generator."""
    print("🧪 Testing Enhanced LaTeX Generator")
    print("=" * 40)
    
    # Load analysis data
    try:
        with open('output_test/analysis.json', 'r') as f:
            analysis_data = json.load(f)
    except FileNotFoundError:
        print("❌ No analysis data found. Run test_with_existing.py first.")
        return False
    
    try:
        generator = EnhancedLaTeXGenerator()
        
        # Convert sections data to ResumeSection objects (simplified)
        from resume_analyzer import ResumeSection, TextBlock
        
        sections = []
        for section_data in analysis_data.get('sections', []):
            content = []
            for block_data in section_data.get('content', []):
                text_block = TextBlock(
                    text=block_data['text'],
                    x=block_data['x'],
                    y=block_data['y'],
                    width=block_data['width'],
                    height=block_data['height'],
                    font_size=block_data['font_size'],
                    is_bold=block_data['is_bold'],
                    is_italic=block_data['is_italic'],
                    alignment=block_data['alignment']
                )
                content.append(text_block)
            
            section = ResumeSection(
                title=section_data['title'],
                content=content,
                section_type=section_data['section_type'],
                y_position=section_data['y_position']
            )
            sections.append(section)
        
        # Generate enhanced LaTeX
        enhanced_tex, enhanced_cls = generator.generate_exact_recreation(sections, analysis_data)
        
        # Save enhanced version
        with open('output_test/enhanced_resume.tex', 'w', encoding='utf-8') as f:
            f.write(enhanced_tex)
        
        with open('output_test/enhanced_resume.cls', 'w', encoding='utf-8') as f:
            f.write(enhanced_cls)
        
        print("✅ Enhanced LaTeX generated successfully!")
        print(f"📄 Enhanced LaTeX: {len(enhanced_tex)} characters")
        print(f"📁 Saved to: output_test/enhanced_resume.tex")
        
        return True
        
    except Exception as e:
        print(f"❌ Enhanced generation failed: {e}")
        return False

def test_preview_service():
    """Test the PDF preview service."""
    print("\n🧪 Testing Preview Service")
    print("=" * 40)
    
    try:
        preview_service = PreviewService()
        
        # Check LaTeX installation
        latex_status = preview_service.compiler.get_latex_installation_status()
        
        print("🔧 LaTeX Installation Status:")
        if latex_status['latex_available']:
            print(f"✅ LaTeX available (recommended: {latex_status['recommended_engine']})")
        else:
            print("❌ LaTeX not available")
        
        print("\n📋 Engine Status:")
        for engine, available in latex_status['engines'].items():
            status = "✅" if available else "❌"
            print(f"  {status} {engine}")
        
        if latex_status['latex_available']:
            # Test with enhanced LaTeX if available
            try:
                with open('output_test/enhanced_resume.tex', 'r', encoding='utf-8') as f:
                    tex_content = f.read()
                with open('output_test/enhanced_resume.cls', 'r', encoding='utf-8') as f:
                    cls_content = f.read()
            except FileNotFoundError:
                # Fallback to basic version
                with open('output_test/generated_resume.tex', 'r', encoding='utf-8') as f:
                    tex_content = f.read()
                with open('output_test/generated_resume.cls', 'r', encoding='utf-8') as f:
                    cls_content = f.read()
            
            print("\n🔄 Testing PDF compilation...")
            preview_result = preview_service.generate_preview(tex_content, cls_content)
            
            if preview_result['success'] and preview_result['pdf_available']:
                print("✅ PDF compilation successful!")
                
                # Save PDF
                import base64
                pdf_bytes = base64.b64decode(preview_result['pdf_base64'])
                
                with open('output_test/compiled_resume.pdf', 'wb') as f:
                    f.write(pdf_bytes)
                
                print(f"📄 PDF saved to: output_test/compiled_resume.pdf")
                
                if preview_result['preview_image']:
                    print("📸 Preview image generated successfully!")
                
                return True
            else:
                print(f"❌ PDF compilation failed: {preview_result['message']}")
                return False
        else:
            print("⚠️ Skipping PDF test - LaTeX not available")
            return True
            
    except Exception as e:
        print(f"❌ Preview service test failed: {e}")
        return False

def test_job_adaptation():
    """Test job adaptation service."""
    print("\n🧪 Testing Job Adaptation Service")
    print("=" * 40)
    
    # Load API configuration
    try:
        with open('config.json', 'r') as f:
            config = json.load(f)
            api_key = config.get('openrouter', {}).get('api_key', '')
            model = config.get('openrouter', {}).get('default_model', 'openai/gpt-4o')
    except Exception as e:
        print(f"❌ Error loading config: {e}")
        return False
    
    if not api_key or api_key == 'your-openrouter-api-key-here':
        print("⚠️ No API key configured. Skipping job adaptation test.")
        return True
    
    try:
        client = OpenRouterClient(api_key, model)
        job_service = JobAdaptationService(client)
        
        # Sample job description
        job_description = """
        Data Engineer Position
        
        We are looking for a senior data engineer with:
        - 5+ years of experience in Python and SQL
        - Experience with AWS, Apache Airflow, and Spark
        - Machine learning pipeline development
        - Real-time data processing with Kafka
        - Docker and Kubernetes experience
        
        Responsibilities:
        - Design and maintain ETL pipelines
        - Optimize data warehouse performance
        - Collaborate with ML engineers
        - Implement data quality monitoring
        """
        
        # Load current LaTeX
        try:
            with open('output_test/enhanced_resume.tex', 'r', encoding='utf-8') as f:
                latex_content = f.read()
        except FileNotFoundError:
            with open('output_test/generated_resume.tex', 'r', encoding='utf-8') as f:
                latex_content = f.read()
        
        print("🎯 Testing job adaptation...")
        adaptation_result = job_service.adapt_resume_to_job(
            latex_content, job_description, "moderate"
        )
        
        if adaptation_result['success']:
            print("✅ Job adaptation successful!")
            
            # Save adapted version
            with open('output_test/job_adapted_resume.tex', 'w', encoding='utf-8') as f:
                f.write(adaptation_result['adapted_latex'])
            
            print(f"📄 Adapted LaTeX: {len(adaptation_result['adapted_latex'])} characters")
            print(f"📁 Saved to: output_test/job_adapted_resume.tex")
            
            print("\n📊 Job Analysis:")
            job_analysis = adaptation_result['job_analysis']
            print(f"  • Technologies: {', '.join(job_analysis['technologies'][:5])}")
            print(f"  • Experience Level: {job_analysis['experience_level']}")
            print(f"  • Role Type: {job_analysis['role_type']}")
            
            return True
        else:
            print(f"❌ Job adaptation failed: {adaptation_result.get('error', 'Unknown error')}")
            return False
            
    except Exception as e:
        print(f"❌ Job adaptation test failed: {e}")
        return False

def main():
    """Run all enhanced feature tests."""
    print("🚀 Testing Enhanced Features")
    print("=" * 50)
    
    results = []
    
    # Test enhanced generator
    results.append(test_enhanced_generator())
    
    # Test preview service
    results.append(test_preview_service())
    
    # Test job adaptation
    results.append(test_job_adaptation())
    
    print("\n" + "=" * 50)
    print("📊 Test Results Summary:")
    
    tests = ["Enhanced Generator", "Preview Service", "Job Adaptation"]
    for i, (test, result) in enumerate(zip(tests, results)):
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {i+1}. {test:20}: {status}")
    
    overall_success = all(results)
    
    if overall_success:
        print("\n🎉 All enhanced features working!")
        print("\n💡 Files generated:")
        print("  • output_test/enhanced_resume.tex - Enhanced LaTeX")
        print("  • output_test/compiled_resume.pdf - Compiled PDF (if LaTeX available)")
        print("  • output_test/job_adapted_resume.tex - Job-adapted version")
        
        print("\n🌐 Your Streamlit app now has:")
        print("  • 👁️ PDF Preview tab")
        print("  • 🎯 Enhanced Generator button")
        print("  • 📦 Job Adaptation feature")
        print("  • 🚀 Direct PDF compilation")
    else:
        print("\n⚠️ Some tests failed, but core functionality should work.")
    
    return overall_success

if __name__ == "__main__":
    main()


