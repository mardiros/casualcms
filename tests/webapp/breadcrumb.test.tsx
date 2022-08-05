import { expect } from "chai";
import React from "react";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import { Route } from "react-router-dom";
import { PageBreadcrumb } from "../../src/webapp/ui/breadcrumb/components";
import { PageMeta } from "../../src/webapp/casualcms/domain/model";

describe("As a user, I can navigate throw the breadcrumb", () => {
  it("Render links using the breadcrumb of the page meta", async () => {

    const meta: PageMeta = {
      "path": "",
      "type": "",
      "breadcrumb": [
        {
          "path": "/home",
          "title": "Home page",
          "slug": "home",
        },
        {
          "path": "/home/cat",
          "title": "Categogo",
          "slug": "cat",
        },
      ],
    }
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageBreadcrumb meta={meta} />} />
      </>,
      "/admin/pages"
    );
    let link = screen.getByText("home");
    expect(link.getAttribute("href")).to.be.equal("/admin/pages/?parent=%2Fhome")

    link = screen.getByText("cat");
    expect(link.getAttribute("href")).to.be.equal("/admin/pages/?parent=%2Fhome%2Fcat")
  })
});
