import React from "react";
import { BrowserRouter, Link, Navigate, Route, Routes } from "react-router-dom";
import { ColorModeProvider, CSSReset, ThemeProvider } from "@chakra-ui/react";
import { theme } from "@chakra-ui/theme";
import { AuthProvider, Login, RequireAuth } from "./ui/login/components";
import { useAuth } from "./ui/login/hooks";
import { PageNotFound } from "./ui/layout/error_404";
import { PageList } from "./ui/pages/page_list";
import { PageNew } from "./ui/pages/page_new";
import { PageTypeList } from "./ui/pages/page_types_list";
import { HomePage } from "./ui/home/components";
import { PageEdit } from "./ui/pages/page_edit";
import { Layout } from "./ui/layout/layout";
import { SiteList } from "./ui/sites/site_list";
import { SiteNew } from "./ui/sites/site_new";
import { SiteEdit } from "./ui/sites/site_edit";
import { SnippetList } from "./ui/snippets/snippet_list";
import { SnippetTypeList } from "./ui/snippets/snippet_types_list";
import { SnippetNew } from "./ui/snippets/snippet_new";
import { SnippetEdit } from "./ui/snippets/snippet_edit";

export const Body: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <HomePage />;
  } else {
    return <Link to="/admin/login">Sign In</Link>;
  }
};

const AuhtenticatedRoutes: React.FunctionComponent<{}> = () => {
  return (
    <RequireAuth>
      <Routes>
        <Route path="" element={<Body />} caseSensitive />
        <Route path="pages" element={<PageList />} caseSensitive />
        <Route path="pages/new" element={<PageTypeList />} caseSensitive />
        <Route path="pages/new/:pageType" element={<PageNew />} caseSensitive />
        <Route path="pages/edit" element={<PageEdit />} caseSensitive />

        <Route path="snippets" element={<SnippetList />} caseSensitive />
        <Route
          path="snippets/new"
          element={<SnippetTypeList />}
          caseSensitive
        />
        <Route
          path="snippets/new/:snippetType"
          element={<SnippetNew />}
          caseSensitive
        />
        <Route
          path="snippets/edit/:snippetType/:snippetSlug"
          element={<SnippetEdit />}
          caseSensitive
        />

        <Route path="sites" element={<SiteList />} caseSensitive />
        <Route path="sites/new" element={<SiteNew />} caseSensitive />
        <Route path="sites/edit" element={<SiteEdit />} caseSensitive />

        <Route path="*" element={<PageNotFound />} />
      </Routes>
    </RequireAuth>
  );
};

const AppRoutes: React.FunctionComponent<{}> = () => {
  return (
    <Routes>
      <Route path="login" element={<Login />} caseSensitive />
      <Route path="*" element={<AuhtenticatedRoutes />} />
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
