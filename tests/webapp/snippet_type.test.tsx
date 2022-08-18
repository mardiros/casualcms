import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";
import {
  SnippetTypeList,
  SnippetTypesTable,
} from "../../src/webapp/ui/snippets/snippet_types_list";

describe("As a user, I can list snippet", () => {
  it("render a spinner while loading", async () => {
    renderWithRouter(
      <Route
        path="/admin/snippet/new"
        element={<SnippetTypesTable isLoading={true} snippetTypes={[]} />}
      />,
      "/admin/snippet/new"
    );
    const spinner = screen.getByText("loading snippet types...");
    expect(spinner).not.equal(null);
  });

  it("render rows per template type", async () => {
    const tpls = [
      { type: "blog:HeaderSnippet" },
      { type: "blog:FooterSnippet" },
    ];
    renderWithRouter(
      <Route
        path="/admin/page/new"
        element={<SnippetTypesTable isLoading={false} snippetTypes={tpls} />}
      />,
      "/admin/page/new"
    );
    let link = screen.getByText("blog:HeaderSnippet", { exact: false });
    expect(link.getAttribute("href")).equal(
      "/admin/snippet/new/blog:HeaderSnippet"
    );
    link = screen.getByText("blog:FooterSnippet", { exact: false });
    expect(link.getAttribute("href")).equal(
      "/admin/snippet/new/blog:FooterSnippet"
    );
  });

  it("list snippet types", async () => {
    renderWithRouter(
      <Route path="/admin/snippet/new" element={<SnippetTypeList />} />,
      "/admin/snippet/new"
    );
    await waitForLoadingLabel("loading snippet types...");
    const tpl = screen.getByText("blog:HeaderSnippet");
    expect(tpl).not.equal(null);
  });
});
