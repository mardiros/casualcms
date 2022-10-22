import { Box } from "@chakra-ui/react";
import React from "react";

import { createEditor } from "slate";
import { withHistory } from "slate-history";
import { Editable, withReact, Slate } from "slate-react";
import { fromHtml } from "./parser";

type RichTextEditorProps = {
  value: string;
};

export const RichTextEditor: React.FunctionComponent<RichTextEditorProps> = (
  props: RichTextEditorProps
) => {
  const { value } = props;
  const editor = React.useMemo(
    () => withHistory(withReact(createEditor())),
    []
  );
  return (
    <Box minW="720px">
      <Slate editor={editor} value={fromHtml(value)}>
        <Box padding={"15px 5px"}>
          <Editable
            placeholder="Lorem ipsum dolor sit amet, ..."
            style={{ minHeight: "150px", overflow: "auto" }}
          />
        </Box>
      </Slate>
    </Box>
  );
};
