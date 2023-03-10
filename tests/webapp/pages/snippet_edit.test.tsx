import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "../helpers";
import config from "../config";
import { SnippetList } from "../../../src/webapp/ui/pages/snippets/snippet_list";
import { SnippetEdit } from "../../../src/webapp/ui/pages/snippets/snippet_edit";

describe("As a user, I can edit existing snippet", () => {
  before(async () => {
    await config.api.snippet.createSnippet("", "blog:HeaderSnippet", {
      key: "header",
      title: "Casual Blog",
    });
  });
  after(async () => {
    await config.api.snippet.deleteSnippet("", {
      key: "header",
      metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
    });
  });

  describe("<SnippetEdit />", async () => {
    it("Load the snippet in an edition form", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/snippets/snippetTypeName" element={<SnippetList />} />
          <Route
            path="/admin/snippets/edit/:snippetTypeName/:snippetKey"
            element={<SnippetEdit />}
          />
        </>,
        "/admin/snippets/edit/blog:HeaderSnippet/header",
      );

      await waitForLoadingLabel("Loading form...");

      let input = screen.getByLabelText("Key", { exact: false });
      expect(input.getAttribute("value")).equal("header");

      input = screen.getByLabelText("Title", { exact: false });
      expect(input.getAttribute("value")).equal("Casual Blog");
    });

    it("Update snippet using the edition form", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/snippets" element={<SnippetList />} />
          <Route
            path="/admin/snippets/edit/:snippetTypeName/:snippetKey"
            element={<SnippetEdit />}
          />
        </>,
        "/admin/snippets/edit/blog:HeaderSnippet/header",
      );

      await waitForLoadingLabel("Loading form...");

      let input = screen.getByLabelText("Title", { exact: false });
      fireEvent.change(input, { target: { value: "New Value" } });

      let button = screen.getByRole("button", { name: "Save" });
      expect(button).not.equal(null);
      fireEvent.click(button);

      await waitForPath("/admin/snippets");

      const snippet = await config.api.snippet.showSnippet("", "header");
      expect(snippet.isOk()).equal(true);
      const snip = snippet.unwrapOr({ title: "" });
      expect(snip.title).equal("New Value");
    });
  });
});
