import isHotkey from "is-hotkey";
import React from "react";
import { Descendant } from "slate";
import { RenderElementProps, RenderLeafProps } from "slate-react";
import { Box } from "@chakra-ui/react";

import { createEditor } from "slate";
import { withHistory } from "slate-history";
import { Editable, withReact, Slate } from "slate-react";
import { fromHtml } from "./parser";
import { toHtml } from "./serializer";
import {
  MyRenderElement,
  MyRenderElementProps,
  MyRenderLeaf,
  MyRenderLeafProps,
} from "./renderer";
import { Toolbar } from "./toolbar/component";
import { toggleMark } from "./toolbar/mark_btn";
import { TypedNode } from "./types";

const HOTKEYS: { [hotkey: string]: string } = {
  "mod+b": "bold",
  "mod+i": "italic",
  "mod+u": "underline",
  "mod+`": "code",
};

type RichTextEditorProps = {
  value: string;
  onChange: (value: string) => void;
};

const withInlines = (editor: any) => {
  const { insertData, insertText, isInline } = editor;

  editor.isInline = (element: TypedNode) =>
    ["link"].includes(element.type) || isInline(element);

  // editor.insertText = text => {
  //   if (text && isUrl(text)) {
  //     wrapLink(editor, text)
  //   } else {
  //     insertText(text)
  //   }
  // }
  // editor.insertData = (data: any) => {
  //   const text = data.getData('text/plain')

  //   if (text && isUrl(text)) {
  //     wrapLink(editor, text)
  //   } else {
  //     insertData(data)
  //   }
  // }

  return editor;
};

export const RichTextEditor: React.FunctionComponent<RichTextEditorProps> = (
  props: RichTextEditorProps
) => {
  const { value, onChange } = props;
  const editor = React.useMemo(
    () => withInlines(withHistory(withReact(createEditor()))),
    []
  );

  const renderElement = React.useCallback(
    (props: RenderElementProps) => (
      <MyRenderElement {...(props as MyRenderElementProps)} />
    ),
    []
  );
  const renderLeaf = React.useCallback(
    (props: RenderLeafProps) => (
      <MyRenderLeaf {...(props as MyRenderLeafProps)} />
    ),
    []
  );

  const onModelChange = React.useCallback((childs: Descendant[]) => {
    // FIXME: antispam here
    console.log(toHtml(childs));
    try {
      onChange(toHtml(childs));
    } catch (e) {
      console.log(e);
    }
  }, []);

  const onKeyDown = (event: React.KeyboardEvent<HTMLDivElement>) => {
    for (const hotkey in HOTKEYS) {
      if (isHotkey(hotkey, event as any)) {
        event.preventDefault();
        const mark = HOTKEYS[hotkey];
        toggleMark(editor, mark);
      }
    }

    // https://github.com/ianstormtaylor/slate/blob/5e7815eded3677177334f0b511944460687f3ded/site/examples/inlines.tsx#L69

    // Default left/right behavior is unit:'character'.
    // This fails to distinguish between two cursor positions, such as
    // <inline>foo<cursor/></inline> vs <inline>foo</inline><cursor/>.
    // Here we modify the behavior to unit:'offset'.
    // This lets the user step into and out of the inline without stepping over characters.
    // You may wish to customize this further to only use unit:'offset' in specific cases.
    // if (editor.selection && SlateRange.isCollapsed(editor.selection)) {
    //   const { nativeEvent } = event
    //   if (isKeyHotkey('left', nativeEvent)) {
    //     event.preventDefault()
    //     Transforms.move(editor, { unit: 'offset', reverse: true })
    //     return
    //   }
    //   if (isKeyHotkey('right', nativeEvent)) {
    //     event.preventDefault()
    //     Transforms.move(editor, { unit: 'offset' })
    //     return
    //   }
    // }
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
            style={{
              minHeight: "150px",
              resize: "both",
              overflow: "auto",
              width: "100%",
            }}
          />
        </Box>
      </Slate>
    </Box>
  );
};
