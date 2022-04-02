import React from "react";
import {
  BrowserRouter,
  Navigate,
  Routes,
  Route,
  Link,
  useLocation,
} from "react-router-dom";
import { Box, Heading, Container } from "react-bulma-components";

import { AuthProvider, Login, RequireAuth } from "./ui/login/components";
import { PageNotFound } from "./ui/error404/components";

const Body: React.FunctionComponent<{}> = () => {
  return <>Welcome To The Casual CMS!</>;
};

const Layout: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Box>
        <Heading>
          <Link to="/admin/login">Sign In</Link>
        </Heading>
      </Box>
      <Container>
        <Routes>
          <Route path="login" element={<Login />} /> {/* Fix the layout */}
          <Route
            path="*"
            element={
              <RequireAuth>
                <Routes>
                  <Route path="" element={<Body />} />
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

const App: React.FunctionComponent<AppProps> = (props: AppProps) => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="admin/*" element={<Layout />} />
          {/* Just in case, those route are not served */}
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
        {props.debugNode}
      </BrowserRouter>
    </AuthProvider>
  );
};

export { App };
