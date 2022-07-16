import React from "react";
import { RenderResult, screen, waitFor } from "@testing-library/react";
import { MemoryRouter, useLocation } from "react-router-dom";
import { Routes } from "react-router-dom";
import { render } from "@testing-library/react";

import config from "./config";

import { AuthContext } from "../../src/webapp/ui/login/components";
import { Account } from "../../src/webapp/casualcms/domain/model";
import { AppContext } from "../../src/webapp/config";

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
  let remember = (account: Account, callback: any) => {};
  let forget = (callback: any) => {};

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
    { interval: 25, timeout: 2000 }
  );
  return resp;
};

export const waitForLoadingLabel = async (
  spinner_label: string
): Promise<boolean> => {
  const resp = await waitFor((): boolean => {
    try {
      let loc = screen.getByText(spinner_label);
    } catch (e) {
      return true;
    }
    throw Error(`Spinner ${spinner_label} here`);
  });
  return resp;
};

export const waitForTitle = async (title: string): Promise<HTMLElement> => {
  const resp = await waitFor((): HTMLElement => {
    let loc = screen.getByText(title);

    if (loc == undefined) {
      throw Error(`Title not ready: ${loc}`);
    }
    return loc;
  });
  return resp;
};

export const waitForLabelText = async (label: string): Promise<HTMLElement> => {
  const resp = await waitFor((): HTMLElement => {
    let loc = screen.getByLabelText(label, { exact: false });

    if (loc == undefined) {
      throw Error(`Location not ready: ${loc}`);
    }
    return loc;
  });
  return resp;
};

export const renderWithRouter = async (
  routes: React.ReactNode,
  path: string,
  options?: { isAuthenticated?: boolean }
): Promise<RenderResult> => {
  const isAuthent =
    options?.isAuthenticated === undefined ? true : options.isAuthenticated;
  let ret = render(
    <AppContext.Provider value={config}>
      <FakeAuth isAuthenticated={isAuthent}>
        <MemoryRouter initialEntries={[path]}>
          <Routes>{routes}</Routes>
          <LocationDisplay />
        </MemoryRouter>
      </FakeAuth>
    </AppContext.Provider>
  );
  return ret;
};
