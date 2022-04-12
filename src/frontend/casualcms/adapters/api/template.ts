import { Result, ok, err } from "neverthrow";

import { ApiError, ITemplateApi } from "casualcms/domain/ports";
import { PartialPageTemplate } from "casualcms/domain/model";

import { FastApiError, BaseFetchApi, castError } from "./base";

export class FetchTemplateApi extends BaseFetchApi implements ITemplateApi {
  async listRoots(
    authntoken: string
  ): Promise<Result<Array<PartialPageTemplate>, ApiError>> {
    const response = await this.fetch("/api/templates", {
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
    return ok(jsonData as PartialPageTemplate);
  }

}
