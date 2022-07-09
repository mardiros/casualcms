import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageNew } from "../../src/webapp/ui/page_new/components";
import { PageList } from "../../src/webapp/ui/page_list/components";
import { renderWithRouter, waitForPath, waitForTitle } from "./helpers";

describe("As a user, I can create the root template", () => {
  it("Create the root page from the web form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/page/new/:tpltype" element={<PageNew />}>
        </Route>
        <Route path="/admin/pages" element={<PageList />}>
        </Route>
      </>,
      "/admin/page/new/blog:HomePage",
    );

    await waitForTitle("HomePage");

    let input = screen.getByLabelText("Title", { exact: false });
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "Welcome Home" } });

    input = screen.getByLabelText("Body", { exact: false });
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "lorem ipsum" } });

    // does now work like that, it raise
    // input = screen.getByLabelText("Id", {exact: false});
    // expect(input).equal(null);

    let button = screen.getByText("Submit");
    expect(button).not.equal(null);
    fireEvent.click(button);
    await waitForPath("/admin/pages");
    await waitForTitle("Pages");

    let links = screen.getAllByText("Edit", { exact: false });
    console.log(links)
    let link = links[1];
    expect(link).not.equal(null);
    expect(link.getAttribute("href")).equal("/admin/page/edit/root/");

    link = screen.getAllByText("View", { exact: false })[1];
    expect(link).not.equal(null);
    expect(link.getAttribute("href")).equal("/");
  });
});
