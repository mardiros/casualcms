import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter, waitForPath } from "./helpers";
import { SettingNew } from "../../src/webapp/ui/settings/setting_new";
import config from "./config";

describe("As a user, I can list setting", () => {
  it("<SettingNew />: Create the setting using the web form", async () => {
    renderWithRouter(
      <>
        <Route
          path="/admin/settings/:hostname/:settingKey/new"
          element={<SettingNew />}
        ></Route>
        <Route
          path="/admin/settings/:hostname"
          element={<div>Settings list</div>}
        ></Route>
      </>,
      "/admin/settings/www.localhost/blog:contact/new"
    );

    const input = await screen.findByLabelText("email", { exact: false });
    fireEvent.change(input, { target: { value: "alice@example.net" } });

    let button = screen.getByText("Submit");
    fireEvent.click(button);

    await waitForPath("/admin/settings/www.localhost");
    const settings = await config.api.setting.listSettings("", "www.localhost");
    expect(settings._unsafeUnwrap()).eql([
      {
        meta: { hostname: "www.localhost", key: "blog:contact" },
      },
    ]);
    const contactSetting = await config.api.setting.showSetting(
      "",
      "www.localhost",
      "blog:contact"
    );
    expect(contactSetting._unsafeUnwrap()).eql({
      email: "alice@example.net",
      meta: { hostname: "www.localhost", key: "blog:contact" },
    });
    await config.api.setting.deleteSetting("", {
      meta: { hostname: "www.localhost", key: "blog:contact" },
    });
  });
});
