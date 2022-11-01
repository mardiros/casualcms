import { NodeType, SlateModel, TypedLeaf, TypedNode } from "./types";
const NODE_TYPE_TEXT = 3;

export const createText = (
  text: string | null,
  attrs?: { [key: string]: boolean }
): TypedLeaf => {
  return {
    type: "TEXT",
    text: text || "",
    bold: attrs?.bold || false,
    italic: attrs?.italic || false,
    underline: attrs?.underline || false,
    strikethrough: attrs?.strikethrough || false,
  };
};

export const createNode = (
  type: NodeType,
  children: SlateModel = []
): TypedNode => {
  const ret: TypedNode = {
    type: type,
    children: children,
  };
  return ret;
};

const deserializeNode = (el: ChildNode): TypedNode | TypedLeaf => {
  if (el.nodeType == NODE_TYPE_TEXT) {
    return createText(el.textContent);
  }

  switch (el.nodeName) {
    case "H1":
      return createNode("h1", deserializeChildNodes(el));
    case "H2":
      return createNode("h2", deserializeChildNodes(el));
    case "H3":
      return createNode("h3", deserializeChildNodes(el));
    case "H4":
      return createNode("h4", deserializeChildNodes(el));
    case "H5":
      return createNode("h5", deserializeChildNodes(el));
    case "H6":
      return createNode("h6", deserializeChildNodes(el));
    case "P":
      return createNode("paragraph", deserializeChildNodes(el));
    case "UL":
      return createNode("ul", deserializeChildNodes(el));
    case "OL":
      return createNode("ol", deserializeChildNodes(el));
    case "LI":
      return createNode("li", deserializeChildNodes(el));
    case "PRE":
      return createNode("code", deserializeChildNodes(el));
    case "BLOCKQUOTE":
      return createNode("blockquote", deserializeChildNodes(el));

    // Leafs
    // case "B":
    case "STRONG":
      return createText(el.textContent, { bold: true });
    case "EM":
      return createText(el.textContent, { italic: true });
    case "U":
      return createText(el.textContent, { underline: true });
    case "S":
      return createText(el.textContent, { strikethrough: true });
  }

  return createText("");
};

const deserializeChildNodes = (el: ChildNode): SlateModel => {
  if (!el.hasChildNodes()) {
    return [createText(el.textContent)];
  }

  const nodes: SlateModel = [];
  el.childNodes.forEach((e) => nodes.push(deserializeNode(e)));
  return nodes;
};

export const defaultModel = (): SlateModel => {
  return [createNode("paragraph")];
};

export const fromHtml = (html: string): SlateModel => {
  if (!html || html.trim().length === 0) {
    return defaultModel();
  }

  // parse html into a DOM document
  const document = new DOMParser().parseFromString(html, "text/html");
  const nodes: SlateModel = [];
  document.body.childNodes.forEach((node) => {
    nodes.push(deserializeNode(node));
  });
  return nodes;
};
