import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter, waitForPath } from "./helpers";
import config from "./config";
import { SettingEdit } from "../../src/webapp/ui/settings/setting_edit";

describe("As a user, I can list setting", () => {
  before(async () => {
    await config.api.site.createSite("", "*", {
      default: true,
      secure: false,
      root_page_path: "/root",
    });
    await config.api.site.createSite("", "www.localhost", {
      default: false,
      secure: false,
      root_page_path: "/index",
    });
    await config.api.setting.createSetting(
      "",
      "www.localhost",
      "blog:contact",
      {
        email: "alice@bob.net",
      }
    );
  });
  after(async () => {
    await config.api.site.deleteSite("", "www.localhost");
    await config.api.site.deleteSite("", "*");
    await config.api.setting.deleteSetting("", {
      hostname: "www.localhost",
      meta: { key: "blog:contact" },
    });
  });

  it.only("Update the setting using the web form", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/settings/:hostname/:settingKey/edit"
          element={<SettingEdit />}
        ></Route>
        <Route
          path="/admin/settings/:hostname"
          element={<div>Settings list</div>}
        ></Route>
      </>,
      "/admin/settings/www.localhost/blog:contact/edit"
    );

    const input = await screen.findByLabelText("email", { exact: false });
    fireEvent.change(input, { target: { value: "bob@example.net" } });

    let button = screen.getByText("Submit");
    fireEvent.click(button);

    await waitForPath("/admin/settings/www.localhost");
    const settings = await config.api.setting.listSettings("", "www.localhost");
    expect(settings._unsafeUnwrap()).eql([
      {
        hostname: "www.localhost",
        meta: { key: "blog:contact" },
      },
    ]);
    const contactSetting = await config.api.setting.showSetting(
      "",
      "www.localhost",
      "blog:contact"
    );
    expect(contactSetting._unsafeUnwrap()).eql({
      hostname: "www.localhost",
      email: "bob@example.net",
      meta: { key: "blog:contact" },
    });
  });
});
