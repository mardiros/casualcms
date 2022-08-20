import { err, ok, Result } from "neverthrow";
import {
  Account,
  PartialPageType,
  PageType,
  PartialPage,
  Page,
  PartialSite,
  Site,
  PartialSnippet,
  PartialSnippetType,
  SnippetType,
  Snippet,
} from "../../src/webapp/casualcms/domain/model";
import {
  ApiError,
  IAccountApi,
  Credentials,
  IPageTypeApi,
  IPageApi,
  ISiteApi,
  SiteOption,
  ISnippetApi,
  ISnippetTypeApi,
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

class FakePageTypeApi implements IPageTypeApi {
  async listPageTypes(
    authntoken: string,
    parentType: string | null
  ): Promise<Result<Array<PartialPageType>, ApiError>> {
    return ok([
      {
        type: parentType ? "casual:Page" : "casual:HomePage",
      },
    ]);
  }
  async showPageType(
    authntoken: string,
    pageType: string
  ): Promise<Result<PageType, ApiError>> {
    if (pageType == "casual:HomePage") {
      return ok({
        uiSchema: {
          slug: { "ui:widget": "text", "ui:placeholder": "slug" },
          title: { "ui:widget": "text", "ui:placeholder": "title" },
          body: { "ui:widget": "text", "ui:placeholder": "body" },
        },
        schema: {
          title: "HomePage",
          type: "object",
          properties: {
            slug: { title: "Slug", type: "string" },
            title: { title: "Title", type: "string" },
            body: { title: "Body", type: "string" },
          },
          required: ["slug", "title", "body"],
          definitions: {},
        },
      });
    }

    if (pageType == "casual:SectionPage") {
      return ok({
        uiSchema: {
          slug: { "ui:widget": "text", "ui:placeholder": "slug" },
          title: { "ui:widget": "text", "ui:placeholder": "title" },
          description: { "ui:widget": "text", "ui:placeholder": "description" },
        },
        schema: {
          title: "HomePage",
          type: "object",
          properties: {
            slug: { title: "Slug", type: "string" },
            title: { title: "Title", type: "string" },
            description: { title: "Description", type: "string" },
          },
          required: ["slug", "title"],
          definitions: {},
        },
      });
    }

    let m = new Map();
    m.set("detail", `${pageType} is undefined`);
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
            type: page.meta.type,
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
    this.sites = [];
  }

  async createSite(
    authntoken: string,
    hostname: string,
    payload: SiteOption
  ): Promise<Result<PartialSite, ApiError>> {
    const postBody = { hostname: hostname, ...payload };
    this.sites.push(postBody);
    return ok(postBody);
  }

  async deleteSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<boolean, ApiError>> {
    const sites = this.sites.filter((site: PartialSite) => {
      return site.hostname != hostname;
    });
    this.sites = sites;
    return ok(true);
  }

  async showSite(
    authntoken: string,
    hostname: string
  ): Promise<Result<Site, ApiError>> {
    const errors: ApiError = new Map();
    errors.set("site", "Site does not exists");
    let res: Result<Site, ApiError> = err(errors);

    this.sites.filter((site: PartialSite) => {
      if (site.hostname == hostname) {
        res = ok(site);
      }
    });
    return res;
  }

  async listSites(
    authntoken: string
  ): Promise<Result<PartialSite[], ApiError>> {
    return ok(this.sites as PartialSite[]);
  }
}

type snippetRecords = {
  [k: string]: PartialSnippet[];
};

export class FakeSnippetApi implements ISnippetApi {
  snippets: snippetRecords;

  constructor() {
    this.snippets = {};
  }

  async listSnippets(
    authntoken: string,
    type: string
  ): Promise<Result<PartialSnippet[], Map<string, string>>> {
    return ok(this.snippets[type] || []);
  }

  async updateSnippet(
    authntoken: string,
    slug: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>> {
    const typ = snippet.meta.type;
    let snippets = this.snippets[typ].filter((snippet: PartialSnippet) => {
      return snippet.slug != slug;
    });
    snippets.push(snippet);
    this.snippets[typ] = snippets;
    return ok(true);
  }

  async showSnippet(
    authntoken: string,
    slug: string
  ): Promise<Result<Snippet, ApiError>> {
    for (const [type, snippets] of Object.entries(this.snippets)) {
      const filteredDnippets = snippets.filter((snippet: PartialSnippet) => {
        return snippet.slug == slug;
      });
      if (filteredDnippets.length == 1) {
        return ok(filteredDnippets[0]);
      }
    }
    let apiError = new Map();
    apiError.set("slug", "Snippet not found");
    return err(apiError);
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
    payload["meta"] = { type: type };
    if (!this.snippets[type]) {
      this.snippets[type] = [];
    }
    this.snippets[type].push(payload);
    return ok(true);
  }
  async deleteSnippet(
    authntoken: string,
    snippet: Snippet
  ): Promise<Result<boolean, ApiError>> {
    const typ = snippet.meta.type;
    const snippets = this.snippets[typ].filter((s: PartialSnippet) => {
      return s.slug != snippet.slug;
    });
    this.snippets[typ] = snippets;
    return ok(true);
  }
}

class FakeSnippetTypeApi implements ISnippetTypeApi {
  async listSnippetTypes(
    authntoken: string
  ): Promise<Result<PartialSnippetType[], Map<string, string>>> {
    return ok([{ type: "blog:HeaderSnippet" }, { type: "blog:FooterSnippet" }]);
  }
  async showSnippetType(
    authntoken: string,
    snippet_type: string
  ): Promise<Result<SnippetType, Map<string, string>>> {
    return ok({
      schema: {
        title: "HeaderSnippet",
        type: "object",
        properties: {
          slug: { title: "Slug", type: "string" },
          title: { title: "Title", type: "string" },
          links: {
            title: "Links",
            type: "array",
            items: { $ref: "#/definitions/Link" },
          },
        },
        required: ["slug", "title"],
        definitions: {
          Link: {
            title: "Link",
            type: "object",
            properties: {
              title: { title: "Title", type: "string" },
              href: { title: "Href", type: "string" },
            },
            required: ["title", "href"],
          },
        },
      },
      uiSchema: {
        slug: { "ui:widget": "text", "ui:placeholder": "slug" },
        title: { "ui:widget": "text", "ui:placeholder": "title" },
        links: {
          items: {
            title: { "ui:widget": "text", "ui:placeholder": "title" },
            href: { "ui:widget": "text", "ui:placeholder": "href" },
          },
        },
      },
    });
  }
}

export class FakeApi implements IApi {
  account: IAccountApi;
  pageType: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.pageType = new FakePageTypeApi();
    this.page = new FakePageApi();
    this.site = new FakeSiteApi();
    this.snippet = new FakeSnippetApi();
    this.snippetType = new FakeSnippetTypeApi();
  }
}
