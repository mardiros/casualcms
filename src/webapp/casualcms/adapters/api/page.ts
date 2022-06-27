import { Result, ok, err } from "neverthrow";

import { ApiError, IPageApi } from "casualcms/domain/ports";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialPage } from "casualcms/domain/model";

export class PageApi extends BaseFetchApi implements IPageApi {
  async createRootPage(
    authntoken: string,
    type: string,
    payload: any,
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch("/api/pages", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        type: type,
        payload: payload
      })
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
  async listRoots(authntoken: string): Promise<Result<PartialPage[], ApiError>> {
    const response = await this.fetch("/api/pages", {
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
    return ok(jsonData as PartialPage[]);
  }

}
