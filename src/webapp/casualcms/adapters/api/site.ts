import { Result, ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSite } from "../../domain/model";
import { ApiError, ISiteApi } from "../../domain/ports";

export class SiteApi extends BaseFetchApi implements ISiteApi {
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
