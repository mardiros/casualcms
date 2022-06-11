import React from "react";
import { BrowserRouter, Navigate, Routes, Route, Link } from "react-router-dom";
import { Container, Box, ThemeProvider, ColorModeProvider, CSSReset, Heading } from "@chakra-ui/react";
import { theme } from "@chakra-ui/theme";
import { AuthProvider, Login, RequireAuth, useAuth } from "./ui/login/components";
import { PageNotFound } from "./ui/error404/components";
import { TemplateList } from "./ui/page_template/components";
import { PageEdit } from "./ui/page_edit/components";

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
    return <Link to="/admin">👕 Casual CMS</Link>
  }
  else {
    return <Link to="/admin/login">Sign In</Link>
  }
}

const Layout: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Box w='100%' p={4} bg='teal.300' h='90px'>
        <Heading>
          <Header />
        </Heading>
      </Box>
      <Box w='100%' p={4} bg='teal.50' h='calc(100vh - 90px)'>
        <Routes>
          <Route path="login" element={<Login />} />
          <Route
            path="*"
            element={
              <RequireAuth>
                <Routes>
                  <Route path="" element={<Body />} />
                  <Route path="page/new" element={<TemplateList />} />
                  <Route path="page/edit/:tpltype" element={<PageEdit />} />
                  <Route path="*" element={<PageNotFound />} />
                </Routes>
              </RequireAuth>
            }
          />
        </Routes>
      </Box>
    </>
  );
};

const ThemedLayout: React.FunctionComponent<{}> = () => {
  return (<>
    <ThemeProvider theme={theme}>
      <ColorModeProvider>
        <CSSReset />
      </ColorModeProvider>
      <Layout />
    </ThemeProvider>
  </>)

}

type AppProps = {
  debugNode?: React.ReactNode;
};

export const App: React.FunctionComponent<AppProps> = (props: AppProps) => {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          <Route path="admin/*" element={<ThemedLayout />} />
          {/* Required in tests */}
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
        {props.debugNode}
      </BrowserRouter>
    </AuthProvider>
  );
};
