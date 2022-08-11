import { Result, ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSite } from "../../domain/model";
import { ApiError, SiteOption, ISiteApi } from "../../domain/ports";

export class SiteApi extends BaseFetchApi implements ISiteApi {
  async createSite(
    authntoken: string,
    hostname: string,
    payload: SiteOption
  ): Promise<Result<PartialSite, ApiError>> {
    const postBody = { hostname: hostname, ...payload };
    const response = await this.fetch("/api/sites", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postBody),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as PartialSite);
  }

  async deleteSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<boolean, ApiError>> {
    const postBody = { hostname: hostname };
    const response = await this.fetch("/api/sites", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(postBody),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }

  async listSites(
    authntoken: string
  ): Promise<Result<PartialSite[], ApiError>> {
    const response = await this.fetch("/api/sites", {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as PartialSite[]);
  }
}
