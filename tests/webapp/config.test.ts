import { expect } from "chai";
import config from "./config";
import { AppConfig } from "../../src/webapp/config";

describe("As an devops, I can configure my application", () => {
  it("Build an AppConfig", async () => {
    const cfg = new AppConfig(config.uow, config.api)
    expect(cfg.uow).equal(config.uow)
    expect(cfg.api).equal(config.api)
  });
});
