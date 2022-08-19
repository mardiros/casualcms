import React from "react";
import { Navigate } from "react-router-dom";
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
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curSnippet = props.curSnippet;

  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.snippet.deleteSnippet(token, curSnippet.slug);
    setConfirmed(true);
  };

  if (confirmed) {
    return <Navigate to="/admin/snippets" replace />;
  }

  return (
    <DeletePopoverForm button_label="Delete this snippet" onSubmit={onSubmit} />
  );
};
