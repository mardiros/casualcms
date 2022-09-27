import React from "react";
import { RenderResult, render, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router-dom";
import { Routes } from "react-router-dom";

import config from "./config";

import { AuthContext } from "../../src/webapp/ui/login/hooks";
import { Account } from "../../src/webapp/casualcms/domain/model";
import { AppContext } from "../../src/webapp/config";
import { ChakraProvider } from "@chakra-ui/react";

export const LocationDisplay = () => {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
};

type FakeAuthProps = {
  children: React.ReactNode;
  isAuthenticated: boolean;
};

export function FakeAuth(props: FakeAuthProps): React.ReactElement {
  const children = props.children;
  const account =
    props.isAuthenticated === false
      ? null
      : {
        id: "123",
        username: "bob",
        token: "abc",
        lang: "en",
      };

  let [authenticatedUser, setUser] = React.useState<Account | null>(account);
  let remember = (account: Account, callback: any) => { };
  let forget = async (callback: () => Promise<boolean>) => {
    setUser(null);
    await callback();
  };

  let value = { authenticatedUser, remember, forget };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export const waitForPath = async (path: string): Promise<HTMLElement> => {
  const resp = await waitFor(
    (): HTMLElement => {
      let loc = screen.getByTestId("location-display");

      if (loc.innerHTML != path) {
        throw Error(`Path not ready: ${loc.innerHTML} (expected ${path})`);
      }
      return loc;
    },
    { interval: 25, timeout: 500 }
  );
  return resp;
};

export const waitForLoadingLabel = async (
  spinner_label: string
): Promise<boolean> => {
  const resp = await waitFor((): boolean => {
    try {
      screen.getByText(spinner_label);
    } catch (e) {
      return true;
    }
    throw Error(`Spinner ${spinner_label} here`);
  });
  return resp;
};

export class ErrorBoundary extends React.Component<{ children: any }> {
  state: { hasError: boolean };
  constructor(props: any) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: any) {
    // Update state so the next render will show the fallback UI.
    return { hasError: true };
  }
  componentDidCatch(error: any, errorInfo: any) {
    // You can also log the error to an error reporting service
    console.log({ error, errorInfo });
  }

  render() {
    if (this.state.hasError) {
      // You can render any custom fallback UI
      return <h1>Something went wrong.</h1>;
    }
    return this.props.children;
  }
}

export const renderWithRouter = async (
  routes: React.ReactNode,
  path: string,
  options?: { isAuthenticated?: boolean }
): Promise<RenderResult> => {
  const isAuthent =
    options?.isAuthenticated === undefined ? true : options.isAuthenticated;
  let ret = render(
    <ErrorBoundary>
      <AppContext.Provider value={config}>
        <FakeAuth isAuthenticated={isAuthent}>
          <MemoryRouter initialEntries={[path]}>
            <Routes>{routes}</Routes>
            <LocationDisplay />
          </MemoryRouter>
        </FakeAuth>
      </AppContext.Provider>
    </ErrorBoundary>,
    {}
  );
  return ret;
};


/** Rendering the Chackra Provider is slow, so, use int for compontents
 * that requires it, such as toastee.
 */
export const renderWithRouterWithTheme = async (
  routes: React.ReactNode,
  path: string,
  options?: { isAuthenticated?: boolean }
): Promise<RenderResult> => {
  const isAuthent =
    options?.isAuthenticated === undefined ? true : options.isAuthenticated;
  let ret = render(
    <ErrorBoundary>
      <ChakraProvider>
        <AppContext.Provider value={config}>
          <FakeAuth isAuthenticated={isAuthent}>
            <MemoryRouter initialEntries={[path]}>
              <Routes>{routes}</Routes>
              <LocationDisplay />
            </MemoryRouter>
          </FakeAuth>
        </AppContext.Provider>
      </ChakraProvider>
    </ErrorBoundary>,
    {}
  );
  return ret;
};
