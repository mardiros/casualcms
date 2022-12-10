import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import config from "../config";
import { Table, Tbody } from "@chakra-ui/react";
import {
  SettingSiteList,
  SettingSiteListTable,
  SettingSiteRow,
} from "../../../src/webapp/ui/pages/settings/settings_sites_list";

describe("As a user, I can list sites in settings", () => {
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

  it("Render a row for a site setting", async () => {
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
              <SettingSiteRow site={site} />
            </Tbody>
          </Table>
        }
      />,
      "/admin/siterow",
    );

    let link = await screen.findByText("Edit", { exact: false });
    expect(link.getAttribute("href")).equal("/admin/settings/*");
  });

  it("Render sites table from the API", async () => {
    renderWithRouter(
      <Route
        path="/admin/sites"
        element={<SettingSiteListTable config={config} token="x" />}
      />,
      "/admin/sites",
    );
    let links = await screen.findAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
    expect(links[0].nodeName).equal("TH");
    expect(links[1].nodeName).equal("A");
    expect(links[1].getAttribute("href")).equal("/admin/settings/*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal("/admin/settings/www.localhost");
  });

  it("Render sites lists from the API", async () => {
    renderWithRouter(
      <Route path="/admin/sites" element={<SettingSiteList />} />,
      "/admin/sites",
    );
    let links = await screen.findAllByText("Edit", { exact: false });
    expect(links.length).equal(3);
    expect(links[0].nodeName).equal("TH");
    expect(links[1].nodeName).equal("A");
    expect(links[1].getAttribute("href")).equal("/admin/settings/*");
    expect(links[2].nodeName).equal("A");
    expect(links[2].getAttribute("href")).equal("/admin/settings/www.localhost");
  });
});
