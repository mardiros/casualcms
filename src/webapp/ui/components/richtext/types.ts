import { Node, Text } from "slate";

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
  | "link";

export type TypedNode = Node & {
  type: NodeType;
};

export type TypedLeaf = Text & {
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
};

export type SlateModel = Array<TypedNode | TypedLeaf>;
