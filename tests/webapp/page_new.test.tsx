import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageNew } from "../../src/webapp/ui/pages/page_new";
import { PageList } from "../../src/webapp/ui/pages/page_list";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "./helpers";
import config from "./config";

describe("As a user, I can create the root page", () => {
  it("Create the root page from the web form", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/page/new/:tpltype" element={<PageNew />}></Route>
        <Route path="/admin/pages" element={<PageList />}></Route>
      </>,
      "/admin/page/new/casual:HomePage"
    );

    await waitForLoadingLabel("Loading pages list");
    await waitForLoadingLabel("Loading form...");

    let input = screen.getByLabelText("Slug", { exact: false });
    expect(input).not.equal(null);
    fireEvent.change(input, { target: { value: "home" } });

    input = screen.getByLabelText("Title", { exact: false });
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
    await waitForLoadingLabel("preparing data...");
    await waitForLoadingLabel("Loading pages list");

    const edits = screen.getAllByText("Edit", { exact: false });
    expect(edits.length).equal(2);
    expect(edits[1].getAttribute("href")).equal(
      "/admin/page/edit?page=%2Fhome"
    );

    await config.api.page.deletePage("", "/home");
  });
});
