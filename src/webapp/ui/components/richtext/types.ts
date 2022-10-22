import { Node, Text } from "slate";

export type NodeType =
  | "paragraph"
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
  | "pre";

export type TypedNode = Node & {
  type: NodeType;
};

export type TypedLeaf = Text & {
  bold?: boolean;
};

export type SlateModel = Array<TypedNode | TypedLeaf>;
