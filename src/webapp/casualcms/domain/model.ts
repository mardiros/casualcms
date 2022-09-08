import { JSONSchema7 } from "json-schema";

export type Account = {
  id: string;
  username: string;
  token: string;
  lang: string;
};

export type PartialPageType = {
  type: string;
};

export type PageType = {
  // type:string;
  schema: JSONSchema7;
  uiSchema: any;
};

export type PartialPageMeta = {
  path: string;
  type: string;
};

export type PartialDraft = {
  slug: string;
  title: string;
  meta: PartialPageMeta;
};

export type BreadCrumbItem = {
  slug: string;
  path: string;
  title: string;
};

export type PageMeta = {
  path: string;
  type: string;
  breadcrumb: BreadCrumbItem[];
};

export type Draft = {
  meta: PageMeta;
  [k: string]: any;
};

export type PartialSite = {
  hostname: string;
  default: boolean;
  root_page_path: string;
  secure: boolean;
};

export type Site = PartialSite;

export type PartialSnippetMeta = {
  type: string;
};

export type PartialSnippet = {
  slug: string;
  meta: PartialSnippetMeta;
};

export type Snippet = PartialSnippet;

export type PartialSnippetType = {
  type: string;
};

export type SnippetType = {
  // type:string;
  schema: JSONSchema7;
  uiSchema: any;
};

export type PartialSettingType = {
  key: string;
};

export type SettingType = {
  // key:string;
  schema: JSONSchema7;
  uiSchema: any;
};

export type PartialSetting = {
  meta: PartialSettingType;
  hostname: string;
};

export type Setting = {
  meta: PartialSettingType;
  [k: string]: any;
};
