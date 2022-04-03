import React from "react";
import { screen, waitFor } from "@testing-library/react";
import { useLocation } from "react-router-dom";

export const LocationDisplay = () => {
  const location = useLocation();
  return <div data-testid="location-display">{location.pathname}</div>;
};

export const waitForPath = async (path: string): Promise<string> => {
  const resp = await waitFor((): string => {
    let loc = screen.getByTestId("location-display");

    if (loc.innerHTML != path) {
      throw Error(`Not ready: ${loc.innerHTML}`);
    }
    return loc.innerHTML;
  });
  return resp;
};

