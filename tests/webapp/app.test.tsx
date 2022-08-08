import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { App, Body} from "../../src/webapp/App";
import { AppContext } from "../../src/webapp/config";
import config from "./config";
import { waitForPath, LocationDisplay, renderWithRouter } from "./helpers";
import { Route } from "react-router-dom";
import { Header } from "../../src/webapp/ui/layout/header";

describe("As a user, I view a different homepage when I am authenticated or not", () => {
  it("The header display a link to home when I am login", async () => {
    renderWithRouter(<Route path="/" element={<Header />} />, "/");
    const link = await screen.findByText("👕 Casual CMS");
    expect(link.getAttribute("href")).equal("/admin");
  });
  it("The header a link to the login page", async () => {
    renderWithRouter(<Route path="/" element={<Header />} />, "/", {
      isAuthenticated: false,
    });
    const link = await screen.findByText("Sign In");
    expect(link.getAttribute("href")).equal("/admin/login");
  });
  it("The body display a link to home when I am login", async () => {
    renderWithRouter(<Route path="/" element={<Body />} />, "/", {
      isAuthenticated: false,
    });
    const link = await screen.findByText("Sign In");
    expect(link.getAttribute("href")).equal("/admin/login");
  });

  it("The body display a welcome message after logged in", async () => {
    renderWithRouter(<Route path="/" element={<Body />} />, "/");
    const link = await screen.findByText("Create my first page");
    expect(link.getAttribute("href")).equal("/admin/page/new");
  });
});

describe("As a user, I am redirect to the login page", () => {
  it("redirect to the login form", async () => {
    render(
      <AppContext.Provider value={config}>
        <App debugNode={<LocationDisplay />} />
      </AppContext.Provider>
    );
    await waitForPath("/admin/login");
    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
  });
});
