import React from "react";
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import { ColorModeProvider, CSSReset, ThemeProvider } from "@chakra-ui/react";
import { theme } from "@chakra-ui/theme";
import { AuthProvider, Login, RequireAuth } from "./ui/login/components";
import { useAuth } from "./ui/login/hooks";
import { PageNotFound } from "./ui/layout/error_404";
import { PageList } from "./ui/pages/page_list";
import { PageNew } from "./ui/pages/page_new";
import { TemplateList } from "./ui/pages/page_template";
import { HomePage } from "./ui/home/components";
import { PageEdit } from "./ui/pages/page_edit";
import { Layout } from "./ui/layout/layout";
import { SiteList } from "./ui/sites/site_list";

export const Body: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <HomePage />;
  } else {
    return <Link to="/admin/login">Sign In</Link>;
  }
};

const AppRoutes: React.FunctionComponent<{}> = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} caseSensitive />
      <Route
        path="*"
        element={
          <RequireAuth>
            <Routes>
              <Route path="" element={<Body />} caseSensitive />
              <Route path="pages" element={<PageList />} caseSensitive />
              <Route path="page/new" element={<TemplateList />} caseSensitive />
              <Route
                path="page/new/:tpltype"
                element={<PageNew />}
                caseSensitive
              />
              <Route path="page/edit" element={<PageEdit />} caseSensitive />

              <Route path="sites" element={<SiteList />} caseSensitive />

              <Route path="*" element={<PageNotFound />} />
            </Routes>
          </RequireAuth>
        }
      />
    </Routes>
  );
};

const ThemedLayout: React.FunctionComponent<{}> = () => {
  return (
    <>
      <ThemeProvider theme={theme}>
        <ColorModeProvider>
          <CSSReset />
        </ColorModeProvider>
        <Layout routes={<AppRoutes />} />
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
