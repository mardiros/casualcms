import React from "react";
import {
  Box,
  Button,
  Container,
  FormControl,
  FormHelperText,
  FormLabel,
  Heading,
  Input,
} from "@chakra-ui/react";
import { Navigate } from "react-router-dom";

import { Account } from "../../casualcms/domain/model";
import { AppContext, useConfig } from "../../config";
import { ApiError } from "../../casualcms/domain/ports";
import { Loader } from "../layout/loader";
import { useAuth, AuthContext } from "./hooks";

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

  let forget = async (callback: () => Promise<boolean>) => {
    setUser(null);
    await callback();
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
  const [authError, setAuthError] = React.useState<boolean>(false);

  React.useEffect(() => {
    async function loadAuthenticatedUser() {
      if (!auth.authenticatedUser) {
        const accountResult = await config.uow.account.getCurrent();
        accountResult
          .map((account: Account) => {
            auth.remember(account, () => {});
          })
          .mapErr((err: any) => {
            setAuthError(true);
          });
      }
    }
    loadAuthenticatedUser();
    return function cleanup() {};
  }, [authError]);

  if (authError) {
    return <Navigate to="/admin/login" replace />;
  }

  if (!auth.authenticatedUser) {
    return <Loader label="Authenticating..." />;
  }

  return <>{children}</>;
}

export const Login: React.FunctionComponent<{}> = () => {
  const auth = useAuth();
  const config = useConfig();
  const [error, setError] = React.useState<ApiError>(null);
  const [authSucceed, setAuthSuceed] = React.useState<boolean>(false);
  // let from = location.state?.from?.pathname || "/admin/";
  const from = "/admin/"; // keep last / to avoid one redirection

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    event.preventDefault();
    const formData = new FormData(event.currentTarget);
    const username = formData.get("username") as string;
    const password = formData.get("password") as string;
    const accountResult = await config.api.account.byCredentials({
      username,
      password,
    });

    accountResult
      .map(async (account: Account) => {
        // XXX save the set here
        const result = await config.uow.account.set(account);
        auth.remember(account, () => {
          setAuthSuceed(true);
        });
      })
      .mapErr((apiError) => {
        setError(apiError);
      });
  }

  if (authSucceed) {
    return <Navigate to={from} replace />;
  }

  return (
    <Container>
      <Heading>Sign In To Casual CMS</Heading>
      <Box>
        <form onSubmit={handleSubmit}>
          <FormControl paddingTop={5}>
            <FormLabel htmlFor="username">Username:</FormLabel>
            <Input id="username" name="username" placeholder="username" />
            {error?.get("username") ? (
              <FormHelperText>{error.get("username")}</FormHelperText>
            ) : (
              <></>
            )}
          </FormControl>
          <FormControl paddingTop={5}>
            <FormLabel htmlFor="password">Password:</FormLabel>
            <Input
              id="password"
              name="password"
              placeholder="password"
              type="password"
            />
          </FormControl>
          <FormControl paddingTop={5}>
            <Button type="submit">Sign In</Button>
          </FormControl>
        </form>
      </Box>
    </Container>
  );
};
