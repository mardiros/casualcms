import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { TemplateList } from "../../src/frontend/ui/page_template/components";
import { AppContext } from "../../src/frontend/config";
import config from "./config";
import { FakeAuth, waitForTitle } from "./helpers";

describe("As a user, I can list root templates", () => {
  it("redirect to the login form", async () => {
    render(
      <AppContext.Provider value={config}>
        <FakeAuth>
          <TemplateList />
        </FakeAuth>
      </AppContext.Provider>
    );
    let content = await waitForTitle("Available Templates");
    let tpl = screen.getByText("casual:Home");
    expect(tpl).not.equal(null);
  });
});
