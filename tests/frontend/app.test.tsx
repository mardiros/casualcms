import { expect } from "chai";
import React from "react";
import { render, screen } from "@testing-library/react";
import { App } from "../../src/frontend/App";

describe("As a user, I am redirect to the login page", () => {
  it("cast a single error", () => {
    render(<App />);
    let input = screen.getByLabelText("Username:");
    expect(input).not.equal(null);
  })
});
