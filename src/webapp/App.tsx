import React from "react";
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import {
  Box,
  ButtonGroup,
  ColorModeProvider,
  CSSReset,
  Flex,
  Heading,
  Spacer,
  ThemeProvider,
} from "@chakra-ui/react";
import { theme } from "@chakra-ui/theme";
import { AuthProvider, Login, RequireAuth } from "./ui/login/components";
import { useAuth } from "./ui/login/hooks";
import { PageNotFound } from "./ui/error404/components";
import { TemplateList } from "./ui/page_template/components";
import { PageList } from "./ui/page_list/components";
import { PageNew } from "./ui/page_new/components";
import { HomePage } from "./ui/home/components";
import { PageEdit } from "./ui/page_edit/components";
import { AccountMenu } from "./ui/account/components";

export const Header: React.FunctionComponent<{}> = (): React.ReactElement => {
  let auth = useAuth();
  return (
    <Flex minWidth="max-content" alignItems="center" gap="2">
      <Box p="2">
        <Heading size="lg" color="teal.800">
          <Link to="/admin">👕 Casual CMS</Link>
        </Heading>
      </Box>
      <Spacer />
      <Box gap="2">
        {auth.authenticatedUser ? (
          <AccountMenu username={auth.authenticatedUser.username} />
        ) : (
          <Box
            as="button"
            borderRadius="md"
            bg="teal"
            color="white"
            px={8}
            h={8}
          >
            <Link to="/admin/login" color="white">
              Sign In
            </Link>
          </Box>
        )}
      </Box>
    </Flex>
  );
};

export const Body: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <HomePage />;
  } else {
    return <Link to="/admin/login">Sign In</Link>;
  }
};

const Layout: React.FunctionComponent<{}> = () => {
  return (
    <>
      <Box w="100%" p={4} bg="teal.300" h="90px">
        <Header />
      </Box>
      <Box
        w="100%"
        p={4}
        bg="teal.50"
        minH="calc(100vh - 90px)"
        color="teal.900"
      >
        <Routes>
          <Route path="login" element={<Login />} caseSensitive />
          <Route
            path="*"
            element={
              <RequireAuth>
                <Routes>
                  <Route path="" element={<Body />} caseSensitive />
                  <Route path="pages" element={<PageList />} caseSensitive />
                  <Route
                    path="page/new"
                    element={<TemplateList />}
                    caseSensitive
                  />
                  <Route
                    path="page/new/:tpltype"
                    element={<PageNew />}
                    caseSensitive
                  />
                  <Route
                    path="page/edit"
                    element={<PageEdit />}
                    caseSensitive
                  />
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
  return (
    <>
      <ThemeProvider theme={theme}>
        <ColorModeProvider>
          <CSSReset />
        </ColorModeProvider>
        <Layout />
      </ThemeProvider>
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
          <Route path="admin/*" element={<ThemedLayout />} caseSensitive />
          {/* Required in tests */}
          <Route path="*" element={<Navigate to="/admin" replace />} />
        </Routes>
        {props.debugNode}
      </BrowserRouter>
    </AuthProvider>
  );
};
