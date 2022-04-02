import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { App } from "../../src/frontend/App";
import { AppContext } from "../../src/frontend/config";
import config from "./config"

describe("As a user, I am redirect to the login page", () => {
  it("cast a single error", () => {
    render(
      <AppContext.Provider value={config}>
        <App />
      </AppContext.Provider>
    );
    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
  })
});
