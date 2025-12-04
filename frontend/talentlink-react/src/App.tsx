import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { LoginScreen } from './screens/LoginScreen';
import { RegisterScreen } from './screens/RegisterScreen';
import { HomeScreen } from './screens/HomeScreen';
import { ProfileScreen } from './screens/ProfileScreen';
import PostJobScreen from './screens/PostJobScreen';
import ApplicationsScreen from './screens/ApplicationsScreen';
import MyApplicationsScreen from './screens/MyApplicationsScreen';
import { ProtectedRoute } from './components/ProtectedRoute';
import { AuthWrapper } from './components/AuthWrapper';
import { MessageBoxProvider } from './components/MessageBoxProvider';

function App() {
  return (
    <MessageBoxProvider>
      <Router>
        <AuthWrapper>
          <Routes>
            <Route path="/login" element={<LoginScreen />} />
            <Route path="/register" element={<RegisterScreen />} />
            <Route
              path="/home"
              element={
                <ProtectedRoute>
                  <HomeScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/profile"
              element={
                <ProtectedRoute>
                  <ProfileScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/post-job"
              element={
                <ProtectedRoute>
                  <PostJobScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/applications"
              element={
                <ProtectedRoute>
                  <ApplicationsScreen />
                </ProtectedRoute>
              }
            />
            <Route
              path="/my-applications"
              element={
                <ProtectedRoute>
                  <MyApplicationsScreen />
                </ProtectedRoute>
              }
            />
            <Route path="/" element={<Navigate to="/login" replace />} />
          </Routes>
        </AuthWrapper>
      </Router>
    </MessageBoxProvider>
  );
}

export default App;
