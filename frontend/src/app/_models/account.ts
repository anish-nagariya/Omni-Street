import { Role } from '.';

export class Account {
  id: string;
  username: string;
  password: string;
  firstName: string;
  lastName: string;
  email: string;
  role: Role;
  jwtToken?: string;
  refreshToken?: string;
}
