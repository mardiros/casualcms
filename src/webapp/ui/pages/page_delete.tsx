import React from "react";
import { useNavigate } from "react-router-dom";
import { Draft } from "../../casualcms/domain/model";
import { AppContext } from "../../config";
import { DeletePopoverForm } from "../layout/confirm";
import { useAuth } from "../login/hooks";

type PageDeletePopoverFormProps = {
  curPage: Draft;
};

export const PageDeletePopoverForm: React.FunctionComponent<
  PageDeletePopoverFormProps
> = (props: PageDeletePopoverFormProps) => {

  const navigate = useNavigate();
  const config = React.useContext(AppContext);
  let auth = useAuth();
  const token = auth.authenticatedUser?.token || "";
  const curPage = props.curPage;

  const [confirmed, setConfirmed] = React.useState<boolean>(false);

  const onSubmit = async () => {
    await config.api.draft.deleteDraft(token, curPage.meta.path);
    setConfirmed(true);
  };

  React.useEffect(() => {
    if (confirmed) {
      const nextPath =
      curPage.meta.breadcrumb.length >= 2
        ? curPage.meta.breadcrumb[curPage.meta.breadcrumb.length - 2].path
        : "";
      const qs = nextPath
        ? new URLSearchParams({
            parent: nextPath,
          })
        : "";
      navigate(`/admin/pages?${qs}`)
    }
  }, [confirmed]);

  return (
    <DeletePopoverForm button_label="Delete this page" onSubmit={onSubmit} />
  );
};
