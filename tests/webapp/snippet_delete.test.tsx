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
      slug: "header",
    });
    await config.api.snippet.createSnippet("", "blog:HeaderSnippet", {
      slug: "alt-header",
    });
  });
  after(async () => {
    await config.api.snippet.deleteSnippet("", {
      slug: "alt-header",
      meta: { type: "blog:HeaderSnippet" },
    });
    await config.api.snippet.deleteSnippet("", {
      slug: "header",
      meta: { type: "blog:HeaderSnippet" },
    });
  });

  it("Delete a snippet", async () => {
    const snippet = {
      slug: "header",
      meta: {
        type: "blog:HeaderSnippet",
      },
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/popin"
          element={<SnippetDeletePopoverForm curSnippet={snippet} />}
        />
        <Route path="/admin/snippets" element={<h4>Snippet list</h4>} />
      </>,
      "/admin/popin"
    );
    let link = screen.getByText("Delete this snippet");
    fireEvent.click(link);

    let subList = await config.api.snippet.listSnippets("");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          type: "blog:HeaderSnippet",
        },
        slug: "header",
      },
      {
        meta: {
          type: "blog:HeaderSnippet",
        },
        slug: "alt-header",
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
        slug: "alt-header",
      },
    ]);
  });
});
