import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter, waitForLoadingLabel } from "../helpers";
import config from "../config";
import { HomePage } from "../../../src/webapp/ui/pages/home/components";
import { ApiError } from "../../../src/webapp/casualcms/domain/ports";
import { PageList } from "../../../src/webapp/ui/pages/pages/page_list";

describe("As a user, I am onboarded with a distinct page", () => {
  describe("<HomePage />", () => {
    it("should display onboarding message", async () => {
      renderWithRouter(<Route path="/" element={<HomePage />} />, "/");
      await screen.findByText("Welcome bob!");
      let link = screen.getByText("Create my first page");
      expect(link.getAttribute("href")).equal("/admin/pages/new");
    });
    it("should redirect to root pages list if exists", async () => {
      before(async function () {
        const resp = await config.api.page.createDraft(
          "",
          "casual:HomePage",
          {
            slug: "root",
            title: "dummy home",
            description: "describe the dummy home",
          },
          null,
        );
        resp.mapErr((err: ApiError) => {
          throw err;
        });
      });
      after(async function () {
        const resp = await config.api.page.deleteDraft("", "/root");
        resp.mapErr((err: ApiError) => {
          throw err;
        });
      });

      renderWithRouter(
        <>
          <Route path="/" element={<HomePage />} />
          <Route path="/admin/pages" element={<PageList />} />
        </>,
        "/",
      );
      let tpl = screen.queryByText("Create my first page");
      expect(tpl).equal(null);
    });
  });
});
