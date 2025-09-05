import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './App.css';

export default function App() {
  const [file, setFile] = useState(null);
  const [jobDescription, setJobDescription] = useState('');
  const [models, setModels] = useState([]);
  const [model, setModel] = useState('');
  const [result, setResult] = useState(null);
  const [atsResult, setAtsResult] = useState(null);
  const [templates, setTemplates] = useState([]);
  const [template, setTemplate] = useState('');
  const [preview, setPreview] = useState('');
  const [loading, setLoading] = useState(false);
  const [resumeText, setResumeText] = useState('');

  useEffect(() => {
    const loadModels = async () => {
      try {
        const res = await axios.get('/api/models');
        setModels(res.data.models);
        setModel(res.data.models[0] || '');
      } catch (err) {
        console.error(err);
      }
    };
    loadModels();
    const loadTemplates = async () => {
      try {
        const res = await axios.get('/api/templates');
        setTemplates(res.data.templates);
        setTemplate(res.data.templates[0]?.id || '');
      } catch (err) {
        console.error(err);
      }
    };
    loadTemplates();
  }, []);

  const submit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const data = new FormData();
      data.append('file', file);
      data.append('job_description', jobDescription);
      if (model) data.append('model', model);
      const res = await axios.post('/api/analyze', data);
      setResult(res.data);
    } catch (err) {
      setResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const fetchAts = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    try {
      const data = new FormData();
      data.append('file', file);
      data.append('job_description', jobDescription);
      const res = await axios.post('/api/ats-score', data);
      setAtsResult(res.data);
    } catch (err) {
      setAtsResult({ error: err.message });
    } finally {
      setLoading(false);
    }
  };

  const previewTemplate = async () => {
    if (!template) return;
    try {
      const res = await axios.post('/api/render-template', {
        template_id: template,
        resume_data: { professional_summary: resumeText },
      });
      setPreview(res.data.html);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    previewTemplate();
  }, [template, resumeText]);

  const enhance = async () => {
    if (!resumeText) return;
    try {
      const res = await axios.post('/api/enhance', { text: resumeText, model });
      setResumeText(res.data.enhanced_text || resumeText);
    } catch (err) {
      console.error(err);
    }
  };

  const matchTemplate = async () => {
    try {
      const res = await axios.post('/api/match-template', { job_description: jobDescription });
      if (res.data.template_id) setTemplate(res.data.template_id);
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="container">
      <h1>Resume Adapter</h1>
      <div className="layout">
        <div className="form-panel">
          <form onSubmit={submit}>
            <div className="form-group">
              <label htmlFor="file">Resume File</label>
              <input
                id="file"
                type="file"
                onChange={(e) => setFile(e.target.files[0])}
              />
            </div>

            <div className="form-group">
              <label htmlFor="job">Job Description</label>
              <textarea
                id="job"
                rows="4"
                value={jobDescription}
                onChange={(e) => setJobDescription(e.target.value)}
              />
            </div>

            <div className="form-group">
              <label htmlFor="model">Model</label>
              <select
                id="model"
                value={model}
                onChange={(e) => setModel(e.target.value)}
              >
                {models.map((m) => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>

            <div className="form-group">
              <label htmlFor="template">Template</label>
              <select
                id="template"
                value={template}
                onChange={(e) => setTemplate(e.target.value)}
              >
                {templates.map((t) => (
                  <option key={t.id} value={t.id}>{t.name}</option>
                ))}
              </select>
              <button type="button" onClick={matchTemplate}>Match</button>
            </div>

            <div className="button-row">
              <button type="submit" disabled={!file || loading}>
                {loading ? 'Analyzing...' : 'Analyze'}
              </button>
              <button onClick={fetchAts} disabled={!file || loading} type="button">
                {loading ? 'Scoring...' : 'ATS Score'}
              </button>
            </div>
          </form>

          <div className="editor">
            <label htmlFor="resumeText">Resume Text</label>
            <textarea
              id="resumeText"
              rows="10"
              value={resumeText}
              onChange={(e) => setResumeText(e.target.value)}
            />
            <div className="button-row">
              <button type="button" onClick={enhance} disabled={!resumeText}>Enhance</button>
            </div>
          </div>

          {result && <pre>{JSON.stringify(result, null, 2)}</pre>}
          {atsResult && <pre>{JSON.stringify(atsResult, null, 2)}</pre>}
        </div>

        <div className="preview-panel" dangerouslySetInnerHTML={{ __html: preview }} />
      </div>
    </div>
  );
}
