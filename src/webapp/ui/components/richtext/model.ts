import { Node } from "slate";

export type NodeType =
  | "paragraph"
  | "strong"
  | "heading1"
  | "heading2"
  | "heading3"
  | "heading4"
  | "heading5"
  | "heading6"
  | "block-quote"
  | "bulleted-list"
  | "image"
  | "link"
  | "list-item"
  | "numbered-list"
  | "pre"
  | "TEXT";

export type TypedNode = Node & {
  type: NodeType;
  attrs?: { [key: string]: any } | undefined;
};

export type SlateModel = Array<TypedNode>;
