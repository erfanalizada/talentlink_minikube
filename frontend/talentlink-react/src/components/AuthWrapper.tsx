import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { TokenStorage } from '../services/tokenStorage';

interface AuthWrapperProps {
  children: React.ReactNode;
}

export const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = () => {
    const isAuthenticated = TokenStorage.isAuthenticated();
    const userId = TokenStorage.getUserId();

    if (isAuthenticated && userId) {
      // If on login or register page, redirect to home
      if (location.pathname === '/login' || location.pathname === '/register' || location.pathname === '/') {
        navigate('/home', { replace: true });
      }
    } else {
      // If not authenticated and not on login/register, redirect to login
      if (location.pathname !== '/login' && location.pathname !== '/register') {
        navigate('/login', { replace: true });
      }
    }

    setIsChecking(false);
  };

  if (isChecking) {
    return (
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          minHeight: '100vh',
          backgroundColor: '#F8FAFC',
        }}
      >
        <div style={{ color: '#64748B', fontSize: '18px' }}>Loading...</div>
      </div>
    );
  }

  return <>{children}</>;
};
