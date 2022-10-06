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
  it("<SnippetTypesTable />: render a spinner while loading", async () => {
    renderWithRouter(
      <Route
        path="/admin/snippets/new/:snippetTypeName"
        element={<SnippetTypesTable isLoading={true} snippetTypes={[]} />}
      />,
      "/admin/snippets/new/blog:HeaderSnippet"
    );
    const spinner = screen.getByText("loading snippet types...");
    expect(spinner).not.equal(null);
  });

  it("<SnippetTypesTable />: render rows per template type", async () => {
    const tpls = [
      { type: "blog:HeaderSnippet", title: "Header Snippet" },
      { type: "blog:FooterSnippet", title: "Footer Snippet" },
    ];
    renderWithRouter(
      <Route
        path="/admin/pages/new"
        element={<SnippetTypesTable isLoading={false} snippetTypes={tpls} />}
      />,
      "/admin/pages/new"
    );
    let link = screen.getByText("Header Snippet", { exact: false });
    expect(link.getAttribute("href")).equal(
      "/admin/snippets/new/blog:HeaderSnippet"
    );
    link = screen.getByText("Footer Snippet", { exact: false });
    expect(link.getAttribute("href")).equal(
      "/admin/snippets/new/blog:FooterSnippet"
    );
  });

  it("<SnippetTypeList />: list snippet types", async () => {
    renderWithRouter(
      <Route path="/admin/snippets" element={<SnippetTypeList />} />,
      "/admin/snippets"
    );
    await waitForLoadingLabel("loading snippet types...");
    const tpl = screen.getByText("Header Snippet");
    expect(tpl).not.equal(null);
  });
});
