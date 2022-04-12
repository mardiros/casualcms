import React from "react";
import { BrowserRouter, Navigate, Routes, Route, Link } from "react-router-dom";
import { Box, Heading, Container } from "react-bulma-components";

import { AuthProvider, Login, RequireAuth, useAuth } from "./ui/login/components";
import { PageNotFound } from "./ui/error404/components";
import { TemplateList } from "./ui/page_template/components";

const Body: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <>
      <p><Link to="/admin">Welcome {auth.authenticatedUser.username}!</Link></p>
      <p><Link to="/admin/page/new">Create my first page</Link>.</p>
    </>
  }
  else {
    return <Link to="/admin/login">Sign In</Link>
  }
};

const Header: React.FunctionComponent<{}> = (): React.ReactElement => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <Link to="/admin">👕</Link>
  }
  else {
    return <Link to="/admin/login">Sign In</Link>
  }
}

const Layout: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Box>
        <Heading>
          <Header />
        </Heading>
      </Box>
      <Container>
        <Routes>
          <Route path="login" element={<Login />} />
          <Route
            path="*"
            element={
              <RequireAuth>
                <Routes>
                  <Route path="" element={<Body />} />
                  <Route path="page/new" element={<TemplateList />} />
                  <Route path="*" element={<PageNotFound />} />
                </Routes>
              </RequireAuth>
            }
          />
        </Routes>
      </Container>
    </>
  );
};

type AppProps = {
  debugNode?: React.ReactNode;
};

export const App: React.FunctionComponent<AppProps> = (props: AppProps) => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="admin/*" element={<Layout />} />
          {/* Required in tests */}
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
        {props.debugNode}
      </BrowserRouter>
    </AuthProvider>
  );
};
