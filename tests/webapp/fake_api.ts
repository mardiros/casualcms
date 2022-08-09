import { err, ok, Result } from "neverthrow";
import {
  Account,
  PartialPageTemplate,
  PageTemplate,
  PartialPage,
  Page,
  PartialSite,
} from "../../src/webapp/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
  ITemplateApi,
  IPageApi,
  ISiteApi,
} from "../../src/webapp/casualcms/domain/ports";
import { IApi } from "../../src/webapp/casualcms/service/api";

class FakeAccountApi implements IAccountApi {
  async byCredentials(creds: Credentials): Promise<Result<Account, ApiError>> {
    if (creds.password != "itsmysecret") {
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
  async logout(authntoken: string): Promise<boolean> {
    return true;
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
    if (tpltype == "casual:HomePage") {
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

    if (tpltype == "casual:SectionPage") {
      return ok({
        uiSchema: {
          id: { "ui:widget": "hidden" },
          slug: { "ui:widget": "text", "ui:placeholder": "slug" },
          title: { "ui:widget": "text", "ui:placeholder": "title" },
          description: { "ui:widget": "text", "ui:placeholder": "description" },
        },
        schema: {
          title: "HomePage",
          type: "object",
          properties: {
            id: { title: "Id", type: "string" },
            slug: { title: "Slug", type: "string" },
            title: { title: "Title", type: "string" },
            description: { title: "Description", type: "string" },
          },
          required: ["id", "slug", "title"],
          definitions: {},
        },
      });
    }

    let m = new Map();
    m.set("detail", `${tpltype} is undefined`);
    return err(m);
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
    payload["meta"] = {
      type: type,
      path: `${parent || ""}/${payload.slug}`,
      breadcrumb: [],
    };
    this.pages.push(payload);
    return ok(true);
  }

  async showPage(
    authntoken: string,
    path: string | null
  ): Promise<Result<Page, Map<string, string>>> {
    let pages: Page[] = [];
    this.pages
      .filter((page) => {
        return page.meta.path == path;
      })
      .map((page) => pages.push(page));
    if (pages.length) {
      return ok(pages[0]);
    } else {
      // FIXME
      const errors = new Map();
      errors.set("page", "Page does not exists");
      return err(errors);
    }
  }
  async listPages(
    authntoken: string,
    parent: string | null
  ): Promise<Result<PartialPage[], Map<string, string>>> {
    let pages: PartialPage[] = [];

    this.pages
      .filter((page: PartialPage) => {
        let starter = parent || "";
        starter = starter.replace(/\\(.)/gm, "$1");
        const startLen = starter.split("/").length;
        const pathLen = page.meta.path.split("/").length;
        return page.meta.path.startsWith(starter) && pathLen == startLen + 1;
      })
      .map((page) =>
        pages.push({
          slug: page.slug,
          title: page.title,
          meta: {
            path: page.meta.path,
            type: "casual:HomePage",
          },
        })
      );
    return ok(pages);
  }
  async updatePage(
    authntoken: string,
    path: string,
    page: Page
  ): Promise<Result<Page, ApiError>> {
    let oldPage: any | null = null;
    const pages: any[] = [];
    this.pages.map((p) => (p.path == path ? (oldPage = p) : pages.push(page)));
    if (pages.length) {
      const newPage = { ...oldPage, ...page };
      const newPath: string[] = newPage.meta.path.split("/");
      newPath[newPath.length - 1] = page.slug;
      newPage.meta.path = newPath.join("/");
      pages.push(newPage);
      this.pages = pages;
      return ok(newPage);
    } else {
      // FIXME
      return err(new Map());
    }

    return ok(page);
  }
  async deletePage(
    authntoken: string,
    path: string
  ): Promise<Result<boolean, ApiError>> {
    const pages = this.pages.filter((page: PartialPage) => {
      return page.meta.path != path;
    });
    this.pages = pages;
    return ok(true);
  }
}

export class FakeSiteApi implements ISiteApi {
  sites: PartialSite[];

  constructor() {
    this.sites = [
      { hostname: "*", default: false, root: "/index" },
      { hostname: "www.localhost", default: true, root: "/root" },
    ];
  }

  async listSites(
    authntoken: string
  ): Promise<Result<PartialSite[], ApiError>> {
    return ok(this.sites as PartialSite[]);
  }
}

export class FakeApi implements IApi {
  account: IAccountApi;
  template: ITemplateApi;
  page: IPageApi;
  site: ISiteApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.template = new FakeTemplateApi();
    this.page = new FakePageApi();
    this.site = new FakeSiteApi();
  }
}
