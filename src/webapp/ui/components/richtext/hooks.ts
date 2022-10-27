import { useSlate } from "slate-react"
import { MyEditor } from "./types"

export const useMyEditor: () => MyEditor = () => {
  return useSlate() as MyEditor;
}
