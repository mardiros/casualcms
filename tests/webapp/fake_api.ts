import { err, ok, Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
} from "../../src/webapp/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
  ITemplateApi,
  IPageApi,
} from "../../src/webapp/casualcms/domain/ports";
import { IApi } from "../../src/webapp/casualcms/service/api";

class FakeAccountApi implements IAccountApi {
  async byCredentials(creds: Credentials): Promise<Result<Account, ApiError>> {
    if (creds.password == "justincase") {
      let errMap = new Map();
      errMap.set("username", "Invalid username or password");
      return err(errMap);
    }
    return ok({
      id: "123",
      token: "abc123",
      lang: "en",
      username: creds.username,
    });
  }
}

class FakeTemplateApi implements ITemplateApi {
  async listTemplates(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<Array<PartialPageTemplate>, ApiError>> {
    return ok([
      {
        type: parentType ? "casual:Page" : "casual:HomePage",
      },
    ]);
  }
  async showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>> {
    if (tpltype != "casual:HomePage") {
      let m = new Map();
      m.set("detail", `${tpltype} is undefined`);
      return err(m);
    }
    return ok({
      uiSchema: {
        id: { "ui:widget": "hidden" },
        slug: { "ui:widget": "text", "ui:placeholder": "slug" },
        title: { "ui:widget": "text", "ui:placeholder": "title" },
        body: { "ui:widget": "text", "ui:placeholder": "body" },
      },
      schema: {
        title: "HomePage",
        type: "object",
        properties: {
          id: { title: "Id", type: "string" },
          slug: { title: "Slug", type: "string" },
          title: { title: "Title", type: "string" },
          body: { title: "Body", type: "string" },
        },
        required: ["id", "slug", "title", "body"],
        definitions: {},
      },
    });
  }
}

class FakePageApi implements IPageApi {
  pages: Array<any>;

  constructor() {
    this.pages = [];
  }
  async createPage(
    authntoken: string,
    type: string,
    payload: any,
    parent: string | null
  ): Promise<Result<boolean, Map<string, string>>> {
    if (parent) {
      let errs = new Map();
      errs.set("FIXME", "FIXME");
      return err(errs);
    }
    payload["path"] = `${parent || ""}/${payload.slug}`;
    this.pages.push(payload);
    return ok(true);
  }

  async showPage(
    authntoken: string,
    path: string | null
  ): Promise<Result<PartialPage, Map<string, string>>> {
    let pages: PartialPage[] = [];
    this.pages
      .filter((page) => {
        return page.path == path;
      })
      .map((page) =>
        pages.push({
          slug: page.slug,
          title: page.title,
          path: page.path,
          type: "casual:HomePage",
        })
      );
    if (pages.length) {
      return ok(pages[0]);
    } else {
      // FIXME
      return err(new Map());
    }
  }
  async listPages(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialPage[], Map<string, string>>> {
    let pages: PartialPage[] = [];
    this.pages
      .filter((page) => {
        let starter = parent || "";
        starter = starter.replace(/\\(.)/gm, "$1");
        const startLen = starter.split("/").length;
        const pathLen = page.path.split("/").length;
        return page.path.startsWith(starter) && pathLen == startLen + 1;
      })
      .map((page) =>
        pages.push({
          slug: page.slug,
          title: page.title,
          path: page.path,
          type: "casual:HomePage",
        })
      );
    return ok(pages);
  }
  async deletePage(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>> {
    const pages = this.pages.filter((page) => {
      return page.path != path;
    });
    this.pages = pages;
    return ok(true);
  }
}

export class FakeApi implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.template = new FakeTemplateApi();
    this.page = new FakePageApi();
  }
}
