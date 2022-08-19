import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { SiteEdit } from "../../src/webapp/ui/sites/site_edit";
import { SiteList } from "../../src/webapp/ui/sites/site_list";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";
import config from "./config";

describe("As a user, I can edit existing sites", () => {
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

  it("Load the site in an edition form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/sites" element={<SiteList />}></Route>
        <Route path="/admin/sites/edit" element={<SiteEdit />}></Route>
      </>,
      "/admin/sites/edit?hostname=www.localhost"
    );

    let input = await screen.findByLabelText("hostname", { exact: false });
    expect(input.getAttribute("value")).equal("www.localhost");
  });
});
