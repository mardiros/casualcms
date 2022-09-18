import React from "react";
import { useNavigate } from "react-router-dom";
import { Snippet } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type SnippetDeletePopoverFormProps = {
  curSnippet: Snippet;
};

export const SnippetDeletePopoverForm: React.FunctionComponent<
  SnippetDeletePopoverFormProps
> = (props: SnippetDeletePopoverFormProps) => {
  const navigate = useNavigate();
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curSnippet = props.curSnippet;
  const snippetType = curSnippet.meta.type;
  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.snippet.deleteSnippet(token, curSnippet);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      navigate(`/admin/snippets/${snippetType}`);
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this snippet" onSubmit={onSubmit} />
  );
};
