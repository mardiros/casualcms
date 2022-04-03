import { expect } from "chai";
import React from "react";
import {
  BrowserRouter,
  Navigate,
  Routes,
  Route,
} from "react-router-dom";

import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { AuthProvider, RequireAuth, Login } from "../../src/frontend/ui/login/components";
import { AppContext } from "../../src/frontend/config";
import config from "./config";
import { waitForPath, LocationDisplay } from "./helpers";


describe("As a user, I can login to the app", () => {
  it("I see an error message for invalid username or password", async () => {
    render(
      <AppContext.Provider value={config}>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="admin/*" element={
                <Routes>
                  <Route path="login" element={<Login />} />
                  <Route
                    path="*"
                    element={
                      <RequireAuth>
                        <Routes>
                          <Route path="" element={<div>Welcome authenticated</div>} />
                          <Route path="*" element={<div>not found</div>} />
                        </Routes>
                      </RequireAuth>
                    }
                  />
                </Routes>
              } />
              <Route path="*" element={<Navigate to="/admin" replace />} />
            </Routes>
            <LocationDisplay />
          </BrowserRouter>
        </AuthProvider>
      </AppContext.Provider>
    );
    await waitForPath("/admin/login");

    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: 'bob' } })

    input = screen.getByLabelText("Password:");
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: 'justincase' } })

    let button = screen.getByText("Sign In");
    expect(button).not.equal(null);
    fireEvent.click(button);
    await waitFor(async () => {
      let errMess = screen.getByText("Invalid username or password");
      expect(errMess).not.equal(null);
    }, { interval: 25, timeout: 100 })


  });
});
