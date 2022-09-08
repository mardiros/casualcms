import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import {
  PageRow,
  PageListTable,
  PageListButtons,
} from "../../src/webapp/ui/pages/page_list";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";
import config from "./config";
import { Table, Tbody } from "@chakra-ui/react";

describe("As a user, I can list pages", () => {
  before(async () => {
    await config.api.draft.createDraft(
      "",
      "casual:HomePage",
      {
        slug: "root",
        title: "Root Page",
        description: "describe the root home",
      },
      null
    );
    await config.api.draft.createDraft(
      "",
      "casual:HomePage",
      {
        slug: "home",
        title: "Home Page",
        description: "describe the home",
      },
      null
    );
    await config.api.draft.createDraft(
      "",
      "casual:SectionPage",
      {
        slug: "sub0",
        title: "Section Page",
        description: "first section",
      },
      "/home"
    );
    await config.api.draft.createDraft(
      "",
      "casual:SectionPage",
      {
        slug: "sub1",
        title: "Another Section Page",
        description: "second section",
      },
      "/home"
    );
  });
  after(async () => {
    await config.api.draft.deleteDraft("", "/home/sub1");
    await config.api.draft.deleteDraft("", "/home/sub0");
    await config.api.draft.deleteDraft("", "/home");
    await config.api.draft.deleteDraft("", "/root");
  });

  it("Render a row for a page", async () => {
    const page = {
      slug: "home",
      title: "Home Page",
      meta: {
        path: "/home",
        type: "casual:HomePage",
      },
    };
    renderWithRouter(
      <Route
        path="/admin/pagerow"
        element={
          <Table>
            <Tbody>
              <PageRow page={page} />
            </Tbody>
          </Table>
        }
      />,
      "/admin/pagerow"
    );
    await waitForLoadingLabel("Loading pages list");

    let link = screen.getByText("Edit", { exact: false });
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/admin/pages/edit?page=%2Fhome");

    link = screen.getByText("View", { exact: false });
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/home");

    link = screen.getByTestId("View child pages");
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/admin/pages/?parent=%2Fhome");
  });

  it("Render root pages table from the API", async () => {
    renderWithRouter(
      <Route
        path="/admin/pages"
        element={
          <PageListTable
            curPage={null}
            parentPath={null}
            config={config}
            token=""
          />
        }
      />,
      "/admin/pages"
    );
    await waitForLoadingLabel("Loading pages list");
    let links = screen.getAllByText("Edit", { exact: false });

    expect(links.length).equal(3);
  });

  it("Render sub pages table from the API", async () => {
    renderWithRouter(
      <Route
        path="/admin/pages"
        element={
          <PageListTable
            curPage={null}
            parentPath="/home"
            config={config}
            token=""
          />
        }
      />,
      "/admin/pages?parent=/home"
    );
    await waitForLoadingLabel("Loading pages list");
    let links = screen.getAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
  });

  it("Redirect to the new page while clicking on the add button", async () => {
    const page = {
      meta: {
        path: "/home",
        type: "casual:HomePage",
        breadcrumb: [],
      },
      slug: "home",
      title: "Home Page",
      description: "describe the home",
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<PageListButtons curPage={page} subPages={[]} />}
        />
        <Route path="/admin/pages/new" element={<h4>New page page</h4>} />
      </>,
      "/admin/pages"
    );
    let link = screen.getByText("Add new page", { exact: false });
    fireEvent.click(link);
    const newPage = screen.getByText("New page page");
    expect(newPage.nodeName).equal("H4");
  });

  it("Render a delete button if there is no child pages", async () => {
    const page = {
      meta: {
        path: "/home/sub1",
        type: "casual:HomePage",
        breadcrumb: [
          {
            path: "/home",
            title: "home",
            slug: "home",
          },
          {
            path: "/home/sub1",
            title: "sub",
            slug: "sub1",
          },
        ],
      },
      slug: "sub1",
      title: "sub",
      description: "",
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/pages/btn"
          element={<PageListButtons curPage={page} subPages={[]} />}
        />
        <Route path="/admin/pages" element={<h4>Page list</h4>} />
      </>,
      "/admin/pages/btn"
    );

    let link = screen.getByText("Delete this page");
    fireEvent.click(link);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    const newPage = await screen.findByText("Page list");
    expect(newPage.nodeName).equal("H4");

    const subList = await config.api.draft.listDrafts("", "/home");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          path: "/home/sub0",
          type: "casual:SectionPage",
        },
        slug: "sub0",
        title: "Section Page",
      },
    ]);
  });
});
