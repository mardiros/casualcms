import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { SiteNew } from "../../../src/webapp/ui/pages/sites/site_new";
import { SiteList } from "../../../src/webapp/ui/pages/sites/site_list";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "../helpers";
import config from "../config";

describe("As a user, I can create a new site", () => {
  before(async () => {
    await config.api.page.createDraft(
      "",
      "casual:HomePage",
      {
        slug: "index",
        title: "Home Page",
        description: "home sweet home",
      },
      null
    );
  });
  after(async () => {
    await config.api.page.deleteDraft("", "/index");
  });

  it("<SiteNew />: Create a site", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/sites/new" element={<SiteNew />}></Route>
        <Route path="/admin/sites" element={<h4>Site list</h4>}></Route>
      </>,
      "/admin/sites/new"
    );

    let input = screen.getByLabelText("Hostname", { exact: false });
    fireEvent.change(input, { target: { value: "www.example.net" } });

    input = screen.getByLabelText("Root page", { exact: false });
    fireEvent.change(input, { target: { value: "/index" } });

    let button = screen.getByRole("button", { name: "Create Site" });
    expect(button).not.equal(null);
    fireEvent.click(button);

    await waitForPath("/admin/sites");
    await screen.findByText("Site list");

    const sites = await config.api.site.listSites("");
    expect(sites.isOk()).equal(true);
    expect(sites._unsafeUnwrap()).eql([
      {
        default: false,
        hostname: "www.example.net",
        root_page_path: "/index",
        secure: false,
      },
    ]);

    await config.api.site.deleteSite("", "www.example.net");
  });
});
