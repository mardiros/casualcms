import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import { ApiErrorUI } from "../../../src/webapp/ui/components/error_api";

describe("As a user, I have beautiful api error", () => {
  describe("<ApiErrorUI />", () => {
    it("Render an error 404 compontent", async () => {
      const error = new Map();
      error.set("username", "Bad username of password");
      renderWithRouter(
        <Route path="/errs" element={<ApiErrorUI error={error} />} />,
        "/errs",
      );
      await screen.findByText("Errors encountered");
      const msg = screen.getByText("Bad username of password");
      expect(msg).not.equal(undefined);
    });
  });
});
