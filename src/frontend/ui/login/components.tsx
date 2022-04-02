import React from "react";
import { Box, Heading, Form, Button } from "react-bulma-components";
const { Control, Field, Label, Input } = Form;
import { useNavigate } from "react-router-dom";

import { Account } from "../../casualcms/domain/model";
import { AppContext } from "../../config";

interface AuthContextType {
  authenticatedUser: Account | null;
  loadAuthenticatedUser: (callback: any) => Promise<void>;
  remember: (account: Account, callback: any) => void;
  forget: (callback: any) => void;
}

let AuthContext = React.createContext<AuthContextType>(null!);

function useAuth() {
  return React.useContext(AuthContext);
}

function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  let [authenticatedUser, setUser] = React.useState<Account | null>(null);
  const config = React.useContext(AppContext);
  const loadAuthenticatedUser = async (callback: any) => {
    if (config == null) {
      throw new Error("Fatal Error: Unconfigured application");
    }
    const accountResult = await config.uow.account.getCurrent();
    accountResult
      .map((account) => setUser(account))
      .mapErr((err) => setUser(null));
    callback();
  };
  let remember = (account: Account, callback: any) => {
    setUser(account);
    callback();
  };

  let forget = (callback: any) => {
    setUser(null);
    callback();
  };

  let value = { authenticatedUser, loadAuthenticatedUser, remember, forget };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

function RequireAuth({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  let auth = useAuth();
  let navigate = useNavigate();
  const [loading, setLoading] = React.useState<boolean>(false);

  React.useEffect(() => {
    async function loadAuthenticatedUser() {
      auth.loadAuthenticatedUser(() => {
        if (!auth.authenticatedUser) {
          navigate("/admin/login", { replace: true });
        } else {
          setLoading(false);
        }
      });
    }
    loadAuthenticatedUser();
    return function cleanup() {};
  }, []);
  if (loading || !auth.authenticatedUser) {
    return <>Loading...</>;
  }

  return <>{children}</>;
}

function Login() {
  return (
    <Box>
      <Heading>Sign In</Heading>
      <form method="POST">
        <Field>
          <Label>
            Username:
            <Control>
              <Input name="username" placeholder="username" />
            </Control>
          </Label>
        </Field>
        <Field>
          <Label>
            Password:
            <Control>
              <Input name="password" placeholder="password" type="password" />
            </Control>
          </Label>
        </Field>
        <Button type="button" color="primary">
          Sign In
        </Button>
      </form>
    </Box>
  );
}

export { AuthProvider, Login, RequireAuth, useAuth };
