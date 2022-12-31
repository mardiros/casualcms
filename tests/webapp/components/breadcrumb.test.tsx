import { expect } from "chai";
import React from "react";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import { Route } from "react-router-dom";
import {
  PageBreadcrumb,
  SiteBreadcrumb,
  SnippetBreadcrumb,
  SettingBreadcrumb,
} from "../../../src/webapp/ui/components/breadcrumb";
import { PageMeta } from "../../../src/webapp/casualcms/domain/model";

describe("As a user, I can navigate throw the breadcrumb", () => {
  describe("<PageBreadcrumb />", () => {
    it("Render links using the breadcrumb of the page meta", async () => {
      const metadata: PageMeta = {
        path: "",
        type: "",
        breadcrumb: {
          items: [
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
        },
      };
      const page = {
        metadata: metadata,
      };
      renderWithRouter(
        <>
          <Route path="/admin/pages" element={<PageBreadcrumb page={page} />} />
        </>,
        "/admin/pages",
      );
      let link = screen.getByText("home");
      expect(link.getAttribute("href")).to.be.equal("/admin/pages/?parent=%2Fhome");

      link = screen.getByText("cat");
      expect(link.getAttribute("href")).to.be.equal(
        "/admin/pages/?parent=%2Fhome%2Fcat",
      );
    });
    it("Render links using the breadcrumb of the page meta with an appending text", async () => {
      const metadata: PageMeta = {
        path: "",
        type: "",
        breadcrumb: {
          items: [
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
        },
      };
      const page = { metadata: metadata };
      renderWithRouter(
        <>
          <Route
            path="/admin/pages"
            element={<PageBreadcrumb page={page} title="New page" />}
          />
        </>,
        "/admin/pages",
      );
      let link = screen.getByText("home");
      expect(link.getAttribute("href")).to.be.equal("/admin/pages/?parent=%2Fhome");

      link = screen.getByText("cat");
      expect(link.getAttribute("href")).to.be.equal(
        "/admin/pages/?parent=%2Fhome%2Fcat",
      );

      const title = screen.getByText("New page");
      expect(title.nodeName).to.be.equal("SPAN");
    });
  });

  describe("<SiteBreadcrumb />", () => {
    it("Render links using the site of the snippet", async () => {
      const site = {
        hostname: "www",
        default: true,
        secure: false,
        root_page_path: "",
      };
      renderWithRouter(
        <>
          <Route path="/admin/sites/edit" element={<SiteBreadcrumb site={site} />} />
        </>,
        "/admin/sites/edit",
      );
      let link = screen.getByText("www");
      expect(link.getAttribute("href")).to.be.equal("/admin/sites/edit?hostname=www");
    });

    it("Render links using the breadcrumb of the snippet", async () => {
      renderWithRouter(
        <>
          <Route
            path="/admin/sites/new"
            element={<SiteBreadcrumb title="new site" />}
          />
        </>,
        "/admin/sites/new",
      );
      const title = screen.getByText("new site");
      expect(title.nodeName).to.be.equal("SPAN");
    });
  });
  describe("<SnippetBreadcrumb />", () => {
    it("Render links using the breadcrumb of the snippet", async () => {
      const snippet = {
        key: "header",
        metadata: { type: "HeaderSnippet", title: "Header Snippet" },
      };
      renderWithRouter(
        <>
          <Route
            path="/admin/snippets/edit/-"
            element={<SnippetBreadcrumb snippet={snippet} />}
          />
        </>,
        "/admin/snippets/edit/-",
      );
      let link = screen.getByText("header");
      expect(link.getAttribute("href")).to.be.equal(
        "/admin/snippets/edit/HeaderSnippet/header",
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
        "/admin/snippets/new",
      );
      const title = screen.getByText("new snippet");
      expect(title.nodeName).to.be.equal("SPAN");
    });

    it("Render links using the breadcrumb of the settings", async () => {
      renderWithRouter(
        <>
          <Route
            path="/admin/settings/:hostname/:settingKey/edit"
            element={<SettingBreadcrumb hostname="www" title="contact" />}
          />
        </>,
        "/admin/settings/www/contact/edit",
      );
      const link = screen.getByText("www");
      expect(link.nodeName).to.be.equal("A");
      expect(link.getAttribute("href")).to.be.equal("/admin/settings/www");

      const title = screen.getByText("contact");
      expect(title.nodeName).to.be.equal("SPAN");
    });
  });
});
