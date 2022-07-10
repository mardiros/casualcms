import React from "react";
import { Box, Button, Container, FormControl, FormHelperText, FormLabel, Heading, Input } from "@chakra-ui/react";
import { useNavigate } from "react-router-dom";

import { Account } from "../../casualcms/domain/model";
import { AppContext, useConfig } from "../../config";
import { ApiError } from "../../casualcms/domain/ports";
import { Loader } from "../loader/components";

interface IAuthContext {
  authenticatedUser: Account | null;
  remember: (account: Account, callback: any) => void;
  forget: (callback: any) => void;
}

export const AuthContext = React.createContext<IAuthContext>(null!);

export function useAuth() {
  return React.useContext(AuthContext);
}

export function AuthProvider({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  let [authenticatedUser, setUser] = React.useState<Account | null>(null);
  let remember = (account: Account, callback: any) => {
    setUser(account);
    callback();
  };

  let forget = (callback: any) => {
    setUser(null);
    callback();
  };

  let value = { authenticatedUser, remember, forget };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function RequireAuth({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  const config = React.useContext(AppContext);
  let auth = useAuth();
  let navigate = useNavigate();

  React.useEffect(() => {
    async function loadAuthenticatedUser() {
      if (!auth.authenticatedUser) {
        const accountResult = await config.uow.account.getCurrent();
        accountResult
          .map((account: Account) => {
            auth.remember(account, () => { })
          })
          .mapErr((err: any) => {
            navigate("/admin/login", { replace: true })
          });
      }
    }
    loadAuthenticatedUser();
    return function cleanup() { };
  }, []);

  if (!auth.authenticatedUser) {
    return <Loader label="Authenticating..."/>;
  }

  return <>{children}</>;
}

export const Login: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  let navigate = useNavigate();
  let config = useConfig();
  const [error, setError] = React.useState<ApiError>(null);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    let formData = new FormData(event.currentTarget);
    let username = formData.get("username") as string;
    let password = formData.get("password") as string;
    // let from = location.state?.from?.pathname || "/admin/";
    let from = "/admin/";  // keep last / to avoid one redirection
    let accountResult = await config.api.account.byCredentials({
      username,
      password,
    });

    accountResult
      .map(async (account) => {
        // XXX save the set here
        const result = await config.uow.account.set(account);
        auth.remember(account, () => {
          navigate(from, { replace: true });
        });
      })
      .mapErr((apiError) => {
        setError(apiError);
      });
  }

  return (
    <Container>
      <Heading>
        Sign In To Casual CMS
      </Heading>
      <Box>
        <form onSubmit={handleSubmit}>
          <FormControl paddingTop={5}>
            <FormLabel htmlFor="username">Username:</FormLabel>
            <Input id="username" name="username" placeholder="username" />
            {error?.get("username") ? (
              <FormHelperText>
                {error.get("username")}
              </FormHelperText>
            ) : <></>}
          </FormControl>
          <FormControl paddingTop={5}>
            <FormLabel htmlFor="password">Password:</FormLabel>
            <Input id="password" name="password" placeholder="password" type="password" />
          </FormControl>
          <FormControl paddingTop={5}>
            <Button type="submit">Sign In</Button>
          </FormControl>
        </form>
      </Box>
    </Container>
  );
};
