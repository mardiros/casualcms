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
        type: parentType ? "casual:Page" : "casual:Home",
      },
    ]);
  }
  async showTemplate(
    authntoken: string,
    tpltype: string
  ): Promise<Result<PageTemplate, ApiError>> {
    if (tpltype != "blog:HomePage") {
      let m = new Map();
      m.set("detail", `${tpltype} is undefined`);
      return err(m);
    }
    return ok({
      uiSchema: {
        id: { "ui:widget": "hidden" },
        slug: { "ui:widget": "hidden" },
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
  async createRootPage(
    authntoken: string,
    type: string,
    payload: any
  ): Promise<Result<boolean, Map<string, string>>> {
    payload["path"] = "/";
    this.pages.push(payload);
    return ok(true);
  }

  // async listRoots(
  //   authntoken: string
  // ): Promise<Result<PartialPage[], Map<string, string>>> {
  //   let roots: PartialPage[] = [];
  //   this.pages
  //     .filter((page) => page.slug == "/")
  //     .map((page) =>
  //       roots.push({ slug: page.slug, title: page.title, path: page.path })
  //     );
  //   return ok(roots);
  // }

  async listPages(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialPage[], Map<string, string>>> {
    let pages: PartialPage[] = [];
    this.pages
      .filter((page) => page.slug.startsWith(parent || "/")) //  fixme count and compare /
      .map((page) =>
        pages.push({
          slug: page.slug,
          title: page.title,
          path: page.path,
          type: "blog:Home",
        })
      );
      return ok(pages);
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
