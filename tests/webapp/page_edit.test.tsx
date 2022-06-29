import { expect } from "chai";
import React from "react";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { PageEdit } from "../../src/webapp/ui/page_edit/components";
import { PageList } from "../../src/webapp/ui/page_list/components";
import { renderWithRouter, waitForPath, waitForTitle } from "./helpers";

describe("As a user, I can create the root template", () => {
  it("Create the root page from the web form", async () => {
    renderWithRouter(
          <PageEdit />,
          "/admin/page/new/:tpltype",
          "/admin/page/new/blog:HomePage",
          <PageList />,
          "/admin/pages",
    );
    await waitForTitle("HomePage");

    let input = screen.getByLabelText("Title", {exact: false});
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "Welcome Home" } });

    input = screen.getByLabelText("Body", {exact: false});
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

    let link = screen.getByText("Welcome Home", {exact: false});
    expect(link).not.equal(null);
    expect(link.getAttribute("href")).equal("/admin/page/edit/root/");

  });
});