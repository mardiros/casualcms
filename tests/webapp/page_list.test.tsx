import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import {
  PageRow,
  PageListTable,
} from "../../src/webapp/ui/pages/page_list";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";
import config from "./config";
import { Table, Tbody } from "@chakra-ui/react";

describe("As a user, I can list pages", () => {
  before(async () => {
    await config.api.page.createPage(
      "",
      "casual:HomePage",
      {
        slug: "root",
        title: "Root Page",
        description: "describe the root home",
      },
      null
    );
    await config.api.page.createPage(
      "",
      "casual:HomePage",
      {
        slug: "home",
        title: "Home Page",
        description: "describe the home",
      },
      null
    );
    await config.api.page.createPage(
      "",
      "casual:SectionPage",
      {
        slug: "sub0",
        title: "Section Page",
        description: "first section",
      },
      "/home"
    );
    await config.api.page.createPage(
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
    await config.api.page.deletePage("", "/home/sub1");
    await config.api.page.deletePage("", "/home/sub0");
    await config.api.page.deletePage("", "/home");
    await config.api.page.deletePage("", "/root");
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
    expect(link.getAttribute("href")).equal("/admin/page/edit?page=%2Fhome");

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
        element={<PageListTable parentPath={null} config={config} token="" />}
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
        element={<PageListTable parentPath="/home" config={config} token="" />}
      />,
      "/admin/pages?parent=/home"
    );
    await waitForLoadingLabel("Loading pages list");
    let links = screen.getAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
  });
});
