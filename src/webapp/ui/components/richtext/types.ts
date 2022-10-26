import { Editor, Node, Text } from "slate";
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

export type TypedNode = Node & {
  type: NodeType;
};

export type TypedLink = TypedNode & {
  type: NodeType;
  href: string;
  children: TypedText[];
};

export type TypedText = Text & {
  type: NodeType;
  bold?: boolean;
  italic?: boolean;
  underline?: boolean;
  strikethrough?: boolean;
};

export type TypedLeafImage = Text & {
  type: NodeType;
  id: string;
  alt?: string;
};

export type TypedLeaf = TypedLeafImage | TypedText;

export type SlateModel = Array<TypedNode | TypedLeaf>;

export type EditorProps = Editor | ReactEditor | HistoryEditor;
