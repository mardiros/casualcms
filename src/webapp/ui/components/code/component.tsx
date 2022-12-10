import React from "react";
import { Box, Select, Textarea } from "@chakra-ui/react";
import { WidgetProps } from "@rjsf/utils";
import { ChevronDownIcon } from "@chakra-ui/icons";

export const CodeEditor: React.FunctionComponent<WidgetProps> = (
  props: WidgetProps,
) => {
  const { options, value, onChange } = props;
  let lang = value?.lang || null;
  let code = value?.code || "";

  const onLangChange = React.useCallback(
    (evt: React.ChangeEvent<HTMLSelectElement>) => {
      evt.preventDefault();
      if (evt.target) {
        lang = evt.target?.value;
        onChange({ lang: lang, code: code });
      }
    },
    [],
  );
  let isSaving: NodeJS.Timeout | null = null;
  const onCodeChange = React.useCallback(
    (evt: React.ChangeEvent<HTMLTextAreaElement>) => {
      evt.preventDefault();
      function saveChange() {
        if (isSaving) {
          clearTimeout(isSaving);
        }
        isSaving = setTimeout(() => {
          try {
            code = evt.target?.value || "";
            onChange({ lang: lang, code: code });
          } catch (e) {
            console.log(e);
          } finally {
            isSaving = null;
          }
        }, 150);
      }
      saveChange();
    },
    [],
  );

  return (
    <Box minW="720px">
      <Select
        icon={<ChevronDownIcon />}
        onChange={onLangChange}
        variant="outline"
        size="md"
      >
        <option value="python" selected={lang === "python"}>
          Python
        </option>
        <option value="typescript" selected={lang === "typescript"}>
          Typescript
        </option>
        <option value="bash" selected={lang === "bash"}>
          Bash
        </option>
      </Select>
      <Textarea onChange={onCodeChange} />
    </Box>
  );
};
