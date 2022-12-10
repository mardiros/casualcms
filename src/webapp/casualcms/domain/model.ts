import { RJSFSchema, UiSchema } from "@rjsf/utils";

// rome-ignore lint/suspicious/noExplicitAny: a dynamic type based on json schema
export type Payload<T = any> = Record<string, T>;

export type Account = {
  id: string;
  username: string;
  token: string;
  lang: string;
};

export type PartialPageType = {
  type: string;
  title: string;
};

export type PageType = {
  // type:string;
  schema: RJSFSchema;
  uiSchema: UiSchema;
};

export type PartialPageMeta = {
  path: string;
  type: string;
  title: string;
};

export type PartialDraft = {
  slug: string;
  title: string;
  metadata: PartialPageMeta;
};

export type BreadCrumbItem = {
  slug: string;
  path: string;
  title: string;
};

export type BreadCrumb = {
  items: BreadCrumbItem[];
};

export type PageMeta = {
  path: string;
  type: string;
  breadcrumb: BreadCrumb;
};

export type Draft = {
  metadata: PageMeta;
} & Payload;

export type PartialSite = {
  hostname: string;
  default: boolean;
  root_page_path: string;
  secure: boolean;
};

export type Site = PartialSite;

export type PartialSnippetMeta = {
  type: string;
  title: string;
};

export type PartialSnippet = {
  key: string;
  metadata: PartialSnippetMeta;
};

export type Snippet = PartialSnippet;

export type PartialSnippetType = {
  type: string;
  title: string;
};

export type SnippetType = {
  // type:string;
  schema: RJSFSchema;
  uiSchema: UiSchema;
};

export type PartialSettingType = {
  key: string;
  title: string;
};

export type PartialSettingMetadata = {
  key: string;
  hostname: string;
};

export type SettingType = {
  // key:string;
  schema: RJSFSchema;
  uiSchema: UiSchema;
};

export type PartialSetting = {
  metadata: PartialSettingMetadata;
};

export type Setting = {
  metadata: PartialSettingMetadata;
} & Payload;
