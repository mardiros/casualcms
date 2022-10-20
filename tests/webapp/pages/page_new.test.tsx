import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageNew } from "../../../src/webapp/ui/pages/pages/page_new";
import { renderWithRouter, waitForLoadingLabel, waitForPath } from "../helpers";
import config from "../config";

describe("As a user, I can create the root page", () => {
  it("<PageNew />: Create the root page from the web form", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/pages/new/:pageTypeName"
          element={<PageNew />}
        ></Route>
        <Route path="/admin/pages" element={<div>Page list</div>}></Route>
      </>,
      "/admin/pages/new/casual:HomePage"
    );

    await waitForLoadingLabel("Loading pages list");
    await waitForLoadingLabel("Loading form...");

    let input = screen.getByLabelText("Slug", { exact: false });
    fireEvent.change(input, { target: { value: "home" } });

    input = screen.getByLabelText("Title", { exact: false });
    fireEvent.change(input, { target: { value: "Welcome Home" } });

    input = screen.getByLabelText("Body", { exact: false });
    fireEvent.change(input, { target: { value: "lorem ipsum" } });

    // does now work like that, it raise
    // input = screen.getByLabelText("Id", {exact: false});
    // expect(input).equal(null);

    let button = screen.getByText("Submit");
    fireEvent.click(button);

    await waitForPath("/admin/pages");
    const pages = await config.api.page.listDrafts("", null);
    expect(pages._unsafeUnwrap()).eql([
      {
        metadata: {
          path: "/home",
          type: "casual:HomePage",
          title: "Home Page",
        },
        slug: "home",
        title: "Welcome Home",
      },
    ]);
    await config.api.page.deleteDraft("", "/home");
  });
});
