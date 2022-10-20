import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import {
  PageTypeList,
  PageTypesTable,
} from "../../../src/webapp/ui/pages/page_types_list";
import { renderWithRouter, waitForLoadingLabel } from "../helpers";

describe("As a user, I can choose a root templates type", () => {
  it("render a spinner while loading", async () => {
    renderWithRouter(
      <Route
        path="/admin/pages/new"
        element={
          <PageTypesTable isLoading={true} parentPath={null} pageTypes={[]} />
        }
      />,
      "/admin/pages/new"
    );
    const spinner = screen.getByText("loading page types...");
    expect(spinner).not.equal(null);
  });
  it("render rows per template type", async () => {
    const tpls = [
      { type: "casual:One", title: "One" },
      { type: "casual:Two", title: "Two" },
    ];
    renderWithRouter(
      <Route
        path="/admin/pages/new"
        element={
          <PageTypesTable
            isLoading={false}
            parentPath={null}
            pageTypes={tpls}
          />
        }
      />,
      "/admin/pages/new"
    );
    let link = screen.getByText("One");
    expect(link.getAttribute("href")).equal("/admin/pages/new/casual:One");
    link = screen.getByText("Two");
    expect(link.getAttribute("href")).equal("/admin/pages/new/casual:Two");
  });

  it("set the parent path as link parameter", async () => {
    renderWithRouter(
      <Route
        path="/admin/pages/new"
        element={
          <PageTypesTable
            isLoading={false}
            parentPath="/home"
            pageTypes={[{ title: "One", type: "casual:One" }]}
          />
        }
      />,
      "/admin/pages/new"
    );
    let link = screen.getByText("One");
    expect(link.getAttribute("href")).equal(
      "/admin/pages/new/casual:One?parent=%2Fhome"
    );
  });

  it("list root templates", async () => {
    renderWithRouter(
      <Route path="/admin/pages/new" element={<PageTypeList />} />,
      "/admin/pages/new"
    );
    await waitForLoadingLabel("loading page types...");
    const tpl = screen.getByText("Home Page");
    expect(tpl).not.equal(null);
  });
});
