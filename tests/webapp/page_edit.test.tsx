import { expect } from "chai";
import React from "react";
import { screen, fireEvent, waitFor, getDefaultNormalizer } from "@testing-library/react";
import { PageEdit } from "../../src/webapp/ui/page_edit/components";
import { renderWithRouter, waitForTitle } from "./helpers";

describe("As a user, I can create the root template", () => {
  it("redirect to the login form", async () => {
    renderWithRouter(
          <PageEdit />,
          "/page/new/:tpltype",
          "/page/new/blog:HomePage",
    );
    await waitForTitle("HomePage");

    let input = screen.getByLabelText("Slug", {exact: false});
    expect(input).not.equal(null);

    input = screen.getByLabelText("Title", {exact: false});
    expect(input).not.equal(null);

    input = screen.getByLabelText("Description", {exact: false});
    expect(input).not.equal(null);

    input = screen.getByLabelText("Body", {exact: false});
    expect(input).not.equal(null);

    // does now work like that, it raise
    // input = screen.getByLabelText("Id", {exact: false});
    // expect(input).equal(null);

    let button = screen.getByText("Submit");
    expect(button).not.equal(null);
    // fireEvent.click(button);
    // await waitFor(
    //   async () => {
    //     let errMess = screen.getByText("bla bla");
    //     expect(errMess).not.equal(null);
    //   },
    //   { interval: 25, timeout: 100 }
    // );

  });
});
