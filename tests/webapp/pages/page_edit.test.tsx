import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { PageEdit } from "../../../src/webapp/ui/pages/pages/page_edit";
import { renderWithRouter, renderWithRouterWithTheme } from "../helpers";
import config from "../config";

describe("As a user, I can edit existing pages", () => {
  before(async () => {
    await config.api.page.createDraft(
      "",
      "casual:HomePage",
      {
        id: "id-home",
        slug: "home",
        title: "Home Page",
        description: "describe the home",
      },
      null,
    );
    await config.api.page.createDraft(
      "",
      "casual:SectionPage",
      {
        id: "id-sub0",
        slug: "sub0",
        title: "Section Page",
        description: "first section",
      },
      "/home",
    );
  });
  after(async () => {
    await config.api.page.deleteDraft("", "/home/sub0");
    await config.api.page.deleteDraft("", "/home");
  });
  describe("<PageEdit />", () => {
    it("Load the root page in an edition form", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/pages/edit" element={<PageEdit />} />
        </>,
        "/admin/pages/edit?page=/home",
      );

      let input = await screen.findByLabelText("Slug", { exact: false });
      expect(input.getAttribute("value")).equal("home");

      input = screen.getByLabelText("Title", { exact: false });
      expect(input.getAttribute("value")).equal("Home Page");
    });

    it("Load the subpage page in an edition form", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/pages/edit" element={<PageEdit />} />
        </>,
        "/admin/pages/edit?page=/home/sub0",
      );

      let input = await screen.findByLabelText("Slug", { exact: false });
      expect(input.getAttribute("value")).equal("sub0");

      input = screen.getByLabelText("Title", { exact: false });
      expect(input.getAttribute("value")).equal("Section Page");

      input = screen.getByLabelText("Description", { exact: false });
      expect(input.getAttribute("value")).equal("first section");
    });

    it("Update the root page using the edition form", async () => {
      renderWithRouterWithTheme(
        <>
          <Route path="/admin/pages/edit" element={<PageEdit />} />
        </>,
        "/admin/pages/edit?page=/home",
      );

      let input = await screen.findByLabelText("Title", { exact: false });
      fireEvent.change(input, { target: { value: "New Value" } });

      input = screen.getByLabelText("Body", { exact: false });
      fireEvent.change(input, { target: { value: "Long time ago" } });

      let button = screen.getByRole("button", { name: "Save" });
      expect(button).not.equal(null);
      fireEvent.click(button);

      let toastee = await screen.findByText("Draft page saved.");
      expect(toastee).not.equal(null);

      const page = await config.api.page.showDraft("", "/home");
      expect(page.isOk()).equal(true);
      expect(page.unwrapOr({ title: "" }).title).equal("New Value");
    });
  });
});
