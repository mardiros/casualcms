import { Result, ok, err } from "neverthrow";

import { ApiError, ITemplateApi } from "casualcms/domain/ports";
import { PartialPageTemplate, PageTemplate } from "casualcms/domain/model";

import { FastApiError, BaseFetchApi, castError } from "./base";

export class FetchTemplateApi extends BaseFetchApi implements ITemplateApi {
  async listTemplates(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<Array<PartialPageTemplate>, ApiError>> {
    const qs = parentType ? new URLSearchParams({ type: parentType }) : "";
    const response = await this.fetch(`/api/templates?${qs}`, {
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
    return ok(jsonData as Array<PartialPageTemplate>);
  }

  async showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>> {
    // FIXME: tpltype should be urlencoded
    const response = await this.fetch(`/api/templates/${tpltype}`, {
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
    return ok(jsonData as PageTemplate);
  }
}
