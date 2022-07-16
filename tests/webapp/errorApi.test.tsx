import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageNotFound } from "../../src/webapp/ui/error404/components";
import { renderWithRouter, waitForTitle } from "./helpers";
import config from "./config";
import { ApiErrorUI } from "../../src/webapp/ui/errorApi/components";

describe("As a user, I have beautiful 404 error", () => {
  it("Render an error 404 compontent", async () => {
    const error = new Map();
    error.set("username", "Bad username of password");
    renderWithRouter(
      <Route path="/errs" element={<ApiErrorUI error={error} />} />,
      "/errs"
    );
    await waitForTitle("Errors encountered");
    const msg = screen.getByText("Bad username of password");
    expect(msg).not.equal(undefined);
  });
});
