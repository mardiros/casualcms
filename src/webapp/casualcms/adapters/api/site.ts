import { ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSite, Site } from "../../domain/model";
import {
  ApiError,
  SiteOption,
  ISiteApi,
  AsyncApiResult,
} from "../../domain/ports";

export class FetchSiteApi extends BaseFetchApi implements ISiteApi {
  async createSite(
    authntoken: string,
    hostname: string,
    payload: SiteOption
  ): AsyncApiResult<PartialSite> {
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

  async listSites(authntoken: string): AsyncApiResult<PartialSite[]> {
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

  async showSite(authntoken: string, hostname: string): AsyncApiResult<Site> {
    const response = await this.fetch(`/api/sites/${hostname}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as Site);
  }
  async updateSite(
    authntoken: string,
    hostname: string,
    site: Site
  ): AsyncApiResult<boolean> {
    const response = await this.fetch(`/api/sites/${hostname}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(site),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }

    return ok(true);
  }

  async deleteSite(
    authntoken: string,
    hostname: string
  ): AsyncApiResult<boolean> {
    const response = await this.fetch(`/api/sites/${hostname}`, {
      method: "DELETE",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      const jsonData = await (response.json() as unknown);
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
}
