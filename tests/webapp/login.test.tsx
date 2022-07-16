import { expect } from "chai";
import React from "react";
import { Navigate, Routes, Route, MemoryRouter } from "react-router-dom";

import {
  render,
  screen,
  fireEvent,
  RenderResult,
} from "@testing-library/react";
import {
  AuthProvider,
  RequireAuth,
  Login,
} from "../../src/webapp/ui/login/components";
import { AppContext } from "../../src/webapp/config";
import config from "./config";
import {
  waitForPath,
  LocationDisplay,
  waitForTitle,
  renderWithRouter,
} from "./helpers";
import { HomePage } from "../../src/webapp/ui/home/components";

export const renderLogin = async (): Promise<RenderResult> => {
  let ret = render(
    <AppContext.Provider value={config}>
      <AuthProvider>
        <MemoryRouter>
          <Routes>
            <Route
              path="admin/*"
              element={
                <Routes>
                  <Route path="login" element={<Login />} />
                  <Route
                    path="*"
                    element={
                      <RequireAuth>
                        <Routes>
                          <Route path="" element={<div>Welcome bob</div>} />
                          <Route path="*" element={<div>not found</div>} />
                        </Routes>
                      </RequireAuth>
                    }
                  />
                </Routes>
              }
            />
            <Route path="*" element={<Navigate to="/admin" replace />} />
          </Routes>
          <LocationDisplay />
        </MemoryRouter>
      </AuthProvider>
    </AppContext.Provider>
  );
  return ret;
};

describe("As a user, I can login to the app", () => {
  it("I see an error message for invalid username or password", async () => {
    await renderLogin();
    await waitForPath("/admin/login");

    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "bob" } });

    input = screen.getByLabelText("Password:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "justincase" } });

    let button = screen.getByText("Sign In");
    expect(button).not.equal(null);
    fireEvent.click(button);
    const title = await waitForTitle("Invalid username or password");
    expect(title.nodeName).equal("DIV");
  });

  it("I am redirected to home after login with correct credentials", async () => {
    await renderLogin();
    await waitForPath("/admin/login");

    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "bob" } });

    input = screen.getByLabelText("Password:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "itsmysecret" } });

    let button = screen.getByText("Sign In");
    expect(button).not.equal(null);
    fireEvent.click(button);

    const title = await waitForTitle("Welcome bob");
    expect(title.nodeName).equal("DIV");
  });

  it("Reuse saved credentials on hard refresh", async () => {
    const bob = {
      id: "123",
      username: "bob",
      token: "abc",
      lang: "en",
    };
    await config.uow.account.set(bob);
    await renderLogin();
    await waitForPath("/admin");

    const title = await waitForTitle("Welcome bob");
    expect(title.nodeName).equal("DIV");
  });
});
