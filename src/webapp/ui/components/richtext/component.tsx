import isHotkey from "is-hotkey";
import React, { useCallback } from "react";
import { BaseEditor, Descendant, Editor, Element, Transforms } from "slate";
import { HistoryEditor } from "slate-history";
import {
  ReactEditor,
  RenderElementProps,
  RenderLeafProps,
  useSlate,
} from "slate-react";
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

import { createEditor, Element as SlateElement } from "slate";
import { withHistory } from "slate-history";
import { Editable, withReact, Slate } from "slate-react";
import { fromHtml } from "./parser";
import { MdFormatBold, MdFormatListBulleted, MdFormatListNumbered, MdLooksOne, MdLooksTwo } from "react-icons/md";
import { NodeType, TypedLeaf, TypedNode } from "./types";
import { toHtml } from "./serializer";

const HOTKEYS: { [hotkey: string]: string } = {
  "mod+b": "bold",
  "mod+i": "italic",
  "mod+u": "underline",
  "mod+`": "code",
};

type EditorProps = Editor | ReactEditor | HistoryEditor;

interface MyElement extends Element {
  type: NodeType;
}

interface MyRenderElementProps extends RenderElementProps {
  element: MyElement;
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

const isBlockActive = (editor: EditorProps, format: string) => {
  const nodeGen = Editor.nodes(editor, {
    match: (node) => {
      const n = node as TypedNode;
      return !Editor.isEditor(n) && SlateElement.isElement(n) && n.type === format;
    }
  });

  let node = nodeGen.next();
  while (!node.done) {
    return true;
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


export const toggleBlock = (editor: EditorProps, format: NodeType) => {
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
    const block = { type: format, children: [] }
    Transforms.wrapNodes(editor, block)
  }
  else {
    Transforms.unwrapNodes(editor, {
      match: n =>
        !Editor.isEditor(n) &&
        SlateElement.isElement(n) &&
        ["ul", "ol", "li"].includes((n as TypedNode).type),
      split: true,
    })
  }
}


export const MyRenderElement = ({
  attributes,
  children,
  element,
}: MyRenderElementProps) => {
  switch (element.type) {
    // case "block-quote":
    //   return (
    //     <chakra.blockquote
    //       style={BlockquoteStyle}
    //       borderLeftWidth={"10px"}
    //       borderLeftColor={"gray.200"}
    //       {...attributes}
    //     >
    //       {children}
    //     </chakra.blockquote>
    //   );
    case "h1":
      return <Heading as="h1" size="3xl" {...attributes}>{children}</Heading>;
    case "h2":
      return <Heading as="h2" size="2xl" {...attributes}>{children}</Heading>;
    case "ul":
      return <UnorderedList {...attributes}>{children}</UnorderedList>;
    case "ol":
      return <OrderedList {...attributes}>{children}</OrderedList>;
    case "li":
      return <ListItem {...attributes}>{children}</ListItem>;
    default:
      return <p {...attributes}>{children}</p>;
  }
};

export const MyRenderLeaf = ({
  attributes,
  children,
  leaf,
}: MyRenderLeafProps) => {
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

type BlockButtonProps = {
  format: NodeType;
  icon: React.ReactElement;
  toggleFn?: (editor: EditorProps, format: NodeType) => void;
}
export const BlockButton = ({
  format,
  icon,
  toggleFn,
}: BlockButtonProps) => {
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

const Toolbar: React.FunctionComponent<{}> = () => {
  return (
    <HStack
      borderWidth={"0 0 1px 0"}
      padding={"10px 5px"}
      spacing={"5px"}
      wrap={"wrap"}
    >
      <MarkButton format="bold" icon={<MdFormatBold />} />
      <BlockButton format="h1" icon={<MdLooksOne />} />
      <BlockButton format="h2" icon={<MdLooksTwo />} />
      <BlockButton format="ul" icon={<MdFormatListBulleted />} toggleFn={toggleListBlock} />
      <BlockButton format="ol" icon={<MdFormatListNumbered />} toggleFn={toggleListBlock} />
    </HStack>
  );
};

type RichTextEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

export const RichTextEditor: React.FunctionComponent<RichTextEditorProps> = (
  props: RichTextEditorProps
) => {
  const { value, onChange } = props;
  const editor = React.useMemo(
    () => withHistory(withReact(createEditor())),
    []
  );

  const renderElement = useCallback(
    (props: RenderElementProps) => (
      <MyRenderElement {...(props as MyRenderElementProps)} />
    ),
    []
  );
  const renderLeaf = useCallback(
    (props: RenderLeafProps) => (
      <MyRenderLeaf {...(props as MyRenderLeafProps)} />
    ),
    []
  );

  const onModelChange = useCallback((childs: Descendant[]) => {
    onChange(toHtml(childs));
  }, []);

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
      <Slate editor={editor} value={fromHtml(value)} onChange={onModelChange}>
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
