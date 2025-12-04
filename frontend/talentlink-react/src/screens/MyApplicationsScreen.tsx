import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card } from '../components/Card';
import { JobService } from '../services/jobService';
import { TokenStorage } from '../services/tokenStorage';
import { Job, JobApplication } from '../types/job';
import styles from './MyApplicationsScreen.module.css';

const MyApplicationsScreen: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [applications, setApplications] = useState<JobApplication[]>([]);
  const [jobs, setJobs] = useState<{ [jobId: number]: Job }>({});
  const [error, setError] = useState('');

  useEffect(() => {
    loadApplications();
  }, []);

  const loadApplications = async () => {
    try {
      setLoading(true);
      setError('');
      const userId = TokenStorage.getUserId();
      if (!userId) {
        setError('User not authenticated');
        return;
      }

      // Load employee's applications
      let myApplications: JobApplication[] = [];
      try {
        myApplications = await JobService.getEmployeeApplications(userId);
        setApplications(myApplications);
      } catch (err) {
        console.error('Failed to load applications', err);
        setApplications([]);
        // Don't show error, just empty state
        setLoading(false);
        return;
      }

      // Only load job details if applications exist
      if (myApplications.length === 0) {
        setJobs({});
        setLoading(false);
        return;
      }

      // Load job details for each application
      const jobsMap: { [jobId: number]: Job } = {};
      for (const app of myApplications) {
        if (!jobsMap[app.job_id]) {
          try {
            const job = await JobService.getJob(app.job_id);
            jobsMap[app.job_id] = job;
          } catch (err) {
            console.error(`Failed to load job ${app.job_id}`, err);
          }
        }
      }
      setJobs(jobsMap);
    } catch (err: any) {
      console.error('Error loading applications:', err);
      // Don't show error to user, just log it
      setApplications([]);
      setJobs({});
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadgeClass = (status: string) => {
    switch (status) {
      case 'accepted':
        return styles.statusAccepted;
      case 'rejected':
        return styles.statusRejected;
      default:
        return styles.statusPending;
    }
  };

  if (loading) {
    return (
      <div className={styles.container}>
        <div className={styles.loading}>Loading your applications...</div>
      </div>
    );
  }

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <button className={styles.backButton} onClick={() => navigate('/home')}>
          ← Back
        </button>
        <h1>My Applications</h1>
      </div>

      {error && <div className={styles.error}>{error}</div>}

      {applications.length === 0 ? (
        <Card>
          <div className={styles.empty}>
            <p>You haven't applied to any jobs yet.</p>
            <p>
              <a href="/home" className={styles.link}>
                Browse available jobs
              </a>{' '}
              and start applying!
            </p>
          </div>
        </Card>
      ) : (
        <div className={styles.applicationsList}>
          {applications.map((app) => {
            const job = jobs[app.job_id];
            return (
              <Card key={app.application_id}>
                <div className={styles.applicationCard}>
                  <div className={styles.cardHeader}>
                    <div>
                      <h2>{job ? job.title : `Job #${app.job_id}`}</h2>
                      {job && job.salary && (
                        <p className={styles.salary}>${job.salary.toLocaleString()}</p>
                      )}
                    </div>
                    <span className={`${styles.statusBadge} ${getStatusBadgeClass(app.status)}`}>
                      {app.status}
                    </span>
                  </div>

                  {job && (
                    <>
                      <p className={styles.jobDescription}>{job.description}</p>
                      {job.skills && job.skills.length > 0 && (
                        <div className={styles.skillsContainer}>
                          {job.skills.map((skill, index) => (
                            <span key={index} className={styles.skillBadge}>
                              {skill}
                            </span>
                          ))}
                        </div>
                      )}
                    </>
                  )}

                  <div className={styles.applicationDetails}>
                    <div className={styles.detailRow}>
                      <strong>Applied on:</strong>{' '}
                      {new Date(app.created_at).toLocaleDateString()}
                    </div>
                    <div className={styles.detailRow}>
                      <strong>CV:</strong>{' '}
                      <a
                        href={`http://talentlink.local${app.cv_url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={styles.link}
                      >
                        View my CV
                      </a>
                    </div>
                    {app.portfolio_url && (
                      <div className={styles.detailRow}>
                        <strong>Portfolio:</strong>{' '}
                        <a
                          href={app.portfolio_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className={styles.link}
                        >
                          {app.portfolio_url}
                        </a>
                      </div>
                    )}
                  </div>

                  {app.status === 'accepted' && (
                    <div className={styles.successMessage}>
                      Congratulations! Your application has been accepted.
                    </div>
                  )}
                  {app.status === 'rejected' && (
                    <div className={styles.rejectedMessage}>
                      Unfortunately, your application was not successful this time.
                    </div>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}
    </div>
  );
};

export default MyApplicationsScreen;
