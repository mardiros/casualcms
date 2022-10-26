import React from "react";
import { Editor, Transforms } from "slate";
import { useSlate } from "slate-react";
import { IconButton } from "@chakra-ui/react";

import { Element as SlateElement } from "slate";
import { EditorProps, NodeType, TypedNode } from "../types";
import { MyElement } from "../renderer";

const isBlockActive = (editor: EditorProps, format: string) => {
  const nodeGen = Editor.nodes(editor, {
    match: (node) => {
      const n = node as TypedNode;
      return (
        !Editor.isEditor(n) && SlateElement.isElement(n) && n.type === format
      );
    },
  });

  let node = nodeGen.next();
  while (!node.done) {
    return true;
  }
  return false;
};

const toggleBlock = (editor: EditorProps, format: NodeType) => {
  const isActivating = !isBlockActive(editor, format);

  const newProperties: Partial<MyElement> = {
    type: isActivating ? format : "paragraph",
  };
  Transforms.setNodes(editor, newProperties);
};

export const toggleListBlock = (editor: EditorProps, format: NodeType) => {
  const isActivating = !isBlockActive(editor, format);

  const newProperties: Partial<MyElement> = {
    type: isActivating ? "li" : "paragraph",
  };
  Transforms.setNodes(editor, newProperties);

  if (isActivating) {
    const block = { type: format, children: [] };
    Transforms.wrapNodes(editor, block);
  } else {
    Transforms.unwrapNodes(editor, {
      match: (n) =>
        !Editor.isEditor(n) &&
        SlateElement.isElement(n) &&
        ["ul", "ol", "li"].includes((n as TypedNode).type),
      split: true,
    });
  }
};

export const toggleMultilineBlock = (editor: EditorProps, format: NodeType) => {
  const isActivating = !isBlockActive(editor, format);

  const newProperties: Partial<MyElement> = {
    type: isActivating ? format : "paragraph",
  };
  Transforms.setNodes(editor, newProperties);

  if (isActivating) {
    const block = { type: format, children: [] };
    Transforms.wrapNodes(editor, block);
  } else {
    Transforms.unwrapNodes(editor, {
      match: (n) =>
        !Editor.isEditor(n) &&
        SlateElement.isElement(n) &&
        [format].includes((n as TypedNode).type),
      split: true,
    });
  }
};

type BlockButtonProps = {
  format: NodeType;
  icon: React.ReactElement;
  toggleFn?: (editor: EditorProps, format: NodeType) => void;
};

export const BlockButton = ({ format, icon, toggleFn }: BlockButtonProps) => {
  const editor = useSlate();
  const callback = toggleFn || toggleBlock;
  return (
    <IconButton
      variant="outline"
      colorScheme="green"
      isActive={isBlockActive(editor, format)}
      onMouseDown={(event) => {
        event.preventDefault();
        callback(editor, format);
      }}
      aria-label={format}
      icon={icon}
      borderWidth={0}
      fontSize={"20px"}
    />
  );
};
