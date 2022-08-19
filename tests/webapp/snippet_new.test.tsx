import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "./helpers";
import { SnippetNew } from "../../src/webapp/ui/snippets/snippet_new";
import config from "./config";

describe("As a user, I can list snippet", () => {
  it("Create the snippet using the web form", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/snippets/new/:snippet_type"
          element={<SnippetNew />}
        ></Route>
        <Route path="/admin/snippets" element={<div>Snippet list</div>}></Route>
      </>,
      "/admin/snippets/new/blog:HeaderSnippet"
    );

    await waitForLoadingLabel("Loading form...");

    let input = screen.getByLabelText("Slug", { exact: false });
    fireEvent.change(input, { target: { value: "header" } });

    input = screen.getByLabelText("Title", { exact: false });
    fireEvent.change(input, { target: { value: "Casual Blog" } });

    let button = screen.getByText("Submit");
    fireEvent.click(button);

    await waitForPath("/admin/snippets");
    const snippets = await config.api.snippet.listSnippets("");
    expect(snippets._unsafeUnwrap()).eql([
      {
        slug: "header",
        title: "Casual Blog",
        meta: { type: "blog:HeaderSnippet" },
      },
    ]);
    await config.api.snippet.deleteSnippet("", "header");
  });
});
