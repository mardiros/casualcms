import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { TemplateList } from "../../src/webapp/ui/page_template/components";
import { renderWithRouter, waitForTitle } from "./helpers";

describe("As a user, I can list root templates", () => {
  it("redirect to the login form", async () => {
    renderWithRouter(
      <Route path="/page/new" element={<TemplateList />} />,
      "/page/new",
    );
    await waitForTitle("Choose A Type Of Template");
    let tpl = screen.getByText("casual:Home");
    expect(tpl).not.equal(null);
  });
});
