import { Result, ok, err } from "neverthrow";

import { ApiError, IPageApi } from "casualcms/domain/ports";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialDraft, Draft } from "casualcms/domain/model";

export class FetchPageApi extends BaseFetchApi implements IPageApi {
  async createDraft(
    authntoken: string,
    type: string,
    payload: any,
    parent: string | null
  ): Promise<Result<boolean, ApiError>> {
    let postBody: any = {
      type: type,
      payload: payload,
    };
    if (parent) {
      postBody.parent = parent;
    }
    const response = await this.fetch("/api/drafts", {
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
  async showDraft(
    authntoken: string,
    path: string
  ): Promise<Result<Draft, ApiError>> {
    const response = await this.fetch(`/api/drafts/${path}`, {
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
    return ok(jsonData as Draft);
  }
  async previewDraft(
    authntoken: string,
    path: string
  ): Promise<Result<string, ApiError>> {
    const response = await this.fetch(`/api/previews${path}`, {
      method: "GET",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
    });
    if (!response.ok) {
      const jsonData = await (response.json() as unknown);
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok((await response.text()) as unknown as string);
  }
  async listDrafts(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialDraft[], ApiError>> {
    const qs = parent ? new URLSearchParams({ parent: parent }) : "";
    const response = await this.fetch(`/api/drafts?${qs}`, {
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
    return ok(jsonData as PartialDraft[]);
  }
  async updateDraft(
    authntoken: string,
    path: string,
    draft: Draft
  ): Promise<Result<Draft, ApiError>> {
    // console.log(draft);
    const payload = { ...draft };
    delete payload.type;
    delete payload.path;
    // console.log(payload);
    const response = await this.fetch(`/api/drafts${path}`, {
      method: "PATCH",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify(payload),
    });
    const jsonData = await (response.json() as unknown);
    if (!response.ok) {
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(jsonData as Draft);
  }
  async publishPage(
    authntoken: string,
    hostname: string,
    path: string
  ): Promise<Result<boolean, Map<string, string>>> {
    throw new Error("Method not implemented.");
  }
  async deleteDraft(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(`/api/drafts${path}`, {
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
