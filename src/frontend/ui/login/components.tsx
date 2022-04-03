import React from "react";
import { Box, Heading, Form, Button } from "react-bulma-components";
const { Control, Field, Label, Input } = Form;
import { useNavigate } from "react-router-dom";

import { Account } from "../../casualcms/domain/model";
import { AppContext, useConfig } from "../../config";
import { ApiError } from "../../casualcms/domain/ports";

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
      console.log("XXX")
      auth.loadAuthenticatedUser(() => {
        if (!auth.authenticatedUser) {
          navigate("/admin/login", { replace: true });
        } else {
          setLoading(false);
        }
      });
    }
    loadAuthenticatedUser();
    return function cleanup() { };
  }, []);
  if (loading || !auth.authenticatedUser) {
    return <>Loading...</>;
  }

  return <>{children}</>;
}

const Login: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  let navigate = useNavigate();
  let config = useConfig();
  const [error, setError] = React.useState<ApiError>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (config == null) {
      throw new Error("Fatal Error: Unconfigured application");
    }

    let formData = new FormData(event.currentTarget);
    let username = formData.get("username") as string;
    let password = formData.get("password") as string;
    // let from = location.state?.from?.pathname || "/";
    let from = "/admin";
    let accountResult = await config.api.account.byCredentials({
      username,
      password,
    });

    accountResult
      .map(async (account) => {
        // const result = await config.uow.account.add(account);
        auth.remember(account, () => {
          navigate(from, { replace: true });
        });
      })
      .mapErr((apiError) => {
        setError(apiError);
      });
  }

  return (
    <Box>
      <Heading>Sign In To Casual CMS</Heading>
      <form onSubmit={handleSubmit} method="POST">
        <Field>
          <Label>
            Username:
            <Control>
              <Input name="username" placeholder="username" />
              {error && error.has("username") &&
                <p className="help is-danger">{error.get("username")}</p>
              }
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
        <Button type="submit" color="primary">
          Sign In
        </Button>
      </form>
    </Box>
  );
};

export { AuthProvider, Login, RequireAuth, useAuth };
