import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';
import { AuthService } from '../services/authService';
import { UserService } from '../services/userService';
import { TokenStorage } from '../services/tokenStorage';
import { DecodedToken, UserRole } from '../types/user';
import { Button } from '../components/Button';
import { Input } from '../components/Input';
import { Card } from '../components/Card';
import styles from './Login.module.css';

export const LoginScreen: React.FC = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!username.trim() || !password.trim()) {
      setError('Please enter username and password');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // Login to Keycloak
      const result = await AuthService.login(username.trim(), password.trim());
      const accessToken = result.access_token;
      const refreshToken = result.refresh_token;
      console.log('Access Token received');

      // Decode JWT to get user info
      const decodedToken = jwtDecode<DecodedToken>(accessToken);
      const userId = decodedToken.sub;
      const userName = decodedToken.preferred_username;
      const email = decodedToken.email;

      // Save tokens for persistence
      TokenStorage.saveTokens(accessToken, refreshToken, userId);
      console.log('Tokens saved to storage');

      // Get user roles from Keycloak token
      const roles = decodedToken.realm_access?.roles || [];

      // Determine user role (employee or employer)
      let userRole = UserRole.EMPLOYEE;
      if (roles.includes('employer')) {
        userRole = UserRole.EMPLOYER;
      }

      console.log(`User ID: ${userId}, Role: ${userRole}`);

      // Try to load existing profile, create if doesn't exist
      try {
        await UserService.loadProfile(userId);
        console.log('Profile loaded successfully');
      } catch (e) {
        console.log('Profile not found, creating new profile...');
        await UserService.createProfile(userId, userName, email, userRole);
        console.log('Profile created successfully');
      }

      // Navigate to home screen
      navigate('/home');
    } catch (e: any) {
      console.error('Login error:', e);
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

          <h1 className={styles.title}>Welcome Back</h1>
          <p className={styles.subtitle}>Sign in to continue</p>

          <form className={styles.form} onSubmit={handleLogin}>
            <Input
              label="Username"
              value={username}
              onChange={setUsername}
              icon={<span className={styles.icon}>👤</span>}
              placeholder="Username"
              required
            />

            <Input
              label="Password"
              type="password"
              value={password}
              onChange={setPassword}
              icon={<span className={styles.icon}>🔒</span>}
              placeholder="Password"
              required
            />

            {error && (
              <div className={styles.errorContainer}>
                <span className={styles.errorIcon}>⚠️</span>
                <span className={styles.errorText}>{error}</span>
              </div>
            )}

            <Button type="submit" loading={isLoading} disabled={isLoading}>
              Sign In
            </Button>

            <div className={styles.divider}>
              <div className={styles.dividerLine} />
              <span className={styles.dividerText}>OR</span>
              <div className={styles.dividerLine} />
            </div>

            <Button variant="outlined" onClick={() => navigate('/register')}>
              Create Account
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
};
