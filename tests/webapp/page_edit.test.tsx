import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageEdit } from "../../src/webapp/ui/page_edit/components";
import { PageList } from "../../src/webapp/ui/page_list/components";
import {
  renderWithRouter,
  waitForLoadingLabel,
  waitForPath,
} from "./helpers";
import config from "./config";

describe("As a user, I can edit existing pages", () => {
  before(async () => {
    await config.api.page.createPage(
      "",
      "casual:HomePage",
      {
        id: "id-home",
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
        id: "id-sub0",
        slug: "sub0",
        title: "Section Page",
        description: "first section",
      },
      "/home"
    );
  });
  after(async () => {
    await config.api.page.deletePage("", "/home/sub0");
    await config.api.page.deletePage("", "/home");
  });

  it("Load the root page in an edition form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageList />}></Route>
        <Route path="/admin/page/edit" element={<PageEdit />}></Route>
      </>,
      "/admin/page/edit?page=/home"
    );

    await waitForLoadingLabel("loading page and page template...");

    let input = screen.getByLabelText("Slug", { exact: false });
    expect(input.getAttribute("value")).equal("home");

    input = screen.getByLabelText("Title", { exact: false });
    expect(input.getAttribute("value")).equal("Home Page");
  });

  it("Load the subpage page in an edition form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageList />}></Route>
        <Route path="/admin/page/edit" element={<PageEdit />}></Route>
      </>,
      "/admin/page/edit?page=/home/sub0"
    );

    await waitForLoadingLabel("loading page and page template...");

    let input = screen.getByLabelText("Slug", { exact: false });
    expect(input.getAttribute("value")).equal("sub0");

    input = screen.getByLabelText("Title", { exact: false });
    expect(input.getAttribute("value")).equal("Section Page");

    input = screen.getByLabelText("Description", { exact: false });
    expect(input.getAttribute("value")).equal("first section");
  });

  it("Load the root page in an edition form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/pages" element={<PageList />}></Route>
        <Route path="/admin/page/edit" element={<PageEdit />}></Route>
      </>,
      "/admin/page/edit?page=/home"
    );

    await waitForLoadingLabel("loading page and page template...");

    let input = screen.getByLabelText("Title", { exact: false });
    fireEvent.change(input, { target: { value: "New Value" } });

    input = screen.getByLabelText("Body", { exact: false });
    fireEvent.change(input, { target: { value: "Long time ago" } });

    let button = screen.getByText("Submit");
    expect(button).not.equal(null);
    fireEvent.click(button);

    await waitForPath("/admin/pages");

    const page = await config.api.page.showPage("", "/home");
    expect(page.isOk()).equal(true);
    expect(page.unwrapOr({ title: "" }).title).equal("New Value");
  });
});
