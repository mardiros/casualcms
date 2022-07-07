import React from "react";
import { BrowserRouter, Navigate, Routes, Route, Link } from "react-router-dom";
import { Container, Box, ThemeProvider, ColorModeProvider, CSSReset, Heading } from "@chakra-ui/react";
import { theme } from "@chakra-ui/theme";
import { AuthProvider, Login, RequireAuth, useAuth } from "./ui/login/components";
import { PageNotFound } from "./ui/error404/components";
import { TemplateList } from "./ui/page_template/components";
import { PageEdit } from "./ui/page_edit/components";
import { PageList } from "./ui/page_list/components";
import { PageNew } from "./ui/page_new/components";

const Body: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <>
      <Heading>
        Welcome {auth.authenticatedUser.username}!
      </Heading>
      <Box>
        <Link to="/admin/page/new">Create my first page</Link>.
      </Box>
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
      <Box w='100%' p={4} bg='teal.50' minH='calc(100vh - 90px)'>
        <Routes>
          <Route path="login" element={<Login />} />
          <Route
            path="*"
            element={
              <RequireAuth>
                <Routes>
                  <Route path="" element={<Body />} />
                  <Route path="pages" element={<PageList root={true}/>} />
                  <Route path="pages/:parentPath*" element={<PageList />} />
                  <Route path="page/new" element={<TemplateList />} />
                  <Route path="page/new/:tpltype" element={<PageNew />} />
                  <Route path="page/edit/root/" element={<PageEdit />} />
                  <Route path="page/edit/root/:parentPath*" element={<PageEdit />} />
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
