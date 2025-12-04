# TalentLink React Frontend

React version of the TalentLink application with Keycloak authentication.

## Features

- **Authentication**: Login and registration with Keycloak
- **User Profiles**: View and edit user profiles (employee/employer roles)
- **Profile Pictures**: Upload and manage profile pictures
- **Responsive Design**: Modern, gradient-based UI matching the Flutter version
- **Protected Routes**: Secure routing with JWT token validation

## Tech Stack

- React 18
- TypeScript
- React Router v6
- Axios for API calls
- JWT Decode for token handling
- CSS Modules for styling

## Getting Started

### Installation

```bash
npm install
```

### Development

```bash
npm start
```

Runs the app in development mode at [http://localhost:3000](http://localhost:3000).

### Build

```bash
npm run build
```

Builds the app for production to the `build` folder.

## Project Structure

```
src/
├── components/          # Reusable UI components
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Select.tsx
│   ├── Card.tsx
│   ├── ProtectedRoute.tsx
│   └── AuthWrapper.tsx
├── screens/            # Screen components
│   ├── LoginScreen.tsx
│   ├── RegisterScreen.tsx
│   ├── HomeScreen.tsx
│   └── ProfileScreen.tsx
├── services/           # API services
│   ├── authService.ts
│   ├── userService.ts
│   └── tokenStorage.ts
├── types/              # TypeScript types
│   └── user.ts
├── theme/              # Theme configuration
│   └── theme.ts
├── App.tsx             # Main app component
└── index.tsx           # Entry point
```

## API Endpoints

The app connects to the following backend services:

- **Auth Service**: `http://talentlink.local/api/auth`
  - POST `/login` - User login
  - POST `/register` - User registration

- **User Service**: `http://talentlink.local/api/users`
  - GET `/profile/:userId` - Get user profile
  - POST `/profile` - Create user profile
  - PUT `/profile/:userId` - Update user profile
  - POST `/profile/:userId/picture` - Upload profile picture

## Features Matching Flutter Version

All features from the Flutter version have been implemented:

1. ✅ Keycloak authentication
2. ✅ JWT token management
3. ✅ Login screen with validation
4. ✅ Register screen with role selection
5. ✅ Home screen with navigation drawer
6. ✅ Profile screen with edit mode
7. ✅ Profile picture upload
8. ✅ Same gradient design and color scheme
9. ✅ Loading states and error handling
10. ✅ Protected routes

## Color Scheme

The app uses the same vibrant color palette as the Flutter version:

- Primary Blue: `#2563EB`
- Primary Purple: `#7C3AED`
- Success Green: `#10B981`
- Error Red: `#EF4444`
- Background: `#F8FAFC`
