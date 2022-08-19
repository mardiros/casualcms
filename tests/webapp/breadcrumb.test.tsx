import { expect } from "chai";
import React from "react";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import { Route } from "react-router-dom";
import {
  PageBreadcrumb,
  SiteBreadcrumb,
  SnippetBreadcrumb,
} from "../../src/webapp/ui/layout/breadcrumb";
import { PageMeta } from "../../src/webapp/casualcms/domain/model";

describe("As a user, I can navigate throw the breadcrumb", () => {
  it("Render links using the breadcrumb of the page meta", async () => {
    const meta: PageMeta = {
      path: "",
      type: "",
      breadcrumb: [
        {
          path: "/home",
          title: "Home page",
          slug: "home",
        },
        {
          path: "/home/cat",
          title: "Categogo",
          slug: "cat",
        },
      ],
    };
    const page = {
      meta: meta,
    };
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageBreadcrumb page={page} />} />
      </>,
      "/admin/pages"
    );
    let link = screen.getByText("home");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/pages/?parent=%2Fhome"
    );

    link = screen.getByText("cat");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/pages/?parent=%2Fhome%2Fcat"
    );
  });
  it("Render links using the breadcrumb of the page meta with an appending text", async () => {
    const meta: PageMeta = {
      path: "",
      type: "",
      breadcrumb: [
        {
          path: "/home",
          title: "Home page",
          slug: "home",
        },
        {
          path: "/home/cat",
          title: "Categogo",
          slug: "cat",
        },
      ],
    };
    const page = { meta: meta };
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<PageBreadcrumb page={page} title="New page" />}
        />
      </>,
      "/admin/pages"
    );
    let link = screen.getByText("home");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/pages/?parent=%2Fhome"
    );

    link = screen.getByText("cat");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/pages/?parent=%2Fhome%2Fcat"
    );

    let title = screen.getByText("New page");
    expect(title).to.not.be.equal(undefined);
  });

  it("Render links using the site of the snippet", async () => {
    const site = {
      hostname: "www",
      default: true,
      secure: false,
      root_page_path: "",
    };
    renderWithRouter(
      <>
        <Route
          path="/admin/sites/edit"
          element={<SiteBreadcrumb site={site} />}
        />
      </>,
      "/admin/sites/edit"
    );
    let link = screen.getByText("www");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/sites/edit?hostname=www"
    );
  });

  it("Render links using the breadcrumb of the snippet", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/sites/new"
          element={<SiteBreadcrumb title="new site" />}
        />
      </>,
      "/admin/sites/new"
    );
    let link = screen.getByText("new site");
    expect(link.getAttribute("href")).to.be.equal("#");
  });

  it("Render links using the breadcrumb of the snippet", async () => {
    const snippet = { slug: "header", meta: { type: "Header" } };
    renderWithRouter(
      <>
        <Route
          path="/admin/snippets/edit"
          element={<SnippetBreadcrumb snippet={snippet} />}
        />
      </>,
      "/admin/snippets/edit"
    );
    let link = screen.getByText("header");
    expect(link.getAttribute("href")).to.be.equal(
      "/admin/snippets/edit?slug=header"
    );
  });

  it("Render links using the breadcrumb of the snippet", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/snippets/new"
          element={<SnippetBreadcrumb title="new snippet" />}
        />
      </>,
      "/admin/snippets/new"
    );
    let link = screen.getByText("new snippet");
    expect(link.getAttribute("href")).to.be.equal("#");
  });
});
