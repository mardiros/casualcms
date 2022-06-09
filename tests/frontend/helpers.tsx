import React from "react";
import { screen, waitFor } from "@testing-library/react";
import { useLocation } from "react-router-dom";

import { AuthContext } from "../../src/frontend/ui/login/components";
import { Account } from "../../src/frontend/casualcms/domain/model";
import { JsxElement } from "typescript";

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
  let remember = (account: Account, callback: any) => {};
  let forget = (callback: any) => {};

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
    let loc = screen.getByLabelText(label, {exact: false});

    if (loc == undefined) {
      throw Error(`Not ready: ${loc}`);
    }
    return loc;
  });
  return resp;
};
