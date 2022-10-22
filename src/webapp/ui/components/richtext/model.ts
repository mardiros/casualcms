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

export interface TypedNode {
  type: NodeType;  // just why :/
}
