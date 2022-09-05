import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen, fireEvent } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { SettingDeletePopoverForm } from "../../src/webapp/ui/settings/settings_delete";

describe("As a user, I can delete a setting", () => {
  before(async () => {
    await config.api.site.createSite("", "news", {
      default: false,
      secure: false,
      root_page_path: "/root",
    });
    await config.api.site.createSite("", "www", {
      default: false,
      secure: false,
      root_page_path: "/index",
    });
    await config.api.setting.createSetting("", "www", "blog:contact", {
      email: "alice@bob.net",
    });
    await config.api.setting.createSetting("", "www", "blog:ff", {
      use_feature: true,
    });
    await config.api.setting.createSetting("", "news", "blog:contact", {
      email: "bob@bob.net",
    });
  });
  after(async () => {
    await config.api.setting.deleteSetting("", "www", {
      meta: { key: "blog:contact" },
    });
    await config.api.setting.deleteSetting("", "www", {
      meta: { key: "blog:ff" },
    });
    await config.api.setting.deleteSetting("", "news", {
      meta: { key: "blog:contact" },
    });
    await config.api.site.deleteSite("", "news");
    await config.api.site.deleteSite("", "www");
  });

  it("Delete a setting", async () => {
    const setting = {
      meta: {
        key: "blog:contact",
      },
      email: "alice@bob.net",
    };

    renderWithRouter(
      <>
        <Route
          path="/admin/settings/:hostname/:key"
          element={
            <SettingDeletePopoverForm hostname="www" curSetting={setting} />
          }
        />
        <Route
          path="/admin/settings/:hostname"
          element={<h4>Setting list</h4>}
        />
      </>,
      "/admin/settings/www/blog:contact"
    );
    let link = screen.getByText("Delete this setting");
    fireEvent.click(link);

    let subList = await config.api.setting.listSettings("", "www");
    expect(subList._unsafeUnwrap()).eql([
      {
        hostname: "www",
        meta: {
          key: "blog:contact",
        },
      },
      {
        hostname: "www",
        meta: {
          key: "blog:ff",
        },
      },
    ]);

    subList = await config.api.setting.listSettings("", "news");
    expect(subList._unsafeUnwrap()).eql([
      {
        hostname: "news",
        meta: {
          key: "blog:contact",
        },
      },
    ]);

    link = screen.getByText("Confirm Deletion");
    fireEvent.click(link);

    subList = await config.api.setting.listSettings("", "www");
    expect(subList._unsafeUnwrap()).eql([
      {
        hostname: "www",
        meta: {
          key: "blog:ff",
        },
      },
    ]);

    subList = await config.api.setting.listSettings("", "news");
    expect(subList._unsafeUnwrap()).eql([
      {
        hostname: "news",
        meta: {
          key: "blog:contact",
        },
      },
    ]);
  });
});
