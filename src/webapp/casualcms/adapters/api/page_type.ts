import { Result, ok, err } from "neverthrow";

import { ApiError, IPageTypeApi } from "casualcms/domain/ports";
import { PartialPageType, PageType } from "casualcms/domain/model";

import { FastApiError, BaseFetchApi, castError } from "./base";

export class FetchPageTypeApi extends BaseFetchApi implements IPageTypeApi {
  async listPageTypes(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<Array<PartialPageType>, ApiError>> {
    const qs = parentType ? new URLSearchParams({ type: parentType }) : "";
    const response = await this.fetch(`/api/pages-types?${qs}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        Accept: "application/json",
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as Array<PartialPageType>);
  }

  async showPageType(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageType, ApiError>> {
    // FIXME: tpltype should be urlencoded
    const response = await this.fetch(`/api/pages-types/${tpltype}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        Accept: "application/json",
      },
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as PageType);
  }
}
