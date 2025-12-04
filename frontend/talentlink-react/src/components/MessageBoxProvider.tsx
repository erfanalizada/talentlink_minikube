import React, { createContext, useState, useCallback, ReactNode } from 'react';
import { MessageBox, MessageType } from './MessageBox';

interface MessageBoxContextType {
  showMessage: (message: string, type: MessageType, autoDismiss?: boolean) => void;
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showWarning: (message: string) => void;
  showInfo: (message: string) => void;
}

export const MessageBoxContext = createContext<MessageBoxContextType | undefined>(undefined);

interface MessageState {
  message: string;
  type: MessageType;
  autoDismiss: boolean;
}

export const MessageBoxProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [messageState, setMessageState] = useState<MessageState | null>(null);

  const showMessage = useCallback((message: string, type: MessageType, autoDismiss = true) => {
    setMessageState({ message, type, autoDismiss });
  }, []);

  const showSuccess = useCallback((message: string) => {
    showMessage(message, 'success');
  }, [showMessage]);

  const showError = useCallback((message: string) => {
    showMessage(message, 'error');
  }, [showMessage]);

  const showWarning = useCallback((message: string) => {
    showMessage(message, 'warning');
  }, [showMessage]);

  const showInfo = useCallback((message: string) => {
    showMessage(message, 'info');
  }, [showMessage]);

  const handleClose = useCallback(() => {
    setMessageState(null);
  }, []);

  return (
    <MessageBoxContext.Provider value={{ showMessage, showSuccess, showError, showWarning, showInfo }}>
      {children}
      {messageState && (
        <MessageBox
          message={messageState.message}
          type={messageState.type}
          onClose={handleClose}
          autoDismiss={messageState.autoDismiss}
        />
      )}
    </MessageBoxContext.Provider>
  );
};
