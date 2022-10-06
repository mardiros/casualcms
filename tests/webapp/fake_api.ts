import { err, Ok, ok, Result } from "neverthrow";
import { string } from "prop-types";
import {
  Account,
  PartialPageType,
  PageType,
  PartialDraft,
  Draft,
  PartialSite,
  Site,
  PartialSnippet,
  PartialSnippetType,
  SnippetType,
  Snippet,
  PartialSettingType,
  PartialSetting,
  Setting,
  SettingType,
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
  ISettingTypeApi,
  ISettingApi,
  AsyncApiResult,
} from "../../src/webapp/casualcms/domain/ports";
import { IApi } from "../../src/webapp/casualcms/service/api";

class FakeAccountApi implements IAccountApi {
  async byCredentials(creds: Credentials): AsyncApiResult<Account> {
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
  ): AsyncApiResult<PartialPageType[]> {
    return ok([
      {
        type: parentType ? "casual:Page" : "casual:HomePage",
        title: parentType ? "Page" : "Home Page",
      },
    ]);
  }
  async showPageType(
    authntoken: string,
    pageType: string
  ): AsyncApiResult<PageType> {
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
  pages: any[];

  constructor() {
    this.pages = [];
  }
  async createDraft(
    authntoken: string,
    type: string,
    payload: any,
    parent: string | null
  ): AsyncApiResult<boolean> {
    payload["metadata"] = {
      type: type,
      path: `${parent || ""}/${payload.slug}`,
      breadcrumb: [],
    };
    this.pages.push(payload);
    return ok(true);
  }

  async listDrafts(
    authntoken: string,
    parent: string | null
  ): AsyncApiResult<PartialDraft[]> {
    let pages: PartialDraft[] = [];

    this.pages
      .filter((page: PartialDraft) => {
        let starter = parent || "";
        starter = starter.replace(/\\(.)/gm, "$1");
        const startLen = starter.split("/").length;
        const pathLen = page.metadata.path.split("/").length;
        return (
          page.metadata.path.startsWith(starter) && pathLen == startLen + 1
        );
      })
      .map((page) =>
        pages.push({
          slug: page.slug,
          title: page.title,
          metadata: {
            path: page.metadata.path,
            type: page.metadata.type,
          },
        })
      );
    return ok(pages);
  }

  async showDraft(
    authntoken: string,
    path: string | null
  ): AsyncApiResult<Draft> {
    let pages: Draft[] = [];
    this.pages
      .filter((page) => {
        return page.metadata.path == path;
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

  async previewDraft(
    authntoken: string,
    path: string | null
  ): AsyncApiResult<string> {
    return ok(`I preview ${path}`);
  }

  async updateDraft(
    authntoken: string,
    path: string,
    page: Draft
  ): AsyncApiResult<Draft> {
    let oldPage: any | null = null;
    const pages: any[] = [];
    this.pages.map((p) => (p.path == path ? (oldPage = p) : pages.push(page)));
    if (pages.length) {
      const newPage = { ...oldPage, ...page };
      const newPath: string[] = newPage.metadata.path.split("/");
      newPath[newPath.length - 1] = page.slug;
      newPage.metadata.path = newPath.join("/");
      pages.push(newPage);
      this.pages = pages;
      return ok(newPage);
    } else {
      // FIXME
      return err(new Map());
    }
  }
  async publishPage(
    authntoken: string,
    hostname: string,
    path: string
  ): AsyncApiResult<boolean> {
    return ok(true);
  }
  async deleteDraft(authntoken: string, path: string): AsyncApiResult<boolean> {
    const pages = this.pages.filter((page: PartialDraft) => {
      return page.metadata.path != path;
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
  ): AsyncApiResult<PartialSite> {
    const postBody = { hostname: hostname, ...payload };
    this.sites.push(postBody);
    return ok(postBody);
  }

  async deleteSite(
    authntoken: string,
    hostname: string
  ): AsyncApiResult<boolean> {
    const sites = this.sites.filter((site: PartialSite) => {
      return site.hostname != hostname;
    });
    this.sites = sites;
    return ok(true);
  }

  async updateSite(
    authntoken: string,
    hostname: string,
    site: Site
  ): AsyncApiResult<boolean> {
    const sites = this.sites.filter((site: PartialSite) => {
      return site.hostname != hostname;
    });
    sites.push(site);
    this.sites = sites;
    return ok(true);
  }

  async showSite(authntoken: string, hostname: string): AsyncApiResult<Site> {
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

  async listSites(authntoken: string): AsyncApiResult<PartialSite[]> {
    return ok(this.sites as PartialSite[]);
  }
}

export class FakeSnippetApi implements ISnippetApi {
  snippets: PartialSnippet[];

  constructor() {
    this.snippets = [];
  }

  async listSnippets(authntoken: string): AsyncApiResult<PartialSnippet[]> {
    return ok(this.snippets || []);
  }

  async updateSnippet(
    authntoken: string,
    key: string,
    snippet: Snippet
  ): AsyncApiResult<boolean> {
    const typ = snippet.metadata.type;
    let snippets = this.snippets.filter((snippet: PartialSnippet) => {
      return snippet.key != key;
    });
    snippets.push(snippet);
    this.snippets = snippets;
    return ok(true);
  }

  async showSnippet(authntoken: string, key: string): AsyncApiResult<Snippet> {
    const snippets = this.snippets.filter((snippet: PartialSnippet) => {
      return snippet.key == key;
    });
    if (snippets.length == 1) {
      return ok(snippets[0]);
    }
    let apiError = new Map();
    apiError.set("key", "Snippet not found");
    return err(apiError);
  }

  async createSnippet(
    authntoken: string,
    type: string,
    payload: any
  ): AsyncApiResult<boolean> {
    let postBody: any = {
      type: type,
      payload: payload,
    };
    const titles: Record<string, string> = {
      "blog:HeaderSnippet": "Header Snippet",
      "blog:FooterSnippet": "Footer Snippet",
    };
    payload["metadata"] = { type: type, title: titles[type] };
    this.snippets.push(payload);
    return ok(true);
  }
  async deleteSnippet(
    authntoken: string,
    snippet: Snippet
  ): AsyncApiResult<boolean> {
    const snippets = this.snippets.filter((s: PartialSnippet) => {
      return s.key != snippet.key;
    });
    this.snippets = snippets;
    return ok(true);
  }
}

class FakeSnippetTypeApi implements ISnippetTypeApi {
  async listSnippetTypes(
    authntoken: string
  ): AsyncApiResult<PartialSnippetType[]> {
    return ok([
      { title: "Header Snippet", type: "blog:HeaderSnippet" },
      { title: "Footer Snippet", type: "blog:FooterSnippet" },
    ]);
  }
  async showSnippetType(
    authntoken: string,
    snippet_type: string
  ): AsyncApiResult<SnippetType> {
    return ok({
      schema: {
        title: "HeaderSnippet",
        type: "object",
        properties: {
          key: { title: "Key", type: "string" },
          title: { title: "Title", type: "string" },
          links: {
            title: "Links",
            type: "array",
            items: { $ref: "#/definitions/Link" },
          },
        },
        required: ["key", "title"],
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
        key: { "ui:widget": "text", "ui:placeholder": "key" },
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

export class FakeSettingApi implements ISettingApi {
  settings: Setting[];

  constructor() {
    this.settings = [];
  }

  async listSettings(
    authntoken: string,
    hostname: string
  ): AsyncApiResult<PartialSetting[]> {
    const settings: PartialSetting[] = [];
    this.settings.map((s) => {
      if (s.metadata.hostname == hostname) {
        settings.push({ metadata: s.metadata });
      }
    });
    return ok(settings);
  }

  async createSetting(
    authntoken: string,
    hostname: string,
    key: string,
    payload: any
  ): AsyncApiResult<boolean> {
    const setting = {
      metadata: { hostname: hostname, key: key },
      ...payload,
    };
    this.settings.push(setting);
    return ok(true);
  }
  async showSetting(
    authntoken: string,
    hostname: string,
    key: string
  ): AsyncApiResult<Setting> {
    const settings = this.settings.map((s) => {
      if (s.metadata.hostname == hostname && s.metadata.key == key) {
        return ok(s);
      }
    });
    if (settings && settings[0]) {
      return settings[0];
    }
    let errMap = new Map();
    errMap.set("key", "Setting not found for this key on this hostname");
    return err(errMap);
  }

  async updateSetting(
    authntoken: string,
    setting: Setting
  ): AsyncApiResult<boolean> {
    const settings: Setting[] = [];
    this.settings.map((s) => {
      if (
        s.metadata.hostname != s.metadata.hostname ||
        s.metadata.key != setting.metadata.key
      ) {
        settings.push(s);
      }
    });
    settings.push(setting);
    this.settings = settings;
    return ok(true);
  }

  async deleteSetting(
    authntoken: string,
    setting: Setting
  ): AsyncApiResult<boolean> {
    const key = setting.metadata.key;
    const hostname = setting.metadata.hostname;
    const settings = this.settings.filter((s: any) => {
      return s.metadata.hostname != hostname || s.metadata.key != key;
    });
    this.settings = settings;
    return ok(true);
  }
}

export class FakeSettingTypeApi implements ISettingTypeApi {
  async listSettingTypes(
    authntoken: string
  ): AsyncApiResult<PartialSettingType[]> {
    return ok([
      { title: "Feature Flags", key: "blog:ff" },
      { title: "Contact", key: "blog:contact" },
    ]);
  }
  async showSettingType(
    authntoken: string,
    key: string
  ): AsyncApiResult<SettingType> {
    const resp: SettingType = {
      schema: {
        title: "ContactSetting",
        type: "object",
        properties: { email: { title: "Email", type: "string" } },
        required: ["email"],
        definitions: {},
      },
      uiSchema: { email: { "ui:widget": "text", "ui:placeholder": "email" } },
    };
    return ok(resp);
  }
}

export class FakeApi implements IApi {
  account: IAccountApi;
  pageType: IPageTypeApi;
  page: IPageApi;
  site: ISiteApi;
  snippet: ISnippetApi;
  snippetType: ISnippetTypeApi;
  setting: ISettingApi;
  settingType: ISettingTypeApi;

  constructor() {
    this.account = new FakeAccountApi();
    this.pageType = new FakePageTypeApi();
    this.page = new FakePageApi();
    this.site = new FakeSiteApi();
    this.snippet = new FakeSnippetApi();
    this.snippetType = new FakeSnippetTypeApi();
    this.setting = new FakeSettingApi();
    this.settingType = new FakeSettingTypeApi();
  }
}
