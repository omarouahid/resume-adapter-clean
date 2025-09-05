#!/usr/bin/env python3
"""Minimal Flask API server for Resume Adapter.

This backend exposes endpoints that a modern React frontend can call.
It reuses the existing configuration utilities and provides a health
check plus a placeholder analysis endpoint. Additional features should
follow the same pattern and leverage the existing service modules.
"""
import os
import requests
from flask import Flask, request, jsonify
import config
from ats_analyzer import ATSAnalyzer
from template_service import template_service

app = Flask(__name__)

ats_service = ATSAnalyzer()


@app.get('/api/health')
def health():
    """Simple health check endpoint."""
    return jsonify({'status': 'ok'})


@app.get('/api/models')
def models():
    """Return available model identifiers from configuration."""
    return jsonify({'models': config.AVAILABLE_MODELS})


@app.get('/api/templates')
def templates():
    """List available resume templates."""
    return jsonify({'templates': template_service.list_templates()})


@app.post('/api/match-template')
def match_template():
    """Return a template id that best matches the job description."""
    data = request.get_json(force=True)
    job_description = data.get('job_description', '')
    template_id = template_service.match_template(job_description)
    if not template_id:
        return jsonify({'error': 'no templates available'}), 404
    return jsonify({'template_id': template_id})


@app.post('/api/render-template')
def render_template_endpoint():
    """Render a template with optional resume data."""
    data = request.get_json(force=True)
    template_id = data.get('template_id')
    resume_data = data.get('resume_data')
    rendered = template_service.render(template_id, resume_data)
    if not rendered:
        return jsonify({'error': 'invalid template id'}), 400
    return jsonify(rendered)


@app.post('/api/analyze')
def analyze():
    """Placeholder resume analysis endpoint.

    The uploaded file is stored in the configured temporary directory.
    Integration with the real analysis modules should be added here.
    """
    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify({'error': 'no file provided'}), 400

    job_description = request.form.get('job_description', '')
    model = request.form.get('model') or config.DEFAULT_MODEL

    temp_dir = config.get_temp_dir()
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded.filename)
    uploaded.save(file_path)

    # TODO: integrate with resume analysis and critique services
    result = {
        'message': f'received {uploaded.filename}',
        'model': model,
        'job_description': job_description,
        'analysis': {},
    }

    os.remove(file_path)
    return jsonify(result)


@app.post('/api/ats-score')
def ats_score():
    """Basic ATS scoring endpoint using the ATSAnalyzer service."""
    uploaded = request.files.get('file')
    if not uploaded:
        return jsonify({'error': 'no file provided'}), 400

    job_description = request.form.get('job_description', '')

    temp_dir = config.get_temp_dir()
    os.makedirs(temp_dir, exist_ok=True)
    file_path = os.path.join(temp_dir, uploaded.filename)
    uploaded.save(file_path)

    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        text = f.read()

    # Minimal resume structure for ATS analysis
    resume_data = {
        'professional_summary': text,
        'job_experiences': [],
        'skills': [{'skills': text.split()}],
        'contact_info': {}
    }

    score = ats_service.analyze_resume(resume_data, job_description)
    os.remove(file_path)
    return jsonify({'ats_score': score.overall_score, 'breakdown': score.__dict__})


@app.post('/api/enhance')
def enhance():
    """Enhance resume text using OpenRouter."""
    data = request.get_json(force=True)
    text = data.get('text', '')
    model = data.get('model') or config.DEFAULT_MODEL
    api_key = config.get_openrouter_api_key()
    if not api_key:
        return jsonify({'error': 'missing OpenRouter API key'}), 400
    payload = {
        'model': model,
        'messages': [
            {'role': 'system', 'content': 'You improve resume content.'},
            {'role': 'user', 'content': f'Enhance the following resume text while keeping the meaning:\n\n{text}'}
        ]
    }
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    try:
        resp = requests.post('https://openrouter.ai/api/v1/chat/completions', json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
        enhanced = resp.json().get('choices', [{}])[0].get('message', {}).get('content', '')
        return jsonify({'enhanced_text': enhanced})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=config.is_debug_mode())
