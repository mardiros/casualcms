import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { TemplateList } from "../../src/webapp/ui/page_template/components";
import { renderWithRouter, waitForTitle } from "./helpers";

describe("As a user, I can choose a root templates type", () => {
  it("list root templates", async () => {
    renderWithRouter(
      <Route path="/page/new" element={<TemplateList />} />,
      "/page/new",
    );
    await waitForTitle("Choose A Type Of Template");
    let tpl = screen.getByText("casual:HomePage");
    expect(tpl).not.equal(null);
  });
});
