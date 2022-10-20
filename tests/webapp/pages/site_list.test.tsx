import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import config from "../config";
import { Table, Tbody } from "@chakra-ui/react";
import {
  SiteList,
  SiteListButtons,
  SiteListTable,
  SiteRow,
} from "../../../src/webapp/ui/sites/site_list";

describe("As a user, I can list settings per sites", () => {
  before(async () => {
    await config.api.site.createSite("", "*", {
      default: true,
      secure: false,
      root_page_path: "/root",
    });
    await config.api.site.createSite("", "www.localhost", {
      default: false,
      secure: false,
      root_page_path: "/index",
    });
  });
  after(async () => {
    await config.api.site.deleteSite("", "www.localhost");
    await config.api.site.deleteSite("", "*");
  });

  it("Render a row for a page", async () => {
    const site = {
      hostname: "*",
      default: true,
      secure: false,
      root_page_path: "/root",
    };
    renderWithRouter(
      <Route
        path="/admin/siterow"
        element={
          <Table>
            <Tbody>
              <SiteRow site={site} />
            </Tbody>
          </Table>
        }
      />,
      "/admin/siterow"
    );

    let link = await screen.findByText("Edit", { exact: false });
    expect(link.getAttribute("href")).equal("/admin/sites/edit?hostname=*");
  });

  it("Render sites table from the API", async () => {
    renderWithRouter(
      <Route
        path="/admin/sites"
        element={<SiteListTable config={config} token="abc" />}
      />,
      "/admin/sites"
    );
    let links = await screen.findAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
    expect(links[0].nodeName).equal("TH");
    expect(links[1].nodeName).equal("A");
    expect(links[1].getAttribute("href")).equal("/admin/sites/edit?hostname=*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal(
      "/admin/sites/edit?hostname=www.localhost"
    );
  });

  it("Render sites lists from the API", async () => {
    renderWithRouter(
      <Route path="/admin/sites" element={<SiteList />} />,
      "/admin/sites"
    );
    let links = await screen.findAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
    expect(links[0].nodeName).equal("TH");
    expect(links[1].nodeName).equal("A");
    expect(links[1].getAttribute("href")).equal("/admin/sites/edit?hostname=*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal(
      "/admin/sites/edit?hostname=www.localhost"
    );
  });
  it("Redirect to the new site while clicking on the add button", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/sites" element={<SiteListButtons />} />
        <Route path="/admin/sites/new" element={<h4>New web site page</h4>} />
      </>,
      "/admin/sites"
    );
    let link = screen.getByText("Add new site", { exact: false });
    fireEvent.click(link);
    const newPage = screen.getByText("New web site page");
    expect(newPage.nodeName).equal("H4");
  });
});
