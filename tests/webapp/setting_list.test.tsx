import { expect } from "chai";
import React from "react";
import { Route } from "react-router-dom";
import { screen } from "@testing-library/react";
import { renderWithRouter } from "./helpers";
import config from "./config";
import { Table, Tbody } from "@chakra-ui/react";
import {
  SettingRow,
  SettingsTable,
  SettingList,
} from "../../src/webapp/ui/settings/settings_list";

describe("As a user, I can list settings of a given site", () => {
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
      metadata: { hostname: "www.localhost", key: "blog:contact" },
    });
  });

  it("<SettingRow />: Render a row for a setting", async () => {
    renderWithRouter(
      <Route
        path="/admin/settingrow"
        element={
          <Table>
            <Tbody>
              <SettingRow
                settingUrl={"/admin/settings/.../edit"}
                settingType={{ title: "Contact", key: "contact" }}
              />
            </Tbody>
          </Table>
        }
      />,
      "/admin/settingrow"
    );

    let link = await screen.findByText("Contact", { exact: false });
    expect(link.getAttribute("href")).equal("/admin/settings/.../edit");
  });

  it("<SettingsTable />: Render table if setting types are loaded", async () => {
    const settingTypes = [
      { title: "Feature Flag", key: "blog:ff" },
      { title: "Contact", key: "blog:contact" },
    ];
    renderWithRouter(
      <Route
        path="/admin/settings/table"
        element={
          <SettingsTable
            config={config}
            token=""
            hostname={"www.localhost"}
            settingTypes={settingTypes}
          />
        }
      />,
      "/admin/settings/table"
    );

    const ff = await screen.findByText("Feature Flag", { exact: false });
    expect(ff.nodeName).equal("A");
    expect(ff.getAttribute("href")).equal(
      "/admin/settings/www.localhost/blog:ff/new"
    );

    const contact = await screen.findByText("Contact", { exact: false });
    expect(contact.nodeName).equal("A");
    expect(contact.getAttribute("href")).equal(
      "/admin/settings/www.localhost/blog:contact/edit"
    );
  });

  it("<SettingList />: Render settings lists from the API", async () => {
    renderWithRouter(
      <Route path="/admin/settings/:hostname" element={<SettingList />} />,
      "/admin/settings/www.localhost"
    );
    const ff = await screen.findByText("Feature Flag", { exact: false });
    expect(ff.getAttribute("href")).equal(
      "/admin/settings/www.localhost/blog:ff/new"
    );

    const contact = await screen.findByText("Contact", { exact: false });
    expect(contact.getAttribute("href")).equal(
      "/admin/settings/www.localhost/blog:contact/edit"
    );
  });
});
