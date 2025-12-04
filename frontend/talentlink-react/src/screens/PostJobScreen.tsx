import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Input } from '../components/Input';
import { Button } from '../components/Button';
import { Card } from '../components/Card';
import { JobService } from '../services/jobService';
import { TokenStorage } from '../services/tokenStorage';
import styles from './PostJobScreen.module.css';

const PostJobScreen: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    salary: '',
    skills: '',
  });

  const handleInputChange = (name: string) => (value: string) => {
    setFormData({
      ...formData,
      [name]: value,
    });
  };

  const handleTextareaChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (!formData.title || !formData.description) {
      setError('Job title and description are required');
      return;
    }

    setLoading(true);
    try {
      const userId = TokenStorage.getUserId();
      if (!userId) {
        setError('User not authenticated');
        return;
      }

      const skillsArray = formData.skills
        .split(',')
        .map((s) => s.trim())
        .filter((s) => s.length > 0);

      await JobService.createJob({
        employer_id: userId,
        title: formData.title,
        description: formData.description,
        salary: formData.salary ? parseFloat(formData.salary) : undefined,
        skills: skillsArray,
      });

      // Reset form
      setFormData({
        title: '',
        description: '',
        salary: '',
        skills: '',
      });

      alert('Job posted successfully!');
      navigate('/home');
    } catch (err: any) {
      setError(err.message || 'Failed to post job');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={() => navigate('/home')}>
          ← Back
        </button>
        <h1>Post a Job</h1>
      </div>

      <Card>
        <form onSubmit={handleSubmit} className={styles.form}>
          {error && <div className={styles.error}>{error}</div>}

          <Input
            label="Job Title"
            value={formData.title}
            onChange={handleInputChange('title')}
            placeholder="e.g., Senior Software Engineer"
            required
          />

          <div className={styles.formGroup}>
            <label htmlFor="description">Job Description</label>
            <textarea
              id="description"
              name="description"
              value={formData.description}
              onChange={handleTextareaChange}
              placeholder="Describe the job responsibilities, requirements, and what you're looking for..."
              className={styles.textarea}
              rows={6}
              required
            />
          </div>

          <Input
            label="Salary (Optional)"
            type="number"
            value={formData.salary}
            onChange={handleInputChange('salary')}
            placeholder="e.g., 80000"
          />

          <div className={styles.formGroup}>
            <label htmlFor="skills">Required Skills (Optional)</label>
            <input
              id="skills"
              name="skills"
              value={formData.skills}
              onChange={(e) => handleInputChange('skills')(e.target.value)}
              placeholder="e.g., React, TypeScript, Node.js (comma-separated)"
              className={styles.input}
            />
            <small className={styles.hint}>Separate skills with commas</small>
          </div>

          <div className={styles.buttonGroup}>
            <Button type="button" variant="outlined" onClick={() => navigate('/home')}>
              Cancel
            </Button>
            <Button type="submit" loading={loading}>
              Post Job
            </Button>
          </div>
        </form>
      </Card>
    </div>
  );
};

export default PostJobScreen;
