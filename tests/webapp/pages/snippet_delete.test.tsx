import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import config from "../config";
import { SnippetDeletePopoverForm } from "../../../src/webapp/ui/snippets/snippet_delete";

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
      metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
    });
    await config.api.snippet.deleteSnippet("", {
      key: "header",
      metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
    });
  });

  it("<SnippetDeletePopoverForm />: Delete a snippet", async () => {
    const snippet = {
      key: "header",
      metadata: {
        type: "blog:HeaderSnippet",
        title: "Header Snippet",
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
        metadata: {
          type: "blog:HeaderSnippet",
          title: "Header Snippet",
        },
        key: "header",
      },
      {
        metadata: {
          type: "blog:HeaderSnippet",
          title: "Header Snippet",
        },
        key: "alt-header",
      },
    ]);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    subList = await config.api.snippet.listSnippets("");
    expect(subList._unsafeUnwrap()).eql([
      {
        metadata: {
          type: "blog:HeaderSnippet",
          title: "Header Snippet",
        },
        key: "alt-header",
      },
    ]);
  });
});
