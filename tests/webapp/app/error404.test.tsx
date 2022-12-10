import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { PageNotFound } from "../../../src/webapp/ui/pages/error_404";
import { renderWithRouter } from "../helpers";

describe("As a user, I have beautiful 404 error", () => {
  it("Render an error 404 compontent", async () => {
    renderWithRouter(<Route path="/e404" element={<PageNotFound />} />, "/e404");
    await screen.findByText("Page Not Found");
    const msg = screen.getByText("This is probably not a problem with npm.");
    expect(msg).not.equal(undefined);
  });
});
