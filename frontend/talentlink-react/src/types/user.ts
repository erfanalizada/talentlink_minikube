export enum UserRole {
  EMPLOYEE = 'employee',
  EMPLOYER = 'employer',
}

export interface UserProfile {
  userId: string;
  username: string;
  email: string;
  role: UserRole;
  description?: string;
  phoneNumber?: string;
  secondaryEmail?: string;
  address?: string;
  profilePictureUrl?: string;
  createdAt?: string;
  updatedAt?: string;
}

export interface DecodedToken {
  sub: string;
  preferred_username: string;
  email: string;
  realm_access: {
    roles: string[];
  };
  exp: number;
  iat: number;
}
