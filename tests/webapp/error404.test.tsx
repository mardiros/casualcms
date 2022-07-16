import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageNotFound } from "../../src/webapp/ui/error404/components";
import { renderWithRouter, waitForTitle } from "./helpers";
import config from "./config";

describe("As a user, I have beautiful 404 error", () => {
  it("Render an error 404 compontent", async () => {
    renderWithRouter(
      <Route path="/e404" element={<PageNotFound />} />,
      "/e404"
    )
    await waitForTitle("Page Not Found");
    const msg = screen.getByText("This is probably not a problem with npm.");
    expect(msg).not.equal(undefined);

  })
})
