import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { PartialPage } from "../../src/webapp/casualcms/domain/model";
import { screen, fireEvent } from "@testing-library/react";
import { PageNew } from "../../src/webapp/ui/page_new/components";
import { PageRow, PageList } from "../../src/webapp/ui/page_list/components";
import { renderWithRouter, waitForPath, waitForTitle } from "./helpers";

describe("As a user, I can list pages", () => {
  it("Create the root page from the web form", async () => {
    const page = {
      slug: "home",
      title: "Home Page",
      path: "/home",
      type: "casual:HomePage",
    }
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageRow page={page} />}></Route>
      </>,
      "/admin/pages"
    );
    await waitForTitle("Home Page");

    let link = screen.getByText("Edit", { exact: false });
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/admin/page/edit/home");

    link = screen.getByText("View", { exact: false });
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/home");

    link = screen.getByDisplayValue("view child pages", { exact: false });
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/home");

  })
})
