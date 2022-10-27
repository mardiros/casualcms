import { BaseEditor } from "slate";
import { HistoryEditor } from "slate-history";
import { ReactEditor } from "slate-react";

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
  | "image"
  | "TEXT"
  | "LINKTEXT"
  | "link";

export type TypedNode = {
  type: NodeType;
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

export type TypedLeafImage = {
  type: NodeType;
  id: string;
  text: string;  // serialized as src attribute
  alt?: string;
};

export type TypedLeaf = TypedLeafImage & TypedText;

export type SlateModel = Array<TypedNode | TypedLeaf>;

export type MyEditor = BaseEditor & ReactEditor & HistoryEditor

declare module 'slate' {
  interface CustomTypes {
    Editor: BaseEditor
    Element: TypedNode
    Text: TypedLeaf
  }
}
