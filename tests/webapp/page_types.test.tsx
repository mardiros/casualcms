import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import {
  PageTypeList,
  PageTypesTable,
} from "../../src/webapp/ui/pages/page_types_list";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";

describe("As a user, I can choose a root templates type", () => {
  it("render a spinner while loading", async () => {
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={
          <PageTypesTable isLoading={true} parentPath={null} pageTypes={[]} />
        }
      />,
      "/admin/page/new"
    );
    const spinner = screen.getByText("loading page types...");
    expect(spinner).not.equal(null);
  });
  it("render rows per template type", async () => {
    const tpls = [{ type: "casual:One" }, { type: "casual:Two" }];
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={
          <PageTypesTable
            isLoading={false}
            parentPath={null}
            pageTypes={tpls}
          />
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
          <PageTypesTable
            isLoading={false}
            parentPath="/home"
            pageTypes={[{ type: "casual:One" }]}
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
      <Route path="/admin/page/new" element={<PageTypeList />} />,
      "/admin/page/new"
    );
    await waitForLoadingLabel("loading page types...");
    const tpl = screen.getByText("casual:HomePage");
    expect(tpl).not.equal(null);
  });
});
