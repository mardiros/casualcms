import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import config from "../config";
import { Table, Tbody } from "@chakra-ui/react";
import {
  SnippetList,
  SnippetListButtons,
  SnippetListTable,
  SnippetRow,
} from "../../../src/webapp/ui/pages/snippets/snippet_list";

describe("As a user, I can list snippet", () => {
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

  describe("<SnippetRow />", () => {
    it("Render a row for a snippet", async () => {
      const snippet = {
        key: "header",
        metadata: { type: "blog:HeaderSnippet", title: "Header Snippet" },
      };

      renderWithRouter(
        <Route
          path="/admin/snippetrow"
          element={
            <Table>
              <Tbody>
                <SnippetRow snippet={snippet} />
              </Tbody>
            </Table>
          }
        />,
        "/admin/snippetrow",
      );

      let link = await screen.findByText("Edit", { exact: false });
      expect(link.getAttribute("href")).equal(
        "/admin/snippets/edit/blog:HeaderSnippet/header",
      );
    });
  });
  describe("<SnippetListTable />", () => {
    it("Render snippets table from the API", async () => {
      renderWithRouter(
        <Route
          path="/admin/snippets"
          element={<SnippetListTable config={config} token="x" />}
        />,
        "/admin/snippets",
      );
      let links = await screen.findAllByText("Edit", { exact: false });
      expect(links.length).equal(3);
    });
  });

  describe("<SnippetList />", () => {
    it("Render snippet lists from the API", async () => {
      renderWithRouter(
        <Route path="/admin/snippets" element={<SnippetList />} />,
        "/admin/snippets",
      );
      let links = await screen.findAllByText("Edit", { exact: false });
      expect(links.length).equal(3);
    });
    it("Redirect to the new snippet while clicking on the add button", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/snippets" element={<SnippetListButtons />} />
          <Route path="/admin/snippets/new" element={<h4>New snippet page</h4>} />
        </>,
        "/admin/snippets",
      );
      let link = screen.getByText("Add new snippet", { exact: false });
      fireEvent.click(link);
      const newPage = screen.getByText("New snippet page");
      expect(newPage.nodeName).equal("H4");
    });
  });
});
