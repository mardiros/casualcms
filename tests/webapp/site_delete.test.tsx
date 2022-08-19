import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { SiteDeletePopoverForm } from "../../src/webapp/ui/sites/site_delete";

describe("As a user, I can delete a site", () => {
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

  it("Delete a site", async () => {
    const site = {
      hostname: "www.localhost",
      default: false,
      secure: false,
      root_page_path: "/index",
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/popin"
          element={<SiteDeletePopoverForm curSite={site} />}
        />
        <Route path="/admin/sites" element={<h4>Site list</h4>} />
      </>,
      "/admin/popin"
    );
    let link = screen.getByText("Delete this site");
    fireEvent.click(link);

    let subList = await config.api.site.listSites("");
    expect(subList._unsafeUnwrap()).eql([
      {
        default: true,
        hostname: "*",
        root_page_path: "/root",
        secure: false,
      },
      {
        default: false,
        hostname: "www.localhost",
        root_page_path: "/index",
        secure: false,
      },
    ]);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    subList = await config.api.site.listSites("");
    expect(subList._unsafeUnwrap()).eql([
      {
        default: true,
        hostname: "*",
        root_page_path: "/root",
        secure: false,
      },
    ]);
  });
});
