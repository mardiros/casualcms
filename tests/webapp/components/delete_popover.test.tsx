import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "../helpers";
import { DeletePopoverForm } from "../../../src/webapp/ui/components/confirm";

describe("As a user, I can confirm deletion", () => {
  it("Display a Confirm Deletion popin", async () => {
    let deleted = false;
    const onSubmit = () => {
      deleted = true;
    };

    renderWithRouter(
      <Route
        path="/admin/popin"
        element={
          <DeletePopoverForm button_label="Delete this stuff" onSubmit={onSubmit} />
        }
      />,
      "/admin/popin",
    );
    let link = screen.getByText("Delete this stuff");
    fireEvent.click(link);
    expect(deleted).equal(false);
    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);
    expect(deleted).equal(true);
  });

  it("Cancel while confirming Deletion popin", async () => {
    let deleted = false;
    const onSubmit = () => {
      deleted = true;
    };

    renderWithRouter(
      <Route
        path="/admin/popin"
        element={
          <DeletePopoverForm button_label="Delete this stuff" onSubmit={onSubmit} />
        }
      />,
      "/admin/popin",
    );
    let link = screen.getByText("Delete this stuff");
    fireEvent.click(link);
    expect(deleted).equal(false);
    link = screen.getByText("Cancel");
    fireEvent.click(link);
    expect(deleted).equal(false);
  });
});
