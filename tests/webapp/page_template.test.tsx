import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import {
  TemplateList,
  TemplateTable,
} from "../../src/webapp/ui/pages/page_template";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";

describe("As a user, I can choose a root templates type", () => {
  it("render a spinner while loading", async () => {
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={
          <TemplateTable isLoading={true} parentPath={null} templates={[]} />
        }
      />,
      "/admin/page/new"
    );
    const spinner = screen.getByText("loading page templates...");
    expect(spinner).not.equal(null);
  });
  it("render rows per template type", async () => {
    const tpls = [{ type: "casual:One" }, { type: "casual:Two" }];
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={
          <TemplateTable isLoading={false} parentPath={null} templates={tpls} />
        }
      />,
      "/admin/page/new"
    );
    let link = screen.getByText("casual:One");
    expect(link.getAttribute("href")).equal("/admin/page/new/casual:One");
    link = screen.getByText("casual:Two");
    expect(link.getAttribute("href")).equal("/admin/page/new/casual:Two");
  });

  it("set the parent path as link parameter", async () => {
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={
          <TemplateTable
            isLoading={false}
            parentPath="/home"
            templates={[{ type: "casual:One" }]}
          />
        }
      />,
      "/admin/page/new"
    );
    let link = screen.getByText("casual:One");
    expect(link.getAttribute("href")).equal(
      "/admin/page/new/casual:One?parent=%2Fhome"
    );
  });

  it("list root templates", async () => {
    renderWithRouter(
      <Route path="/admin/page/new" element={<TemplateList />} />,
      "/admin/page/new"
    );
    await waitForLoadingLabel("loading page templates...");
    const tpl = screen.getByText("casual:HomePage");
    expect(tpl).not.equal(null);
  });
});
