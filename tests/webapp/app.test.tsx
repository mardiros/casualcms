import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { App } from "../../src/webapp/App";
import { AppContext } from "../../src/webapp/config";
import config from "./config";
import { waitForPath, LocationDisplay } from "./helpers";

describe("As a user, I am redirect to the login page", () => {
  it("redirect to the login form", async () => {
    render(
      <AppContext.Provider value={config}>
        <App debugNode={<LocationDisplay />} />
      </AppContext.Provider>
    );
    await waitForPath("/admin/login");
    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
  });
});
