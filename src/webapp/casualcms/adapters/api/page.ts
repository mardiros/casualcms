import { Result, ok, err } from "neverthrow";

import { ApiError, IPageApi } from "casualcms/domain/ports";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialPage } from "casualcms/domain/model";

export class PageApi extends BaseFetchApi implements IPageApi {
  async createPage(
    authntoken: string,
    type: string,
    payload: any,
    parent: string | null,
  ): Promise<Result<boolean, ApiError>> {
    let postBody: any = {
      type: type,
      payload: payload,
    }
    if (parent) {
      postBody.parent = parent
    }
    const response = await this.fetch("/api/pages", {
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
  async listPages(
    authntoken: string,
    parent: string | null,
  ): Promise<Result<PartialPage[], ApiError>> {
    const qs = parent ? new URLSearchParams({ parent: parent }): "";
    const response = await this.fetch(`/api/pages?${qs}`, {
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
