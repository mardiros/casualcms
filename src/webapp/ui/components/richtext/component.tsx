import isHotkey from "is-hotkey";
import React, { useCallback } from "react";
import { Editor, Element} from "slate";
import { HistoryEditor } from "slate-history";
import { ReactEditor, RenderElementProps, RenderLeafProps, useSlate } from "slate-react";
import {
  Box,
  HStack,
  chakra,
  ListItem,
  OrderedList,
  UnorderedList,
  Heading,
  IconButton,
} from "@chakra-ui/react";

import { createEditor } from "slate";
import { withHistory } from "slate-history";
import { Editable, withReact, Slate } from "slate-react";
import { fromHtml } from "./parser";
import { MdFormatBold } from "react-icons/md";
import { NodeType, TypedLeaf } from "./types";

const HOTKEYS: { [hotkey: string]: string } = {
  "mod+b": "bold",
  "mod+i": "italic",
  "mod+u": "underline",
  "mod+`": "code",
};

type RichTextEditorProps = {
  value: string;
};

type EditorProps = Editor | ReactEditor | HistoryEditor;


interface MyElement extends Element {
  type: NodeType;
}

interface MyRenderElementProps extends RenderElementProps {
  element: MyElement
}


interface MyRenderLeafProps extends RenderLeafProps {
  leaf: TypedLeaf;
}

const BlockquoteStyle: React.CSSProperties | undefined = {
  margin: "1.5em 10px",
  padding: "0.5em 10px",
};


const isMarkActive = (editor: EditorProps, format: string) => {
  const marks = Editor.marks(editor);
  if (marks) {
    const myMarks = marks as TypedLeaf;
    const myFormat = format as keyof TypedLeaf;
    return myMarks[myFormat] === true;
  }
  return false;
};

export const toggleMark = (editor: EditorProps, format: string): void => {
  const isActive = isMarkActive(editor, format);
  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
};


export const MyRenderElement = ({
  attributes,
  children,
  element,
}: MyRenderElementProps) => {
  switch (element.type) {
    case "block-quote":
      return (
        <chakra.blockquote
          style={BlockquoteStyle}
          borderLeftWidth={"10px"}
          borderLeftColor={"gray.200"}
          {...attributes}
        >
          {children}
        </chakra.blockquote>
      );
    case "list-item":
      return <ListItem {...attributes}>{children}</ListItem>;
    case "numbered-list":
      return <OrderedList {...attributes}>{children}</OrderedList>;
    case "bulleted-list":
      return <UnorderedList {...attributes}>{children}</UnorderedList>;
    case "heading1":
      return (
        <Heading as="h1" size="3xl" {...attributes}>
          {children}
        </Heading>
      );
    case "heading2":
      return (
        <Heading as="h2" size="2xl" {...attributes}>
          {children}
        </Heading>
      );
    default:
      return <p {...attributes}>{children}</p>;
  }
};


export const MyRenderLeaf = ({ attributes, children, leaf }: MyRenderLeafProps) => {

  if (leaf.bold) {
    children = <strong>{children}</strong>;
  }

  return <span {...attributes}>{children}</span>;
};


export const MarkButton = ({
  format,
  icon,
}: {
  format: string;
  icon: React.ReactElement;
}) => {
  const editor = useSlate();
  return (
    <IconButton
      variant="outline"
      colorScheme="blue"
      isActive={isMarkActive(editor, format)}
      onMouseDown={(event) => {
        event.preventDefault();
        toggleMark(editor, format);
      }}
      aria-label={format}
      icon={icon}
      borderWidth={0}
      fontSize={"20px"}
    />
  );
};

const Toolbar: React.FunctionComponent<{}> = () => {
  return (
    <HStack
      borderWidth={"0 0 1px 0"}
      padding={"10px 5px"}
      spacing={"5px"}
      wrap={"wrap"}
    >
      <MarkButton format="bold" icon={<MdFormatBold />} />
    </HStack>
  );
};


export const RichTextEditor: React.FunctionComponent<RichTextEditorProps> = (
  props: RichTextEditorProps
) => {
  const { value } = props;
  const editor = React.useMemo(
    () => withHistory(withReact(createEditor())),
    []
  );

  const renderElement = useCallback(
    (props: RenderElementProps) => <MyRenderElement {...props as MyRenderElementProps} />,
    []
  );
  const renderLeaf = useCallback(
    (props: RenderLeafProps) => <MyRenderLeaf {...props as MyRenderLeafProps} />,
    []
  );

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    for (const hotkey in HOTKEYS) {
      if (isHotkey(hotkey, event as any)) {
        event.preventDefault();
        const mark = HOTKEYS[hotkey];
        toggleMark(editor, mark);
      }
    }
  };


  return (
    <Box minW="720px">
      <Slate editor={editor} value={fromHtml(value)}>
        <Box padding={"15px 5px"}>
          <Toolbar />
          <Editable
            placeholder="Lorem ipsum dolor sit amet, ..."
            renderElement={renderElement}
            renderLeaf={renderLeaf}
            onKeyDown={onKeyDown}
            style={{ minHeight: "150px", overflow: "auto" }}
          />
        </Box>
      </Slate>
    </Box>
  );
};
