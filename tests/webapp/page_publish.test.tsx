import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import {
  PublishButton,
  PublishResultBox,
  SelectableHostname,
  SiteCheckBox,
} from "../../src/webapp/ui/pages/page_publish";
import { renderWithRouter, waitForPath } from "./helpers";
import config from "./config";
import { err, ok } from "neverthrow";

describe("As a user, I can publish existing pages", () => {
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
      null
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
      "/home"
    );

    await config.api.site.createSite("", "www", {
      default: false,
      secure: false,
      root_page_path: "/index",
    });

    await config.api.site.createSite("", "test", {
      default: false,
      secure: false,
      root_page_path: "/test",
    });

    await config.api.site.createSite("", "stage", {
      default: false,
      secure: false,
      root_page_path: "/home",
    });

    await config.api.site.createSite("", "preprod", {
      default: false,
      secure: false,
      root_page_path: "/home",
    });

    await config.api.site.createSite("", "www", {
      default: false,
      secure: false,
      root_page_path: "/home",
    });
  });
  after(async () => {
    await config.api.site.deleteSite("", "www");
    await config.api.site.deleteSite("", "preprod");
    await config.api.site.deleteSite("", "stage");
    await config.api.site.deleteSite("", "test");
    await config.api.page.deleteDraft("", "/home/sub0");
    await config.api.page.deleteDraft("", "/home");
  });

  it("<PublishResultBox /> display the publication result", async () => {
    const errs = new Map();
    errs.set("hostname", "deleted");

    const hostnames: SelectableHostname[] = [
      {
        hostname: "stage.alice.bob",
        secure: true,
        root_page_path: "/home",
        selected: true,
        response: ok(true),
      },
      {
        hostname: "preprod.alice.bob",
        secure: true,
        root_page_path: "/home",
        selected: true,
        response: err(errs),
      },
      {
        hostname: "www",
        secure: true,
        root_page_path: "/home",
        selected: false,
      },
    ];
    let closed = false;
    function onClose() {
      closed = true;
    }
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={
            <PublishResultBox
              pagePath="/home"
              hostnames={hostnames}
              onClose={onClose}
            />
          }
        ></Route>
      </>,
      "/admin/pages"
    );
    const boxes = screen.getAllByRole("publication_result");
    expect(boxes.length).equal(3);
    expect(boxes[0].textContent?.trim()).equal("stage.alice.bob View");

    const view_result = screen.getByRole("view_publication_result");
    expect(view_result.getAttribute("href")).equal("https://stage.alice.bob/");

    expect(boxes[1].textContent?.trim()).equal("preprod.alice.bob ERROR");
    expect(boxes[2].textContent?.trim()).equal("www Ignored");

    const close = screen.getByRole("close_publish_popover");
    fireEvent.click(close);
    expect(closed).equal(true);
  });

  it("<SiteCheckBox /> let configure sites to publish the page", async () => {
    const hostname: SelectableHostname = {
      hostname: "www",
      secure: true,
      root_page_path: "/home",
      selected: false,
    };
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<SiteCheckBox hostname={hostname} />}
        ></Route>
      </>,
      "/admin/pages"
    );
    const cbx = screen.getByLabelText("www");
    // expect(cbx.getAttribute("checked")).equal(false);
    fireEvent.click(cbx);
    expect(hostname.selected).equal(true);
  });
  it("<SiteCheckBox /> let remove site to publish the page", async () => {
    const hostname: SelectableHostname = {
      hostname: "www",
      secure: true,
      root_page_path: "/home",
      selected: true,
    };
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<SiteCheckBox hostname={hostname} />}
        ></Route>
      </>,
      "/admin/pages"
    );
    const cbx = screen.getByLabelText("www");
    fireEvent.click(cbx);
    expect(hostname.selected).equal(false);
  });
  it("<PublishButton /> display the publication popover", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<PublishButton token="x" pagePath="/home" />}
        ></Route>
      </>,
      "/admin/pages"
    );
    const btn = screen.getByText("Publish");
    fireEvent.click(btn);
    const boxes = await screen.findAllByRole("select_site");
    expect(boxes.length).equal(3);
    expect(boxes[0].textContent).equal("stage");
    expect(boxes[1].textContent).equal("preprod");
    expect(boxes[2].textContent).equal("www");

    fireEvent.click(boxes[0]);
    fireEvent.click(boxes[1]);

    const submitBtn = screen.getByRole("publish");
    fireEvent.click(submitBtn);
    const closeBtn = await screen.findByRole("close_publish_popover");

    const result = await screen.findAllByRole("publication_result");
    expect(result.length).equal(3);
    expect(result[0].textContent).equal("stage View");
    expect(result[1].textContent).equal("preprod View");
    expect(result[2].textContent).equal("www Ignored");
    fireEvent.click(closeBtn);
  });

  it("<PageEditButtons /> display the publish button", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/pages"
          element={<PublishButton token="x" pagePath="/home" />}
        ></Route>
      </>,
      "/admin/pages"
    );

    const btn = screen.getByRole("open_publish_popover");
    expect(btn).not.equal(undefined);
  });
});
