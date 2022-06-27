import { expect } from "chai";
import React from "react";
import { screen, fireEvent, waitFor } from "@testing-library/react";
import { PageEdit } from "../../src/webapp/ui/page_edit/components";
import { renderWithRouter, waitForPath, waitForTitle } from "./helpers";

describe("As a user, I can create the root template", () => {
  it("redirect to the login form", async () => {
    renderWithRouter(
          <PageEdit />,
          "/page/new/:tpltype",
          "/page/new/blog:HomePage",
    );
    await waitForTitle("HomePage");

    let input = screen.getByLabelText("Title", {exact: false});
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "Welcome Home" } });

    input = screen.getByLabelText("Description", {exact: false});
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "My home page" } });

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

    let title = screen.getByLabelText("Pages", {exact: false});
    expect(title).not.equal(null);

    let page = screen.getByLabelText("Welcome Home", {exact: false});
    expect(page).not.equal(null);
    expect(page.getAttribute("href")).equal("/admin/pages/");


  });
});
