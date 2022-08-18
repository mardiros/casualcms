import { Result, ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSnippetType, SnippetType } from "../../domain/model";
import { ApiError, ISnippetTypeApi } from "../../domain/ports";

export class FetchSnippetTypeApi
  extends BaseFetchApi
  implements ISnippetTypeApi
{
  async listSnippetTypes(
    authntoken: string
  ): Promise<Result<Array<PartialSnippetType>, ApiError>> {
    const response = await this.fetch("/api/snippets-types", {
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
    return ok(jsonData as Array<PartialSnippetType>);
  }

  async showSnippetType(
    authntoken: string,
    snippet_type: string
  ): Promise<Result<SnippetType, ApiError>> {
    // FIXME: snippet_type should be urlencoded
    const response = await this.fetch(`/api/snippets-types/${snippet_type}`, {
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
    return ok(jsonData as SnippetType);
  }
}
