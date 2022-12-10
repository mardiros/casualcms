import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { SiteEdit } from "../../../src/webapp/ui/pages/sites/site_edit";
import { SiteList } from "../../../src/webapp/ui/pages/sites/site_list";
import { renderWithRouter, waitForLoadingLabel } from "../helpers";
import config from "../config";

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
        <Route path="/admin/sites" element={<SiteList />} />
        <Route path="/admin/sites/edit" element={<SiteEdit />} />
      </>,
      "/admin/sites/edit?hostname=www.localhost",
    );

    let input = await screen.findByLabelText("hostname", { exact: false });
    expect(input.getAttribute("value")).equal("www.localhost");
  });

  it("Update the site using the edition form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/sites" element={<SiteList />} />
        <Route path="/admin/sites/edit" element={<SiteEdit />} />
      </>,
      "/admin/sites/edit?hostname=www.localhost",
    );

    let input = await screen.findByLabelText("hostname", { exact: false });
    fireEvent.change(input, { target: { value: "www2.localhost" } });

    input = await screen.findByLabelText("Root Page", { exact: false });
    fireEvent.change(input, { target: { value: "/new-index" } });

    let button = screen.getByText("Submit");
    fireEvent.click(button);

    const sites = await config.api.site.listSites("");
    expect(sites.isOk()).equal(true);
    expect(sites._unsafeUnwrap()).eql([
      {
        hostname: "*",
        default: true,
        secure: false,
        root_page_path: "/root",
      },
      {
        hostname: "www2.localhost",
        root_page_path: "/new-index",
        default: false,
        secure: false,
      },
    ]);
    // delete per hostname...
    await config.api.site.deleteSite("", "www2.localhost");
  });
});
