import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AuthService } from '../services/authService';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Select } from '../components/Select';
import { Card } from '../components/Card';
import styles from './Login.module.css';

export const RegisterScreen: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [role, setRole] = useState('employee');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [validationErrors, setValidationErrors] = useState<{
    username?: string;
    email?: string;
    password?: string;
    confirmPassword?: string;
  }>({});

  const validate = (): boolean => {
    const errors: typeof validationErrors = {};

    if (!username.trim()) {
      errors.username = 'Enter username';
    }

    if (!email.trim()) {
      errors.email = 'Enter email';
    } else if (!email.includes('@')) {
      errors.email = 'Enter valid email';
    }

    if (!password.trim()) {
      errors.password = 'Enter password';
    } else if (password.length < 6) {
      errors.password = 'Minimum 6 characters';
    }

    if (!confirmPassword.trim()) {
      errors.confirmPassword = 'Confirm your password';
    } else if (confirmPassword !== password) {
      errors.confirmPassword = 'Passwords do not match';
    }

    setValidationErrors(errors);
    return Object.keys(errors).length === 0;
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    setIsLoading(true);
    setError(null);

    try {
      await AuthService.register({
        username: username.trim(),
        email: email.trim(),
        password: password.trim(),
        role,
      });

      alert('Account created! Please login to continue.');
      navigate('/login');
    } catch (e: any) {
      console.error('Registration error:', e);
      setError(e.message.replace('Error: ', ''));
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <div className={styles.content}>
        <Card>
          <div className={styles.logo}>
            <div className={styles.logoText}>TalentLink</div>
          </div>

          <h1 className={styles.title}>Create Account</h1>
          <p className={styles.subtitle}>Join TalentLink today</p>

          <form className={styles.form} onSubmit={handleRegister}>
            <Input
              label="Username"
              value={username}
              onChange={(val) => {
                setUsername(val);
                setValidationErrors({ ...validationErrors, username: undefined });
              }}
              icon={<span className={styles.icon}>👤</span>}
              placeholder="Username"
              error={validationErrors.username}
              required
            />

            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(val) => {
                setEmail(val);
                setValidationErrors({ ...validationErrors, email: undefined });
              }}
              icon={<span className={styles.icon}>📧</span>}
              placeholder="Email"
              error={validationErrors.email}
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(val) => {
                setPassword(val);
                setValidationErrors({ ...validationErrors, password: undefined });
              }}
              icon={<span className={styles.icon}>🔒</span>}
              placeholder="Password"
              error={validationErrors.password}
              required
            />

            <Input
              label="Confirm Password"
              type="password"
              value={confirmPassword}
              onChange={(val) => {
                setConfirmPassword(val);
                setValidationErrors({ ...validationErrors, confirmPassword: undefined });
              }}
              icon={<span className={styles.icon}>🔒</span>}
              placeholder="Confirm Password"
              error={validationErrors.confirmPassword}
              required
            />

            <Select
              label="I am a..."
              value={role}
              onChange={setRole}
              options={[
                { value: 'employee', label: 'Job Seeker / Employee' },
                { value: 'employer', label: 'Recruiter / Employer' },
              ]}
              icon={<span className={styles.icon}>💼</span>}
            />

            {error && (
              <div className={styles.errorContainer}>
                <span className={styles.errorIcon}>⚠️</span>
                <span className={styles.errorText}>{error}</span>
              </div>
            )}

            <Button type="submit" loading={isLoading} disabled={isLoading}>
              Create Account
            </Button>

            <div className={styles.divider}>
              <div className={styles.dividerLine} />
              <span className={styles.dividerText}>OR</span>
              <div className={styles.dividerLine} />
            </div>

            <Button variant="outlined" onClick={() => navigate('/login')}>
              Already have an account? Sign In
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
};
