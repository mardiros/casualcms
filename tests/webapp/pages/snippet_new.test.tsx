import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "../helpers";
import { SnippetNew } from "../../../src/webapp/ui/pages/snippets/snippet_new";
import config from "../config";

describe("As a user, I can list snippet", () => {
  describe("<SnippetNew />", () => {
    it("Create the snippet using the web form", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/snippets/new/:snippetTypeName" element={<SnippetNew />} />
          <Route path="/admin/snippets" element={<div>Snippet list</div>} />
        </>,
        "/admin/snippets/new/blog:HeaderSnippet",
      );

      await waitForLoadingLabel("Loading form...");

      let input = screen.getByLabelText("Key", { exact: false });
      fireEvent.change(input, { target: { value: "header" } });

      input = screen.getByLabelText("Title", { exact: false });
      fireEvent.change(input, { target: { value: "Casual Blog" } });

      let button = screen.getByRole("button", { name: "Create Snippet" });
      fireEvent.click(button);

      await waitForPath("/admin/snippets");
      const snippets = await config.api.snippet.listSnippets("");
      expect(snippets._unsafeUnwrap()).eql([
        {
          key: "header",
          title: "Casual Blog",
          metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
        },
      ]);
      await config.api.snippet.deleteSnippet("", {
        key: "header",
        metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
      });
    });
  });
});
