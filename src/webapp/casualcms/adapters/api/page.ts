import { Result, ok, err } from "neverthrow";

import { ApiError, IPageApi } from "casualcms/domain/ports";

import { FastApiError, BaseFetchApi, castError } from "./base";
import { PartialPage, Page } from "casualcms/domain/model";

export class FetchPageApi extends BaseFetchApi implements IPageApi {
  async createPage(
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
  async showPage(
    authntoken: string,
    path: string
  ): Promise<Result<Page, ApiError>> {
    const response = await this.fetch(`/api/pages/${path}`, {
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
    return ok(jsonData as Page);
  }
  async listPages(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialPage[], ApiError>> {
    const qs = parent ? new URLSearchParams({ parent: parent }) : "";
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
  async updatePage(
    authntoken: string,
    path: string,
    page: Page
  ): Promise<Result<Page, ApiError>> {
    // console.log(page);
    const payload = { ...page };
    delete payload.type;
    delete payload.path;
    // console.log(payload);
    const response = await this.fetch(`/api/pages${path}`, {
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
    return ok(jsonData as Page);
  }
  async deletePage(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>> {
    const response = await this.fetch(`/api/pages${path}`, {
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
