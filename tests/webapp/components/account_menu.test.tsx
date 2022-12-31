import { expect } from "chai";
import React from "react";
import { fireEvent, screen } from "@testing-library/react";
import { renderWithRouter, waitForPath } from "../helpers";
import { Route } from "react-router-dom";
import config from "../config";
import { useAuth } from "../../../src/webapp/ui/pages/login/hooks";
import { AccountMenu } from "../../../src/webapp/ui/components/account_menu";

export const LogoutResult: React.FunctionComponent<{}> = () => {
  let auth = useAuth();
  if (auth.authenticatedUser != null) {
    return <div>Still logged in</div>;
  } else {
    return <h4>Logged out</h4>;
  }
};

describe("As a user, I can safely logout", () => {
  describe("<AccountMenu />", () => {
    it("Delete the session on logout", async () => {
      renderWithRouter(
        <>
          <Route path="/admin/pages" element={<AccountMenu username="alice" />} />
          <Route path="/admin/login" element={<LogoutResult />} />
        </>,
        "/admin/pages",
      );
      let link = screen.getByText("Logout");
      const evt = fireEvent.click(link);
      expect(evt).equal(true);
      await waitForPath("/admin/login");
      const account = await config.uow.account.getCurrent();
      expect(account.isErr()).equal(true);
      expect(account._unsafeUnwrapErr()).equal("Gone");

      const message = screen.getByText("Logged out");
      expect(message.nodeName).equal("H4");
    });
  });
});
