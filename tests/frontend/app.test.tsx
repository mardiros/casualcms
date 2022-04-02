import { expect } from "chai";
import React from "react";
import { render, screen, waitFor } from "@testing-library/react";
import { App } from "../../src/frontend/App";
import { AppContext } from "../../src/frontend/config";
import config from "./config"
import {useLocation} from 'react-router-dom'

export const LocationDisplay = () => {
  const location = useLocation()
  return <div data-testid="location-display">{location.pathname}</div>
}

const waitForPath = async (path: string): Promise<string> => {
  const resp = await waitFor(
    (): string => {
      let loc = screen.getByTestId('location-display');

      if (loc.innerHTML != path) {
        throw Error(`Not ready: ${loc.innerHTML}`)
      }
      return loc.innerHTML
    });
  return resp;
}

describe("As a user, I am redirect to the login page", () => {
  it("cast a single error", async () => {
    render(
      <AppContext.Provider value={config}>
        <App debugNode={<LocationDisplay/>} />
      </AppContext.Provider>
    );
    let loc = await waitForPath("/admin/login");
    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
  })
});
