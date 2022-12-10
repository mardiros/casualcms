import React from "react";
import { useNavigate } from "react-router-dom";
import { Snippet } from "../../../casualcms/domain/model";
import { useConfig } from "../../../config";
import { DeletePopoverForm } from "../../components/confirm";
import { useAuth } from "../login/hooks";

type SnippetDeletePopoverFormProps = {
  curSnippet: Snippet;
};

export const SnippetDeletePopoverForm: React.FunctionComponent<
  SnippetDeletePopoverFormProps
> = (props: SnippetDeletePopoverFormProps) => {
  const navigate = useNavigate();
  const config = useConfig();
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curSnippet = props.curSnippet;
  const snippetType = curSnippet.metadata.type;
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

  return <DeletePopoverForm button_label="Delete this snippet" onSubmit={onSubmit} />;
};
