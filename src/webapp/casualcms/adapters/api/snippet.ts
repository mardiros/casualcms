import { Result, ok, err } from "neverthrow";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialSnippet, Snippet } from "../../domain/model";
import { ApiError, ISnippetApi } from "../../domain/ports";

export class FetchSnippetApi extends BaseFetchApi implements ISnippetApi {
  async listSnippets(
    authntoken: string,
    type: string
  ): Promise<Result<PartialSnippet[], ApiError>> {
    const qs = new URLSearchParams({ type: type });
    const response = await this.fetch(`/api/snippets?${qs}`, {
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
    return ok(jsonData as PartialSnippet[]);
  }

  async showSnippet(
    authntoken: string,
    slug: string
  ): Promise<Result<Snippet, ApiError>> {
    const response = await this.fetch(`/api/snippets/${slug}`, {
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
    return ok(jsonData as Snippet);
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

  async updateSnippet(
    authntoken: string,
    slug: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(`/api/snippets/${slug}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(snippet),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }

  async deleteSnippet(
    authntoken: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(`/api/snippets/${snippet.slug}`, {
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
