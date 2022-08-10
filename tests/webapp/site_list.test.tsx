import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { Table, Tbody } from "@chakra-ui/react";
import {
  SiteList,
  SiteListTable,
  SiteRow,
} from "../../src/webapp/ui/sites/site_list";

describe("As a user, I can list sites", () => {
  // before(async () => {
  //   await config.api.site.createSite(
  //     "",
  //     "www.example.net",
  //     {
  //       default: true,
  //       root_page_path: "/root",
  //     },
  //   );
  // });
  // after(async () => {
  //   await config.api.page.deleteSite("", "www.example.net");
  // });

  it("Render a row for a page", async () => {
    const site = {
      hostname: "*",
      default: true,
      root_page_path: "/index",
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
    expect(link.getAttribute("href")).equal("/admin/site/edit?site=*");
  });

  it("Render sites table from the API", async () => {
    renderWithRouter(
      <Route
        path="/admin/sites"
        element={<SiteListTable config={config} token="" />}
      />,
      "/admin/sites"
    );
    let links = await screen.findAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
    expect(links[0].nodeName).equal("TH");
    expect(links[1].nodeName).equal("A");
    expect(links[1].getAttribute("href")).equal("/admin/site/edit?site=*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal(
      "/admin/site/edit?site=www.localhost"
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
    expect(links[1].getAttribute("href")).equal("/admin/site/edit?site=*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal(
      "/admin/site/edit?site=www.localhost"
    );
  });
});
