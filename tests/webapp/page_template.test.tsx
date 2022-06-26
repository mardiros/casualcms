import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { TemplateList } from "../../src/webapp/ui/page_template/components";
import { AppContext } from "../../src/webapp/config";
import config from "./config";
import { renderWithRouter, waitForTitle } from "./helpers";

describe("As a user, I can list root templates", () => {
  it("redirect to the login form", async () => {
    renderWithRouter(
      <TemplateList />,
      "/page/new",
      "/page/new",
    );
    await waitForTitle("Available Templates");
    let tpl = screen.getByText("casual:Home");
    expect(tpl).not.equal(null);
  });
});
