import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { PageDeletePopoverForm } from "../../src/webapp/ui/pages/page_delete";

describe("As a user, I can delete a page", () => {
  before(async () => {
    await config.api.page.createPage(
      "",
      "casual:HomePage",
      {
        slug: "home",
        title: "Home Page",
        description: "describe the home",
      },
      null
    );
    await config.api.page.createPage(
      "",
      "casual:SectionPage",
      {
        slug: "sub0",
        title: "Section Page",
        description: "first section",
      },
      "/home"
    );
    await config.api.page.createPage(
      "",
      "casual:SectionPage",
      {
        slug: "sub1",
        title: "Another Section Page",
        description: "second section",
      },
      "/home"
    );
  });
  after(async () => {
    await config.api.page.deletePage("", "/home/sub1");
    await config.api.page.deletePage("", "/home/sub0");
    await config.api.page.deletePage("", "/home");
  });

  it("Delete a page", async () => {
    const page = {
      slug: "sub1",
      title: "Section Page",
      description: "first section",
      meta: {
        path: "/home/sub1",
        type: "casual:HomePage",
        breadcrumb: [
          {
            path: "/home",
            title: "home",
            slug: "home",
          },
          {
            path: "/home/sub1",
            title: "sub",
            slug: "sub1",
          },
        ],
      },
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/popin"
          element={<PageDeletePopoverForm curPage={page} />}
        />
        <Route path="/admin/pages" element={<h4>Page list</h4>} />
      </>,
      "/admin/popin"
    );
    let link = screen.getByText("Delete this page");
    fireEvent.click(link);

    let subList = await config.api.page.listPages("", "/home");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          path: "/home/sub0",
          type: "casual:SectionPage",
        },
        slug: "sub0",
        title: "Section Page",
      },
      {
        meta: {
          path: "/home/sub1",
          type: "casual:SectionPage",
        },
        slug: "sub1",
        title: "Another Section Page",
      },
    ]);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    subList = await config.api.page.listPages("", "/home");
    expect(subList._unsafeUnwrap()).eql([
      {
        meta: {
          path: "/home/sub0",
          type: "casual:SectionPage",
        },
        slug: "sub0",
        title: "Section Page",
      },
    ]);
  });
});
