import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { SnippetDeletePopoverForm } from "../../src/webapp/ui/snippets/snippet_delete";

describe("As a user, I can delete a snippet", () => {
  before(async () => {
    await config.api.snippet.createSnippet("", "blog:HeaderSnippet", {
      key: "header",
    });
    await config.api.snippet.createSnippet("", "blog:HeaderSnippet", {
      key: "alt-header",
    });
  });
  after(async () => {
    await config.api.snippet.deleteSnippet("", {
      key: "alt-header",
      meta: { type: "blog:HeaderSnippet" },
    });
    await config.api.snippet.deleteSnippet("", {
      key: "header",
      meta: { type: "blog:HeaderSnippet" },
    });
  });

  it("Delete a snippet", async () => {
    const snippet = {
      key: "header",
      meta: {
        type: "blog:HeaderSnippet",
      },
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/snippets/blog:HeaderSnippet"
          element={<SnippetDeletePopoverForm curSnippet={snippet} />}
        />
        <Route path="/admin/snippets" element={<h4>Snippet list</h4>} />
      </>,
      "/admin/snippets/blog:HeaderSnippet"
    );
    let link = screen.getByText("Delete this snippet");
    fireEvent.click(link);

    let subList = await config.api.snippet.listSnippets("");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          type: "blog:HeaderSnippet",
        },
        key: "header",
      },
      {
        meta: {
          type: "blog:HeaderSnippet",
        },
        key: "alt-header",
      },
    ]);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    subList = await config.api.snippet.listSnippets("");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          type: "blog:HeaderSnippet",
        },
        key: "alt-header",
      },
    ]);
  });
});
