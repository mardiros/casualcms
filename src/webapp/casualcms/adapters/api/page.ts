import { ok, err } from "neverthrow";

import { AsyncApiResult, ApiError, IPageApi } from "casualcms/domain/ports";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialDraft, Draft, Payload } from "casualcms/domain/model";

export class FetchPageApi extends BaseFetchApi implements IPageApi {
  async listDrafts(
    authntoken: string,
    parent: string | null
  ): AsyncApiResult<PartialDraft[]> {
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
  async createDraft(
    authntoken: string,
    type: string,
    payload: Payload,
    parent: string | null
  ): AsyncApiResult<boolean> {
    let postBody: Payload = {
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
  async showDraft(authntoken: string, path: string): AsyncApiResult<Draft> {
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
  async previewDraft(authntoken: string, path: string): AsyncApiResult<string> {
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

  async updateDraft(
    authntoken: string,
    path: string,
    draft: Draft
  ): AsyncApiResult<Draft> {
    // console.log(draft);
    const payload = { ...draft };
    payload.type = undefined;
    payload.path = undefined;
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
  ): AsyncApiResult<boolean> {
    const response = await this.fetch("/api/pages", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${authntoken}`,
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ hostname: hostname, path: path }),
    });
    if (!response.ok) {
      const jsonData = await (response.json() as unknown);
      return err(castError(jsonData as FastApiError) as ApiError);
    }
    return ok(true);
  }
  async deleteDraft(authntoken: string, path: string): AsyncApiResult<boolean> {
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
