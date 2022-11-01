import React from "react";
import { Editor } from "slate";
import { IconButton } from "@chakra-ui/react";

import { MyEditor, TextMark } from "../types";
import { useMyEditor } from "../hooks";

const isMarkActive = (editor: MyEditor, format: TextMark) => {
  const marks = Editor.marks(editor);
  if (marks) {
    return (marks[format] as boolean) === true;
  }
  return false;
};

export const toggleMark = (editor: MyEditor, format: TextMark): void => {
  const isActive = isMarkActive(editor, format);
  if (isActive) {
    Editor.removeMark(editor, format);
  } else {
    Editor.addMark(editor, format, true);
  }
};

export const MarkButton = ({
  format,
  icon,
}: {
  format: TextMark;
  icon: React.ReactElement;
}) => {
  const editor = useMyEditor();
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
