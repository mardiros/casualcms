import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel } from "./helpers";
import config from "./config";
import { HomePage } from "../../src/webapp/ui/home/components";
import { ApiError } from "../../src/webapp/casualcms/domain/ports";
import { PageList } from "../../src/webapp/ui/page_list/components";

describe("As a user, I have to create a first root template", () => {
  it("display onboarding message", async () => {
    renderWithRouter(<Route path="/" element={<HomePage />} />, "/");
    await screen.findByText("Welcome bob!");
    let link = screen.getByText("Create my first page");
    expect(link).not.equal(undefined);
    expect(link.getAttribute("href")).equal("/admin/page/new");
  });
});

describe("As a user, I am redirected to the root list if one exists", () => {
  before(async function () {
    const resp = await config.api.page.createPage(
      "",
      "casual:HomePage",
      {
        slug: "root",
        title: "dummy home",
        description: "describe the dummy home",
      },
      null
    );
    resp.mapErr((err: ApiError) => {
      throw err;
    });
  });
  after(async function () {
    const resp = await config.api.page.deletePage("", "/root");
    resp.mapErr((err: ApiError) => {
      throw err;
    });
  });
  it("redirect to root pages list if exists", async () => {
    renderWithRouter(
      <>
        <Route path="/" element={<HomePage />} />
        <Route path="/admin/pages" element={<PageList />} />
      </>,
      "/"
    );
    let tpl = await screen.findByText("dummy home");
    expect(tpl).not.equal(null);
  });
});
