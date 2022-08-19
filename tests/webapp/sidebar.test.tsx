import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import { SideBar } from "../../src/webapp/ui/layout/sidebar";

describe("As a user, I can see which entry menu I am in", () => {
  it("render the entry menu in a distinct way", async () => {
    renderWithRouter(
      <>
        <Route path="/admin/pages/new" element={<SideBar />} />
        <Route path="/admin/sites" element={<SideBar />} />
        <Route path="/admin/pages" element={<SideBar />} />
      </>,
      "/admin/pages/new"
    );
    let menuItem = screen.getByText("Pages");
    expect(menuItem.getAttribute("data-selected")).equal("true");

    menuItem = screen.getByText("Sites");
    expect(menuItem.getAttribute("data-selected")).equal("false");

    fireEvent.click(menuItem);

    menuItem = screen.getByText("Sites");
    expect(menuItem.getAttribute("data-selected")).equal("true");

    menuItem = screen.getByText("Pages");
    expect(menuItem.getAttribute("data-selected")).equal("false");

    fireEvent.click(menuItem);

    menuItem = screen.getByText("Pages");
    expect(menuItem.getAttribute("data-selected")).equal("true");

    menuItem = screen.getByText("Sites");
    expect(menuItem.getAttribute("data-selected")).equal("false");
  });
});
