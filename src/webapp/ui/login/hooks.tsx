import React from "react";

import { Account } from "../../casualcms/domain/model";

interface IAuthContext {
  authenticatedUser: Account | null;
  remember: (account: Account, callback: any) => void;
  forget: (callback: any) => void;
}

export const AuthContext = React.createContext<IAuthContext>(null!);

export function useAuth() {
  return React.useContext(AuthContext);
}
