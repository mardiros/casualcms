import React from "react";
import { RenderResult, screen, waitFor } from "@testing-library/react";
import { useLocation } from "react-router-dom";
import { BrowserRouter, Navigate, Routes, Route } from "react-router-dom";
import { render } from "@testing-library/react";

import config from "./config";

import { AuthContext } from "../../src/frontend/ui/login/components";
import { Account } from "../../src/frontend/casualcms/domain/model";
import { AppContext } from "../../src/frontend/config";



export const LocationDisplay = () => {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
};


export function FakeAuth({
  children,
}: {
  children: React.ReactNode;
}): React.ReactElement {
  const bob = {
    id: "123",
    username: "bob",
    token: "abc",
    lang: "en",
  };

  let [authenticatedUser, setUser] = React.useState<Account | null>(bob);
  let remember = (account: Account, callback: any) => { };
  let forget = (callback: any) => { };

  let value = { authenticatedUser, remember, forget };
  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;

}

export const waitForPath = async (path: string): Promise<HTMLElement> => {
  const resp = await waitFor((): HTMLElement => {
    let loc = screen.getByTestId("location-display");

    if (loc.innerHTML != path) {
      throw Error(`Not ready: ${loc.innerHTML}`);
    }
    return loc;
  });
  return resp;
};



export const waitForTitle = async (title: string): Promise<HTMLElement> => {
  const resp = await waitFor((): HTMLElement => {
    let loc = screen.getByText(title);

    if (loc == undefined) {
      throw Error(`Not ready: ${loc}`);
    }
    return loc;
  });
  return resp;
};

export const waitForLabelText = async (label: string): Promise<HTMLElement> => {
  const resp = await waitFor((): HTMLElement => {
    let loc = screen.getByLabelText(label, { exact: false });

    if (loc == undefined) {
      throw Error(`Not ready: ${loc}`);
    }
    return loc;
  });
  return resp;
};


export const renderWithRouter = async(
  ui: React.ReactNode,
  pattern: string,
  path: string,
):  Promise<RenderResult> => {
  let ret = render(
    <AppContext.Provider value={config}>
      <FakeAuth>
        <BrowserRouter>
          <Routes>
            <Route path={pattern} element={ui}>
            </Route>
            <Route path="*" element={<Navigate to={path} replace={true} />}>
            </Route>
          </Routes>
          <LocationDisplay />
        </BrowserRouter>
      </FakeAuth>
    </AppContext.Provider>
  );
  await waitForPath(path)
  return ret
}
