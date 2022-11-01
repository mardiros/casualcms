import { BaseEditor } from "slate";
import { HistoryEditor } from "slate-history";
import { ReactEditor } from "slate-react";
import { Type } from "typescript";

export type FeatureType =
  | "bold"
  | "italic"
  | "underline"
  | "strikethrough"
  | "paragraph"
  | "h1"
  | "h2"
  | "h3"
  | "h4"
  | "h5"
  | "h6"
  | "ul"
  | "ol"
  | "li"
  | "blockquote"
  | "code"
  | "link";

export type NodeType =
  | "paragraph"
  | "h1"
  | "h2"
  | "h3"
  | "h4"
  | "h5"
  | "h6"
  | "ul"
  | "ol"
  | "li"
  | "blockquote"
  | "code"
  | "TEXT"
  | "link";

export type TypedNode = {
  type: NodeType;
  children: SlateModel;
};

export type TypedLink = TypedNode & {
  type: NodeType;
  href: string;
  children: TypedText[];
};

export type TypedText = {
  type: NodeType;
  text: string;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
};

export type TextMark = keyof Omit<TypedText, "type" | "text">;

export type TypedLeaf = TypedText;

export type SlateModel = Array<TypedNode | TypedLink | TypedLeaf>;

export type MyEditor = BaseEditor & ReactEditor & HistoryEditor;

declare module "slate" {
  interface CustomTypes {
    Editor: BaseEditor;
    Element: TypedNode;
    Text: TypedLeaf;
  }
}
