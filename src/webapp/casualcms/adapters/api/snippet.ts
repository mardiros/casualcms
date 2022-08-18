import { Result, ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSnippet } from "../../domain/model";
import { ApiError, ISnippetApi } from "../../domain/ports";

export class FetchSnippetApi extends BaseFetchApi implements ISnippetApi {
  async listSnippets(
    authntoken: string
  ): Promise<Result<PartialSnippet[], ApiError>> {
    const response = await this.fetch("/api/snippets", {
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
    return ok(jsonData as PartialSnippet[]);
  }

  async createSnippet(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, ApiError>> {
    let postBody: any = {
      type: type,
      payload: payload,
    };
    const response = await this.fetch("/api/snippets", {
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
  async deleteSnippet(
    authntoken: string,
    slug: string
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(`/api/snippets/${slug}`, {
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
